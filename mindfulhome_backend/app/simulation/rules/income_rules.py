from app.simulation.models.rules import IncomeRules
from app.models.user import User

class IncomeRulesGenerator:
    @staticmethod
    def generate_rules(user: User) -> IncomeRules:
        """Genera reglas de ingreso basadas en el perfil del usuario"""
        base_rules = IncomeRules()
        
        # Ajustar según tipo de ingreso
        if user.income_variability == "VARIABLE":
            base_rules.monthly_volatility = 0.03
            base_rules.downside_shock_probability = 0.08
        elif user.income_variability == "MIXTO":
            base_rules.monthly_volatility = 0.02
            base_rules.downside_shock_probability = 0.05
        
        # Ajustar según tipo de contrato
        if user.contract_type == "FIJO":
            base_rules.downside_shock_probability = 0.01
        elif user.contract_type == "PRESTACION_SERVICIOS":
            base_rules.downside_shock_probability = 0.10
            base_rules.monthly_volatility = 0.025
        
        # Ajustar según antigüedad
        if user.job_seniority_months and user.job_seniority_months > 24:
            base_rules.downside_shock_probability *= 0.5
        
        return base_rules