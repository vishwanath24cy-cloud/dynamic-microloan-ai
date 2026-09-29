"""Test script for GET /api/borrowers/{id}/recommendation endpoint across Borrowers 1-5.
"""
import json
from fastapi.testclient import TestClient
from app.main import app


def test_recommendation_api():
    print("=== TESTING /api/borrowers/{id}/recommendation ENDPOINT ===")

    with TestClient(app) as client:
        # Test all 5 demo borrowers
        for b_id in range(1, 6):
            response = client.get(f"/api/borrowers/{b_id}/recommendation")
            assert response.status_code == 200, f"Expected 200 OK for borrower {b_id}, got {response.status_code}: {response.text}"
            data = response.json()

            print(f"\n[Borrower {b_id}: {data['borrower_name']}]")
            print(f"  Recommendation:          {data['recommendation']}")
            print(f"  Suggested Amount:        {data['suggested_payment_amount']}")
            print(f"  Suggested Structure:     {data['suggested_payment_structure']}")
            print(f"  Stress Level:            {data['stress_level']}")
            print(f"  Persistent Status:       {data['persistent_stress_status']}")
            print(f"  Lender Review Required:  {data['lender_review_required']}")
            print(f"  Reason:                  {data['reason']}")

            # Specific assertions
            if b_id == 1:
                assert data["recommendation"] == "NORMAL_PAYMENT"
                assert data["stress_level"] == "LOW"
                assert data["lender_review_required"] is False
            elif b_id == 2:
                assert data["recommendation"] in ["SPLIT_PAYMENT", "REDUCED_PAYMENT"]
                assert data["lender_review_required"] is False
            elif b_id == 3:
                assert data["recommendation"] == "REVIEW_REQUIRED"
                assert data["persistent_stress_status"] == "PERSISTENT_STRESS"
                assert data["lender_review_required"] is True
            elif b_id == 4:
                assert data["recommendation"] == "NORMAL_PAYMENT"
                assert data["stress_level"] == "LOW"
                assert data["lender_review_required"] is False
            elif b_id == 5:
                assert data["recommendation"] == "REVIEW_REQUIRED"
                assert data["persistent_stress_status"] == "SEVERE_PERSISTENT_STRESS"
                assert data["lender_review_required"] is True

        # Test non-existent borrower (404)
        not_found = client.get("/api/borrowers/999/recommendation")
        assert not_found.status_code == 404

    print("\nALL 5 BORROWER RECOMMENDATION ENDPOINT TESTS PASSED!")


if __name__ == "__main__":
    test_recommendation_api()
