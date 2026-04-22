"""
Key financial ratio calculations.
"""
from app.models.user import User
from app.schemas.analysis import MortgageResult, CashflowResult, RatiosResult


def calculate_ratios(
    user: User,
    mortgage: MortgageResult,
    cashflow: CashflowResult,
) -> RatiosResult:
    income = user.monthly_income or 0
    fixed = user.fixed_expenses or 0
    variable = user.variable_expenses or 0
    debt = user.monthly_debt_payments or 0
    emergency_fund = user.emergency_fund or 0

    housing_cost = cashflow.housing_cost
    total_expenses = cashflow.expenses  # already adjusted for dependents

    # Mortgage ratio: cuota / ingreso
    mortgage_ratio = mortgage.monthly_payment / income if income else 0

    # Debt ratio: deudas mensuales / ingreso (sin hipoteca)
    debt_ratio = debt / income if income else 0

    # Housing ratio: costo total de vivienda / ingreso
    housing_ratio = housing_cost / income if income else 0

    # Emergency months: fondo emergencia / gastos mensuales totales
    monthly_total = total_expenses + housing_cost
    emergency_months = emergency_fund / monthly_total if monthly_total else 0

    # Free cash flow ratio: (ingreso - gastos fijos - deuda - vivienda) / ingreso
    free_cash_flow = income - fixed - debt - housing_cost
    free_cash_flow_ratio = free_cash_flow / income if income else 0

    # Discretionary income ratio: (ingreso - todo) / ingreso
    discretionary_income = income - fixed - variable - debt - housing_cost
    discretionary_income_ratio = discretionary_income / income if income else 0

    return RatiosResult(
        mortgage_ratio=round(mortgage_ratio, 4),
        debt_ratio=round(debt_ratio, 4),
        housing_ratio=round(housing_ratio, 4),
        emergency_months=round(emergency_months, 2),
        free_cash_flow_ratio=round(free_cash_flow_ratio, 4),
        discretionary_income_ratio=round(discretionary_income_ratio, 4),
    )
