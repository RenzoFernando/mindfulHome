import pytest
import numpy as np
from datetime import datetime
from app.simulation.engine.aggregator import SimulationAggregator
from app.simulation.models.simulation_state import SimulationState, RiskStatus
from app.simulation.models.results import MetricPercentiles, TimelinePoint

class TestSimulationAggregator:
    """Pruebas del agregador de simulaciones"""
    
    @pytest.fixture
    def mock_simulations(self):
        """Crear simulaciones mock para pruebas"""
        simulations = []
        
        for sim_id in range(100):
            states = []
            for month in range(13):
                state = SimulationState(
                    month=month,
                    date=datetime.now().date(),
                    monthly_income=5000000,
                    fixed_expenses=1500000,
                    variable_expenses=1000000,
                    monthly_debt_payments=500000,
                    housing_cost=1500000,
                    total_savings=10000000 + sim_id * 100000,
                    emergency_fund=5000000
                )
                state.liquidity = np.random.normal(500000, 200000)
                state.housing_ratio = np.random.normal(0.3, 0.05)
                
                # Asignar estado de riesgo basado en liquidez
                if state.liquidity > 1000000:
                    state.risk_status = RiskStatus.SAFE
                elif state.liquidity > 250000:
                    state.risk_status = RiskStatus.MODERATE
                elif state.liquidity > 0:
                    state.risk_status = RiskStatus.RISKY
                else:
                    state.risk_status = RiskStatus.CRITICAL
                    
                states.append(state)
            simulations.append(states)
            
        return simulations
    
    def test_timeline_construction(self, mock_simulations):
        """Verificar construcción del timeline"""
        aggregator = SimulationAggregator(mock_simulations)
        results = aggregator.aggregate_results()
        
        assert len(results.timeline) == 13  # 12 meses + inicial
        assert isinstance(results.timeline[0], TimelinePoint)
        
    def test_percentile_calculation(self, mock_simulations):
        """Verificar cálculo de percentiles"""
        aggregator = SimulationAggregator(mock_simulations)
        results = aggregator.aggregate_results()
        
        # Verificar que p10 <= p50 <= p90
        for point in results.timeline:
            assert point.liquidity.p10 <= point.liquidity.p50
            assert point.liquidity.p50 <= point.liquidity.p90
            
    def test_stability_probability(self, mock_simulations):
        """Verificar cálculo de probabilidad de estabilidad"""
        aggregator = SimulationAggregator(mock_simulations)
        results = aggregator.aggregate_results()
        
        assert 0 <= results.stability_probability <= 1
        
        # En el mes final, la probabilidad debería ser razonable
        final_point = results.timeline[-1]
        assert 0 <= final_point.stability_probability <= 1
        
    def test_risk_distribution(self, mock_simulations):
        """Verificar distribución de riesgos"""
        aggregator = SimulationAggregator(mock_simulations)
        results = aggregator.aggregate_results()
        
        for point in results.timeline:
            total_prob = sum(point.risk_distribution.values())
            assert abs(total_prob - 1.0) < 0.01  # Debe sumar 1
            
    def test_extreme_cases(self, mock_simulations):
        """Verificar identificación de mejores y peores casos"""
        aggregator = SimulationAggregator(mock_simulations)
        results = aggregator.aggregate_results()
        
        # Mejor caso debería tener mejor liquidez que el peor caso
        assert results.best_case_results.get('liquidity', 0) >= results.worst_case_results.get('liquidity', 0)
        
    def test_sensitivity_analysis(self, mock_simulations):
        """Verificar análisis de sensibilidad"""
        aggregator = SimulationAggregator(mock_simulations)
        results = aggregator.aggregate_results()
        
        assert len(results.top_sensitive_variables) > 0
        for var in results.top_sensitive_variables:
            assert -1 <= var.correlation <= 1
            assert var.impact_score >= 0
            assert var.recommendation  # No debe estar vacío