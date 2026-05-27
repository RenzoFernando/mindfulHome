from app.simulation.models.rules import ExpenseRules
from app.models.user import User

class ExpenseRulesGenerator:
    @staticmethod
    def generate_rules(user: User) -> ExpenseRules:
        base_rules = ExpenseRules()

        if user.dependents and user.dependents > 2:
            base_rules.unexpected_expense_probability = 0.03
            base_rules.unexpected_expense_range = (200000, 2000000)

        if user.monthly_income and user.monthly_income > 10000000:
            base_rules.unexpected_expense_range = (200000, 2000000)

        return base_rules