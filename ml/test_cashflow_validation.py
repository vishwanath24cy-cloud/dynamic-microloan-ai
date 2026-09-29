"""Validation tests for cashflow prediction on 4 distinct borrower scenarios.

Tests:
1. Stable borrower (Borrower 1)
2. Seasonal borrower (Borrower 4)
3. Temporary income downturn borrower (Borrower 2)
4. Deteriorating borrower (Borrower 5)
"""
import json
from cashflow_prediction import predict_cashflow


def run_tests():
    print("=== TESTING CASH-FLOW PREDICTIONS ACROSS SCENARIOS ===")

    test_ids = [
        (1, "Stable Income Borrower"),
        (4, "Seasonal Income Borrower"),
        (2, "Temporary Income Downturn Borrower"),
        (5, "Deteriorating Borrower"),
    ]

    results = {}
    for b_id, label in test_ids:
        res = predict_cashflow(b_id)
        results[label] = res
        print(f"\n[{label} - ID {b_id}]")
        print(f"  Name: {res['borrower_name']}")
        print(f"  Scenario: {res['financial_scenario']}")
        print(f"  Predicted Income:        INR {res['predicted_income']:,.2f}")
        print(f"  Predicted Expenses:      INR {res['predicted_expenses']:,.2f}")
        print(f"  Predicted Available Cash:INR {res['predicted_available_cash']:,.2f}")
        print(f"  Scheduled EMI:           INR {res['emi_amount']:,.2f}")
        print(f"  Models Used:             Income={res['model_info']['income_model']}, Expense={res['model_info']['expense_model']}")

        # Basic reasonableness checks
        assert res["predicted_income"] > 0, "Predicted income must be positive"
        assert res["predicted_expenses"] > 0, "Predicted expenses must be positive"
        assert round(res["predicted_available_cash"], 2) == round(res["predicted_income"] - res["predicted_expenses"], 2)

    # Scenario-specific reasonableness
    # Stable borrower should have healthy positive available cash > EMI
    assert results["Stable Income Borrower"]["predicted_available_cash"] > results["Stable Income Borrower"]["emi_amount"]

    # Deteriorating borrower should have negative or severely constricted available cash
    assert results["Deteriorating Borrower"]["predicted_available_cash"] < results["Deteriorating Borrower"]["emi_amount"]

    print("\nALL SCENARIO VALIDATION TESTS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    run_tests()
