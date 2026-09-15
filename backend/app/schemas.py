from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class LoanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    loan_id: int
    borrower_id: int
    loan_amount: float
    emi_amount: float
    loan_start_date: str
    repayment_frequency: str


class TransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    transaction_id: int
    borrower_id: int
    date: str
    income: float
    expenses: float
    cash_balance: float


class RepaymentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    repayment_id: int
    borrower_id: int
    date: str
    amount: float
    days_late: int
    status: str


class PredictionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    prediction_id: int
    borrower_id: int
    prediction_date: str
    predicted_income: float
    predicted_expenses: float
    predicted_available_cash: float


class RecommendationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    recommendation_id: int
    borrower_id: int
    recommendation: str
    stress_level: str
    persistent_stress: bool
    reason: str
    created_at: str


class BorrowerSummaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    borrower_id: int
    name: str
    age: int
    occupation: str
    total_loan_amount: float
    monthly_emi: float
    latest_stress_level: str
    persistent_stress: bool


class BorrowerDetailOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    borrower_id: int
    name: str
    age: int
    occupation: str
    loans: List[LoanOut] = []
    transactions: List[TransactionOut] = []
    repayments: List[RepaymentOut] = []
    predictions: List[PredictionOut] = []
    recommendations: List[RecommendationOut] = []


class DashboardSummary(BaseModel):
    total_borrowers: int
    total_loans: int
    total_loan_volume: float
    total_monthly_emi: float
    stress_distribution: dict
    persistent_stress_count: int
