import json
from app.main import app
from fastapi.testclient import TestClient
from app.database import engine, init_db
from sqlalchemy import inspect


def main():
    print("=== 1. VERIFY DATABASE TABLES ===")
    init_db()
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print("Tables in microloans.db:", tables)
    expected_tables = {
        "borrowers",
        "loans",
        "transactions",
        "repayments",
        "predictions",
        "recommendations",
    }
    assert expected_tables.issubset(set(tables)), f"Missing tables: {expected_tables - set(tables)}"

    print("\n=== 2. VERIFY API ENDPOINTS VIA TESTCLIENT ===")
    with TestClient(app) as client:
        # Health check
        health = client.get("/health").json()
        print("Health Check:", health)
        assert health["status"] == "healthy"
        assert health["database"] == "connected"

        # List Borrowers
        res = client.get("/api/borrowers")
        assert res.status_code == 200
        borrowers = res.json()
        print(f"Total Borrowers: {len(borrowers)}")
        assert len(borrowers) == 5, f"Expected 5 borrowers, got {len(borrowers)}"

        for b in borrowers:
            print(f"  [{b['borrower_id']}] {b['name']} ({b['occupation']}) - Stress: {b['latest_stress_level']} | Persistent: {b['persistent_stress']}")

        # Verify Borrower A (LOW stress)
        b_a = client.get("/api/borrowers/1").json()
        assert b_a["recommendations"][0]["stress_level"] == "LOW"
        assert b_a["recommendations"][0]["persistent_stress"] is False

        # Verify Borrower B (MEDIUM stress)
        b_b = client.get("/api/borrowers/2").json()
        assert b_b["recommendations"][0]["stress_level"] == "MEDIUM"
        assert b_b["recommendations"][0]["persistent_stress"] is False

        # Verify Borrower C (HIGH stress, persistent_stress=True)
        b_c = client.get("/api/borrowers/3").json()
        assert b_c["recommendations"][0]["stress_level"] == "HIGH"
        assert b_c["recommendations"][0]["persistent_stress"] is True

        # Verify Borrower D (LOW stress seasonal recovery)
        b_d = client.get("/api/borrowers/4").json()
        assert b_d["recommendations"][0]["stress_level"] == "LOW"
        assert b_d["recommendations"][0]["persistent_stress"] is False

        # Verify Borrower E (SEVERE stress, persistent_stress=True)
        b_e = client.get("/api/borrowers/5").json()
        assert b_e["recommendations"][0]["stress_level"] == "SEVERE"
        assert b_e["recommendations"][0]["persistent_stress"] is True

        # Verify sub-endpoints
        loans = client.get("/api/borrowers/1/loans").json()
        assert len(loans) == 1
        txs = client.get("/api/borrowers/1/transactions").json()
        assert len(txs) == 6
        reps = client.get("/api/borrowers/1/repayments").json()
        assert len(reps) == 5
        preds = client.get("/api/borrowers/1/predictions").json()
        assert len(preds) == 1
        recs = client.get("/api/borrowers/1/recommendations").json()
        assert len(recs) == 1

        # Verify Dashboard Summary
        summary = client.get("/api/dashboard/summary").json()
        print("\nDashboard Summary:")
        print(json.dumps(summary, indent=2))
        assert summary["total_borrowers"] == 5
        assert summary["total_loans"] == 5
        assert summary["persistent_stress_count"] == 2
        assert summary["stress_distribution"] == {
            "LOW": 2,
            "MEDIUM": 1,
            "HIGH": 1,
            "SEVERE": 1,
        }

        # Verify 404 behavior
        not_found = client.get("/api/borrowers/999")
        assert not_found.status_code == 404
        assert not_found.json()["detail"] == "Borrower with id 999 not found"

    print("\nALL DATABASE AND API ENDPOINT TESTS PASSED!")


if __name__ == "__main__":
    main()
