import numpy as np
from datetime import datetime, timedelta
from app.simulation.models.simulation_state import SimulationState
from app.simulation.models.rules import SimulationRules

class MonthSimulator:
    def __init__(self, rules: SimulationRules):
        self.rules = rules
        
    def transition(self, current_state: SimulationState, random_seed: int = None) -> SimulationState:
        """Calcula el estado del próximo mes"""
        if random_seed:
            np.random.seed(random_seed)
            
        next_state = current_state.copy(deep=True)
        next_state.month += 1
        next_state.date = current_state.date + timedelta(days=30)
        
        # 1. Evolución de ingresos
        next_state.monthly_income = self._evolve_income(current_state)
        
        # 2. Evolución de gastos
        next_state.fixed_expenses = self._evolve_expenses(current_state.fixed_expenses)
        next_state.variable_expenses = self._evolve_variable_expenses(current_state)
        
        # 3. Evolución de deudas (antes de manejar ahorros)
        next_state.monthly_debt_payments = self._evolve_debt(current_state)
        
        # 4. Actualizar housing cost (con inflación)
        next_state.housing_cost = current_state.housing_cost * (1 + self._get_monthly_inflation())
        
        # 5. Manejo de ahorros y emergencias (después de tener todos los gastos)
        next_state = self._handle_savings_and_emergencies(current_state, next_state)
        
        # 6. Calcular métricas
        next_state.calculate_metrics()
        
        # 7. Actualizar contadores de recuperación si aplica
        if next_state.has_emergency_usage and next_state.months_since_recovery is not None:
            next_state.months_since_recovery += 1
            
        return next_state
    
    def _evolve_income(self, state: SimulationState) -> float:
        # Aplicar crecimiento anual con volatilidad mensual
        monthly_growth = np.random.normal(
            self.rules.income.annual_growth_mean / 12,
            self.rules.income.annual_growth_std / np.sqrt(12)
        )
        
        # Volatilidad mensual adicional
        volatility_impact = np.random.normal(0, self.rules.income.monthly_volatility)
        
        new_income = state.monthly_income * (1 + monthly_growth + volatility_impact)
        
        # Verificar shock negativo
        if np.random.random() < self.rules.income.downside_shock_probability:
            shock_impact = np.random.uniform(*self.rules.income.downside_shock_impact)
            new_income *= (1 + shock_impact)
            
        return max(new_income, 0)
    
    def _evolve_expenses(self, current_expense: float) -> float:
        monthly_inflation = self._get_monthly_inflation()
        return current_expense * (1 + monthly_inflation)
    
    def _evolve_variable_expenses(self, state: SimulationState) -> float:
        base_evolution = self._evolve_expenses(state.variable_expenses)
        volatility = np.random.normal(0, self.rules.expenses.variable_expense_volatility)
        new_expenses = base_evolution * (1 + volatility)
        
        # Gastos inesperados
        if np.random.random() < self.rules.expenses.unexpected_expense_probability:
            unexpected = np.random.uniform(*self.rules.expenses.unexpected_expense_range)
            new_expenses += unexpected
            
        return max(new_expenses, 0)
    
    def _evolve_debt(self, state: SimulationState) -> float:
        """Evoluciona los pagos de deuda mensuales"""
        current_payment = state.monthly_debt_payments
        
        # Verificar estabilidad en pagos
        if np.random.random() > self.rules.debt.debt_payment_stability:
            # Usuario no puede pagar la deuda completa este mes
            # Reducir pago entre 20-50%
            reduction = np.random.uniform(0.2, 0.5)
            new_payment = current_payment * (1 - reduction)
        else:
            new_payment = current_payment
            
        # Posible refinanciamiento
        if np.random.random() < self.rules.debt.refinancing_probability:
            # Refinanciar puede aumentar o disminuir la cuota
            change = np.random.uniform(-0.15, 0.25)  # Puede subir o bajar
            new_payment = new_payment * (1 + change)
            
        # Ajustar por inflación
        new_payment = new_payment * (1 + self._get_monthly_inflation())
        
        return max(new_payment, 0)
    
    def _handle_savings_and_emergencies(self, current_state: SimulationState, 
                                        next_state: SimulationState) -> SimulationState:
        """Maneja la lógica de ahorros, contribuciones y uso de fondo de emergencia"""
        
        # Calcular flujo de caja del mes
        total_expenses = (next_state.fixed_expenses + next_state.variable_expenses + next_state.monthly_debt_payments + next_state.housing_cost)
        raw_liquidity = next_state.monthly_income - total_expenses
        
        # Determinar si podemos ahorrar este mes
        savings_contribution = 0
        emergency_used = 0
        
        # Umbral para usar fondo de emergencia
        threshold = next_state.monthly_income * self.rules.savings.emergency_usage_threshold
        
        if raw_liquidity >= 0:
            # Mes positivo: ahorrar según ratio
            savings_contribution = next_state.monthly_income * self.rules.savings.savings_contribution_ratio
            
            emergency_target = next_state.monthly_income * 3  # 3 meses de ingresos como target
            if next_state.emergency_fund < emergency_target and self.rules.savings.rebuild_behavior:
                rebuild_amount = min(savings_contribution * 0.3, emergency_target - next_state.emergency_fund)
                next_state.emergency_fund += rebuild_amount
                savings_contribution -= rebuild_amount
            
            # Resto va a ahorros totales
            next_state.total_savings += savings_contribution
            
            if current_state.has_emergency_usage and self.rules.savings.rebuild_behavior:
                if current_state.months_since_recovery and current_state.months_since_recovery > 2:
                    recovery_contribution = raw_liquidity * 0.2
                    next_state.emergency_fund += recovery_contribution
                    raw_liquidity -= recovery_contribution
            
            next_state.liquidity = raw_liquidity - savings_contribution
            next_state.liquidity_after_savings = next_state.liquidity
            
        else:
            deficit = abs(raw_liquidity)
            
            if next_state.emergency_fund >= deficit:
                next_state.emergency_fund -= deficit
                emergency_used = deficit
                next_state.liquidity = 0
                next_state.liquidity_after_savings = 0
                next_state.has_emergency_usage = True
                next_state.months_since_recovery = 0
            else:
                if next_state.emergency_fund > 0:
                    emergency_used = next_state.emergency_fund
                    next_state.emergency_fund = 0
                    deficit -= emergency_used
                
                next_state.liquidity = -deficit
                next_state.liquidity_after_savings = next_state.liquidity
                next_state.has_emergency_usage = True
                next_state.months_since_recovery = 0
                
                if deficit > next_state.monthly_income and next_state.total_savings > 0:
                    savings_used = min(deficit, next_state.total_savings)
                    next_state.total_savings -= savings_used
                    next_state.liquidity += savings_used
                    
        # Registrar uso de emergencia en metadata
        if emergency_used > 0:
            next_state.has_emergency_usage = True
            
        return next_state
    
    def _get_monthly_inflation(self) -> float:
        return np.random.normal(
            self.rules.expenses.inflation_mean / 12,
            self.rules.expenses.inflation_std / np.sqrt(12)
        )