"""Inference module for cash-flow prediction.

Loads trained model artifacts and generates forward 1-month cash-flow forecasts
for a given borrower:
- predicted_income
- predicted_expenses
- predicted_available_cash (predicted_income - predicted_expenses)
"""
import json
import math
from pathlib import Path
from typing import Dict, Any, Optional
import joblib
import numpy as np
import pandas as pd

ML_DIR = Path(__file__).resolve().parent
MODELS_DIR = ML_DIR / "models"
DATA_DIR = ML_DIR.parent / "data"

INCOME_MODEL_PATH = MODELS_DIR / "cashflow_income_model.joblib"
EXPENSE_MODEL_PATH = MODELS_DIR / "cashflow_expense_model.joblib"
METADATA_PATH = MODELS_DIR / "cashflow_metadata.json"


class CashFlowPredictor:
    """Predicts next-month cash-flow components for a borrower."""

    def __init__(self):
        self._income_model = None
        self._expense_model = None
        self._metadata = None
        self._load_models()

    def _load_models(self):
        if not INCOME_MODEL_PATH.exists() or not EXPENSE_MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Trained models not found in {MODELS_DIR}. Run train_cashflow_model.py first."
            )
        self._income_model = joblib.load(INCOME_MODEL_PATH)
        self._expense_model = joblib.load(EXPENSE_MODEL_PATH)

        if METADATA_PATH.exists():
            with open(METADATA_PATH, "r", encoding="utf-8") as f:
                self._metadata = json.load(f)
        else:
            self._metadata = {}

    def predict_cashflow(self, borrower_id: int) -> Dict[str, Any]:
        """Generates forward cash-flow predictions for a borrower based on recent history.

        Args:
            borrower_id: Target borrower ID

        Returns:
            Dictionary with predicted_income, predicted_expenses, and predicted_available_cash.
        """
        # Load transactions and borrower metadata
        tx_path = DATA_DIR / "borrower_transactions.csv"
        borrowers_path = DATA_DIR / "borrowers.csv"

        if not tx_path.exists() or not borrowers_path.exists():
            raise FileNotFoundError("Borrower data files missing from data/ directory.")

        b_df = pd.read_csv(borrowers_path)
        tx_df = pd.read_csv(tx_path)

        borrower_info = b_df[b_df["borrower_id"] == borrower_id]
        if borrower_info.empty:
            raise ValueError(f"Borrower with ID {borrower_id} not found.")

        borrower_rec = borrower_info.iloc[0]
        tx_sub = tx_df[tx_df["borrower_id"] == borrower_id].copy()
        tx_sub["date"] = pd.to_datetime(tx_sub["date"])
        tx_sub = tx_sub.sort_values("date").reset_index(drop=True)

        if len(tx_sub) < 3:
            raise ValueError(f"Insufficient history for borrower {borrower_id} (requires at least 3 months).")

        # Extract last 3 months
        last_3 = tx_sub.iloc[-3:].reset_index(drop=True)
        m_t = last_3.iloc[-1]
        m_t_1 = last_3.iloc[-2]
        m_t_2 = last_3.iloc[-3]

        # Calculate forward target month cyclical features (next month after last recorded date)
        next_month_num = (m_t["date"].month % 12) + 1
        month_sin = math.sin(2 * math.pi * next_month_num / 12)
        month_cos = math.cos(2 * math.pi * next_month_num / 12)

        inc_3m = [m_t_2["income"], m_t_1["income"], m_t["income"]]
        exp_3m = [m_t_2["expenses"], m_t_1["expenses"], m_t["expenses"]]

        feature_dict = {
            "age": float(borrower_rec["age"]),
            "loan_amount": float(borrower_rec["loan_amount"]),
            "emi_amount": float(m_t["emi_amount"]),
            "income_lag_1": float(m_t["income"]),
            "income_lag_2": float(m_t_1["income"]),
            "income_lag_3": float(m_t_2["income"]),
            "expense_lag_1": float(m_t["expenses"]),
            "expense_lag_2": float(m_t_1["expenses"]),
            "expense_lag_3": float(m_t_2["expenses"]),
            "available_cash_lag_1": float(m_t["available_cash"]),
            "income_roll_mean_3": float(np.mean(inc_3m)),
            "income_roll_std_3": float(np.std(inc_3m)),
            "expense_roll_mean_3": float(np.mean(exp_3m)),
            "expense_roll_std_3": float(np.std(exp_3m)),
            "month_sin": month_sin,
            "month_cos": month_cos,
        }

        feature_cols = self._metadata.get(
            "feature_cols", list(feature_dict.keys())
        )
        x_input = pd.DataFrame([feature_dict])[feature_cols]

        pred_income = float(self._income_model.predict(x_input)[0])
        pred_expenses = float(self._expense_model.predict(x_input)[0])

        # Floor expenses realistically
        pred_income = max(0.0, round(pred_income, 2))
        pred_expenses = max(0.0, round(pred_expenses, 2))
        pred_avail_cash = round(pred_income - pred_expenses, 2)

        return {
            "borrower_id": int(borrower_id),
            "borrower_name": borrower_rec["name"],
            "financial_scenario": borrower_rec["financial_scenario"],
            "predicted_income": pred_income,
            "predicted_expenses": pred_expenses,
            "predicted_available_cash": pred_avail_cash,
            "emi_amount": float(m_t["emi_amount"]),
            "model_info": {
                "income_model": self._metadata.get("selected_income_model", "RandomForestRegressor"),
                "expense_model": self._metadata.get("selected_expense_model", "LinearRegression"),
            },
        }


# Singleton instance for direct function call
_predictor_instance: Optional[CashFlowPredictor] = None


def predict_cashflow(borrower_id: int) -> Dict[str, Any]:
    """Public functional interface to predict cash flow for a borrower."""
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = CashFlowPredictor()
    return _predictor_instance.predict_cashflow(borrower_id)


if __name__ == "__main__":
    # Smoke test on Borrower 1
    res = predict_cashflow(1)
    print("Test Prediction (Borrower 1):", res)
