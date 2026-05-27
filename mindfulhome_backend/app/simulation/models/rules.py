# app/simulation/models/rules.py
from pydantic import BaseModel, Field

class IncomeRules(BaseModel):
    annual_growth_mean: float = 0.035  # 3.5% crecimiento anual (realista)
    annual_growth_std: float = 0.005   # 0.5% desviación (más estable)
    monthly_volatility: float = 0.001  # 0.1% volatilidad mensual
    downside_shock_probability: float = 0.005  # 0.5% probabilidad (1 vez cada ~17 años)
    downside_shock_impact: tuple = (-0.15, -0.05)  # Entre -5% y -15%
    recovery_months: tuple = (2, 6)  # Recuperación más rápida

class ExpenseRules(BaseModel):
    inflation_mean: float = 0.025  # 2.5% inflación anual (más realista)
    inflation_std: float = 0.005   # 0.5% desviación
    variable_expense_volatility: float = 0.01  # 1% volatilidad
    unexpected_expense_probability: float = 0.01  # 1% al mes (cada ~8 años)
    unexpected_expense_range: tuple = (50000, 500000)  # Gastos más pequeños

class SavingsRules(BaseModel):
    savings_contribution_ratio: float = 0.05  # 5% de la liquidez (más conservador)
    emergency_usage_threshold: float = 0
    rebuild_behavior: bool = True

class DebtRules(BaseModel):
    debt_payment_stability: float = 0.99  # 99% estable
    refinancing_probability: float = 0.005  # 0.5% probabilidad

class SimulationRules(BaseModel):
    income: IncomeRules = Field(default_factory=IncomeRules)
    expenses: ExpenseRules = Field(default_factory=ExpenseRules)
    savings: SavingsRules = Field(default_factory=SavingsRules)
    debt: DebtRules = Field(default_factory=DebtRules)