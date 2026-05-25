import pytest
from datetime import datetime
from app.simulation.engine.monte_carlo import MonteCarloEngine
from app.simulation.engine.aggregator import SimulationAggregator
from app.simulation.models.simulation_state import SimulationState
from app.simulation.models.rules import SimulationRules, IncomeRules, ExpenseRules, SavingsRules, DebtRules

class TestFullSimulationPipeline:
    """Pruebas de integración del pipeline completo"""
    
    @pytest.fixture
    def realistic_user_state(self):
        """Estado realista de un usuario típico"""
        return SimulationState(
            month=0,
            date=datetime.now().date(),
            monthly_income=4500000,
            fixed_expenses=1200000,
            variable_expenses=800000,
            monthly_debt_payments=400000,
            housing_cost=1500000,
            total_savings=15000000,
            emergency_fund=8000000
        )
    
    @pytest.fixture
    def realistic_rules(self):
        """Reglas realistas para un usuario típico"""
        return SimulationRules(
            income=IncomeRules(
                annual_growth_mean=0.04,
                annual_growth_std=0.02,
                monthly_volatility=0.01,
                downside_shock_probability=0.03,
                downside_shock_impact=(-0.3, -0.1),
                recovery_months=(3, 6)
            ),
            expenses=ExpenseRules(
                inflation_mean=0.05,
                inflation_std=0.015,
                variable_expense_volatility=0.05,
                unexpected_expense_probability=0.05,
                unexpected_expense_range=(500000, 3000000)
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
    
    def test_end_to_end_simulation(self, realistic_user_state, realistic_rules):
        """Prueba end-to-end de simulación Monte Carlo"""
        
        engine = MonteCarloEngine(
            rules=realistic_rules,
            initial_state=realistic_user_state,
            num_simulations=100,
            months=360  # 30 años
        )
        
        simulations = engine.run(parallel=False)
        
        assert len(simulations) == 100
        assert all(len(sim) == 361 for sim in simulations)
        
        aggregator = SimulationAggregator(simulations)
        results = aggregator.aggregate_results()
        
        assert results.num_simulations == 100
        assert results.simulation_months == 360
        
        assert len(results.timeline) == 361
        assert results.timeline[0].month == 0
        
        assert 0 <= results.stability_probability <= 1
        assert 0 <= results.liquidity_shortfall_probability <= 1
        
        assert len(results.top_sensitive_variables) > 0
        
        early_stability = results.timeline[12].stability_probability  # Año 1
        late_stability = results.timeline[120].stability_probability  # Año 10
        
        assert abs(late_stability - early_stability) <= 0.5
        
    def test_stress_scenario(self, realistic_user_state, realistic_rules):
        """Prueba de escenario de estrés (pérdida de empleo)"""
        
        stress_rules = realistic_rules.copy(deep=True)
        stress_rules.income.downside_shock_probability = 0.5
        stress_rules.income.downside_shock_impact = (-0.5, -0.3)
        
        engine = MonteCarloEngine(
            rules=stress_rules,
            initial_state=realistic_user_state,
            num_simulations=100,
            months=60
        )
        
        simulations = engine.run(parallel=False)
        aggregator = SimulationAggregator(simulations)
        results = aggregator.aggregate_results()
        
        assert results.stability_probability < 0.7
        assert results.liquidity_shortfall_probability > 0.2
                
    def test_optimistic_scenario(self, realistic_user_state, realistic_rules):
        """Prueba de escenario optimista"""
        
        # Caso base con reglas realistas
        base_engine = MonteCarloEngine(
            rules=realistic_rules,
            initial_state=realistic_user_state,
            num_simulations=30,
            months=12
        )
        base_simulations = base_engine.run(parallel=False)
        base_aggregator = SimulationAggregator(base_simulations)
        base_results = base_aggregator.aggregate_results()
        
        # Caso optimista con reglas mejoradas
        optimistic_rules = SimulationRules(
            income=IncomeRules(
                annual_growth_mean=0.08,
                annual_growth_std=0.01,
                monthly_volatility=0.005,
                downside_shock_probability=0.005,
                downside_shock_impact=(-0.2, -0.1),
                recovery_months=(2, 4)
            ),
            expenses=ExpenseRules(
                inflation_mean=0.03,
                inflation_std=0.01,
                variable_expense_volatility=0.02,
                unexpected_expense_probability=0.02,
                unexpected_expense_range=(200000, 1000000)
            ),
            savings=SavingsRules(
                savings_contribution_ratio=0.15,
                emergency_usage_threshold=-0.1,
                rebuild_behavior=True
            ),
            debt=DebtRules(
                debt_payment_stability=0.98,
                refinancing_probability=0.01
            )
        )
        
        engine = MonteCarloEngine(
            rules=optimistic_rules,
            initial_state=realistic_user_state,
            num_simulations=30,
            months=12
        )
        
        simulations = engine.run(parallel=False)
        aggregator = SimulationAggregator(simulations)
        results = aggregator.aggregate_results()
        
        # Verificar que el escenario optimista es mejor que el base
        assert results.stability_probability >= base_results.stability_probability
        
        # Verificar mejora en liquidez
        if 'liquidity' in results.expected_results and 'liquidity' in base_results.expected_results:
            liquidity_opt = results.expected_results['liquidity'].p50
            liquidity_base = base_results.expected_results['liquidity'].p50
            assert liquidity_opt >= liquidity_base