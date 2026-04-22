"""
Mortgage calculation engine.
Formula: M = P * [r(1+r)^n] / [(1+r)^n - 1]
"""
from app.schemas.analysis import PropertyInput, MortgageResult


def calculate_mortgage(prop: PropertyInput) -> MortgageResult:
    loan_amount = prop.property_price - prop.down_payment
    monthly_rate = prop.annual_interest_rate / 100 / 12
    num_payments = prop.loan_term_years * 12

    if monthly_rate == 0:
        monthly_payment = loan_amount / num_payments
    else:
        factor = (1 + monthly_rate) ** num_payments
        monthly_payment = loan_amount * (monthly_rate * factor) / (factor - 1)

    total_paid = monthly_payment * num_payments
    total_interest = total_paid - loan_amount

    return MortgageResult(
        loan_amount=round(loan_amount, 2),
        monthly_rate=round(monthly_rate, 6),
        num_payments=num_payments,
        monthly_payment=round(monthly_payment, 2),
        total_paid=round(total_paid, 2),
        total_interest=round(total_interest, 2),
    )
