"""Validation script for Step 5 & Step 5B stress prediction across Borrowers A-E.
"""
from stress_prediction import predict_stress


def test_borrowers():
    print("=== TESTING STRESS PREDICTION & PERSISTENT STRESS ACROSS BORROWERS A-E ===")

    test_borrowers = [
        (1, "Borrower A (Aarav Sharma - Stable)"),
        (2, "Borrower B (Bhavna Patel - Temporary Downturn)"),
        (3, "Borrower C (Chirag Verma - 2 Consecutive Stress Months)"),
        (4, "Borrower D (Deepika Nair - Seasonal Income)"),
        (5, "Borrower E (Eshwar Rao - Continuous Deterioration)"),
    ]

    results = {}
    for b_id, label in test_borrowers:
        res = predict_stress(b_id)
        results[b_id] = res

        print(f"\n[{label}]")
        print(f"  Borrower ID:          {res['borrower_id']}")
        print(f"  Stress Level:         {res['stress_level']} (Confidence: {res['confidence'] * 100:.1f}%)")
        print(f"  Probabilities:        {res['class_probabilities']}")
        print(f"  Consecutive Months:   {res['persistent_stress']['consecutive_high_stress_months']}")
        print(f"  Persistent Status:    {res['persistent_stress']['persistent_stress_status']}")
        print(f"  Required Action:      {res['persistent_stress']['required_action']}")
        print(f"  Factors:              AvailCash={res['important_financial_factors']['available_cash']}, DaysLate={res['important_financial_factors']['days_late']}, Late3M={res['important_financial_factors']['late_payments_last_3m']}")

    # Verification assertions
    # Borrower A: LOW stress
    assert results[1]["stress_level"] == "LOW"
    assert results[1]["persistent_stress"]["persistent_stress_status"] == "NONE"

    # Borrower C: PERSISTENT_STRESS and LENDER_REVIEW_REQUIRED
    assert results[3]["persistent_stress"]["consecutive_high_stress_months"] >= 2, f"Expected >= 2 consecutive high stress months for Borrower C, got {results[3]['persistent_stress']['consecutive_high_stress_months']}"
    assert results[3]["persistent_stress"]["persistent_stress_status"] in ["PERSISTENT_STRESS", "SEVERE_PERSISTENT_STRESS"]
    assert "LENDER_REVIEW_REQUIRED" in results[3]["persistent_stress"]["required_action"] or "HUMAN_INTERVENTION_REQUIRED" in results[3]["persistent_stress"]["required_action"]

    # Borrower E: SEVERE_PERSISTENT_STRESS
    assert results[5]["stress_level"] == "HIGH"
    assert results[5]["persistent_stress"]["persistent_stress_status"] == "SEVERE_PERSISTENT_STRESS"
    assert results[5]["persistent_stress"]["required_action"] == "HUMAN_INTERVENTION_REQUIRED"

    print("\nALL STRESS & PERSISTENT STRESS VALIDATIONS PASSED!")


if __name__ == "__main__":
    test_borrowers()
