"""
Post-purchase cashflow analysis.
"""
from app.models.user import User
from app.schemas.analysis import MortgageResult, CashflowResult
from app.models.analysis import RiskStatus


def _classify_liquidity(liquidity: float, income: float) -> RiskStatus:
    if income == 0:
        return RiskStatus.CRITICAL
    ratio = liquidity / income
    if ratio > 0.20:
        return RiskStatus.SAFE
    elif ratio > 0.05:
        return RiskStatus.MODERATE
    elif ratio > 0:
        return RiskStatus.RISKY
    else:
        return RiskStatus.CRITICAL


def calculate_cashflow(user: User, mortgage: MortgageResult) -> CashflowResult:
    income = user.monthly_income or 0
    fixed = user.fixed_expenses or 0
    variable = user.variable_expenses or 0
    debt = user.monthly_debt_payments or 0
    dependents = user.dependents or 0
    savings_goal = user.monthly_savings_goal or 0

    # Base expenses
    base_expenses = fixed + variable + debt

    # Dependent adjustment: each dependent = 10% of base expenses
    adjusted_expenses = base_expenses * (1 + 0.1 * dependents)

    # Housing cost: mortgage + overlap rent if applicable
    housing_cost = mortgage.monthly_payment
    if user.is_renting and user.monthly_rent and user.rent_mortgage_overlap_months:
        # Amortize overlap cost over 12 months to get monthly impact
        overlap_monthly = (user.monthly_rent * user.rent_mortgage_overlap_months) / 12
        housing_cost += overlap_monthly

    total_expenses = adjusted_expenses + housing_cost
    liquidity = income - total_expenses
    liquidity_after_savings = liquidity - savings_goal

    status = _classify_liquidity(liquidity, income)

    return CashflowResult(
        income=round(income, 2),
        expenses=round(adjusted_expenses, 2),
        debt=round(debt, 2),
        housing_cost=round(housing_cost, 2),
        liquidity=round(liquidity, 2),
        liquidity_after_savings=round(liquidity_after_savings, 2),
        status=status,
    )
