"""Comprehensive End-to-End System Test Suite.

Verifies all integrated modules together:
1. SQLite Database layer & schema integrity
2. Synthetic Dataset integrity
3. ML Cash-Flow Prediction (Step 4)
4. ML Repayment Stress Detection & Persistent Stress Rules (Step 5 & 5B)
5. Dynamic Repayment Recommendation Engine (Step 6)
6. Explainable AI Insights (Step 7)
7. All FastAPI REST API Endpoints across Borrowers A-E
"""
import sys
import json
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BACKEND_DIR.parent
ML_DIR = PROJECT_DIR / "ml"
DATA_DIR = PROJECT_DIR / "data"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(ML_DIR) not in sys.path:
    sys.path.insert(0, str(ML_DIR))

from fastapi.testclient import TestClient
from app.main import app
from app.database import engine, check_db_connection, SessionLocal
from app.models import Borrower, Loan, Transaction, Repayment
from sqlalchemy import inspect

from cashflow_prediction import predict_cashflow
from stress_prediction import predict_stress
from recommendation_engine import generate_recommendation
from explainability import explain_recommendation


def run_e2e_verification():
    print("=================================================================")
    print("   AI-BASED DYNAMIC MICROLOAN PLANNER: FULL E2E SYSTEM AUDIT     ")
    print("=================================================================\n")

    # -------------------------------------------------------------
    # 1. DATABASE LAYER AUDIT
    # -------------------------------------------------------------
    print("[TEST 1/7] Auditing SQLite Database & Schema...")
    db_status = check_db_connection()
    assert db_status == "connected", f"Database not connected: {db_status}"

    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    required_tables = {"borrowers", "loans", "transactions", "repayments", "predictions", "recommendations"}
    missing_tables = required_tables - tables
    assert not missing_tables, f"Missing database tables: {missing_tables}"

    db = SessionLocal()
    borrower_count = db.query(Borrower).count()
    loan_count = db.query(Loan).count()
    tx_count = db.query(Transaction).count()
    rep_count = db.query(Repayment).count()
    db.close()

    assert borrower_count == 5, f"Expected 5 demo borrowers, found {borrower_count}"
    assert loan_count == 5, f"Expected 5 loans, found {loan_count}"
    assert tx_count >= 25, f"Expected >= 25 transactions, found {tx_count}"
    assert rep_count >= 20, f"Expected >= 20 repayments, found {rep_count}"
    print(f"  -> DB Connected: 6 tables verified, {borrower_count} demo borrowers with loans and transaction history.")

    # -------------------------------------------------------------
    # 2. SYNTHETIC DATASET AUDIT
    # -------------------------------------------------------------
    print("\n[TEST 2/7] Auditing Synthetic Training Dataset...")
    borrowers_csv = DATA_DIR / "borrowers.csv"
    tx_csv = DATA_DIR / "borrower_transactions.csv"
    assert borrowers_csv.exists(), f"Missing {borrowers_csv}"
    assert tx_csv.exists(), f"Missing {tx_csv}"

    import pandas as pd
    b_df = pd.read_csv(borrowers_csv)
    tx_df = pd.read_csv(tx_csv)
    assert len(b_df) == 500, f"Expected 500 borrowers in CSV, found {len(b_df)}"
    assert len(tx_df) == 9000, f"Expected 9,000 transactions in CSV, found {len(tx_df)}"
    assert tx_df.isnull().sum().sum() == 0, "Null values detected in transactions CSV"
    print(f"  -> Synthetic Dataset Verified: 500 borrowers, 9,000 monthly records, 0 missing values.")

    # -------------------------------------------------------------
    # 3. CASH-FLOW PREDICTION ML AUDIT (STEP 4)
    # -------------------------------------------------------------
    print("\n[TEST 3/7] Auditing Step 4 ML Cash-Flow Predictor...")
    for b_id in range(1, 6):
        cf = predict_cashflow(b_id)
        assert cf["predicted_income"] > 0, f"Non-positive income for B{b_id}"
        assert cf["predicted_expenses"] > 0, f"Non-positive expenses for B{b_id}"
        expected_cash = round(cf["predicted_income"] - cf["predicted_expenses"], 2)
        assert abs(cf["predicted_available_cash"] - expected_cash) < 0.05, f"Inconsistent available cash for B{b_id}"
    print("  -> Step 4 Predictor Verified: Models load from ml/models/, outputs adhere to income - expenses formula.")

    # -------------------------------------------------------------
    # 4. REPAYMENT STRESS & PERSISTENT STRESS AUDIT (STEP 5 & 5B)
    # -------------------------------------------------------------
    print("\n[TEST 4/7] Auditing Step 5 & 5B Repayment Stress Classifier & Rules...")
    stress_results = {}
    for b_id in range(1, 6):
        s = predict_stress(b_id)
        stress_results[b_id] = s
        assert s["stress_level"] in ["LOW", "MEDIUM", "HIGH"]
        assert 0.0 <= s["confidence"] <= 1.0

    # Borrower A: LOW stress
    assert stress_results[1]["stress_level"] == "LOW"
    assert stress_results[1]["persistent_stress"]["persistent_stress_status"] == "NONE"

    # Borrower B: MEDIUM stress
    assert stress_results[2]["stress_level"] == "MEDIUM"

    # Borrower C: HIGH stress, exactly 2 consecutive months -> PERSISTENT_STRESS
    assert stress_results[3]["stress_level"] == "HIGH"
    assert stress_results[3]["persistent_stress"]["consecutive_high_stress_months"] == 2
    assert stress_results[3]["persistent_stress"]["persistent_stress_status"] == "PERSISTENT_STRESS"
    assert stress_results[3]["persistent_stress"]["required_action"] == "LENDER_REVIEW_REQUIRED"

    # Borrower D: LOW stress (rebounded)
    assert stress_results[4]["stress_level"] == "LOW"

    # Borrower E: HIGH stress, 4 consecutive months -> SEVERE_PERSISTENT_STRESS
    assert stress_results[5]["stress_level"] == "HIGH"
    assert stress_results[5]["persistent_stress"]["consecutive_high_stress_months"] >= 3
    assert stress_results[5]["persistent_stress"]["persistent_stress_status"] == "SEVERE_PERSISTENT_STRESS"
    assert stress_results[5]["persistent_stress"]["required_action"] == "HUMAN_INTERVENTION_REQUIRED"
    print("  -> Step 5 & 5B Verified: Random Forest classifier and persistent stress rules pass across all test personas.")

    # -------------------------------------------------------------
    # 5. DYNAMIC REPAYMENT RECOMMENDATION ENGINE AUDIT (STEP 6)
    # -------------------------------------------------------------
    print("\n[TEST 5/7] Auditing Step 6 Dynamic Repayment Engine...")
    rec_results = {}
    for b_id in range(1, 6):
        r = generate_recommendation(b_id)
        rec_results[b_id] = r
        assert r["recommendation"] in ["NORMAL_PAYMENT", "SPLIT_PAYMENT", "REDUCED_PAYMENT", "REVIEW_REQUIRED"]

    # Verify expected recommendations
    assert rec_results[1]["recommendation"] == "NORMAL_PAYMENT"
    assert rec_results[1]["lender_review_required"] is False

    assert rec_results[2]["recommendation"] == "SPLIT_PAYMENT"
    assert rec_results[2]["suggested_payment_amount"] == 1400.0  # 50% split of 2800 EMI

    assert rec_results[3]["recommendation"] == "REVIEW_REQUIRED"
    assert rec_results[3]["lender_review_required"] is True

    assert rec_results[4]["recommendation"] == "NORMAL_PAYMENT"
    assert rec_results[4]["lender_review_required"] is False

    assert rec_results[5]["recommendation"] == "REVIEW_REQUIRED"
    assert rec_results[5]["lender_review_required"] is True
    print("  -> Step 6 Engine Verified: Transparent decision logic successfully assigns correct advisory pathways.")

    # -------------------------------------------------------------
    # 6. EXPLAINABLE AI AUDIT (STEP 7)
    # -------------------------------------------------------------
    print("\n[TEST 6/7] Auditing Step 7 Explainable AI (XAI)...")
    for b_id in range(1, 6):
        exp = explain_recommendation(b_id)
        assert "summary" in exp and len(exp["summary"]) > 10
        assert "top_factors" in exp and len(exp["top_factors"]) >= 2
        assert "explanation" in exp and len(exp["explanation"]) > 20

    # Verify Borrower C narrative highlights 2 consecutive months
    b3_factors_str = " ".join(explain_recommendation(3)["top_factors"])
    assert "Two consecutive high-stress months" in b3_factors_str
    print("  -> Step 7 XAI Verified: Severity-ranked factor attribution and narrative explanations generated for all profiles.")

    # -------------------------------------------------------------
    # 7. FASTAPI REST API ENDPOINTS AUDIT
    # -------------------------------------------------------------
    print("\n[TEST 7/7] Auditing Full FastAPI REST API Suite via TestClient...")
    with TestClient(app) as client:
        # Base & Health
        assert client.get("/health").status_code == 200
        assert client.get("/").status_code == 200
        assert client.get("/api/dashboard/summary").status_code == 200

        # Borrowers list
        b_list_res = client.get("/api/borrowers")
        assert b_list_res.status_code == 200
        assert len(b_list_res.json()) == 5

        # Borrower detail endpoints for Borrower 1 through 5
        for b_id in range(1, 6):
            assert client.get(f"/api/borrowers/{b_id}").status_code == 200
            assert client.get(f"/api/borrowers/{b_id}/loans").status_code == 200
            assert client.get(f"/api/borrowers/{b_id}/transactions").status_code == 200
            assert client.get(f"/api/borrowers/{b_id}/repayments").status_code == 200
            assert client.get(f"/api/borrowers/{b_id}/predictions").status_code == 200
            assert client.get(f"/api/borrowers/{b_id}/recommendations").status_code == 200

            # Live ML endpoints
            cf_api = client.get(f"/api/borrowers/{b_id}/cashflow-prediction")
            assert cf_api.status_code == 200
            assert "predicted_available_cash" in cf_api.json()

            stress_api = client.get(f"/api/borrowers/{b_id}/stress")
            assert stress_api.status_code == 200
            assert "stress_level" in stress_api.json()

            rec_api = client.get(f"/api/borrowers/{b_id}/recommendation")
            assert rec_api.status_code == 200
            rec_json = rec_api.json()
            assert "recommendation" in rec_json
            assert "top_factors" in rec_json
            assert "explanation" in rec_json

        # 404 tests
        assert client.get("/api/borrowers/999").status_code == 404
        assert client.get("/api/borrowers/999/cashflow-prediction").status_code == 404
        assert client.get("/api/borrowers/999/stress").status_code == 404
        assert client.get("/api/borrowers/999/recommendation").status_code == 404

    print("  -> FastAPI REST API Suite Verified: All 12 routes return 200 OK with validated payloads.")

    print("\n=================================================================")
    print("   ALL 7 SYSTEM AUDITS PASSED WITH ZERO ERRORS (100% HEALTHY)   ")
    print("=================================================================")


if __name__ == "__main__":
    run_e2e_verification()
