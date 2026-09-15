from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Borrower(Base):
    __tablename__ = "borrowers"

    borrower_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    occupation = Column(String(100), nullable=False)

    # Relationships
    loans = relationship("Loan", back_populates="borrower", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="borrower", cascade="all, delete-orphan")
    repayments = relationship("Repayment", back_populates="borrower", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="borrower", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="borrower", cascade="all, delete-orphan")


class Loan(Base):
    __tablename__ = "loans"

    loan_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    borrower_id = Column(Integer, ForeignKey("borrowers.borrower_id", ondelete="CASCADE"), nullable=False)
    loan_amount = Column(Float, nullable=False)
    emi_amount = Column(Float, nullable=False)
    loan_start_date = Column(String(20), nullable=False)
    repayment_frequency = Column(String(20), nullable=False, default="monthly")

    # Relationship
    borrower = relationship("Borrower", back_populates="loans")


class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    borrower_id = Column(Integer, ForeignKey("borrowers.borrower_id", ondelete="CASCADE"), nullable=False)
    date = Column(String(20), nullable=False)
    income = Column(Float, nullable=False)
    expenses = Column(Float, nullable=False)
    cash_balance = Column(Float, nullable=False)

    # Relationship
    borrower = relationship("Borrower", back_populates="transactions")


class Repayment(Base):
    __tablename__ = "repayments"

    repayment_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    borrower_id = Column(Integer, ForeignKey("borrowers.borrower_id", ondelete="CASCADE"), nullable=False)
    date = Column(String(20), nullable=False)
    amount = Column(Float, nullable=False)
    days_late = Column(Integer, nullable=False, default=0)
    status = Column(String(20), nullable=False, default="paid")

    # Relationship
    borrower = relationship("Borrower", back_populates="repayments")


class Prediction(Base):
    __tablename__ = "predictions"

    prediction_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    borrower_id = Column(Integer, ForeignKey("borrowers.borrower_id", ondelete="CASCADE"), nullable=False)
    prediction_date = Column(String(20), nullable=False)
    predicted_income = Column(Float, nullable=False)
    predicted_expenses = Column(Float, nullable=False)
    predicted_available_cash = Column(Float, nullable=False)

    # Relationship
    borrower = relationship("Borrower", back_populates="predictions")


class Recommendation(Base):
    __tablename__ = "recommendations"

    recommendation_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    borrower_id = Column(Integer, ForeignKey("borrowers.borrower_id", ondelete="CASCADE"), nullable=False)
    recommendation = Column(String(255), nullable=False)
    stress_level = Column(String(20), nullable=False)
    persistent_stress = Column(Boolean, nullable=False, default=False)
    reason = Column(String(500), nullable=False)
    created_at = Column(String(30), nullable=False)

    # Relationship
    borrower = relationship("Borrower", back_populates="recommendations")
