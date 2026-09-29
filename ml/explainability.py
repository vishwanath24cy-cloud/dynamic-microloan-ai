"""Explainable AI (XAI) Module for Repayment Stress & Recommendation Insights.

Provides transparent, evidence-based explanations of:
1. Repayment stress classification
2. Dynamic repayment recommendations
3. Persistent stress rule triggers

Identifies key financial factors, quantifies their impact, and generates
human-readable narratives for loan officers and borrowers.
"""
import sys
from pathlib import Path
from typing import Dict, Any, List

ML_DIR = Path(__file__).resolve().parent
PROJECT_DIR = ML_DIR.parent
BACKEND_DIR = PROJECT_DIR / "backend"

if str(ML_DIR) not in sys.path:
    sys.path.insert(0, str(ML_DIR))
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from cashflow_prediction import predict_cashflow
from stress_prediction import predict_stress


from typing import Dict, Any, List, Optional

def explain_recommendation(borrower_id: int, rec_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Generates an evidence-based explanation for a borrower's stress level and recommendation.

    Args:
        borrower_id: Target borrower ID
        rec_data: Optional precomputed recommendation payload from recommendation_engine

    Returns:
        Dictionary containing summary, stress_level, recommendation, top_factors, and explanation.
    """
    # 1. Fetch ML predictions & stress metrics
    cf_res = predict_cashflow(borrower_id)
    stress_res = predict_stress(borrower_id)

    # 2. Extract key metrics
    stress_level = stress_res["stress_level"]
    persistent_info = stress_res["persistent_stress"]
    persistent_status = persistent_info["persistent_stress_status"]
    consecutive_high_months = persistent_info["consecutive_high_stress_months"]

    fin_factors = stress_res["important_financial_factors"]
    current_emi = fin_factors["emi_amount"]
    current_avail_cash = fin_factors["available_cash"]
    days_late = fin_factors["days_late"]
    late_3m = fin_factors["late_payments_last_3m"]
    inc_change_pct = fin_factors["monthly_income_change_pct"]
    exp_change_pct = fin_factors["monthly_expense_change_pct"]
    rep_to_inc_pct = fin_factors["repayment_to_income_pct"]
    volatility = fin_factors["income_volatility"]

    pred_income = cf_res["predicted_income"]
    pred_expenses = cf_res["predicted_expenses"]
    pred_avail_cash = cf_res["predicted_available_cash"]

    # 3. Determine Recommendation
    if rec_data is not None:
        rec_res = rec_data
    else:
        from recommendation_engine import generate_recommendation
        rec_res = generate_recommendation(borrower_id)

    recommendation = rec_res["recommendation"]
    lender_review_required = rec_res["lender_review_required"]

    # 4. Synthesize Top Contributing Factors with Severity Scoring
    factor_candidates = []

    # Factor A: Consecutive stress months
    if consecutive_high_months >= 3:
        factor_candidates.append({
            "severity": 100,
            "text": f"{consecutive_high_months} consecutive high-stress months detected (severe chronic distress)",
            "category": "persistent_stress",
        })
    elif consecutive_high_months == 2:
        factor_candidates.append({
            "severity": 95,
            "text": "Two consecutive high-stress months detected (triggers mandatory persistent stress policy)",
            "category": "persistent_stress",
        })
    elif consecutive_high_months == 1:
        factor_candidates.append({
            "severity": 40,
            "text": "Single-period temporary liquidity stress detected",
            "category": "persistent_stress",
        })

    # Factor B: Available cash vs EMI
    if current_avail_cash < 0:
        factor_candidates.append({
            "severity": 90,
            "text": f"Current available cash is in severe deficit (-INR {abs(current_avail_cash):,.2f}), well below monthly EMI (INR {current_emi:,.2f})",
            "category": "liquidity",
        })
    elif current_avail_cash < current_emi:
        factor_candidates.append({
            "severity": 75,
            "text": f"Current available cash (INR {current_avail_cash:,.2f}) is insufficient to service full EMI (INR {current_emi:,.2f})",
            "category": "liquidity",
        })
    elif current_avail_cash >= current_emi * 2.5:
        factor_candidates.append({
            "severity": 10,
            "text": f"Robust cash-flow buffer: Available cash (INR {current_avail_cash:,.2f}) provides {current_avail_cash/current_emi:.1f}x coverage over EMI",
            "category": "liquidity",
        })

    # Factor C: Repayment delinquency
    if days_late > 30:
        factor_candidates.append({
            "severity": 85,
            "text": f"Severe payment delinquency of {days_late} days late with missed installment records",
            "category": "repayment",
        })
    elif days_late > 0:
        factor_candidates.append({
            "severity": 65,
            "text": f"Recent installment delayed by {days_late} days ({late_3m} delayed payment(s) over past 3 months)",
            "category": "repayment",
        })
    elif days_late == 0 and late_3m == 0:
        factor_candidates.append({
            "severity": 5,
            "text": "Perfect on-time repayment history with zero recorded payment delays",
            "category": "repayment",
        })

    # Factor D: Income momentum
    if inc_change_pct <= -25.0:
        factor_candidates.append({
            "severity": 70,
            "text": f"Monthly income contracted substantially by {abs(inc_change_pct):.1f}%",
            "category": "income_trend",
        })
    elif inc_change_pct >= 25.0:
        factor_candidates.append({
            "severity": 15,
            "text": f"Monthly revenue expanded by +{inc_change_pct:.1f}% providing strong surplus",
            "category": "income_trend",
        })

    # Factor E: Forward-looking forecast
    if pred_avail_cash < 0:
        factor_candidates.append({
            "severity": 60,
            "text": f"ML forecast projects continued negative cash balance (-INR {abs(pred_avail_cash):,.2f}) into the next cycle",
            "category": "forecast",
        })
    elif pred_avail_cash > current_emi * 1.5:
        factor_candidates.append({
            "severity": 20,
            "text": f"ML model forecasts strong cash-flow recovery (INR {pred_avail_cash:,.2f} projected available cash next month)",
            "category": "forecast",
        })

    # Factor F: Debt burden / volatility
    if rep_to_inc_pct > 30.0:
        factor_candidates.append({
            "severity": 50,
            "text": f"Elevated debt-to-income ratio ({rep_to_inc_pct:.1f}% of gross earnings allocated to EMI)",
            "category": "debt_burden",
        })

    # Sort factors by importance (highest severity first)
    factor_candidates.sort(key=lambda x: x["severity"], reverse=True)
    top_factors = [f["text"] for f in factor_candidates[:4]]

    # 5. Build Human-Readable Narrative Explanation
    if recommendation == "NORMAL_PAYMENT":
        summary = f"Borrower {borrower_id} ({stress_res['borrower_name']}) maintains sound financial health with LOW stress. Standard EMI payment is advised."
        explanation = (
            f"Financial analysis indicates consistent liquidity stability for {stress_res['borrower_name']}. "
            f"The borrower generates an available monthly cash buffer of INR {current_avail_cash:,.2f} "
            f"against a scheduled EMI of INR {current_emi:,.2f} ({current_avail_cash/current_emi:.1f}x coverage). "
            f"With on-time repayment history and forward projections indicating continued surplus (INR {pred_avail_cash:,.2f}), "
            f"no loan modifications are necessary."
        )
    elif recommendation in ["SPLIT_PAYMENT", "REDUCED_PAYMENT"]:
        summary = f"Borrower {borrower_id} ({stress_res['borrower_name']}) is facing temporary liquidity pressure with {stress_level} stress, but ML forecast indicates near-term recovery."
        explanation = (
            f"The borrower experienced a transient liquidity squeeze resulting in available cash of INR {current_avail_cash:,.2f} "
            f"against an EMI of INR {current_emi:,.2f}. However, persistent stress criteria are NOT met (consecutive stress months: {consecutive_high_months}), "
            f"and ML cash-flow models project a strong forward recovery to INR {pred_avail_cash:,.2f} available cash. "
            f"A temporary {recommendation.replace('_', ' ').lower()} arrangement is recommended to prevent default while avoiding debt restructuring."
        )
    elif persistent_status == "PERSISTENT_STRESS":
        summary = f"Borrower {borrower_id} ({stress_res['borrower_name']}) has triggered PERSISTENT STRESS (2 consecutive months). Underwriter review is required."
        explanation = (
            f"Critical policy threshold reached: High repayment stress has persisted for two consecutive monthly cycles. "
            f"Recent cash deficit of -INR {abs(current_avail_cash):,.2f} coupled with payment delays ({days_late} days late) "
            f"proves that current loan terms are unsustainable. Pursuant to institutional credit guidelines, automated payment "
            f"reductions are locked, and human underwriter review is required to evaluate formal restructuring or tenor extension."
        )
    else:  # SEVERE_PERSISTENT_STRESS
        summary = f"Borrower {borrower_id} ({stress_res['borrower_name']}) is in SEVERE PERSISTENT STRESS ({consecutive_high_months} months). Immediate human workout counseling required."
        explanation = (
            f"Severe multi-period distress: Borrower has accumulated {consecutive_high_months} consecutive cycles of chronic cash deficits "
            f"(-INR {abs(current_avail_cash):,.2f}) and escalating delinquency ({days_late} days late). "
            f"Projected next-month available cash remains negative (-INR {abs(pred_avail_cash):,.2f}). "
            f"All automated collections are paused; mandatory credit officer intervention and loan workout counseling are required immediately."
        )

    return {
        "borrower_id": int(borrower_id),
        "borrower_name": stress_res["borrower_name"],
        "summary": summary,
        "stress_level": stress_level,
        "recommendation": recommendation,
        "lender_review_required": lender_review_required,
        "top_factors": top_factors,
        "explanation": explanation,
        "metrics_snapshot": {
            "current_available_cash": current_avail_cash,
            "scheduled_emi": current_emi,
            "days_late": days_late,
            "consecutive_high_stress_months": consecutive_high_months,
            "predicted_available_cash": pred_avail_cash,
            "income_change_pct": inc_change_pct,
        },
    }


if __name__ == "__main__":
    for i in range(1, 6):
        res = explain_recommendation(i)
        print(f"\n==================== BORROWER {i}: {res['borrower_name']} ====================")
        print(f"Stress Level:   {res['stress_level']}")
        print(f"Recommendation: {res['recommendation']}")
        print("Top Factors:")
        for idx, tf in enumerate(res["top_factors"], 1):
            print(f"  {idx}. {tf}")
        print(f"Summary:        {res['summary']}")
        print(f"Explanation:    {res['explanation']}")
