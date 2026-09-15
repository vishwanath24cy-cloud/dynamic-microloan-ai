from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models import Borrower, Loan, Transaction, Repayment, Prediction, Recommendation
from app.database import SessionLocal, init_db


def seed_demo_data(db: Session, force: bool = False):
    """Populates the database with 5 distinct realistic demo borrower scenarios."""
    borrower_count = db.query(Borrower).count()
    if borrower_count > 0 and not force:
        return {"status": "skipped", "message": f"Database already contains {borrower_count} borrowers."}

    if force and borrower_count > 0:
        # Clear existing data for fresh seed
        db.query(Recommendation).delete()
        db.query(Prediction).delete()
        db.query(Repayment).delete()
        db.query(Transaction).delete()
        db.query(Loan).delete()
        db.query(Borrower).delete()
        db.commit()

    now_iso = datetime.now(timezone.utc).isoformat()

    # -------------------------------------------------------------
    # 1. BORROWER A: Stable income and expenses -> LOW stress
    # -------------------------------------------------------------
    borrower_a = Borrower(name="Aarav Sharma", age=34, occupation="Grocery Store Owner")
    db.add(borrower_a)
    db.flush()

    loan_a = Loan(
        borrower_id=borrower_a.borrower_id,
        loan_amount=50000.0,
        emi_amount=4500.0,
        loan_start_date="2026-01-15",
        repayment_frequency="monthly",
    )
    db.add(loan_a)

    transactions_a = [
        Transaction(borrower_id=borrower_a.borrower_id, date="2026-01-31", income=45000.0, expenses=28000.0, cash_balance=17000.0),
        Transaction(borrower_id=borrower_a.borrower_id, date="2026-02-28", income=46000.0, expenses=28500.0, cash_balance=30000.0),
        Transaction(borrower_id=borrower_a.borrower_id, date="2026-03-31", income=45500.0, expenses=27800.0, cash_balance=43200.0),
        Transaction(borrower_id=borrower_a.borrower_id, date="2026-04-30", income=47000.0, expenses=29000.0, cash_balance=56700.0),
        Transaction(borrower_id=borrower_a.borrower_id, date="2026-05-31", income=48000.0, expenses=29500.0, cash_balance=70700.0),
        Transaction(borrower_id=borrower_a.borrower_id, date="2026-06-30", income=46500.0, expenses=28800.0, cash_balance=83900.0),
    ]
    db.add_all(transactions_a)

    repayments_a = [
        Repayment(borrower_id=borrower_a.borrower_id, date="2026-02-15", amount=4500.0, days_late=0, status="paid"),
        Repayment(borrower_id=borrower_a.borrower_id, date="2026-03-15", amount=4500.0, days_late=0, status="paid"),
        Repayment(borrower_id=borrower_a.borrower_id, date="2026-04-15", amount=4500.0, days_late=0, status="paid"),
        Repayment(borrower_id=borrower_a.borrower_id, date="2026-05-15", amount=4500.0, days_late=0, status="paid"),
        Repayment(borrower_id=borrower_a.borrower_id, date="2026-06-15", amount=4500.0, days_late=0, status="paid"),
    ]
    db.add_all(repayments_a)

    prediction_a = Prediction(
        borrower_id=borrower_a.borrower_id,
        prediction_date="2026-07-01",
        predicted_income=47500.0,
        predicted_expenses=29000.0,
        predicted_available_cash=18500.0,
    )
    db.add(prediction_a)

    recommendation_a = Recommendation(
        borrower_id=borrower_a.borrower_id,
        recommendation="Maintain standard monthly EMI of ₹4,500. Excellent credit health.",
        stress_level="LOW",
        persistent_stress=False,
        reason="Consistent healthy revenue surplus (>3.5x EMI) with zero late repayment history.",
        created_at=now_iso,
    )
    db.add(recommendation_a)

    # -------------------------------------------------------------
    # 2. BORROWER B: Temporary income decrease -> Temporary MEDIUM/HIGH stress
    # -------------------------------------------------------------
    borrower_b = Borrower(name="Bhavna Patel", age=29, occupation="Artisan Textile Weaver")
    db.add(borrower_b)
    db.flush()

    loan_b = Loan(
        borrower_id=borrower_b.borrower_id,
        loan_amount=30000.0,
        emi_amount=2800.0,
        loan_start_date="2026-01-10",
        repayment_frequency="monthly",
    )
    db.add(loan_b)

    transactions_b = [
        Transaction(borrower_id=borrower_b.borrower_id, date="2026-01-31", income=25000.0, expenses=16000.0, cash_balance=9000.0),
        Transaction(borrower_id=borrower_b.borrower_id, date="2026-02-28", income=25500.0, expenses=16200.0, cash_balance=15300.0),
        Transaction(borrower_id=borrower_b.borrower_id, date="2026-03-31", income=24800.0, expenses=16500.0, cash_balance=20800.0),
        Transaction(borrower_id=borrower_b.borrower_id, date="2026-04-30", income=24000.0, expenses=16000.0, cash_balance=26000.0),
        Transaction(borrower_id=borrower_b.borrower_id, date="2026-05-31", income=14500.0, expenses=14200.0, cash_balance=2300.0),  # Material bottleneck
        Transaction(borrower_id=borrower_b.borrower_id, date="2026-06-30", income=19000.0, expenses=15500.0, cash_balance=3500.0),  # Partial rebound
    ]
    db.add_all(transactions_b)

    repayments_b = [
        Repayment(borrower_id=borrower_b.borrower_id, date="2026-02-10", amount=2800.0, days_late=0, status="paid"),
        Repayment(borrower_id=borrower_b.borrower_id, date="2026-03-10", amount=2800.0, days_late=0, status="paid"),
        Repayment(borrower_id=borrower_b.borrower_id, date="2026-04-10", amount=2800.0, days_late=0, status="paid"),
        Repayment(borrower_id=borrower_b.borrower_id, date="2026-05-16", amount=2800.0, days_late=6, status="paid"),
        Repayment(borrower_id=borrower_b.borrower_id, date="2026-06-13", amount=2800.0, days_late=3, status="paid"),
    ]
    db.add_all(repayments_b)

    prediction_b = Prediction(
        borrower_id=borrower_b.borrower_id,
        prediction_date="2026-07-01",
        predicted_income=24500.0,
        predicted_expenses=16000.0,
        predicted_available_cash=8500.0,
    )
    db.add(prediction_b)

    recommendation_b = Recommendation(
        borrower_id=borrower_b.borrower_id,
        recommendation="Grant 7-day payment window flexibility or optional 25% EMI relief for July.",
        stress_level="MEDIUM",
        persistent_stress=False,
        reason="Temporary raw material supply delay caused isolated 1-month revenue squeeze; upcoming cash flow is projected to normalize.",
        created_at=now_iso,
    )
    db.add(recommendation_b)

    # -------------------------------------------------------------
    # 3. BORROWER C: HIGH stress for 2 consecutive months -> PERSISTENT STRESS
    # -------------------------------------------------------------
    borrower_c = Borrower(name="Chirag Verma", age=42, occupation="Independent Delivery Driver")
    db.add(borrower_c)
    db.flush()

    loan_c = Loan(
        borrower_id=borrower_c.borrower_id,
        loan_amount=40000.0,
        emi_amount=3600.0,
        loan_start_date="2026-01-20",
        repayment_frequency="monthly",
    )
    db.add(loan_c)

    transactions_c = [
        Transaction(borrower_id=borrower_c.borrower_id, date="2026-01-31", income=32000.0, expenses=21500.0, cash_balance=10500.0),
        Transaction(borrower_id=borrower_c.borrower_id, date="2026-02-28", income=31500.0, expenses=22000.0, cash_balance=16400.0),
        Transaction(borrower_id=borrower_c.borrower_id, date="2026-03-31", income=33000.0, expenses=22500.0, cash_balance=23300.0),
        Transaction(borrower_id=borrower_c.borrower_id, date="2026-04-30", income=31000.0, expenses=22000.0, cash_balance=28700.0),
        Transaction(borrower_id=borrower_c.borrower_id, date="2026-05-31", income=18000.0, expenses=22000.0, cash_balance=900.0),   # Month 1 high stress
        Transaction(borrower_id=borrower_c.borrower_id, date="2026-06-30", income=17500.0, expenses=21500.0, cash_balance=400.0),   # Month 2 high stress
    ]
    db.add_all(transactions_c)

    repayments_c = [
        Repayment(borrower_id=borrower_c.borrower_id, date="2026-02-20", amount=3600.0, days_late=0, status="paid"),
        Repayment(borrower_id=borrower_c.borrower_id, date="2026-03-20", amount=3600.0, days_late=0, status="paid"),
        Repayment(borrower_id=borrower_c.borrower_id, date="2026-04-20", amount=3600.0, days_late=0, status="paid"),
        Repayment(borrower_id=borrower_c.borrower_id, date="2026-06-04", amount=3600.0, days_late=15, status="late"),
        Repayment(borrower_id=borrower_c.borrower_id, date="2026-07-12", amount=3600.0, days_late=22, status="late"),
    ]
    db.add_all(repayments_c)

    prediction_c = Prediction(
        borrower_id=borrower_c.borrower_id,
        prediction_date="2026-07-01",
        predicted_income=19000.0,
        predicted_expenses=21000.0,
        predicted_available_cash=-2000.0,
    )
    db.add(prediction_c)

    recommendation_c = Recommendation(
        borrower_id=borrower_c.borrower_id,
        recommendation="Trigger Persistent Stress Protocol: Extend loan tenor by 6 months and reduce EMI to ₹1,800/month.",
        stress_level="HIGH",
        persistent_stress=True,
        reason="Severe cash-flow deficit exceeding EMI threshold for 2 consecutive months (May & June 2026) due to vehicle overhaul.",
        created_at=now_iso,
    )
    db.add(recommendation_c)

    # -------------------------------------------------------------
    # 4. BORROWER D: Seasonal income -> Income later improves
    # -------------------------------------------------------------
    borrower_d = Borrower(name="Deepika Nair", age=36, occupation="Agricultural Produce Trader")
    db.add(borrower_d)
    db.flush()

    loan_d = Loan(
        borrower_id=borrower_d.borrower_id,
        loan_amount=60000.0,
        emi_amount=5200.0,
        loan_start_date="2026-01-05",
        repayment_frequency="monthly",
    )
    db.add(loan_d)

    transactions_d = [
        Transaction(borrower_id=borrower_d.borrower_id, date="2026-01-31", income=39000.0, expenses=25000.0, cash_balance=14000.0),
        Transaction(borrower_id=borrower_d.borrower_id, date="2026-02-28", income=36000.0, expenses=24500.0, cash_balance=20300.0),
        Transaction(borrower_id=borrower_d.borrower_id, date="2026-03-31", income=22000.0, expenses=21500.0, cash_balance=6000.0),   # Sowing season dip
        Transaction(borrower_id=borrower_d.borrower_id, date="2026-04-30", income=21000.0, expenses=21000.0, cash_balance=2400.0),   # Lean season
        Transaction(borrower_id=borrower_d.borrower_id, date="2026-05-31", income=54000.0, expenses=27000.0, cash_balance=24200.0),  # Harvest starts
        Transaction(borrower_id=borrower_d.borrower_id, date="2026-06-30", income=59000.0, expenses=28000.0, cash_balance=49800.0),  # Peak market sales
    ]
    db.add_all(transactions_d)

    repayments_d = [
        Repayment(borrower_id=borrower_d.borrower_id, date="2026-02-05", amount=5200.0, days_late=0, status="paid"),
        Repayment(borrower_id=borrower_d.borrower_id, date="2026-03-05", amount=5200.0, days_late=0, status="paid"),
        Repayment(borrower_id=borrower_d.borrower_id, date="2026-04-11", amount=5200.0, days_late=6, status="paid"),
        Repayment(borrower_id=borrower_d.borrower_id, date="2026-05-09", amount=5200.0, days_late=4, status="paid"),
        Repayment(borrower_id=borrower_d.borrower_id, date="2026-06-05", amount=5200.0, days_late=0, status="paid"),
    ]
    db.add_all(repayments_d)

    prediction_d = Prediction(
        borrower_id=borrower_d.borrower_id,
        prediction_date="2026-07-01",
        predicted_income=57000.0,
        predicted_expenses=27500.0,
        predicted_available_cash=29500.0,
    )
    db.add(prediction_d)

    recommendation_d = Recommendation(
        borrower_id=borrower_d.borrower_id,
        recommendation="Apply Dynamic Seasonal Repayment: Maintain standard EMI with optional surplus prepayments.",
        stress_level="LOW",
        persistent_stress=False,
        reason="Predictable agricultural seasonality completed. Post-harvest revenue surge provides substantial cash surplus.",
        created_at=now_iso,
    )
    db.add(recommendation_d)

    # -------------------------------------------------------------
    # 5. BORROWER E: Continuous income decrease and repeated late payments -> SEVERE stress
    # -------------------------------------------------------------
    borrower_e = Borrower(name="Eshwar Rao", age=48, occupation="Small Cafeteria Operator")
    db.add(borrower_e)
    db.flush()

    loan_e = Loan(
        borrower_id=borrower_e.borrower_id,
        loan_amount=75000.0,
        emi_amount=6800.0,
        loan_start_date="2026-01-01",
        repayment_frequency="monthly",
    )
    db.add(loan_e)

    transactions_e = [
        Transaction(borrower_id=borrower_e.borrower_id, date="2026-01-31", income=52000.0, expenses=38000.0, cash_balance=14000.0),
        Transaction(borrower_id=borrower_e.borrower_id, date="2026-02-28", income=42000.0, expenses=37500.0, cash_balance=11700.0),
        Transaction(borrower_id=borrower_e.borrower_id, date="2026-03-31", income=33000.0, expenses=36000.0, cash_balance=4200.0),
        Transaction(borrower_id=borrower_e.borrower_id, date="2026-04-30", income=25000.0, expenses=35000.0, cash_balance=700.0),
        Transaction(borrower_id=borrower_e.borrower_id, date="2026-05-31", income=19000.0, expenses=34000.0, cash_balance=-1400.0),  # Negative cash balance
        Transaction(borrower_id=borrower_e.borrower_id, date="2026-06-30", income=16500.0, expenses=33000.0, cash_balance=-5100.0),  # Deep deficit
    ]
    db.add_all(transactions_e)

    repayments_e = [
        Repayment(borrower_id=borrower_e.borrower_id, date="2026-02-01", amount=6800.0, days_late=0, status="paid"),
        Repayment(borrower_id=borrower_e.borrower_id, date="2026-03-15", amount=6800.0, days_late=14, status="late"),
        Repayment(borrower_id=borrower_e.borrower_id, date="2026-05-03", amount=6800.0, days_late=32, status="missed"),
        Repayment(borrower_id=borrower_e.borrower_id, date="2026-06-15", amount=0.0, days_late=45, status="missed"),
        Repayment(borrower_id=borrower_e.borrower_id, date="2026-07-02", amount=0.0, days_late=61, status="missed"),
    ]
    db.add_all(repayments_e)

    prediction_e = Prediction(
        borrower_id=borrower_e.borrower_id,
        prediction_date="2026-07-01",
        predicted_income=15500.0,
        predicted_expenses=32500.0,
        predicted_available_cash=-17000.0,
    )
    db.add(prediction_e)

    recommendation_e = Recommendation(
        borrower_id=borrower_e.borrower_id,
        recommendation="Urgent Microfinance Intervention: Immediate EMI freeze, loan restructuring, and credit counselor outreach.",
        stress_level="SEVERE",
        persistent_stress=True,
        reason="Continuous 4-month revenue contraction with chronic negative cash flow and 60+ days delinquency.",
        created_at=now_iso,
    )
    db.add(recommendation_e)

    db.commit()
    return {"status": "success", "message": "Successfully seeded 5 demo borrowers with full financial histories."}


if __name__ == "__main__":
    init_db()
    db = SessionLocal()
    res = seed_demo_data(db, force=True)
    print(res)
    db.close()
