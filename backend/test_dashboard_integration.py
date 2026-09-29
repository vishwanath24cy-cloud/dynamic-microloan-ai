"""Live Frontend-Backend Integration Test Suite.

Verifies:
1. FastAPI backend server is live on http://localhost:8000
2. React Vite frontend server is live on http://localhost:5173
3. All endpoints consumed by the Step 8 Frontend Dashboard return valid 200 responses
4. Data integrity across all 5 demo borrower personas (A-E)
"""
import urllib.request
import json
import sys

def test_endpoint(url, desc):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Step8-Tester/1.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            status = response.getcode()
            body = response.read().decode("utf-8")
            assert status == 200, f"Expected 200, got {status} for {url}"
            return body
    except Exception as e:
        print(f"FAILED: {desc} ({url}) -> {e}")
        sys.exit(1)

def run_tests():
    print("==================================================================")
    print("    STEP 8: INTERACTIVE FRONTEND & API INTEGRATION AUDIT          ")
    print("==================================================================\n")

    # 1. Test Vite Frontend Server
    print("[TEST 1/5] Checking Frontend Server on http://localhost:5173...")
    fe_html = test_endpoint("http://localhost:5173/", "Vite Frontend Root")
    assert "<!DOCTYPE html>" in fe_html or "<html" in fe_html, "Frontend HTML structure missing"
    assert "/src/main.jsx" in fe_html, "React entrypoint not referenced in index.html"
    print("  -> Vite dev server is UP, serving index.html with React 18 mount point.\n")

    # 2. Test FastAPI Backend Health
    print("[TEST 2/5] Checking Backend Server on http://localhost:8000/health...")
    be_health_json = json.loads(test_endpoint("http://localhost:8000/health", "FastAPI Health"))
    assert be_health_json.get("status") == "healthy", f"Degraded health: {be_health_json}"
    assert be_health_json.get("database") == "connected", f"Database not connected: {be_health_json}"
    print(f"  -> FastAPI backend is UP, status: {be_health_json.get('status')}, DB: {be_health_json.get('database')}.\n")

    # 3. Test Dashboard Summary Endpoint
    print("[TEST 3/5] Testing GET /api/dashboard/summary...")
    summary = json.loads(test_endpoint("http://localhost:8000/api/dashboard/summary", "Dashboard Summary"))
    assert summary["total_borrowers"] == 5, f"Expected 5 borrowers, found {summary['total_borrowers']}"
    assert summary["total_loans"] == 5, f"Expected 5 loans, found {summary['total_loans']}"
    assert summary["total_loan_volume"] > 0, "Non-positive total loan volume"
    assert summary["total_monthly_emi"] > 0, "Non-positive total monthly EMI"
    assert "stress_distribution" in summary, "Missing stress distribution"
    print(f"  -> Portfolio KPIs: {summary['total_borrowers']} Borrowers, {summary['total_loans']} Loans, "
          f"Vol: INR {summary['total_loan_volume']:,.0f}, EMI: INR {summary['total_monthly_emi']:,.0f}.\n")

    # 4. Test Borrowers List Endpoint
    print("[TEST 4/5] Testing GET /api/borrowers...")
    borrowers = json.loads(test_endpoint("http://localhost:8000/api/borrowers", "Borrowers List"))
    assert len(borrowers) == 5, f"Expected 5 demo borrowers, got {len(borrowers)}"
    print("  -> Received all 5 demo borrowers:")
    for b in borrowers:
        print(f"     * ID #{b['borrower_id']}: {b['name']} ({b['occupation']}) - Stress: {b['latest_stress_level']}")
    print()

    # 5. Test Live Recommendation & Cash-Flow for All 5 Borrowers
    print("[TEST 5/5] Testing GET /api/borrowers/{id}/recommendation across all 5 personas...")
    expected_outcomes = {
        1: ("NORMAL_PAYMENT", "LOW", "NONE"),
        2: ("SPLIT_PAYMENT", "MEDIUM", "TEMPORARY_STRESS"),
        3: ("REVIEW_REQUIRED", "HIGH", "PERSISTENT_STRESS"),
        4: ("NORMAL_PAYMENT", "LOW", "NONE"),
        5: ("REVIEW_REQUIRED", "HIGH", "SEVERE_PERSISTENT_STRESS"),
    }

    for b_id in range(1, 6):
        rec = json.loads(test_endpoint(f"http://localhost:8000/api/borrowers/{b_id}/recommendation", f"Rec B{b_id}"))
        txs = json.loads(test_endpoint(f"http://localhost:8000/api/borrowers/{b_id}/transactions", f"Txs B{b_id}"))
        
        # Verify required keys for UI rendering
        assert "borrower_id" in rec
        assert "borrower_name" in rec
        assert "current_emi" in rec
        assert "current_available_cash" in rec
        assert "predicted_available_cash" in rec
        assert "stress_level" in rec
        assert "persistent_stress_status" in rec
        assert "recommendation" in rec
        assert "summary" in rec and len(rec["summary"]) > 5
        assert "top_factors" in rec and len(rec["top_factors"]) >= 2
        assert "explanation" in rec and len(rec["explanation"]) > 10
        assert len(txs) >= 6, f"Expected >= 6 transaction cycles for B{b_id}, found {len(txs)}"

        exp_rec, exp_stress, exp_persist = expected_outcomes[b_id]
        assert rec["recommendation"] == exp_rec, f"B{b_id} expected {exp_rec}, got {rec['recommendation']}"
        assert rec["stress_level"] == exp_stress, f"B{b_id} expected {exp_stress}, got {rec['stress_level']}"
        assert rec["persistent_stress_status"] == exp_persist, f"B{b_id} expected {exp_persist}, got {rec['persistent_stress_status']}"

        print(f"  -> Borrower #{b_id} ({rec['borrower_name']}):")
        print(f"     Recommendation: {rec['recommendation']}")
        print(f"     Stress Level:   {rec['stress_level']} ({rec['persistent_stress_status']})")
        print(f"     Suggested Amt:  {rec['suggested_payment_amount']}")
        print(f"     Top Factor #1:  {rec['top_factors'][0]}")
        print(f"     Transactions:   {len(txs)} historical cycles loaded")
        print()

    print("==================================================================")
    print("    ALL STEP 8 FRONTEND-BACKEND INTEGRATION TESTS PASSED (100%)   ")
    print("==================================================================")

if __name__ == "__main__":
    run_tests()
