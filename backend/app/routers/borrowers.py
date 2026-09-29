from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Borrower, Loan, Transaction, Repayment, Prediction, Recommendation
from app.schemas import (
    BorrowerSummaryOut,
    BorrowerDetailOut,
    LoanOut,
    TransactionOut,
    RepaymentOut,
    PredictionOut,
    RecommendationOut,
    DashboardSummary,
)
from app.seed import seed_demo_data
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from recommendation_engine import generate_recommendation, predict_cashflow, predict_stress

router = APIRouter(prefix="/api", tags=["Borrowers & Financial Analytics"])


@router.get("/borrowers", response_model=List[BorrowerSummaryOut])
def list_borrowers(db: Session = Depends(get_db)):
    """Retrieves all registered borrowers with consolidated loan amounts and current stress status."""
    borrowers = db.query(Borrower).all()
    results = []

    for b in borrowers:
        total_loan = sum(l.loan_amount for l in b.loans)
        total_emi = sum(l.emi_amount for l in b.loans)
        latest_rec = b.recommendations[-1] if b.recommendations else None
        stress = latest_rec.stress_level if latest_rec else "UNKNOWN"
        persistent = latest_rec.persistent_stress if latest_rec else False

        results.append(
            BorrowerSummaryOut(
                borrower_id=b.borrower_id,
                name=b.name,
                age=b.age,
                occupation=b.occupation,
                total_loan_amount=total_loan,
                monthly_emi=total_emi,
                latest_stress_level=stress,
                persistent_stress=persistent,
            )
        )

    return results


@router.get("/borrowers/{borrower_id}", response_model=BorrowerDetailOut)
def get_borrower_detail(borrower_id: int, db: Session = Depends(get_db)):
    """Retrieves detailed profile of a borrower including loans, transactions, repayments, predictions, and recommendations."""
    borrower = db.query(Borrower).filter(Borrower.borrower_id == borrower_id).first()
    if not borrower:
        raise HTTPException(status_code=404, detail=f"Borrower with id {borrower_id} not found")
    return borrower


@router.get("/borrowers/{borrower_id}/loans", response_model=List[LoanOut])
def get_borrower_loans(borrower_id: int, db: Session = Depends(get_db)):
    """Retrieves all loans associated with a borrower."""
    loans = db.query(Loan).filter(Loan.borrower_id == borrower_id).all()
    return loans


@router.get("/borrowers/{borrower_id}/transactions", response_model=List[TransactionOut])
def get_borrower_transactions(borrower_id: int, db: Session = Depends(get_db)):
    """Retrieves transaction cash-flow history for a borrower sorted chronologically."""
    transactions = (
        db.query(Transaction)
        .filter(Transaction.borrower_id == borrower_id)
        .order_by(Transaction.date.asc())
        .all()
    )
    return transactions


@router.get("/borrowers/{borrower_id}/repayments", response_model=List[RepaymentOut])
def get_borrower_repayments(borrower_id: int, db: Session = Depends(get_db)):
    """Retrieves repayment log and delinquency records for a borrower."""
    repayments = (
        db.query(Repayment)
        .filter(Repayment.borrower_id == borrower_id)
        .order_by(Repayment.date.asc())
        .all()
    )
    return repayments


@router.get("/borrowers/{borrower_id}/predictions", response_model=List[PredictionOut])
def get_borrower_predictions(borrower_id: int, db: Session = Depends(get_db)):
    """Retrieves cash-flow prediction records for a borrower."""
    predictions = (
        db.query(Prediction)
        .filter(Prediction.borrower_id == borrower_id)
        .order_by(Prediction.prediction_date.asc())
        .all()
    )
    return predictions


@router.get("/borrowers/{borrower_id}/recommendations", response_model=List[RecommendationOut])
def get_borrower_recommendations(borrower_id: int, db: Session = Depends(get_db)):
    """Retrieves repayment plan recommendations and stress assessments for a borrower."""
    recommendations = (
        db.query(Recommendation)
        .filter(Recommendation.borrower_id == borrower_id)
        .order_by(Recommendation.created_at.desc())
        .all()
    )
    return recommendations


@router.get("/borrowers/{borrower_id}/cashflow-prediction")
def get_live_cashflow_prediction(borrower_id: int):
    """Predicts next-month income, expenses, and available cash using trained ML models."""
    try:
        return predict_cashflow(borrower_id)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to generate cashflow prediction: {str(exc)}")


@router.get("/borrowers/{borrower_id}/stress")
def get_live_stress_prediction(borrower_id: int):
    """Predicts repayment stress and evaluates persistent stress rules using ML."""
    try:
        return predict_stress(borrower_id)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to evaluate repayment stress: {str(exc)}")


@router.get("/borrowers/{borrower_id}/recommendation")
def get_live_recommendation(borrower_id: int):
    """Generates a dynamic repayment recommendation using the ML cash-flow & stress engine."""
    try:
        recommendation_data = generate_recommendation(borrower_id)
        return recommendation_data
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendation: {str(exc)}")



@router.get("/dashboard/summary", response_model=DashboardSummary)
def get_dashboard_summary(db: Session = Depends(get_db)):
    """Provides high-level portfolio KPIs and stress distribution."""
    borrowers = db.query(Borrower).all()
    total_borrowers = len(borrowers)

    loans = db.query(Loan).all()
    total_loans = len(loans)
    total_loan_volume = sum(l.loan_amount for l in loans)
    total_monthly_emi = sum(l.emi_amount for l in loans)

    stress_distribution = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "SEVERE": 0}
    persistent_stress_count = 0

    for b in borrowers:
        if b.recommendations:
            latest = b.recommendations[-1]
            level = latest.stress_level
            stress_distribution[level] = stress_distribution.get(level, 0) + 1
            if latest.persistent_stress:
                persistent_stress_count += 1

    return DashboardSummary(
        total_borrowers=total_borrowers,
        total_loans=total_loans,
        total_loan_volume=total_loan_volume,
        total_monthly_emi=total_monthly_emi,
        stress_distribution=stress_distribution,
        persistent_stress_count=persistent_stress_count,
    )


@router.post("/seed")
def seed_data(force: bool = False, db: Session = Depends(get_db)):
    """Seeds or resets the demo borrowers dataset."""
    result = seed_demo_data(db, force=force)
    return result
