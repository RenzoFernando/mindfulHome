from app.simulation.models.rules import SavingsRules
from app.models.user import User

class SavingsRulesGenerator:
    @staticmethod
    def generate_rules(user: User) -> SavingsRules:
        base_rules = SavingsRules(
            savings_contribution_ratio=0.08,
            emergency_usage_threshold=0,
            rebuild_behavior=True
        )

        if user.monthly_income:
            if user.monthly_income > 15000000:
                base_rules.savings_contribution_ratio = 0.12
            elif user.monthly_income > 5000000:
                base_rules.savings_contribution_ratio = 0.10
            elif user.monthly_income < 2000000:
                base_rules.savings_contribution_ratio = 0.03

        if user.income_variability == "VARIABLE" or user.contract_type == "PRESTACION_SERVICIOS":
            base_rules.emergency_usage_threshold = 0.05

        return base_rules