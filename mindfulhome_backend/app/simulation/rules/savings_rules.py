from app.simulation.models.rules import SavingsRules
from app.models.user import User

class SavingsRulesGenerator:
    @staticmethod
    def generate_rules(user: User) -> SavingsRules:
        """Genera reglas de ahorro basadas en el perfil del usuario"""
        base_rules = SavingsRules(
            savings_contribution_ratio=0.1,
            emergency_usage_threshold=0,
            rebuild_behavior=True
        )
        
        # Ajustar ratio de contribución según ingresos
        if user.monthly_income:
            if user.monthly_income > 15000000:  # >15M COP
                base_rules.savings_contribution_ratio = 0.15
            elif user.monthly_income > 5000000:  # 5M-15M COP
                base_rules.savings_contribution_ratio = 0.12
            elif user.monthly_income < 2000000:  # <2M COP
                base_rules.savings_contribution_ratio = 0.05
        
        # Ajustar según meta de ahorro
        if user.monthly_savings_goal and user.monthly_income:
            goal_ratio = user.monthly_savings_goal / user.monthly_income
            if goal_ratio > base_rules.savings_contribution_ratio:
                # Usuario es más agresivo en ahorro
                base_rules.savings_contribution_ratio = min(goal_ratio, 0.25)
        
        # Ajustar umbral de emergencia según estabilidad laboral
        if user.income_variability == "VARIABLE" or user.contract_type == "PRESTACION_SERVICIOS":
            base_rules.emergency_usage_threshold = 0.1
        elif user.income_variability == "FIJO" and user.contract_type == "INDEFINIDO":
            base_rules.emergency_usage_threshold = -0.05  # Permitir liquidez negativa pequeña antes de usar fondo
        
        # Comportamiento de reconstrucción según historial
        if user.total_savings and user.total_savings > 0:
            base_rules.rebuild_behavior = True
        else:
            base_rules.rebuild_behavior = False
            
        return base_rules