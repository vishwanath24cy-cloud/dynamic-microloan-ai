"""Training & Model Selection Script for Cash-Flow Prediction.

Trains and compares:
- Linear Regression
- Random Forest Regressor

Evaluates on a held-out temporal test set using MAE, RMSE, and R2.
Saves the superior model artifacts to ml/models/.
"""
import json
from pathlib import Path
import joblib
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor

from data_preprocessing import create_cashflow_dataset
from model_evaluation import evaluate_regression

MODELS_DIR = Path(__file__).resolve().parent / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)


def train_and_select_models():
    print("=== STEP 4: CASH-FLOW PREDICTION MODEL TRAINING ===")
    df, feature_cols, target_cols = create_cashflow_dataset()
    print(f"Total engineered dataset rows: {len(df)}")
    print(f"Feature columns ({len(feature_cols)}): {feature_cols}")

    # Temporal split: Use dates up to 2026-02-28 for training (~10 months), remaining 4 months for testing
    split_date = pd.to_datetime("2026-02-28")
    train_mask = df["date"] <= split_date
    test_mask = df["date"] > split_date

    X_train = df.loc[train_mask, feature_cols]
    X_test = df.loc[test_mask, feature_cols]

    y_train_inc = df.loc[train_mask, "target_next_income"]
    y_test_inc = df.loc[test_mask, "target_next_income"]

    y_train_exp = df.loc[train_mask, "target_next_expenses"]
    y_test_exp = df.loc[test_mask, "target_next_expenses"]

    print(f"Train samples: {len(X_train)}, Test samples: {len(X_test)}")

    # -------------------------------------------------------------
    # 1. Income Prediction Models
    # -------------------------------------------------------------
    print("\n--- Training Income Models ---")
    lr_inc = LinearRegression()
    lr_inc.fit(X_train, y_train_inc)
    lr_inc_preds = lr_inc.predict(X_test)
    lr_inc_metrics = evaluate_regression(y_test_inc, lr_inc_preds)
    print(f"Linear Regression (Income): {lr_inc_metrics}")

    rf_inc = RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1)
    rf_inc.fit(X_train, y_train_inc)
    rf_inc_preds = rf_inc.predict(X_test)
    rf_inc_metrics = evaluate_regression(y_test_inc, rf_inc_preds)
    print(f"Random Forest (Income):    {rf_inc_metrics}")

    # Select best Income model based on R2
    if rf_inc_metrics["R2"] >= lr_inc_metrics["R2"]:
        best_inc_model = rf_inc
        best_inc_name = "RandomForestRegressor"
        best_inc_metrics = rf_inc_metrics
    else:
        best_inc_model = lr_inc
        best_inc_name = "LinearRegression"
        best_inc_metrics = lr_inc_metrics

    print(f"Selected Best Income Model: {best_inc_name} (R2={best_inc_metrics['R2']})")

    # -------------------------------------------------------------
    # 2. Expense Prediction Models
    # -------------------------------------------------------------
    print("\n--- Training Expense Models ---")
    lr_exp = LinearRegression()
    lr_exp.fit(X_train, y_train_exp)
    lr_exp_preds = lr_exp.predict(X_test)
    lr_exp_metrics = evaluate_regression(y_test_exp, lr_exp_preds)
    print(f"Linear Regression (Expenses): {lr_exp_metrics}")

    rf_exp = RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1)
    rf_exp.fit(X_train, y_train_exp)
    rf_exp_preds = rf_exp.predict(X_test)
    rf_exp_metrics = evaluate_regression(y_test_exp, rf_exp_preds)
    print(f"Random Forest (Expenses):    {rf_exp_metrics}")

    # Select best Expense model based on R2
    if rf_exp_metrics["R2"] >= lr_exp_metrics["R2"]:
        best_exp_model = rf_exp
        best_exp_name = "RandomForestRegressor"
        best_exp_metrics = rf_exp_metrics
    else:
        best_exp_model = lr_exp
        best_exp_name = "LinearRegression"
        best_exp_metrics = lr_exp_metrics

    print(f"Selected Best Expense Model: {best_exp_name} (R2={best_exp_metrics['R2']})")

    # -------------------------------------------------------------
    # 3. Save Selected Models & Metadata
    # -------------------------------------------------------------
    inc_model_path = MODELS_DIR / "cashflow_income_model.joblib"
    exp_model_path = MODELS_DIR / "cashflow_expense_model.joblib"
    joblib.dump(best_inc_model, inc_model_path)
    joblib.dump(best_exp_model, exp_model_path)

    metadata = {
        "feature_cols": feature_cols,
        "selected_income_model": best_inc_name,
        "income_metrics": best_inc_metrics,
        "selected_expense_model": best_exp_name,
        "expense_metrics": best_exp_metrics,
        "all_comparisons": {
            "income": {
                "LinearRegression": lr_inc_metrics,
                "RandomForestRegressor": rf_inc_metrics,
            },
            "expenses": {
                "LinearRegression": lr_exp_metrics,
                "RandomForestRegressor": rf_exp_metrics,
            },
        },
    }
    with open(MODELS_DIR / "cashflow_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"\nSaved models and metadata to {MODELS_DIR}")
    return metadata


if __name__ == "__main__":
    train_and_select_models()
