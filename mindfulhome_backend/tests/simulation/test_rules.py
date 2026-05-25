import pytest
import numpy as np
from app.simulation.models.rules import (
    IncomeRules, ExpenseRules, SavingsRules, DebtRules, SimulationRules
)
from app.simulation.rules.income_rules import IncomeRulesGenerator
from app.simulation.rules.expense_rules import ExpenseRulesGenerator
from app.simulation.rules.savings_rules import SavingsRulesGenerator
from app.simulation.rules.debt_rules import DebtRulesGenerator
from app.models.user import User, IncomeType, IncomeVariability, ContractType

class TestRulesGeneration:
    """Pruebas para la generación de reglas según perfil de usuario"""
    
    def test_income_rules_for_stable_employee(self):
        """Usuario empleado fijo debe tener baja volatilidad"""
        user = User(
            monthly_income=5000000,
            income_type=IncomeType.EMPLEADO,
            income_variability=IncomeVariability.FIJO,
            contract_type=ContractType.INDEFINIDO,
            job_seniority_months=36
        )
        
        rules = IncomeRulesGenerator.generate_rules(user)
        
        assert rules.monthly_volatility <= 0.02
        assert rules.downside_shock_probability <= 0.03
        assert rules.annual_growth_mean == 0.04
        
    def test_income_rules_for_variable_income(self):
        """Usuario independiente debe tener mayor volatilidad"""
        user = User(
            monthly_income=5000000,
            income_type=IncomeType.INDEPENDIENTE,
            income_variability=IncomeVariability.VARIABLE,
            contract_type=ContractType.PRESTACION_SERVICIOS,
            job_seniority_months=6
        )
        
        rules = IncomeRulesGenerator.generate_rules(user)
        
        assert rules.monthly_volatility >= 0.025
        assert rules.downside_shock_probability >= 0.05
        assert rules.recovery_months == (3, 12)
        
    def test_expense_rules_with_dependents(self):
        """Usuarios con dependientes tienen más gastos inesperados"""
        user = User(
            monthly_income=5000000,
            fixed_expenses=1500000,
            variable_expenses=1000000,
            dependents=3
        )
        
        rules = ExpenseRulesGenerator.generate_rules(user)
        
        assert rules.unexpected_expense_probability >= 0.08
        assert rules.unexpected_expense_range[1] >= 6000000
        
    def test_savings_rules_for_high_income(self):
        """Altos ingresos = mayor ratio de ahorro"""
        user = User(
            monthly_income=20000000,
            monthly_savings_goal=4000000,
            income_variability=IncomeVariability.FIJO
        )
        
        rules = SavingsRulesGenerator.generate_rules(user)
        
        assert rules.savings_contribution_ratio >= 0.15
        assert rules.emergency_usage_threshold <= 0
        
    def test_debt_rules_for_high_indebtedness(self):
        """Alto endeudamiento = menor estabilidad en pagos"""
        user = User(
            monthly_income=5000000,
            monthly_debt_payments=2500000,
            total_debt=50000000,
            total_savings=5000000
        )
        
        rules = DebtRulesGenerator.generate_rules(user)
        
        assert rules.debt_payment_stability <= 0.90
        assert rules.refinancing_probability >= 0.05

class TestRulesValidation:
    """Pruebas de validación de reglas"""
    
    def test_income_rules_bounds(self):
        """Verificar que las reglas de ingreso estén en rangos válidos"""
        user = User(monthly_income=5000000)
        rules = IncomeRulesGenerator.generate_rules(user)
        
        assert 0 <= rules.annual_growth_mean <= 0.10
        assert 0 <= rules.annual_growth_std <= 0.05
        assert 0 <= rules.monthly_volatility <= 0.10
        assert 0 <= rules.downside_shock_probability <= 0.20
        assert rules.downside_shock_impact[0] < 0
        assert rules.downside_shock_impact[1] < 0
        
    def test_expense_rules_bounds(self):
        """Verificar que las reglas de gastos estén en rangos válidos"""
        user = User(monthly_income=5000000)
        rules = ExpenseRulesGenerator.generate_rules(user)
        
        assert 0 <= rules.inflation_mean <= 0.15
        assert 0 <= rules.inflation_std <= 0.05
        assert 0 <= rules.variable_expense_volatility <= 0.20
        assert 0 <= rules.unexpected_expense_probability <= 0.20
        assert rules.unexpected_expense_range[0] > 0