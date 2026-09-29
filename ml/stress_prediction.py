"""Inference & Persistent Stress Detection Module.

Classifies a borrower's repayment stress (LOW, MEDIUM, HIGH) using the trained
Random Forest Classifier, and applies transparent rule-based logic to detect
consecutive high-stress months (TEMPORARY_STRESS, PERSISTENT_STRESS, SEVERE_PERSISTENT_STRESS).
"""
import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import joblib
import numpy as np
import pandas as pd

ML_DIR = Path(__file__).resolve().parent
MODELS_DIR = ML_DIR / "models"
DATA_DIR = ML_DIR.parent / "data"
BACKEND_DIR = ML_DIR.parent / "backend"

STRESS_MODEL_PATH = MODELS_DIR / "stress_classifier.joblib"
METADATA_PATH = MODELS_DIR / "stress_metadata.json"


class StressPredictor:
    """Predicts repayment stress and evaluates consecutive persistent stress."""

    def __init__(self):
        self._model = None
        self._metadata = None
        self._load_model()

    def _load_model(self):
        if not STRESS_MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Trained stress model not found at {STRESS_MODEL_PATH}. Run train_stress_model.py first."
            )
        self._model = joblib.load(STRESS_MODEL_PATH)
        if METADATA_PATH.exists():
            with open(METADATA_PATH, "r", encoding="utf-8") as f:
                self._metadata = json.load(f)
        else:
            self._metadata = {}

    def _load_borrower_history(self, borrower_id: int):
        """Loads borrower profile and transaction history from SQLite database or fallback CSV."""
        # Check SQLite DB first (especially for demo borrowers 1-5)
        try:
            if str(BACKEND_DIR) not in sys.path:
                sys.path.insert(0, str(BACKEND_DIR))
            from app.database import SessionLocal
            from app.models import Borrower, Transaction, Repayment, Loan

            db = SessionLocal()
            b = db.query(Borrower).filter(Borrower.borrower_id == borrower_id).first()
            if b and len(b.transactions) >= 3:
                loan = db.query(Loan).filter(Loan.borrower_id == borrower_id).first()
                emi = loan.emi_amount if loan else 0.0
                txs = db.query(Transaction).filter(Transaction.borrower_id == borrower_id).order_by(Transaction.date.asc()).all()
                reps = db.query(Repayment).filter(Repayment.borrower_id == borrower_id).order_by(Repayment.date.asc()).all()

                n_tx = len(txs)
                n_rep = len(reps)
                rows = []
                for i, t in enumerate(txs):
                    rep_idx = i - (n_tx - n_rep)
                    if 0 <= rep_idx < n_rep:
                        rep = reps[rep_idx]
                        days_late = rep.days_late
                        status = rep.status
                    else:
                        days_late = 0
                        status = "paid"
                    rows.append({
                        "borrower_id": borrower_id,
                        "date": pd.to_datetime(t.date),
                        "income": float(t.income),
                        "expenses": float(t.expenses),
                        "available_cash": round(float(t.income) - float(t.expenses), 2),
                        "cash_balance": float(t.cash_balance),
                        "emi_amount": emi,
                        "days_late": days_late,
                        "repayment_status": status,
                    })
                db.close()

                b_rec = {
                    "borrower_id": b.borrower_id,
                    "name": b.name,
                    "age": b.age,
                    "occupation": b.occupation,
                    "financial_scenario": (
                        "stable_income" if b.borrower_id == 1 else
                        "temporary_income_decrease" if b.borrower_id == 2 else
                        "two_consecutive_months_high_stress" if b.borrower_id == 3 else
                        "seasonal_income" if b.borrower_id == 4 else
                        "continuous_deterioration"
                    ),
                }
                return b_rec, pd.DataFrame(rows)
            db.close()
        except Exception:
            pass

        # Fallback to CSV
        tx_path = DATA_DIR / "borrower_transactions.csv"
        borrowers_path = DATA_DIR / "borrowers.csv"

        if not tx_path.exists() or not borrowers_path.exists():
            raise FileNotFoundError("Data files missing from data/ directory.")

        b_df = pd.read_csv(borrowers_path)
        tx_df = pd.read_csv(tx_path)

        b_info = b_df[b_df["borrower_id"] == borrower_id]
        if b_info.empty:
            raise ValueError(f"Borrower with ID {borrower_id} not found.")

        b_rec = b_info.iloc[0].to_dict()
        tx_sub = tx_df[tx_df["borrower_id"] == borrower_id].copy()
        tx_sub["date"] = pd.to_datetime(tx_sub["date"])
        tx_sub = tx_sub.sort_values("date").reset_index(drop=True)

        return b_rec, tx_sub

    def evaluate_persistent_stress(self, tx_sub: pd.DataFrame, current_stress_level: str) -> Dict[str, Any]:
        """Step 5B: Transparent rule-based consecutive stress detection.

        Rules:
        - 1 high-stress month -> TEMPORARY_STRESS
        - 2 consecutive high-stress months -> PERSISTENT_STRESS & LENDER_REVIEW_REQUIRED
        - 3+ consecutive high-stress months -> SEVERE_PERSISTENT_STRESS & HUMAN_INTERVENTION_REQUIRED
        """
        # Determine high-stress status for recent historical months
        # A month has HIGH stress if: available_cash <= 0, days_late > 10, or status in [late, missed]
        recent_stress_flags = []
        for _, row in tx_sub.iterrows():
            is_high = (
                row["available_cash"] <= 0
                or row["days_late"] > 10
                or row["repayment_status"] in ["late", "missed"]
            )
            recent_stress_flags.append(is_high)

        # Count consecutive HIGH stress months from the most recent cycle backwards
        consecutive_high_months = 0
        for is_high in reversed(recent_stress_flags):
            if is_high:
                consecutive_high_months += 1
            else:
                break

        # If current predicted stress is HIGH, ensure at least 1 count
        if current_stress_level == "HIGH" and consecutive_high_months == 0:
            consecutive_high_months = 1

        # Transparent rule assignments
        if consecutive_high_months >= 3:
            status = "SEVERE_PERSISTENT_STRESS"
            action = "HUMAN_INTERVENTION_REQUIRED"
            explanation = (
                f"Borrower has experienced {consecutive_high_months} consecutive months of severe cash deficit "
                f"and repayment distress. Formal credit officer intervention and loan workout required."
            )
        elif consecutive_high_months == 2:
            status = "PERSISTENT_STRESS"
            action = "LENDER_REVIEW_REQUIRED"
            explanation = (
                "High repayment stress has occurred for two consecutive months. "
                "Requires underwriter/lender review before offering structural restructuring."
            )
        elif consecutive_high_months == 1:
            status = "TEMPORARY_STRESS"
            action = "MONITOR_CLOSELY"
            explanation = (
                "Single-period liquidity stress detected. May qualify for short-term grace period or split payment."
            )
        else:
            status = "NONE"
            action = "STANDARD_OPERATION"
            explanation = "No chronic stress detected; healthy cash flow buffers."

        return {
            "consecutive_high_stress_months": consecutive_high_months,
            "persistent_stress_status": status,
            "required_action": action,
            "explanation": explanation,
        }

    def predict_stress(self, borrower_id: int) -> Dict[str, Any]:
        """Classifies repayment stress and runs transparent persistent stress rules."""
        b_rec, tx_sub = self._load_borrower_history(borrower_id)

        if len(tx_sub) < 3:
            raise ValueError(f"Insufficient history for borrower {borrower_id} (requires at least 3 months).")

        curr = tx_sub.iloc[-1]
        prev = tx_sub.iloc[-2]
        prev2 = tx_sub.iloc[-3]

        avail_cash = float(curr["available_cash"])
        emi = float(curr["emi_amount"])
        days_late = int(curr["days_late"])

        inc_change = float((curr["income"] - prev["income"]) / (prev["income"] + 1e-5))
        exp_change = float((curr["expenses"] - prev["expenses"]) / (prev["expenses"] + 1e-5))

        inc_history = [float(prev2["income"]), float(prev["income"]), float(curr["income"])]
        inc_volatility = float(np.std(inc_history) / (np.mean(inc_history) + 1e-5))

        late_count_3m = sum(1 for r in [prev2, prev, curr] if r["days_late"] > 0)
        rep_to_income = float(emi / (curr["income"] + 1e-5))
        cf_trend = float((curr["available_cash"] - prev["available_cash"]) / (abs(prev["available_cash"]) + 1e-5))
        cash_balance = float(curr["cash_balance"])

        feature_dict = {
            "available_cash": avail_cash,
            "income_change": inc_change,
            "expense_change": exp_change,
            "emi_amount": emi,
            "repayment_to_income_ratio": rep_to_income,
            "days_late": days_late,
            "num_late_payments_3m": late_count_3m,
            "income_volatility": inc_volatility,
            "cash_flow_trend": cf_trend,
            "cash_balance": cash_balance,
        }

        feature_cols = self._metadata.get("feature_cols", list(feature_dict.keys()))
        x_input = pd.DataFrame([feature_dict])[feature_cols]

        pred_class = str(self._model.predict(x_input)[0])
        probabilities = self._model.predict_proba(x_input)[0]
        class_labels = list(self._model.classes_)
        prob_dict = {lbl: round(float(prob), 4) for lbl, prob in zip(class_labels, probabilities)}
        confidence = prob_dict.get(pred_class, 1.0)

        # Evaluate persistent stress (Step 5B)
        persistent_info = self.evaluate_persistent_stress(tx_sub, pred_class)

        # Important contributing factors for transparency
        factors = {
            "available_cash": round(avail_cash, 2),
            "emi_amount": round(emi, 2),
            "cash_to_emi_ratio": round(avail_cash / (emi + 1e-5), 2),
            "days_late": days_late,
            "late_payments_last_3m": late_count_3m,
            "monthly_income_change_pct": round(inc_change * 100, 1),
            "monthly_expense_change_pct": round(exp_change * 100, 1),
            "repayment_to_income_pct": round(rep_to_income * 100, 1),
            "income_volatility": round(inc_volatility, 3),
        }

        return {
            "borrower_id": int(borrower_id),
            "borrower_name": b_rec["name"],
            "financial_scenario": b_rec.get("financial_scenario", "unknown"),
            "stress_level": pred_class,
            "confidence": confidence,
            "class_probabilities": prob_dict,
            "persistent_stress": persistent_info,
            "important_financial_factors": factors,
            "model_used": self._metadata.get("selected_model", "RandomForestClassifier"),
        }


_stress_predictor: Optional[StressPredictor] = None


def predict_stress(borrower_id: int) -> Dict[str, Any]:
    """Public functional interface to predict repayment stress for a borrower."""
    global _stress_predictor
    if _stress_predictor is None:
        _stress_predictor = StressPredictor()
    return _stress_predictor.predict_stress(borrower_id)


if __name__ == "__main__":
    for i in range(1, 6):
        res = predict_stress(i)
        print(f"Borrower {i} ({res['borrower_name']}): Stress={res['stress_level']} | Persistent={res['persistent_stress']['persistent_stress_status']} | Action={res['persistent_stress']['required_action']}")
