import math
from typing import Dict, Any, List, Optional


class EMIEngine:
    @staticmethod
    def calculate_emi(
        total_price: float,
        down_payment: Optional[float] = None,
        down_payment_percent: Optional[float] = None,
        tenure_months: int = 60,
        annual_interest_rate: float = 9.5,
        include_schedule: bool = False,
    ) -> Dict[str, Any]:
        """
        Pure deterministic reducing-balance EMI calculation with complete
        amortization schedule generation.
        """
        if total_price <= 0:
            raise ValueError("Total vehicle price must be strictly positive")

        if tenure_months <= 0 or tenure_months > 120:
            raise ValueError("Tenure months must be between 1 and 120 months")

        if annual_interest_rate < 0 or annual_interest_rate > 50:
            raise ValueError("Annual interest rate must be between 0% and 50%")

        # Resolve down payment
        if down_payment is not None:
            dp = max(0.0, float(down_payment))
            dp_pct = round((dp / total_price) * 100.0, 2)
        elif down_payment_percent is not None:
            dp_pct = min(100.0, max(0.0, float(down_payment_percent)))
            dp = round(total_price * (dp_pct / 100.0), 2)
        else:
            # Default 20% down payment
            dp_pct = 20.0
            dp = round(total_price * 0.20, 2)

        principal = round(total_price - dp, 2)
        if principal <= 0:
            return {
                "principal_loan_amount": 0.0,
                "down_payment": dp,
                "down_payment_percent": dp_pct,
                "tenure_months": tenure_months,
                "annual_interest_rate": annual_interest_rate,
                "monthly_emi": 0.0,
                "total_interest_payable": 0.0,
                "total_amount_payable": dp,
                "schedule": [],
            }

        monthly_rate = (annual_interest_rate / 12.0) / 100.0

        if monthly_rate > 0:
            factor = (1.0 + monthly_rate) ** tenure_months
            monthly_emi = round(principal * monthly_rate * factor / (factor - 1.0), 2)
        else:
            monthly_emi = round(principal / tenure_months, 2)

        # Generate amortization schedule
        schedule: List[Dict[str, Any]] = []
        balance = principal
        total_interest = 0.0

        for month in range(1, tenure_months + 1):
            if monthly_rate > 0:
                interest_payment = round(balance * monthly_rate, 2)
            else:
                interest_payment = 0.0

            # Adjust last month rounding
            if month == tenure_months:
                principal_payment = balance
                monthly_installment = round(principal_payment + interest_payment, 2)
                closing_balance = 0.0
            else:
                principal_payment = round(monthly_emi - interest_payment, 2)
                closing_balance = round(balance - principal_payment, 2)
                monthly_installment = monthly_emi

            total_interest += interest_payment

            if include_schedule:
                schedule.append({
                    "month": month,
                    "opening_balance": balance,
                    "emi": monthly_installment,
                    "principal": principal_payment,
                    "interest": interest_payment,
                    "closing_balance": max(0.0, closing_balance),
                })

            balance = closing_balance

        total_interest = round(total_interest, 2)
        total_repayment = round(principal + total_interest, 2)

        return {
            "principal_loan_amount": principal,
            "down_payment": dp,
            "down_payment_percent": dp_pct,
            "tenure_months": tenure_months,
            "annual_interest_rate": annual_interest_rate,
            "monthly_emi": monthly_emi,
            "total_interest_payable": total_interest,
            "total_loan_repayment": total_repayment,
            "total_cost_with_downpayment": round(dp + total_repayment, 2),
            "amortization_schedule": schedule if include_schedule else None,
        }


emi_engine = EMIEngine()
