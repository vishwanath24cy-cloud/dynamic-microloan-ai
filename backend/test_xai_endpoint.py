"""Test script to verify Explainable AI output in GET /api/borrowers/{id}/recommendation.
"""
from fastapi.testclient import TestClient
from app.main import app


def test_xai():
    print("=== VERIFYING EXPLAINABLE AI INTEGRATION IN RECOMMENDATION API ===")
    client = TestClient(app)

    for b_id in range(1, 6):
        res = client.get(f"/api/borrowers/{b_id}/recommendation")
        assert res.status_code == 200, f"Error {res.status_code}: {res.text}"
        data = res.json()

        print(f"\n--- Borrower {b_id}: {data['borrower_name']} ---")
        print(f"Stress Level:   {data['stress_level']}")
        print(f"Recommendation: {data['recommendation']}")
        print(f"Persistent:     {data['persistent_stress_status']}")
        print(f"Review Reqd:    {data['lender_review_required']}")
        print("Top Factors:")
        for idx, tf in enumerate(data.get("top_factors", []), 1):
            print(f"  {idx}. {tf}")
        print(f"Summary:        {data.get('summary')}")
        print(f"Explanation:    {data.get('explanation')}")

        # Assertions
        assert "summary" in data and data["summary"]
        assert "top_factors" in data and len(data["top_factors"]) > 0
        assert "explanation" in data and data["explanation"]

    print("\nALL EXPLAINABLE AI ENDPOINT TESTS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    test_xai()
