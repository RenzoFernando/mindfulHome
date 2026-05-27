from app.simulation.models.rules import IncomeRules
from app.models.user import User

class IncomeRulesGenerator:
    @staticmethod
    def generate_rules(user: User) -> IncomeRules:
        base_rules = IncomeRules()

        if user.income_variability == "VARIABLE":
            base_rules.monthly_volatility = 0.008
            base_rules.downside_shock_probability = 0.02
        elif user.income_variability == "MIXTO":
            base_rules.monthly_volatility = 0.005
            base_rules.downside_shock_probability = 0.015

        if user.contract_type == "FIJO":
            base_rules.downside_shock_probability = 0.005
        elif user.contract_type == "PRESTACION_SERVICIOS":
            base_rules.downside_shock_probability = 0.03
            base_rules.monthly_volatility = 0.01

        if user.job_seniority_months and user.job_seniority_months > 24:
            base_rules.downside_shock_probability *= 0.7

        return base_rules