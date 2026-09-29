"""Dynamic Repayment Recommendation Engine.

Combines:
- Current loan terms & EMI
- Current available cash & cash balance
- Predicted income, expenses, and available cash (from Step 4 ML models)
- Repayment stress classification (from Step 5 ML classifier)
- Persistent stress detection status (from Step 5B rule engine)

Possible outputs:
1. NORMAL_PAYMENT
2. REDUCED_PAYMENT
3. SPLIT_PAYMENT
4. REVIEW_REQUIRED

Important Guardrail:
This system is an advisory decision-support tool. It does NOT automatically
approve, reject, or permanently restructure loans. Significant repayment adjustments
require lender/human underwriter review.
"""
import sys
from pathlib import Path
from typing import Dict, Any, Optional

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BACKEND_DIR.parent
ML_DIR = PROJECT_DIR / "ml"
if str(ML_DIR) not in sys.path:
    sys.path.insert(0, str(ML_DIR))

from cashflow_prediction import predict_cashflow
from stress_prediction import predict_stress


def generate_recommendation(borrower_id: int) -> Dict[str, Any]:
    """Evaluates borrower financials and generates an actionable repayment recommendation.

    Args:
        borrower_id: Target borrower ID

    Returns:
        Dictionary containing recommendation, stress level, persistent stress status,
        suggested structure, reason, and underlying financial factors.
    """
    # 1. Run ML Cash-Flow Forecast (Step 4)
    cf_res = predict_cashflow(borrower_id)
    pred_income = cf_res["predicted_income"]
    pred_expenses = cf_res["predicted_expenses"]
    pred_available_cash = cf_res["predicted_available_cash"]

    # 2. Run ML Stress Prediction & Persistent Stress Detection (Step 5 & 5B)
    stress_res = predict_stress(borrower_id)
    stress_level = stress_res["stress_level"]
    persistent_info = stress_res["persistent_stress"]
    persistent_status = persistent_info["persistent_stress_status"]
    consecutive_high_months = persistent_info["consecutive_high_stress_months"]

    fin_factors = stress_res["important_financial_factors"]
    current_emi = fin_factors["emi_amount"]
    current_available_cash = fin_factors["available_cash"]
    days_late = fin_factors["days_late"]
    late_3m = fin_factors["late_payments_last_3m"]

    # 3. Decision Logic Engine
    # -------------------------------------------------------------
    # CASE 4: Severe Persistent Stress (3+ consecutive months)
    # -------------------------------------------------------------
    if consecutive_high_months >= 3 or persistent_status == "SEVERE_PERSISTENT_STRESS":
        recommendation = "REVIEW_REQUIRED"
        persistent_stress_status = "SEVERE_PERSISTENT_STRESS"
        suggested_amount = None
        suggested_structure = "Collections hold; immediate formal credit officer review and workout consultation."
        reason = (
            f"Severe persistent stress detected across {consecutive_high_months} consecutive months with acute "
            f"negative cash-flow (-INR {abs(current_available_cash):,.2f}). Automated repayment reductions are halted to "
            f"prevent compounding balance; formal human credit officer intervention is required."
        )
        lender_review_required = True

    # -------------------------------------------------------------
    # CASE 3: Persistent Stress (2 consecutive months)
    # -------------------------------------------------------------
    elif consecutive_high_months == 2 or persistent_status == "PERSISTENT_STRESS":
        recommendation = "REVIEW_REQUIRED"
        persistent_stress_status = "PERSISTENT_STRESS"
        suggested_amount = None
        suggested_structure = "Lender underwriter review required prior to tenor extension or restructuring."
        reason = (
            "High repayment stress has occurred for two consecutive months. "
            "Underwriter credit policy mandates lender review before offering structural repayment relief."
        )
        lender_review_required = True

    # -------------------------------------------------------------
    # CASE 2: Temporary Stress (1 month stress or tight cash, with recovery evidence)
    # -------------------------------------------------------------
    elif (
        stress_level in ["HIGH", "MEDIUM"]
        or current_available_cash < current_emi * 1.2
        or days_late > 0
    ):
        persistent_stress_status = persistent_status if persistent_status != "NONE" else "TEMPORARY_STRESS"

        # Check evidence of cash-flow recovery from Step 4 ML predictions
        if pred_available_cash > current_emi:
            # Strong forward recovery predicted: Offer Split Payment to bridge timing
            recommendation = "SPLIT_PAYMENT"
            suggested_amount = round(current_emi / 2.0, 2)
            suggested_structure = "Temporary bi-weekly split: 50% now, remaining 50% upon expected mid-cycle income inflow."
            reason = (
                f"Current available cash (INR {current_available_cash:,.2f}) is compressed against monthly EMI (INR {current_emi:,.2f}), "
                f"but predicted future available cash (INR {pred_available_cash:,.2f}) indicates solid recovery. "
                f"A split installment eases liquidity without requiring debt write-downs."
            )
            lender_review_required = False

        elif pred_available_cash > 0:
            # Partial recovery: Offer Temporary Reduced Payment
            recommendation = "REDUCED_PAYMENT"
            suggested_amount = round(max(current_emi * 0.5, pred_available_cash * 0.7), 2)
            suggested_structure = "Temporary 30-day reduced installment subject to standard lender microloan policy."
            reason = (
                f"Temporary single-period revenue contraction detected. Projected forward cash flow (INR {pred_available_cash:,.2f}) "
                f"supports a temporary installment adjustment to prevent delinquency."
            )
            lender_review_required = False

        else:
            # Negative forward cash flow without persistent history yet: Review required
            recommendation = "REVIEW_REQUIRED"
            suggested_amount = None
            suggested_structure = "Early risk review: evaluate potential loan restructuring."
            reason = (
                f"Current available cash (INR {current_available_cash:,.2f}) and near-term projected cash flow "
                f"(INR {pred_available_cash:,.2f}) are insufficient to cover scheduled EMI. Lender review recommended."
            )
            lender_review_required = True

    # -------------------------------------------------------------
    # CASE 1: Healthy Borrower (Comfortable cash buffer & LOW stress)
    # -------------------------------------------------------------
    else:
        recommendation = "NORMAL_PAYMENT"
        persistent_stress_status = "NONE"
        suggested_amount = current_emi
        suggested_structure = "Standard contracted monthly EMI repayment."
        reason = (
            f"Borrower exhibits healthy financial stability. Current available cash (INR {current_available_cash:,.2f}) "
            f"and predicted cash flow (INR {pred_available_cash:,.2f}) comfortably support scheduled EMI (INR {current_emi:,.2f}) "
            f"with zero persistent payment delays."
        )
        lender_review_required = False

    # Package full response
    response_payload = {
        "borrower_id": int(borrower_id),
        "borrower_name": stress_res["borrower_name"],
        "current_emi": round(float(current_emi), 2),
        "current_available_cash": round(float(current_available_cash), 2),
        "predicted_income": round(float(pred_income), 2),
        "predicted_expenses": round(float(pred_expenses), 2),
        "predicted_available_cash": round(float(pred_available_cash), 2),
        "stress_level": stress_level,
        "persistent_stress_status": persistent_stress_status,
        "consecutive_high_stress_months": consecutive_high_months,
        "recommendation": recommendation,
        "suggested_payment_amount": suggested_amount,
        "suggested_payment_structure": suggested_structure,
        "reason": reason,
        "lender_review_required": lender_review_required,
        "important_financial_factors": {
            **fin_factors,
            "predicted_income": round(float(pred_income), 2),
            "predicted_expenses": round(float(pred_expenses), 2),
            "predicted_available_cash": round(float(pred_available_cash), 2),
        },
    }

    # Attach Explainable AI (Step 7)
    try:
        from explainability import explain_recommendation
        exp_res = explain_recommendation(borrower_id, rec_data=response_payload)
        response_payload["summary"] = exp_res.get("summary", reason)
        response_payload["top_factors"] = exp_res.get("top_factors", [])
        response_payload["explanation"] = exp_res.get("explanation", reason)
    except Exception:
        response_payload["summary"] = reason
        response_payload["top_factors"] = []
        response_payload["explanation"] = reason

    return response_payload


if __name__ == "__main__":
    for b_id in range(1, 6):
        res = generate_recommendation(b_id)
        print(f"\n[{res['borrower_name']} - ID {b_id}]")
        print(f"  Recommendation:  {res['recommendation']}")
        print(f"  Stress:          {res['stress_level']} | Persistent: {res['persistent_stress_status']}")
        print(f"  Review Required: {res['lender_review_required']}")
        print(f"  Reason:          {res['reason']}")
