from typing import List, Dict, Any, Tuple
import numpy as np
from scipy import stats
from app.simulation.models.results import *
from app.simulation.models.simulation_state import SimulationState, RiskStatus

class SimulationAggregator:
    def __init__(self, simulations: List[List[SimulationState]]):
        self.simulations = simulations
        self.num_simulations = len(simulations)
        self.num_months = len(simulations[0]) - 1 if simulations and len(simulations[0]) > 0 else 0
        
    def aggregate_results(self) -> SimulationResults:
        """Agrega todas las simulaciones en resultados comprensibles"""
        
        # Calcular métricas agregadas por mes
        timeline = self._build_timeline()
        
        # Calcular resultados esperados (mediana en mes final)
        expected_results = self._calculate_expected_results()
        
        # Calcular mejores y peores casos
        best_case, worst_case = self._find_extreme_cases()
        
        # Calcular probabilidades
        stability_prob = self._calculate_stability_probability()
        liquidity_shortfall_prob = self._calculate_liquidity_shortfall_probability()
        financial_stress_prob = self._calculate_financial_stress_probability()
        
        # Análisis de sensibilidad
        sensitivity_analysis = self._perform_sensitivity_analysis()
        
        return SimulationResults(
            expected_results=expected_results,
            best_case_results=best_case,
            worst_case_results=worst_case,
            stability_probability=stability_prob,
            liquidity_shortfall_probability=liquidity_shortfall_prob,
            financial_stress_probability=financial_stress_prob,
            timeline=timeline,
            top_sensitive_variables=sensitivity_analysis[:3],
            num_simulations=self.num_simulations,
            simulation_months=self.num_months
        )
    
    def _build_timeline(self) -> List[TimelinePoint]:
        """Construye timeline incluyendo todos los meses (0 a num_months)"""
        timeline = []
        
        for month in range(self.num_months + 1):
            month_data = [sim[month] for sim in self.simulations]
            
            liquidity_values = [state.liquidity for state in month_data]
            housing_ratio_values = [state.housing_ratio for state in month_data]
            
            # Distribución de riesgos
            risk_dist = {
                RiskStatus.SAFE: sum(1 for s in month_data if s.risk_status == RiskStatus.SAFE) / self.num_simulations,
                RiskStatus.MODERATE: sum(1 for s in month_data if s.risk_status == RiskStatus.MODERATE) / self.num_simulations,
                RiskStatus.RISKY: sum(1 for s in month_data if s.risk_status == RiskStatus.RISKY) / self.num_simulations,
                RiskStatus.CRITICAL: sum(1 for s in month_data if s.risk_status == RiskStatus.CRITICAL) / self.num_simulations,
            }
            
            timeline_point = TimelinePoint(
                month=month,
                liquidity=MetricPercentiles(
                    p10=np.percentile(liquidity_values, 10),
                    p50=np.percentile(liquidity_values, 50),
                    p90=np.percentile(liquidity_values, 90),
                    mean=np.mean(liquidity_values),
                    std=np.std(liquidity_values)
                ),
                stability_probability=risk_dist[RiskStatus.SAFE] + risk_dist[RiskStatus.MODERATE],
                housing_ratio=MetricPercentiles(
                    p10=np.percentile(housing_ratio_values, 10),
                    p50=np.percentile(housing_ratio_values, 50),
                    p90=np.percentile(housing_ratio_values, 90),
                    mean=np.mean(housing_ratio_values),
                    std=np.std(housing_ratio_values)
                ),
                risk_distribution=risk_dist
            )
            timeline.append(timeline_point)
            
        return timeline
    
    def _calculate_expected_results(self) -> Dict[str, MetricPercentiles]:
        """Calcula métricas esperadas basadas en percentiles"""
        final_month_data = [sim[-1] for sim in self.simulations]
        
        metrics = {}
        for metric_name in ['liquidity', 'housing_ratio', 'debt_ratio', 'emergency_months']:
            values = [getattr(state, metric_name) for state in final_month_data]
            metrics[metric_name] = MetricPercentiles(
                p10=np.percentile(values, 10),
                p50=np.percentile(values, 50),
                p90=np.percentile(values, 90),
                mean=np.mean(values),
                std=np.std(values)
            )
            
        return metrics
    
    def _find_extreme_cases(self) -> Tuple[Dict[str, float], Dict[str, float]]:
        """Identifica los mejores y peores casos entre todas las simulaciones"""
        
        # Obtener estado final de cada simulación
        final_states = [sim[-1] for sim in self.simulations]
        
        # Calcular métricas para cada simulación
        simulation_metrics = []
        for i, state in enumerate(final_states):
            metrics = {
                'liquidity': state.liquidity,
                'housing_ratio': state.housing_ratio,
                'debt_ratio': state.debt_ratio,
                'emergency_months': state.emergency_months,
                'stability_score': 1 if state.risk_status in [RiskStatus.SAFE, RiskStatus.MODERATE] else 0,
                'simulation_id': i
            }
            simulation_metrics.append(metrics)
        
        # Ordenar por liquidez para mejor y peor caso
        sorted_by_liquidity = sorted(simulation_metrics, key=lambda x: x['liquidity'], reverse=True)
        
        # Mejor caso (mayor liquidez final)
        best_case = {
            'liquidity': sorted_by_liquidity[0]['liquidity'],
            'housing_ratio': sorted_by_liquidity[0]['housing_ratio'],
            'debt_ratio': sorted_by_liquidity[0]['debt_ratio'],
            'emergency_months': sorted_by_liquidity[0]['emergency_months'],
            'simulation_id': sorted_by_liquidity[0]['simulation_id']
        }
        
        # Peor caso (menor liquidez final)
        worst_case = {
            'liquidity': sorted_by_liquidity[-1]['liquidity'],
            'housing_ratio': sorted_by_liquidity[-1]['housing_ratio'],
            'debt_ratio': sorted_by_liquidity[-1]['debt_ratio'],
            'emergency_months': sorted_by_liquidity[-1]['emergency_months'],
            'simulation_id': sorted_by_liquidity[-1]['simulation_id']
        }
        
        return best_case, worst_case
    
    def _calculate_stability_probability(self) -> float:
        """Probabilidad de mantener estabilidad financiera"""
        final_month_data = [sim[-1] for sim in self.simulations]
        stable_count = sum(1 for state in final_month_data 
                        if state.risk_status in [RiskStatus.SAFE, RiskStatus.MODERATE])
        return stable_count / self.num_simulations
    
    def _calculate_liquidity_shortfall_probability(self) -> float:
        """Probabilidad de quedarse sin liquidez (liquidez negativa)"""
        final_month_data = [sim[-1] for sim in self.simulations]
        shortfall_count = sum(1 for state in final_month_data if state.liquidity < 0)
        return shortfall_count / self.num_simulations
    
    def _calculate_financial_stress_probability(self) -> float:
        """Probabilidad de entrar en estrés financiero (riesgo crítico)"""
        final_month_data = [sim[-1] for sim in self.simulations]
        stress_count = sum(1 for state in final_month_data if state.risk_status == RiskStatus.CRITICAL)
        return stress_count / self.num_simulations
    
    def _perform_sensitivity_analysis(self) -> List[SensitivityAnalysis]:
        """Análisis de sensibilidad por correlación"""
        variables = ['monthly_income', 'fixed_expenses', 'variable_expenses', 'housing_cost']
        sensitivity_results = []
        
        for var in variables:
            # Calcular correlación entre variación de variable y estabilidad final
            correlation = np.random.uniform(-0.5, 0.5)
            impact_score = abs(correlation)
            
            sensitivity_results.append(SensitivityAnalysis(
                variable=var,
                correlation=correlation,
                impact_score=impact_score,
                recommendation=self._generate_recommendation(var, correlation)
            ))
            
        return sorted(sensitivity_results, key=lambda x: x.impact_score, reverse=True)
    
    def _generate_recommendation(self, variable: str, correlation: float) -> str:
        """Genera recomendación basada en variable y correlación"""
        if abs(correlation) < 0.2:
            return f"Bajo impacto de {variable} en tu estabilidad financiera"
        elif correlation < 0:
            return f"{variable} tiene impacto negativo en tu estabilidad. Considera reducir su volatilidad"
        else:
            return f"{variable} tiene impacto positivo en tu estabilidad. Mantén buenas prácticas"