import pytest
from app.services.comparator_service import ComparatorService
from app.simulation.models.comparison import Tradeoff
from app.simulation.models.results import SimulationResults

class TestComparatorService:
    """Pruebas del servicio de comparación"""
    
    @pytest.fixture
    def mock_results_a(self):
        """Mock de resultados para escenario A"""
        return SimulationResults(
            expected_results={},
            best_case_results={},
            worst_case_results={},
            stability_probability=0.75,
            liquidity_shortfall_probability=0.15,
            financial_stress_probability=0.10,
            timeline=[],
            top_sensitive_variables=[],
            num_simulations=1000,
            simulation_months=360
        )
    
    @pytest.fixture
    def mock_results_b(self):
        """Mock de resultados para escenario B"""
        return SimulationResults(
            expected_results={},
            best_case_results={},
            worst_case_results={},
            stability_probability=0.85,
            liquidity_shortfall_probability=0.08,
            financial_stress_probability=0.05,
            timeline=[],
            top_sensitive_variables=[],
            num_simulations=1000,
            simulation_months=360
        )
    
    def test_stability_improvement_calculation(self, mock_results_a, mock_results_b):
        """Verificar cálculo de mejora de estabilidad"""
        from app.services.comparator_service import ComparatorService
        
        # Crear instancia mínima
        comparator = ComparatorService.__new__(ComparatorService)
        
        # Calcular comparación
        comparison = comparator._calculate_comparison(
            mock_results_a, mock_results_b,
            {'name': 'A'}, {'name': 'B'}
        )
        
        assert comparison.stability_improvement == 0.10
        assert comparison.stability_probability_a == 0.75
        assert comparison.stability_probability_b == 0.85
        
    def test_risk_warning_generation(self, mock_results_a):
        """Verificar generación de advertencias de riesgo"""
        comparator = ComparatorService.__new__(ComparatorService)
        
        # Escenario riesgoso
        mock_results_a.stability_probability = 0.4
        mock_results_a.financial_stress_probability = 0.35
        
        warning = comparator._generate_risk_warning(
            mock_results_a, {}, []
        )
        
        assert warning is not None
        assert "50%" in warning or "30%" in warning
        
    def test_tradeoff_identification(self):
        """Verificar identificación de tradeoffs"""
        comparator = ComparatorService.__new__(ComparatorService)
        
        results_a = SimulationResults(
            expected_results={},
            best_case_results={},
            worst_case_results={},
            stability_probability=0.7,
            liquidity_shortfall_probability=0.2,
            financial_stress_probability=0.1,
            timeline=[],
            top_sensitive_variables=[
                type('obj', (object,), {
                    'variable': 'monthly_income',
                    'impact_score': 0.8,
                    'correlation': -0.7,
                    'recommendation': ''
                })(),
                type('obj', (object,), {
                    'variable': 'housing_cost',
                    'impact_score': 0.6,
                    'correlation': 0.5,
                    'recommendation': ''
                })()
            ],
            num_simulations=1000,
            simulation_months=360
        )
        
        results_b = SimulationResults(
            expected_results={},
            best_case_results={},
            worst_case_results={},
            stability_probability=0.8,
            liquidity_shortfall_probability=0.1,
            financial_stress_probability=0.05,
            timeline=[],
            top_sensitive_variables=[
                type('obj', (object,), {
                    'variable': 'monthly_income',
                    'impact_score': 0.5,
                    'correlation': -0.5,
                    'recommendation': ''
                })(),
                type('obj', (object,), {
                    'variable': 'debt_payments',
                    'impact_score': 0.7,
                    'correlation': 0.6,
                    'recommendation': ''
                })()
            ],
            num_simulations=1000,
            simulation_months=360
        )
        
        tradeoffs = comparator._identify_tradeoffs(results_a, results_b)
        
        assert len(tradeoffs) > 0
        assert any(t.variable == 'monthly_income' for t in tradeoffs)