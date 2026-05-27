import pytest
import numpy as np
from datetime import datetime
from app.simulation.engine.aggregator import SimulationAggregator
from app.simulation.models.simulation_state import SimulationState, RiskStatus

class TestSimulationAggregatorDetailed:
    """Pruebas detalladas del agregador"""
    
    @pytest.fixture
    def healthy_simulation(self):
        """Simulación con condiciones financieras saludables Y VARIABILIDAD REAL"""
        simulations = []
        
        for sim_id in range(100):
            states = []
            
            # Base mensual (misma para todos)
            monthly_income = 8000000
            fixed_expenses = 1500000
            variable_expenses = 1000000
            monthly_debt_payments = 300000
            housing_cost = 2000000
            total_savings = 20000000
            emergency_fund = 10000000
            
            # Variabilidad: cada simulación tiene una liquidez base diferente
            # entre 1M y 3M, variando por sim_id
            base_liquidity = 1000000 + (sim_id * 20000)  # 1M a 3M
            
            for month in range(61):  # 60 meses + inicial
                # La liquidez crece con el tiempo, pero cada simulación tiene su propia base
                monthly_growth = month * 30000  # 30k por mes
                liquidity = base_liquidity + monthly_growth
                
                state = SimulationState(
                    month=month,
                    date=datetime.now().date(),
                    monthly_income=monthly_income,
                    fixed_expenses=fixed_expenses,
                    variable_expenses=variable_expenses,
                    monthly_debt_payments=monthly_debt_payments,
                    housing_cost=housing_cost,
                    total_savings=total_savings + sim_id * 50000,  # variación en ahorros
                    emergency_fund=emergency_fund + sim_id * 25000  # variación en fondo
                )
                state.liquidity = liquidity
                state.housing_ratio = housing_cost / monthly_income
                state.debt_ratio = monthly_debt_payments / monthly_income
                state.emergency_months = state.emergency_fund / (fixed_expenses + variable_expenses)
                
                # Clasificar riesgo basado en liquidez
                if liquidity > 1500000:
                    state.risk_status = RiskStatus.SAFE
                elif liquidity > 800000:
                    state.risk_status = RiskStatus.MODERATE
                elif liquidity > 0:
                    state.risk_status = RiskStatus.RISKY
                else:
                    state.risk_status = RiskStatus.CRITICAL
                    
                states.append(state)
            simulations.append(states)
        
        # Verificar que hay variabilidad
        print(f"\nPrimera simulación liquidez final: {simulations[0][-1].liquidity:,.0f}")
        print(f"Última simulación liquidez final: {simulations[-1][-1].liquidity:,.0f}")
        
        return simulations
    
    @pytest.fixture
    def stressed_simulation(self):
        """Simulación con condiciones financieras estresadas"""
        simulations = []
        
        for sim_id in range(100):
            states = []
            # Liquidez inicial baja y decreciente
            base_liquidity = -1000000  # Liquidez negativa inicial
            for month in range(61):
                # Liquidez que empeora con el tiempo
                liquidity = base_liquidity - (month * 100000)
                # Ingreso bajo en relación a gastos
                monthly_income = 3000000
                housing_cost = 2500000  # 83% del ingreso (muy malo)
                
                state = SimulationState(
                    month=month,
                    date=datetime.now().date(),
                    monthly_income=monthly_income,
                    fixed_expenses=1500000,
                    variable_expenses=1000000,
                    monthly_debt_payments=500000,
                    housing_cost=housing_cost,
                    total_savings=1000000,
                    emergency_fund=500000
                )
                state.liquidity = liquidity
                state.housing_ratio = housing_cost / monthly_income
                state.debt_ratio = 500000 / monthly_income
                state.emergency_months = 500000 / (1500000 + 1000000)
                
                # Clasificar riesgo
                if liquidity > 0:
                    state.risk_status = RiskStatus.RISKY
                else:
                    state.risk_status = RiskStatus.CRITICAL
                    
                states.append(state)
            simulations.append(states)
            
        return simulations
    
    def test_healthy_simulation_health_score(self, healthy_simulation):
        """Verificar que simulaciones saludables tengan score alto"""
        aggregator = SimulationAggregator(healthy_simulation)
        
        # Calcular health score para cada simulación individualmente
        scores = []
        for sim in healthy_simulation:
            score = aggregator._calculate_financial_health_score(sim)
            scores.append(score)
        
        avg_score = np.mean(scores)
        print(f"\nScore promedio (saludable): {avg_score:.2f}")
        
        # Una simulación saludable debería tener score > 0.7
        assert avg_score > 0.7
    
    def test_stressed_simulation_health_score(self, stressed_simulation):
        """Verificar que simulaciones estresadas tengan score bajo"""
        aggregator = SimulationAggregator(stressed_simulation)
        
        scores = []
        for sim in stressed_simulation:
            score = aggregator._calculate_financial_health_score(sim)
            scores.append(score)
        
        avg_score = np.mean(scores)
        print(f"\nScore promedio (estresado): {avg_score:.2f}")
        
        # Una simulación estresada debería tener score < 0.3
        assert avg_score < 0.3
    
    def test_stability_probability_healthy(self, healthy_simulation):
        """Verificar probabilidad de estabilidad en simulación saludable"""
        aggregator = SimulationAggregator(healthy_simulation)
        results = aggregator.aggregate_results()
        
        print(f"\nEstabilidad (saludable): {results.stability_probability:.2%}")
        
        # Debería ser alta (>80%)
        assert results.stability_probability > 0.8
    
    def test_stability_probability_stressed(self, stressed_simulation):
        """Verificar probabilidad de estabilidad en simulación estresada"""
        aggregator = SimulationAggregator(stressed_simulation)
        results = aggregator.aggregate_results()
        
        print(f"\nEstabilidad (estresado): {results.stability_probability:.2%}")
        
        # Debería ser baja (<20%)
        assert results.stability_probability < 0.2
    
    def test_extreme_cases_healthy(self, healthy_simulation):
        """Verificar que mejor y peor caso tengan sentido en simulación saludable"""
        aggregator = SimulationAggregator(healthy_simulation)
        results = aggregator.aggregate_results()
        
        best_liquidity = results.best_case_results.get('liquidity', 0)
        worst_liquidity = results.worst_case_results.get('liquidity', 0)
        
        print(f"\nMejor caso liquidez: ${best_liquidity:,.0f}")
        print(f"Peor caso liquidez: ${worst_liquidity:,.0f}")
        
        # Ambos deberían ser positivos
        assert best_liquidity > 0
        assert worst_liquidity > 0
        # Mejor caso mejor que peor caso
        assert best_liquidity > worst_liquidity
    
    def test_extreme_cases_stressed(self, stressed_simulation):
        """Verificar que mejor y peor caso tengan sentido en simulación estresada"""
        aggregator = SimulationAggregator(stressed_simulation)
        results = aggregator.aggregate_results()
        
        best_liquidity = results.best_case_results.get('liquidity', 0)
        worst_liquidity = results.worst_case_results.get('liquidity', 0)
        
        print(f"\nMejor caso liquidez: ${best_liquidity:,.0f}")
        print(f"Peor caso liquidez: ${worst_liquidity:,.0f}")
        
        # Ambos deberían ser negativos o al menos el peor caso negativo
        assert worst_liquidity < 0
    
    def test_trajectory_classification(self):
        """Verificar clasificación de trayectorias"""
        aggregator = SimulationAggregator([[]])  # Placeholder
        
        # Caso 1: Crecimiento estable
        stable_states = []
        for i in range(60):
            state = SimulationState(
                month=i,
                date=datetime.now().date(),
                monthly_income=5000000,
                fixed_expenses=1500000,
                variable_expenses=1000000,
                monthly_debt_payments=300000,
                housing_cost=1500000,
                total_savings=10000000,
                emergency_fund=5000000,
                liquidity=1000000 + i * 100000,
                housing_ratio=0.3,
                debt_ratio=0.06,
                emergency_months=2
            )
            state.risk_status = RiskStatus.SAFE if i > 10 else RiskStatus.MODERATE
            stable_states.append(state)
        
        trajectory = aggregator._analyze_trajectory({"states": stable_states})
        print(f"\nTrayectoria crecimiento estable: {trajectory['type']}")
        assert trajectory['type'] == "stable_growth"
        
        # Caso 2: Deterioro progresivo
        decline_states = []
        for i in range(60):
            liquidity = 2000000 - i * 100000
            state = SimulationState(
                month=i,
                date=datetime.now().date(),
                monthly_income=3000000,
                fixed_expenses=2000000,
                variable_expenses=1500000,
                monthly_debt_payments=500000,
                housing_cost=2000000,
                total_savings=5000000 - i * 50000,
                emergency_fund=2000000 - i * 30000,
                liquidity=liquidity,
                housing_ratio=0.67,
                debt_ratio=0.17,
                emergency_months=0.5
            )
            state.risk_status = RiskStatus.CRITICAL if liquidity < 0 else RiskStatus.RISKY
            decline_states.append(state)
        
        trajectory = aggregator._analyze_trajectory({"states": decline_states})
        print(f"Trayectoria deterioro: {trajectory['type']}")
        assert trajectory['type'] == "progressive_decline"
    
    def test_financial_health_score_components(self):
        """Verificar cada componente del health score por separado"""
        aggregator = SimulationAggregator([[]])
        
        # Crear una simulación con estabilidad perfecta
        perfect_states = []
        for i in range(60):
            state = SimulationState(
                month=i,
                date=datetime.now().date(),
                monthly_income=5000000,
                fixed_expenses=1500000,
                variable_expenses=1000000,
                monthly_debt_payments=300000,
                housing_cost=1500000,
                total_savings=20000000,
                emergency_fund=10000000,
                liquidity=2000000,
                housing_ratio=0.3,
                debt_ratio=0.06,
                emergency_months=4,
                risk_status=RiskStatus.SAFE
            )
            perfect_states.append(state)
        
        score = aggregator._calculate_financial_health_score(perfect_states)
        print(f"\nScore con estabilidad perfecta: {score:.2f}")
        assert score > 0.9
        
        # Crear una simulación con mucha volatilidad pero buen final
        volatile_states = []
        for i in range(60):
            liquidity = 2000000 + np.random.normal(0, 1000000)
            state = SimulationState(
                month=i,
                date=datetime.now().date(),
                monthly_income=5000000,
                fixed_expenses=1500000,
                variable_expenses=1000000,
                monthly_debt_payments=300000,
                housing_cost=1500000,
                total_savings=20000000,
                emergency_fund=10000000,
                liquidity=liquidity,
                housing_ratio=0.3,
                debt_ratio=0.06,
                emergency_months=4,
                risk_status=RiskStatus.SAFE if liquidity > 500000 else RiskStatus.MODERATE
            )
            volatile_states.append(state)
        
        score = aggregator._calculate_financial_health_score(volatile_states)
        print(f"Score con volatilidad: {score:.2f}")
        # La volatilidad debería penalizar, score menor que el perfecto
        assert score < 0.95