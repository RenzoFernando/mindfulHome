from pydantic import BaseModel, Field

class IncomeRules(BaseModel):
    annual_growth_mean: float = 0.04
    annual_growth_std: float = 0.02
    monthly_volatility: float = 0.01
    downside_shock_probability: float = 0.03
    downside_shock_impact: tuple = (-0.4, -0.15)
    recovery_months: tuple = (3, 12)

class ExpenseRules(BaseModel):
    inflation_mean: float = 0.05
    inflation_std: float = 0.015
    variable_expense_volatility: float = 0.08
    unexpected_expense_probability: float = 0.06
    unexpected_expense_range: tuple = (500000, 5000000)

class SavingsRules(BaseModel):
    savings_contribution_ratio: float = 0.1
    emergency_usage_threshold: float = 0
    rebuild_behavior: bool = True

class DebtRules(BaseModel):
    debt_payment_stability: float = 0.95
    refinancing_probability: float = 0.02

class SimulationRules(BaseModel):
    income: IncomeRules = Field(default_factory=IncomeRules)
    expenses: ExpenseRules = Field(default_factory=ExpenseRules)
    savings: SavingsRules = Field(default_factory=SavingsRules)
    debt: DebtRules = Field(default_factory=DebtRules)