from app.simulation.models.rules import DebtRules
from app.models.user import User

class DebtRulesGenerator:
    @staticmethod
    def generate_rules(user: User) -> DebtRules:
        base_rules = DebtRules(
            debt_payment_stability=0.98,
            refinancing_probability=0.01
        )

        if user.monthly_income and user.monthly_debt_payments:
            debt_to_income = user.monthly_debt_payments / user.monthly_income

            if debt_to_income > 0.4:
                base_rules.debt_payment_stability = 0.92
                base_rules.refinancing_probability = 0.04
            elif debt_to_income > 0.3:
                base_rules.debt_payment_stability = 0.95
                base_rules.refinancing_probability = 0.03
            elif debt_to_income < 0.15:
                base_rules.debt_payment_stability = 0.99
                base_rules.refinancing_probability = 0.005

        if user.income_variability == "VARIABLE":
            base_rules.debt_payment_stability *= 0.98
            base_rules.refinancing_probability *= 1.2
        elif user.income_variability == "FIJO" and user.contract_type == "INDEFINIDO":
            base_rules.debt_payment_stability = min(base_rules.debt_payment_stability * 1.01, 0.995)

        if user.total_debt and user.total_savings:
            debt_to_savings = user.total_debt / user.total_savings if user.total_savings > 0 else float('inf')

            if debt_to_savings > 5:
                base_rules.debt_payment_stability *= 0.97
                base_rules.refinancing_probability *= 1.1

        base_rules.debt_payment_stability = max(0.85, min(0.995, base_rules.debt_payment_stability))
        base_rules.refinancing_probability = max(0.002, min(0.08, base_rules.refinancing_probability))

        return base_rules