from app.simulation.models.rules import DebtRules
from app.models.user import User

class DebtRulesGenerator:
    @staticmethod
    def generate_rules(user: User) -> DebtRules:
        """Genera reglas de deuda basadas en el perfil del usuario"""
        base_rules = DebtRules(
            debt_payment_stability=0.95,
            refinancing_probability=0.02
        )
        
        # Ajustar según nivel de endeudamiento
        if user.monthly_income and user.monthly_debt_payments:
            debt_to_income = user.monthly_debt_payments / user.monthly_income
            
            if debt_to_income > 0.4:  # Alto nivel de endeudamiento
                base_rules.debt_payment_stability = 0.85  # Mayor riesgo de impago
                base_rules.refinancing_probability = 0.08  # Mayor probabilidad de buscar refinanciamiento
            elif debt_to_income > 0.3:  # Endeudamiento moderado
                base_rules.debt_payment_stability = 0.92
                base_rules.refinancing_probability = 0.05
            elif debt_to_income < 0.15:  # Bajo endeudamiento
                base_rules.debt_payment_stability = 0.98
                base_rules.refinancing_probability = 0.01
        
        # Ajustar según tipo de ingresos
        if user.income_variability == "VARIABLE":
            # Ingresos variables aumentan riesgo de impago
            base_rules.debt_payment_stability *= 0.95
            base_rules.refinancing_probability *= 1.5
        elif user.income_variability == "FIJO" and user.contract_type == "INDEFINIDO":
            # Ingresos estables mejoran estabilidad
            base_rules.debt_payment_stability *= 1.02
        
        # Ajustar según antigüedad laboral
        if user.job_seniority_months and user.job_seniority_months > 36:
            # Mayor antigüedad = más estabilidad
            base_rules.debt_payment_stability = min(base_rules.debt_payment_stability * 1.03, 0.99)
        
        # Ajustar según deuda total vs ahorros
        if user.total_debt and user.total_savings:
            debt_to_savings = user.total_debt / user.total_savings if user.total_savings > 0 else float('inf')
            if debt_to_savings > 5:  # Deuda muy alta vs ahorros
                base_rules.debt_payment_stability *= 0.9
                base_rules.refinancing_probability *= 1.3
        
        # Limitar valores a rangos realistas
        base_rules.debt_payment_stability = max(0.70, min(0.99, base_rules.debt_payment_stability))
        base_rules.refinancing_probability = max(0.005, min(0.15, base_rules.refinancing_probability))
        
        return base_rules