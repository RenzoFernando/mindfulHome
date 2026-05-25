import numpy as np
from typing import Tuple, List, Dict, Any, Optional
from sqlalchemy.orm import Session
from scipy import stats
from app.services.scenario_service import ScenarioService
from app.simulation.engine.aggregator import SimulationAggregator
from app.simulation.models.comparison import (
    ScenarioComparison, Tradeoff, TimelineComparisonPoint, ComparisonResponse
)
from app.simulation.models.results import SimulationResults
from app.simulation.models.scenario import ScenarioInput
from app.models.simulation import SavedScenario

class ComparatorService:
    """Servicio para comparar escenarios y analizar tradeoffs"""
    
    def __init__(self, db: Session):
        self.db = db
        self.scenario_service = ScenarioService(db)
        
    async def compare_scenarios(
        self,
        scenario_a: Optional[int],
        scenario_b: Optional[int],
        temporal_scenario: Optional[ScenarioInput] = None,
        user_id: Optional[int] = None
    ) -> ComparisonResponse:
        """
        Compara dos escenarios (guardados o temporal vs guardado)
        
        Args:
            scenario_a: ID del primer escenario (puede ser None si es temporal)
            scenario_b: ID del segundo escenario (puede ser None si es temporal)
            temporal_scenario: Escenario temporal para comparar
            user_id: ID del usuario (requerido para escenarios guardados)
        """
        # Cargar o ejecutar escenarios
        results_a, metadata_a = await self._get_scenario_results(
            scenario_a, temporal_scenario if not scenario_a else None, user_id
        )
        results_b, metadata_b = await self._get_scenario_results(
            scenario_b, temporal_scenario if not scenario_b else None, user_id
        )
        
        # Calcular comparación
        comparison = self._calculate_comparison(
            results_a, results_b, metadata_a, metadata_b
        )
        
        # Construir timeline comparativo
        timeline = self._build_comparison_timeline(results_a, results_b)
        
        # Analizar tradeoffs
        tradeoff_analysis = self._analyze_tradeoffs(
            results_a, results_b, metadata_a, metadata_b
        )
        
        return ComparisonResponse(
            comparison=comparison,
            timeline=timeline,
            tradeoff_analysis=tradeoff_analysis
        )
    
    async def _get_scenario_results(self, scenario_id: Optional[int], temporal_scenario: Optional[ScenarioInput], user_id: Optional[int]) -> Tuple[SimulationResults, Dict[str, Any]]:
        """Obtiene los resultados de un escenario (guardado o temporal)"""
        
        if scenario_id:
            saved = self.db.query(SavedScenario).filter(
                SavedScenario.id == scenario_id
            ).first()
            
            if not saved:
                raise ValueError(f"Escenario {scenario_id} no encontrado")
            
            scenario_input = ScenarioInput(
                user_snapshot_id=saved.user_snapshot_id,
                overrides=saved.scenario_overrides or {},
                simulation_months=saved.simulation_config.get('simulation_months', 360),
                num_simulations=saved.simulation_config.get('num_simulations', 1000)
            )
            
            # Si ya tiene resultados cacheados, usarlos
            if saved.results_summary:
                # Reconstruir resultados desde cache
                results = SimulationResults(**saved.results_summary)
            else:
                results = self.scenario_service.run_scenario(scenario_input)
            
            metadata = {
                'name': saved.name,
                'type': 'saved',
                'id': saved.id,
                'overrides': saved.scenario_overrides
            }
        else:
            # Escenario temporal
            results = self.scenario_service.run_scenario(temporal_scenario)
            metadata = {
                'name': 'Escenario Actual',
                'type': 'temporal',
                'id': None,
                'overrides': temporal_scenario.overrides if temporal_scenario else {}
            }
            
        return results, metadata
    
    def _calculate_comparison(self, results_a: SimulationResults, results_b: SimulationResults, metadata_a: Dict[str, Any], metadata_b: Dict[str, Any]) -> ScenarioComparison:
        """Calcula métricas de comparación entre escenarios"""
        
        # Calcular mejora en estabilidad
        stability_improvement = results_b.stability_probability - results_a.stability_probability
        
        # Comparar métricas principales
        metrics_comparison = {
            'stability_probability': {
                'a': results_a.stability_probability,
                'b': results_b.stability_probability,
                'delta': results_b.stability_probability - results_a.stability_probability,
                'percentage_change': ((results_b.stability_probability - results_a.stability_probability) 
                                    / results_a.stability_probability * 100) if results_a.stability_probability > 0 else 0
            },
            'liquidity_shortfall': {
                'a': results_a.liquidity_shortfall_probability,
                'b': results_b.liquidity_shortfall_probability,
                'delta': results_b.liquidity_shortfall_probability - results_a.liquidity_shortfall_probability
            },
            'financial_stress': {
                'a': results_a.financial_stress_probability,
                'b': results_b.financial_stress_probability,
                'delta': results_b.financial_stress_probability - results_a.financial_stress_probability
            }
        }
        
        # Obtener top 3 ratios
        top_ratios_a = self._extract_top_ratios(results_a)
        top_ratios_b = self._extract_top_ratios(results_b)
        
        # Analizar tradeoffs
        tradeoffs = self._identify_tradeoffs(results_a, results_b)
        
        # Generar recomendación
        recommendation = self._generate_recommendation(
            metrics_comparison, tradeoffs, stability_improvement
        )
        
        # Advertencia de riesgo
        risk_warning = self._generate_risk_warning(
            results_b, metrics_comparison, tradeoffs
        )
        
        return ScenarioComparison(
            scenario_a_id=metadata_a.get('id'),
            scenario_a_name=metadata_a.get('name', 'Escenario A'),
            scenario_b_id=metadata_b.get('id'),
            scenario_b_name=metadata_b.get('name', 'Escenario B'),
            stability_probability_a=results_a.stability_probability,
            stability_probability_b=results_b.stability_probability,
            stability_improvement=stability_improvement,
            metrics_comparison=metrics_comparison,
            top_ratios_a=top_ratios_a,
            top_ratios_b=top_ratios_b,
            tradeoffs=tradeoffs,
            recommendation=recommendation,
            risk_warning=risk_warning
        )
    
    def _extract_top_ratios(self, results: SimulationResults) -> List[Dict[str, Any]]:
        """Extrae los 3 ratios más relevantes de los resultados"""
        ratios = [
            {'name': 'Liquidez Mensual', 'value': results.expected_results.get('liquidity', {}).get('p50', 0),
            'unit': 'COP', 'description': 'Capacidad de ahorro mensual'},
            {'name': 'Ratio de Vivienda', 'value': results.expected_results.get('housing_ratio', {}).get('p50', 0),
            'unit': '%', 'description': 'Porcentaje de ingresos destinado a vivienda'},
            {'name': 'Ratio de Deuda', 'value': results.expected_results.get('debt_ratio', {}).get('p50', 0),
            'unit': '%', 'description': 'Porcentaje de ingresos destinado a deudas'},
            {'name': 'Meses de Emergencia', 'value': results.expected_results.get('emergency_months', {}).get('p50', 0),
            'unit': 'meses', 'description': 'Capacidad de cobertura con fondo de emergencia'}
        ]
        
        ratios.sort(key=lambda x: abs(x['value']), reverse=True)
        return ratios[:3]
    
    def _identify_tradeoffs(self, results_a: SimulationResults, results_b: SimulationResults) -> List[Tradeoff]:
        """Identifica tradeoffs entre escenarios"""
        tradeoffs = []
        
        # Analizar cada variable sensible
        for var_a in results_a.top_sensitive_variables:
            var_b = next(
                (v for v in results_b.top_sensitive_variables if v.variable == var_a.variable),
                None
            )
            
            if var_b:
                # Calcular delta de sensibilidad
                delta_sensitivity = var_b.impact_score - var_a.impact_score
                
                # Si hay cambio significativo en sensibilidad
                if abs(delta_sensitivity) > 0.1:
                    tradeoff = self._analyze_variable_tradeoff(
                        var_a.variable, 
                        var_a.impact_score, 
                        var_b.impact_score,
                        results_a, 
                        results_b
                    )
                    if tradeoff:
                        tradeoffs.append(tradeoff)
        
        # Ordenar por impacto
        tradeoffs.sort(key=lambda x: x.impact_score, reverse=True)
        
        # Limitar a top 3
        return tradeoffs[:3]
    
    def _analyze_variable_tradeoff(self, variable: str, sensitivity_a: float, sensitivity_b: float, results_a: SimulationResults, results_b: SimulationResults) -> Optional[Tradeoff]:
        """Analiza tradeoff específico de una variable"""
        
        delta_sensitivity = sensitivity_b - sensitivity_a
        impact_score = min(abs(delta_sensitivity) * 2, 1.0)
        
        # Determinar beneficio y costo según variable
        if variable == 'monthly_income':
            if sensitivity_b < sensitivity_a:
                benefit = "Menor vulnerabilidad ante cambios en ingresos"
                cost = "Mayor estabilidad pero posible menor flexibilidad"
            else:
                benefit = "Mayor capacidad de crecimiento"
                cost = "Mayor vulnerabilidad ante caídas de ingresos"
                
        elif variable == 'housing_cost':
            if sensitivity_b < sensitivity_a:
                benefit = "Menor exposición al costo de vivienda"
                cost = "Posiblemente vivienda más alejada o pequeña"
            else:
                benefit = "Mejor ubicación o tamaño de vivienda"
                cost = "Mayor vulnerabilidad ante cambios en gastos de vivienda"
                
        elif variable == 'fixed_expenses':
            if sensitivity_b < sensitivity_a:
                benefit = "Gastos fijos más estables y controlados"
                cost = "Posibles restricciones en estilo de vida"
            else:
                benefit = "Mayor flexibilidad en gastos"
                cost = "Mayor vulnerabilidad ante incrementos de gastos fijos"
                
        elif variable == 'debt_payments':
            if sensitivity_b < sensitivity_a:
                benefit = "Menor carga de deuda"
                cost = "Posiblemente menor capacidad de apalancamiento"
            else:
                benefit = "Mayor capacidad de inversión vía deuda"
                cost = "Mayor vulnerabilidad ante cambios en capacidad de pago"
        else:
            # Tradeoff genérico
            benefit = f"Mejor control sobre {variable}"
            cost = f"Posibles restricciones en {variable}"
        
        # Calcular confianza basada en consistencia de datos
        confidence = min(abs(delta_sensitivity) * 2, 0.95)
        
        # Generar recomendación específica
        if delta_sensitivity < 0:
            recommendation = f"El escenario B reduce la sensibilidad a {variable}. Esto es positivo para la estabilidad, pero asegúrate de que los beneficios justifiquen cualquier restricción."
        else:
            recommendation = f"El escenario B aumenta la sensibilidad a {variable}. Considera si el beneficio adicional vale el mayor riesgo."
        
        return Tradeoff(
            variable=variable,
            benefit=benefit,
            cost=cost,
            impact_score=impact_score,
            confidence=confidence,
            correlation_a=sensitivity_a,
            correlation_b=sensitivity_b,
            delta_sensitivity=delta_sensitivity,
            recommendation=recommendation
        )
    
    def _build_comparison_timeline(self, results_a: SimulationResults, results_b: SimulationResults) -> List[TimelineComparisonPoint]:
        """Construye timeline comparativo entre escenarios"""
        
        timeline = []
        max_months = min(len(results_a.timeline), len(results_b.timeline))
        
        for i in range(max_months):
            point_a = results_a.timeline[i]
            point_b = results_b.timeline[i]
            
            timeline_point = TimelineComparisonPoint(
                month=point_a.month,
                stability_probability_a=point_a.stability_probability,
                stability_probability_b=point_b.stability_probability,
                liquidity_p50_a=point_a.liquidity.p50,
                liquidity_p50_b=point_b.liquidity.p50,
                housing_ratio_a=point_a.housing_ratio.p50,
                housing_ratio_b=point_b.housing_ratio.p50,
                confidence_interval_a={
                    'lower': point_a.liquidity.p10,
                    'upper': point_a.liquidity.p90
                },
                confidence_interval_b={
                    'lower': point_b.liquidity.p10,
                    'upper': point_b.liquidity.p90
                }
            )
            timeline.append(timeline_point)
            
        return timeline
    
    def _generate_recommendation(self, metrics: Dict[str, Any], tradeoffs: List[Tradeoff], stability_improvement: float) -> str:
        """Genera recomendación basada en la comparación"""
        
        if stability_improvement > 0.1:
            stability_msg = "significativamente más estable"
        elif stability_improvement > 0:
            stability_msg = "ligeramente más estable"
        elif stability_improvement > -0.1:
            stability_msg = "similar en estabilidad"
        else:
            stability_msg = "menos estable"
            
        recommendation = f"El escenario B es {stability_msg} que el escenario A. "
        
        if tradeoffs:
            recommendation += "Principales tradeoffs identificados:\n"
            for tradeoff in tradeoffs[:2]:
                recommendation += f"• {tradeoff.benefit} vs {tradeoff.cost}\n"
        
        return recommendation
    
    def _generate_risk_warning(self, results: SimulationResults, metrics: Dict[str, Any], tradeoffs: List[Tradeoff]) -> Optional[str]:
        """Genera advertencia de riesgo si es necesario"""
        
        warnings = []
        
        # Verificar estabilidad baja
        if results.stability_probability < 0.5:
            warnings.append("Probabilidad de estabilidad menor al 50%")
        
        # Verificar alto riesgo de estrés financiero
        if results.financial_stress_probability > 0.3:
            warnings.append("Alto riesgo de estrés financiero (>30%)")
        
        # Verificar tradeoffs riesgosos
        for tradeoff in tradeoffs:
            if tradeoff.impact_score > 0.7 and tradeoff.delta_sensitivity > 0:
                warnings.append(f"Alta sensibilidad a {tradeoff.variable}")
        
        return "\n".join(warnings) if warnings else None
    
    def _analyze_tradeoffs(self, results_a: SimulationResults, results_b: SimulationResults,metadata_a: Dict[str, Any], metadata_b: Dict[str, Any]) -> Dict[str, Any]:
        """Análisis detallado de tradeoffs entre escenarios"""
        
        sensitivity_changes = []
        
        for var_a in results_a.top_sensitive_variables:
            var_b = next(
                (v for v in results_b.top_sensitive_variables if v.variable == var_a.variable),
                None
            )
            
            if var_b:
                change = {
                    'variable': var_a.variable,
                    'sensitivity_a': var_a.impact_score,
                    'sensitivity_b': var_b.impact_score,
                    'absolute_change': var_b.impact_score - var_a.impact_score,
                    'relative_change': ((var_b.impact_score - var_a.impact_score) 
                                       / var_a.impact_score * 100) if var_a.impact_score > 0 else 0
                }
                sensitivity_changes.append(change)
        
        # Identificar nuevas sensibilidades (variables que aparecen en B pero no en A)
        new_sensitivities = [
            v for v in results_b.top_sensitive_variables 
            if v.variable not in [va.variable for va in results_a.top_sensitive_variables]
        ]
        
        # Identificar sensibilidades que desaparecen
        lost_sensitivities = [
            v for v in results_a.top_sensitive_variables
            if v.variable not in [vb.variable for vb in results_b.top_sensitive_variables]
        ]
        
        net_risk_reduction = self._calculate_net_risk_reduction(results_a, results_b)
        
        return {
            'sensitivity_changes': sensitivity_changes,
            'new_sensitivities': [v.dict() for v in new_sensitivities],
            'lost_sensitivities': [v.dict() for v in lost_sensitivities],
            'net_risk_reduction': net_risk_reduction,
            'summary': self._generate_tradeoff_summary(
                sensitivity_changes, new_sensitivities, lost_sensitivities, net_risk_reduction
            )
        }
    
    def _calculate_net_risk_reduction(self,results_a: SimulationResults,results_b: SimulationResults) -> Dict[str, float]:
        """Calcula reducción neta de riesgo entre escenarios"""
        
        return {
            'stability_improvement': results_b.stability_probability - results_a.stability_probability,
            'liquidity_risk_reduction': results_a.liquidity_shortfall_probability - results_b.liquidity_shortfall_probability,
            'stress_reduction': results_a.financial_stress_probability - results_b.financial_stress_probability,
            'overall_risk_score': (
                (results_a.liquidity_shortfall_probability + results_a.financial_stress_probability) -
                (results_b.liquidity_shortfall_probability + results_b.financial_stress_probability)
            ) / 2
        }
    
    def _generate_tradeoff_summary(self, sensitivity_changes: List[Dict], new_sensitivities: List[Dict], lost_sensitivities: List[Dict], net_risk_reduction: Dict[str, float]) -> str:
        """Genera resumen ejecutivo de tradeoffs"""
        
        summary_parts = []
        
        if net_risk_reduction['overall_risk_score'] > 0:
            summary_parts.append(f"Reducción neta de riesgo del {net_risk_reduction['overall_risk_score']*100:.1f}%")
        else:
            summary_parts.append(f"Aumento neto de riesgo del {abs(net_risk_reduction['overall_risk_score'])*100:.1f}%")
        
        if lost_sensitivities:
            variables = [v['variable'] for v in lost_sensitivities[:2]]
            summary_parts.append(f"Menor sensibilidad a: {', '.join(variables)}")
        
        if new_sensitivities:
            variables = [v['variable'] for v in new_sensitivities[:2]]
            summary_parts.append(f"Nueva sensibilidad a: {', '.join(variables)}")
        
        return " | ".join(summary_parts)