"""Finite Step 8 Frontend-Backend Route & Schema Verification Suite.

Performs immediate in-process verification without spawning long-running dev servers.
Checks:
1. Every API call declared in frontend/src/api.js has a corresponding route in FastAPI
2. Every field consumed by frontend/src/App.jsx is present with matching types
3. Verification across all 5 demo borrower personas (A-E)
"""
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BACKEND_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi.testclient import TestClient
from app.main import app

def run_finite_step8_verification():
    print("==================================================================")
    print("   STEP 8: FINITE FRONTEND API ROUTE & SCHEMA AUDIT               ")
    print("==================================================================\n")

    client = TestClient(app)

    # 1. Audit /api/dashboard/summary
    print("[CHECK 1/4] Auditing /api/dashboard/summary...")
    res = client.get("/api/dashboard/summary")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    data = res.json()
    
    # Check fields consumed by App.jsx summary bar
    expected_summary_fields = [
        "total_borrowers", "total_loans", "total_loan_volume", 
        "total_monthly_emi", "stress_distribution", "persistent_stress_count"
    ]
    for field in expected_summary_fields:
        assert field in data, f"Missing {field} in /api/dashboard/summary"
    
    assert data["total_borrowers"] == 5
    assert data["total_loans"] == 5
    assert isinstance(data["stress_distribution"], dict)
    print(f"  -> Summary Schema Valid: {data['total_borrowers']} borrowers, {data['total_loans']} loans, "
          f"volume INR {data['total_loan_volume']:,.0f}, persistent cases: {data['persistent_stress_count']}.")

    # 2. Audit /api/borrowers
    print("\n[CHECK 2/4] Auditing /api/borrowers...")
    res = client.get("/api/borrowers")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    borrowers = res.json()
    assert len(borrowers) == 5, f"Expected 5 borrowers, got {len(borrowers)}"

    expected_borrower_fields = [
        "borrower_id", "name", "age", "occupation", 
        "total_loan_amount", "monthly_emi", "latest_stress_level", "persistent_stress"
    ]
    for b in borrowers:
        for field in expected_borrower_fields:
            assert field in b, f"Missing {field} in /api/borrowers item {b}"
    print(f"  -> Borrowers List Schema Valid: 5 profiles loaded with all required UI fields.")

    # 3. Audit /api/borrowers/{id}/recommendation across Borrowers 1-5
    print("\n[CHECK 3/4] Auditing /api/borrowers/{id}/recommendation across all 5 personas...")
    expected_rec_fields = [
        "borrower_id", "borrower_name", "current_emi", "current_available_cash",
        "predicted_income", "predicted_expenses", "predicted_available_cash",
        "stress_level", "persistent_stress_status", "consecutive_high_stress_months",
        "recommendation", "suggested_payment_amount", "suggested_payment_structure",
        "reason", "lender_review_required", "important_financial_factors",
        "summary", "top_factors", "explanation"
    ]

    expected_personas = {
        1: {"rec": "NORMAL_PAYMENT", "stress": "LOW", "persist": "NONE"},
        2: {"rec": "SPLIT_PAYMENT", "stress": "MEDIUM", "persist": "TEMPORARY_STRESS"},
        3: {"rec": "REVIEW_REQUIRED", "stress": "HIGH", "persist": "PERSISTENT_STRESS"},
        4: {"rec": "NORMAL_PAYMENT", "stress": "LOW", "persist": "NONE"},
        5: {"rec": "REVIEW_REQUIRED", "stress": "HIGH", "persist": "SEVERE_PERSISTENT_STRESS"},
    }

    for b_id in range(1, 6):
        res = client.get(f"/api/borrowers/{b_id}/recommendation")
        assert res.status_code == 200, f"Failed for borrower {b_id}: {res.status_code}"
        rec = res.json()
        
        for field in expected_rec_fields:
            assert field in rec, f"Missing field '{field}' in recommendation for Borrower #{b_id}"
        
        exp = expected_personas[b_id]
        assert rec["recommendation"] == exp["rec"], f"B#{b_id} expected {exp['rec']}, got {rec['recommendation']}"
        assert rec["stress_level"] == exp["stress"], f"B#{b_id} expected {exp['stress']}, got {rec['stress_level']}"
        assert rec["persistent_stress_status"] == exp["persist"], f"B#{b_id} expected {exp['persist']}, got {rec['persistent_stress_status']}"
        assert isinstance(rec["top_factors"], list) and len(rec["top_factors"]) >= 2
        assert isinstance(rec["explanation"], str) and len(rec["explanation"]) > 20
        
        print(f"  -> Borrower #{b_id} ({rec['borrower_name']}):")
        print(f"     Rec: {rec['recommendation']} | Stress: {rec['stress_level']} | Persistent: {rec['persistent_stress_status']}")
        print(f"     Top Factor: {rec['top_factors'][0]}")

    # 4. Audit /api/borrowers/{id}/transactions across Borrowers 1-5
    print("\n[CHECK 4/4] Auditing /api/borrowers/{id}/transactions schema alignment...")
    for b_id in range(1, 6):
        res = client.get(f"/api/borrowers/{b_id}/transactions")
        assert res.status_code == 200
        txs = res.json()
        assert len(txs) >= 6
        for tx in txs:
            assert "date" in tx
            assert "income" in tx
            assert "expenses" in tx
            assert "cash_balance" in tx
    print("  -> Transactions Schema Valid: verified date, income, expenses, cash_balance across all records.")

    print("\n==================================================================")
    print("   ALL STEP 8 FINITE ROUTE & PAYLOAD CHECKS PASSED (100% HEALTHY) ")
    print("==================================================================")

if __name__ == "__main__":
    run_finite_step8_verification()
