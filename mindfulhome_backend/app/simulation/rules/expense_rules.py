from app.simulation.models.rules import ExpenseRules
from app.models.user import User

class ExpenseRulesGenerator:
    @staticmethod
    def generate_rules(user: User) -> ExpenseRules:
        base_rules = ExpenseRules()
        
        # Ajustar según dependientes
        if user.dependents and user.dependents > 2:
            base_rules.unexpected_expense_probability = 0.10
            base_rules.unexpected_expense_range = (1000000, 8000000)
        
        # Ajustar según nivel de ingresos
        if user.monthly_income and user.monthly_income > 10000000:
            base_rules.unexpected_expense_range = (1000000, 10000000)
        
        return base_rules