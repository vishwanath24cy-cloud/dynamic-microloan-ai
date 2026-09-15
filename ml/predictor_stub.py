"""Baseline Cash-Flow Predictor & Dynamic Repayment Stub.

This module serves as a placeholder for the ML models to be developed during the hackathon.
"""
from typing import Dict, Any, List


class CashFlowPredictor:
    """Predicts future cash flow and recommends dynamic loan repayment schedules."""

    def __init__(self, buffer_ratio: float = 0.2):
        self.buffer_ratio = buffer_ratio

    def predict_repayment_capacity(
        self, historical_cash_flows: List[float], standard_emi: float
    ) -> Dict[str, Any]:
        """Calculates recommended repayment based on average recent cash flows.

        Args:
            historical_cash_flows: List of recent net cash flow amounts.
            standard_emi: The standard contracted monthly installment.

        Returns:
            Dictionary with recommended installment and status flag.
        """
        if not historical_cash_flows:
            return {
                "recommended_installment": standard_emi,
                "confidence": 0.5,
                "status": "insufficient_data",
            }

        avg_flow = sum(historical_cash_flows) / len(historical_cash_flows)
        safe_capacity = max(0.0, avg_flow * (1.0 - self.buffer_ratio))

        # Dynamically adjust installment: if cash flow is lower, ease installment; if higher, allow surplus paydown
        if safe_capacity < standard_emi:
            recommended = max(standard_emi * 0.5, safe_capacity)
            flag = "reduced_repayment_recommended"
        else:
            recommended = standard_emi
            flag = "normal_repayment"

        return {
            "avg_projected_cashflow": round(avg_flow, 2),
            "safe_capacity": round(safe_capacity, 2),
            "recommended_installment": round(recommended, 2),
            "status": flag,
        }


if __name__ == "__main__":
    predictor = CashFlowPredictor()
    sample_flows = [1200.0, 950.0, 800.0, 1100.0]
    result = predictor.predict_repayment_capacity(sample_flows, standard_emi=900.0)
    print("Sample ML Predictor Output:", result)
