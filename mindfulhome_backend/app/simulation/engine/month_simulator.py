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
            
        next_state = current_state.model_copy(deep=True)
        next_state.month += 1
        next_state.date = current_state.date + timedelta(days=30)
        
        # 1. Evolución de ingresos
        next_state.monthly_income = self._evolve_income(current_state)
        
        # 2. Evolución de gastos
        next_state.fixed_expenses = self._evolve_expenses(current_state.fixed_expenses)
        next_state.variable_expenses = self._evolve_variable_expenses(current_state)
        
        # 3. Evolución de deudas
        next_state.monthly_debt_payments = self._evolve_debt(current_state)
        
        # 4. Manejar el fin del período de overlap
        if next_state.rent_overlap_months_remaining > 0:
            next_state.rent_overlap_months_remaining -= 1
            
            # Cuando termina el overlap, dejar de pagar renta
            if next_state.rent_overlap_months_remaining == 0:
                next_state.is_renting = False
                next_state.housing_cost = next_state.base_mortgage_payment
                print(f"DEBUG: Período de overlap terminado en mes {next_state.month}. Ahora solo hipoteca.")
            else:
                # Durante overlap, el housing cost es hipoteca + renta
                next_state.housing_cost = next_state.base_mortgage_payment + next_state.base_monthly_rent
        else:
            # Sin overlap, actualizar housing cost con inflación (solo si no es renta pura)
            if next_state.has_mortgage:
                next_state.housing_cost = current_state.housing_cost * (1 + self._get_monthly_inflation())
            elif next_state.is_renting:
                # Si es solo renta, aplicar inflación a la renta
                next_state.housing_cost = current_state.housing_cost * (1 + self._get_monthly_inflation())
                next_state.base_monthly_rent = next_state.housing_cost
        
        # 5. Manejo de ahorros y emergencias
        next_state = self._handle_savings_and_emergencies(current_state, next_state)
        
        # 6. Calcular métricas
        next_state.calculate_metrics()
        
        # 7. Actualizar contadores de recuperación si aplica
        if next_state.has_emergency_usage and next_state.months_since_recovery is not None:
            next_state.months_since_recovery += 1
            
        return next_state
    
    def _evolve_income(self, state: SimulationState) -> float:
        """Evoluciona el ingreso mensual con crecimiento y shocks"""
        # Aplicar crecimiento anual con volatilidad mensual
        monthly_growth = np.random.normal(
            self.rules.income.annual_growth_mean / 12,
            self.rules.income.annual_growth_std / np.sqrt(12)
        )
        
        # Volatilidad mensual adicional
        volatility_impact = np.random.normal(0, self.rules.income.monthly_volatility)
        
        new_income = state.monthly_income * (1 + monthly_growth + volatility_impact)
        
        # Verificar shock negativo (pérdida de empleo, reducción de horas, etc.)
        if np.random.random() < self.rules.income.downside_shock_probability:
            shock_impact = np.random.uniform(*self.rules.income.downside_shock_impact)
            new_income *= (1 + shock_impact)
            
        return max(new_income, 0)
    
    def _evolve_expenses(self, current_expense: float) -> float:
        """Evoluciona gastos por inflación"""
        monthly_inflation = self._get_monthly_inflation()
        return current_expense * (1 + monthly_inflation)
    
    def _evolve_variable_expenses(self, state: SimulationState) -> float:
        """Evoluciona gastos variables con volatilidad y gastos inesperados"""
        base_evolution = self._evolve_expenses(state.variable_expenses)
        
        # Volatilidad mensual de gastos variables
        volatility = np.random.normal(0, self.rules.expenses.variable_expense_volatility)
        new_expenses = base_evolution * (1 + volatility)
        
        # Gastos inesperados (reparaciones, salud, etc.)
        if np.random.random() < self.rules.expenses.unexpected_expense_probability:
            unexpected = np.random.uniform(*self.rules.expenses.unexpected_expense_range)
            new_expenses += unexpected
            
        return max(new_expenses, 0)
    
    def _evolve_debt(self, state: SimulationState) -> float:
        """Evoluciona los pagos de deuda mensuales"""
        current_payment = state.monthly_debt_payments
        
        if np.random.random() > self.rules.debt.debt_payment_stability:
            reduction = np.random.uniform(0.2, 0.5)
            new_payment = current_payment * (1 - reduction)
        else:
            new_payment = current_payment
            
        if np.random.random() < self.rules.debt.refinancing_probability:
            change = np.random.uniform(-0.15, 0.25)
            new_payment = new_payment * (1 + change)
            
        # Ajustar por inflación
        new_payment = new_payment * (1 + self._get_monthly_inflation())
        
        return max(new_payment, 0)
    
    def _handle_savings_and_emergencies(self, current_state: SimulationState, 
                                        next_state: SimulationState) -> SimulationState:
        """
        Maneja la lógica de ahorros y uso de fondo de emergencia.
        """
        
        # Calcular flujo de caja del mes
        total_expenses = (
            next_state.fixed_expenses + 
            next_state.variable_expenses + 
            next_state.monthly_debt_payments + 
            next_state.housing_cost
        )
        cash_flow = next_state.monthly_income - total_expenses
        
        # La liquidez ES el flujo de caja (simple y realista)
        next_state.liquidity = cash_flow
        next_state.liquidity_after_savings = cash_flow
        
        # Solo usar fondo de emergencia si hay déficit SIGNIFICATIVO
        if cash_flow < 0:
            deficit = abs(cash_flow)
            
            # Usar fondo de emergencia solo si el déficit supera el 10% del ingreso
            if deficit > next_state.monthly_income * 0.1 and next_state.emergency_fund > 0:
                if next_state.emergency_fund >= deficit:
                    next_state.emergency_fund -= deficit
                    next_state.liquidity = 0
                    next_state.liquidity_after_savings = 0
                    next_state.has_emergency_usage = True
                else:
                    # Usar parte del fondo
                    next_state.liquidity += next_state.emergency_fund
                    next_state.liquidity_after_savings = next_state.liquidity
                    next_state.emergency_fund = 0
                    next_state.has_emergency_usage = True
        else:
            # Mes positivo: ahorrar solo si hay excedente significativo
            # (más del 5% del ingreso después de gastos)
            if cash_flow > next_state.monthly_income * 0.05:
                savings_contribution = cash_flow * 0.1  # Ahorrar 10% del excedente
                
                # Reconstruir fondo de emergencia si es necesario
                if next_state.emergency_fund < next_state.monthly_income * 3:
                    rebuild = min(savings_contribution * 0.3, 
                                next_state.monthly_income * 3 - next_state.emergency_fund)
                    next_state.emergency_fund += rebuild
                    savings_contribution -= rebuild
                
                if savings_contribution > 0:
                    next_state.total_savings += savings_contribution
            
            # Resetear flag de emergencia después de tiempo suficiente
            if current_state.has_emergency_usage and current_state.months_since_recovery:
                if current_state.months_since_recovery > 6:  # 6 meses de recuperación
                    next_state.has_emergency_usage = False
                    next_state.months_since_recovery = None
                        
        return next_state
    
    def _get_monthly_inflation(self) -> float:
        """
        Calcula inflación mensual a partir de tasa anual.
        Ejemplo: 5% anual -> ~0.407% mensual
        """
        return np.random.normal(
            self.rules.expenses.inflation_mean / 12,
            self.rules.expenses.inflation_std / np.sqrt(12)
        )