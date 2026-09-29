"""Data Preprocessing & Feature Engineering Module.

Prepares historical financial records for cash-flow regression and repayment stress classification.
Uses temporal splitting to avoid data leakage.
"""
import math
from pathlib import Path
from typing import Tuple, List, Dict, Any
import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
BORROWERS_CSV = DATA_DIR / "borrowers.csv"
TRANSACTIONS_CSV = DATA_DIR / "borrower_transactions.csv"


def load_raw_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Loads borrowers and transaction datasets."""
    borrowers_df = pd.read_csv(BORROWERS_CSV)
    transactions_df = pd.read_csv(TRANSACTIONS_CSV)
    transactions_df["date"] = pd.to_datetime(transactions_df["date"])
    transactions_df = transactions_df.sort_values(by=["borrower_id", "date"]).reset_index(drop=True)
    return borrowers_df, transactions_df


def create_cashflow_dataset() -> Tuple[pd.DataFrame, List[str], List[str]]:
    """Engineers lag and rolling features for predicting next month's income and expenses.

    Features created:
    - Lag 1, 2, 3 of income and expenses
    - 3-month rolling mean and standard deviation of income and expenses
    - Month cyclical encodings (month_sin, month_cos)
    - Loan EMI and borrower age

    Targets:
    - target_next_income (income in t+1)
    - target_next_expenses (expenses in t+1)
    """
    borrowers_df, df = load_raw_data()

    # Merge borrower metadata
    df = df.merge(
        borrowers_df[["borrower_id", "age", "loan_amount"]],
        on="borrower_id",
        how="left",
    )

    records = []
    # Group by borrower to compute lag and rolling features per borrower
    for b_id, b_group in df.groupby("borrower_id"):
        b_group = b_group.sort_values("date").reset_index(drop=True)
        n = len(b_group)

        for i in range(3, n - 1):  # Need at least 3 previous months and 1 future month
            curr = b_group.iloc[i]
            prev1 = b_group.iloc[i - 1]
            prev2 = b_group.iloc[i - 2]
            prev3 = b_group.iloc[i - 3]
            next_row = b_group.iloc[i + 1]

            inc_3m = [prev2["income"], prev1["income"], curr["income"]]
            exp_3m = [prev2["expenses"], prev1["expenses"], curr["expenses"]]

            month_num = curr["date"].month
            month_sin = math.sin(2 * math.pi * month_num / 12)
            month_cos = math.cos(2 * math.pi * month_num / 12)

            feat = {
                "borrower_id": b_id,
                "date": curr["date"],
                "age": curr["age"],
                "loan_amount": curr["loan_amount"],
                "emi_amount": curr["emi_amount"],
                "income_lag_1": curr["income"],
                "income_lag_2": prev1["income"],
                "income_lag_3": prev2["income"],
                "expense_lag_1": curr["expenses"],
                "expense_lag_2": prev1["expenses"],
                "expense_lag_3": prev2["expenses"],
                "available_cash_lag_1": curr["available_cash"],
                "income_roll_mean_3": float(np.mean(inc_3m)),
                "income_roll_std_3": float(np.std(inc_3m)),
                "expense_roll_mean_3": float(np.mean(exp_3m)),
                "expense_roll_std_3": float(np.std(exp_3m)),
                "month_sin": month_sin,
                "month_cos": month_cos,
                # Targets
                "target_next_income": next_row["income"],
                "target_next_expenses": next_row["expenses"],
            }
            records.append(feat)

    feature_df = pd.DataFrame(records)

    feature_cols = [
        "age", "loan_amount", "emi_amount",
        "income_lag_1", "income_lag_2", "income_lag_3",
        "expense_lag_1", "expense_lag_2", "expense_lag_3",
        "available_cash_lag_1",
        "income_roll_mean_3", "income_roll_std_3",
        "expense_roll_mean_3", "expense_roll_std_3",
        "month_sin", "month_cos"
    ]
    target_cols = ["target_next_income", "target_next_expenses"]

    return feature_df, feature_cols, target_cols


def create_stress_dataset() -> Tuple[pd.DataFrame, List[str], str]:
    """Engineers financial liquidity and repayment behavior features for stress classification.

    Stress Classes:
    - LOW: Available cash >= 1.5 * EMI and on-time payments
    - MEDIUM: 0 < Available cash < 1.5 * EMI or minor payment delay (1-10 days)
    - HIGH: Available cash <= 0 or payment delay > 10 days or missed payment
    """
    borrowers_df, df = load_raw_data()
    df = df.merge(
        borrowers_df[["borrower_id", "age", "loan_amount"]],
        on="borrower_id",
        how="left",
    )

    records = []
    for b_id, b_group in df.groupby("borrower_id"):
        b_group = b_group.sort_values("date").reset_index(drop=True)
        n = len(b_group)

        for i in range(2, n):  # Need at least 2 historical periods for changes
            curr = b_group.iloc[i]
            prev = b_group.iloc[i - 1]
            prev2 = b_group.iloc[i - 2]

            avail_cash = curr["available_cash"]
            emi = curr["emi_amount"]
            days_late = curr["days_late"]
            status = curr["repayment_status"]

            # Income & expense changes (%)
            inc_change = (curr["income"] - prev["income"]) / (prev["income"] + 1e-5)
            exp_change = (curr["expenses"] - prev["expenses"]) / (prev["expenses"] + 1e-5)

            # Volatility over last 3 periods
            inc_history = [prev2["income"], prev["income"], curr["income"]]
            inc_volatility = float(np.std(inc_history) / (np.mean(inc_history) + 1e-5))

            # Count late payments in last 3 months
            late_count_3m = sum(1 for row in [prev2, prev, curr] if row["days_late"] > 0)

            # Repayment to income ratio
            rep_to_income = emi / (curr["income"] + 1e-5)

            # Cash flow trend
            cf_trend = (curr["available_cash"] - prev["available_cash"]) / (abs(prev["available_cash"]) + 1e-5)

            # Ground truth stress label
            if avail_cash >= emi * 1.5 and days_late == 0 and status == "paid":
                stress_label = "LOW"
            elif avail_cash <= 0 or days_late > 10 or status in ["late", "missed"]:
                stress_label = "HIGH"
            else:
                stress_label = "MEDIUM"

            rec = {
                "borrower_id": b_id,
                "date": curr["date"],
                "available_cash": avail_cash,
                "income_change": inc_change,
                "expense_change": exp_change,
                "emi_amount": emi,
                "repayment_to_income_ratio": rep_to_income,
                "days_late": days_late,
                "num_late_payments_3m": late_count_3m,
                "income_volatility": inc_volatility,
                "cash_flow_trend": cf_trend,
                "cash_balance": curr["cash_balance"],
                "stress_label": stress_label,
            }
            records.append(rec)

    stress_df = pd.DataFrame(records)

    feature_cols = [
        "available_cash",
        "income_change",
        "expense_change",
        "emi_amount",
        "repayment_to_income_ratio",
        "days_late",
        "num_late_payments_3m",
        "income_volatility",
        "cash_flow_trend",
        "cash_balance",
    ]
    target_col = "stress_label"

    return stress_df, feature_cols, target_col
