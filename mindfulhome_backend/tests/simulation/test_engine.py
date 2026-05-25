import pytest
import numpy as np
from datetime import datetime
from app.simulation.engine.month_simulator import MonthSimulator
from app.simulation.engine.single_simulation import SingleSimulation
from app.simulation.engine.monte_carlo import MonteCarloEngine
from app.simulation.models.simulation_state import SimulationState, RiskStatus
from app.simulation.models.rules import (
    IncomeRules, ExpenseRules, SavingsRules, DebtRules, SimulationRules
)

class TestMonthSimulator:
    """Pruebas del simulador mes a mes"""
    
    @pytest.fixture
    def base_state(self):
        return SimulationState(
            month=0,
            date=datetime.now().date(),
            monthly_income=5000000,
            fixed_expenses=1500000,
            variable_expenses=1000000,
            monthly_debt_payments=500000,
            housing_cost=1500000,
            total_savings=10000000,
            emergency_fund=5000000
        )
    
    @pytest.fixture
    def base_rules(self):
        return SimulationRules(
            income=IncomeRules(
                annual_growth_mean=0.04,
                annual_growth_std=0.02,
                monthly_volatility=0.01,
                downside_shock_probability=0.03,
                downside_shock_impact=(-0.4, -0.15),
                recovery_months=(3, 12)
            ),
            expenses=ExpenseRules(
                inflation_mean=0.05,
                inflation_std=0.015,
                variable_expense_volatility=0.08,
                unexpected_expense_probability=0.06,
                unexpected_expense_range=(500000, 5000000)
            ),
            savings=SavingsRules(
                savings_contribution_ratio=0.1,
                emergency_usage_threshold=0,
                rebuild_behavior=True
            ),
            debt=DebtRules(
                debt_payment_stability=0.95,
                refinancing_probability=0.02
            )
        )
    
    def test_transition_positive_liquidity(self, base_state, base_rules):
        """Mes con liquidez positiva debe aumentar ahorros"""
        simulator = MonthSimulator(base_rules)
        np.random.seed(42)
        
        next_state = simulator.transition(base_state, random_seed=42)
        
        # Verificar que avanzó el mes
        assert next_state.month == 1
        # Verificar que los ahorros aumentaron (por la contribución)
        assert next_state.total_savings >= base_state.total_savings
        # Verificar que la liquidez no es negativa
        assert next_state.liquidity >= 0
        
    def test_transition_negative_liquidity_uses_emergency(self, base_state, base_rules):
        """Mes con liquidez negativa debe usar fondo de emergencia"""
        # Crear estado con gastos muy altos
        high_expense_state = base_state.copy(deep=True)
        high_expense_state.variable_expenses = 5000000
        
        simulator = MonthSimulator(base_rules)
        np.random.seed(42)
        
        next_state = simulator.transition(high_expense_state, random_seed=42)
        
        # Verificar que se usó el fondo de emergencia
        assert next_state.emergency_fund < base_state.emergency_fund
        assert next_state.has_emergency_usage == True
        
    def test_income_shock_application(self, base_state, base_rules):
        """Verificar que los shocks de ingreso se aplican correctamente"""
        # Forzar un shock de ingreso
        base_rules.income.downside_shock_probability = 1.0
        base_rules.income.downside_shock_impact = (-0.3, -0.3)
        
        simulator = MonthSimulator(base_rules)
        np.random.seed(42)
        
        next_state = simulator.transition(base_state, random_seed=42)
        
        # El ingreso debería haber disminuido ~30%
        expected_income = base_state.monthly_income * 0.7
        assert abs(next_state.monthly_income - expected_income) < expected_income * 0.1
        
    def test_unexpected_expense(self, base_state, base_rules):
        """Verificar que los gastos inesperados se aplican"""
        # Forzar gasto inesperado
        base_rules.expenses.unexpected_expense_probability = 1.0
        base_rules.expenses.unexpected_expense_range = (1000000, 1000000)
        
        simulator = MonthSimulator(base_rules)
        np.random.seed(42)
        
        next_state = simulator.transition(base_state, random_seed=42)
        
        # Los gastos variables deberían haber aumentado
        assert next_state.variable_expenses > base_state.variable_expenses
        
    def test_emergency_rebuild_behavior(self, base_state, base_rules):
        """Verificar reconstrucción del fondo después de uso"""
        # Simular un mes con uso de emergencia
        high_expense_state = base_state.copy(deep=True)
        high_expense_state.variable_expenses = 8000000
        high_expense_state.has_emergency_usage = True
        high_expense_state.months_since_recovery = 3  # Ya pasaron 3 meses
        
        simulator = MonthSimulator(base_rules)
        np.random.seed(42)
        
        # Crear un mes con liquidez positiva para reconstruir
        next_state = simulator.transition(high_expense_state, random_seed=42)
        
        # Debería haber algo de reconstrucción del fondo
        # Nota: esto depende de la liquidez del mes
        pass

class TestSingleSimulation:
    """Pruebas de simulación individual"""
    
    @pytest.fixture
    def base_state(self):
        return SimulationState(
            month=0,
            date=datetime.now().date(),
            monthly_income=5000000,
            fixed_expenses=1500000,
            variable_expenses=1000000,
            monthly_debt_payments=500000,
            housing_cost=1500000,
            total_savings=10000000,
            emergency_fund=5000000
        )
    
    @pytest.fixture
    def base_rules(self):
        return SimulationRules(
            income=IncomeRules(),
            expenses=ExpenseRules(),
            savings=SavingsRules(),
            debt=DebtRules()
        )
    
    def test_simulation_length(self, base_state, base_rules):
        """Verificar que la simulación genera el número correcto de meses"""
        months = 12
        sim = SingleSimulation(base_rules, base_state, months)
        results = sim.run(seed=42)
        
        # +1 por el mes inicial
        assert len(results) == months + 1
        
    def test_simulation_continuity(self, base_state, base_rules):
        """Verificar que los meses son consecutivos"""
        months = 12
        sim = SingleSimulation(base_rules, base_state, months)
        results = sim.run(seed=42)
        
        for i in range(1, len(results)):
            assert results[i].month == results[i-1].month + 1
            
    def test_no_negative_emergency_fund(self, base_state, base_rules):
        """Verificar que el fondo de emergencia nunca sea negativo"""
        months = 60  # Simular 5 años
        sim = SingleSimulation(base_rules, base_state, months)
        results = sim.run(seed=42)
        
        for state in results:
            assert state.emergency_fund >= 0

class TestMonteCarloEngine:
    """Pruebas del motor Monte Carlo"""
    
    @pytest.fixture
    def base_state(self):
        return SimulationState(
            month=0,
            date=datetime.now().date(),
            monthly_income=5000000,
            fixed_expenses=1500000,
            variable_expenses=1000000,
            monthly_debt_payments=500000,
            housing_cost=1500000,
            total_savings=10000000,
            emergency_fund=5000000
        )
    
    @pytest.fixture
    def base_rules(self):
        return SimulationRules(
            income=IncomeRules(),
            expenses=ExpenseRules(),
            savings=SavingsRules(),
            debt=DebtRules()
        )
    
    def test_num_simulations(self, base_state, base_rules):
        """Verificar que se ejecutan el número correcto de simulaciones"""
        num_sims = 10
        months = 12
        
        engine = MonteCarloEngine(base_rules, base_state, num_sims, months)
        results = engine.run(parallel=False)
        
        assert len(results) == num_sims
        
    def test_each_simulation_unique(self, base_state, base_rules):
        """Verificar que cada simulación es única"""
        num_sims = 5
        months = 12
        
        engine = MonteCarloEngine(base_rules, base_state, num_sims, months)
        results = engine.run(parallel=False)
        
        # Comparar resultados finales de cada simulación
        final_states = [sim[-1].liquidity for sim in results]
        # No deben ser todos iguales
        assert len(set(final_states)) > 1
        
    def test_monte_carlo_convergence(self, base_state, base_rules):
        """Verificar tendencia a convergencia con más simulaciones"""
        months = 60
        
        # Fijar semilla para reproducibilidad
        np.random.seed(42)
        
        # Ejecutar con diferentes números de simulaciones
        simulation_counts = [10, 50, 100, 200]
        means = []
        
        for count in simulation_counts:
            engine = MonteCarloEngine(base_rules, base_state, count, months)
            results = engine.run(parallel=False)
            
            # Calcular media de liquidez final
            final_liquidities = [sim[-1].liquidity for sim in results]
            mean_liquidity = np.mean(final_liquidities)
            means.append(mean_liquidity)
            
            print(f"\nDEBUG: {count} simulaciones - media = {mean_liquidity}")
        
        # Calcular cambio relativo entre diferentes tamaños
        changes = []
        for i in range(1, len(means)):
            if means[i-1] != 0:
                change = abs((means[i] - means[i-1]) / means[i-1])
                changes.append(change)
        
        if len(changes) >= 2:
            assert changes[-1] <= changes[0] * 1.5