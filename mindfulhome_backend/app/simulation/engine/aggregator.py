from typing import List, Dict, Any, Tuple, Optional
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
        
        # Calcular timeline
        timeline = self._build_timeline()
        
        # Calcular métricas agregadas
        expected_metrics = self._calculate_expected_metrics()
        
        # Calcular mejores y peores casos
        best_case_data, worst_case_data, expected_case_data = self._find_meaningful_extreme_cases()
        
        # Calcular probabilidades
        stability_prob = self._calculate_stability_probability()
        liquidity_shortfall_prob = self._calculate_liquidity_shortfall_probability()
        financial_stress_prob = self._calculate_financial_stress_probability()
        
        # Calcular métricas de estrés y recuperación
        stress_metrics = self._calculate_stress_metrics()
        
        # Generar eventos clave del timeline
        timeline_events = self._extract_key_events()
        
        # Generar insights generales ESTÁTICOS
        general_insights = self._get_static_general_insights(stability_prob, expected_metrics)
        
        # Generar narrativas ESTÁTICAS para cada caso
        best_case_narrative = self._get_static_case_narrative("best", best_case_data, stress_metrics.get("best", {}))
        expected_case_narrative = self._get_static_case_narrative("expected", expected_case_data, stress_metrics.get("expected", {}))
        worst_case_narrative = self._get_static_case_narrative("worst", worst_case_data, stress_metrics.get("worst", {}))
        
        # Análisis de sensibilidad con recomendaciones estáticas
        sensitivity_analysis = self._perform_static_sensitivity_analysis()
        
        # Calcular métricas esperadas finales
        expected_results = self._calculate_expected_results()
        
        return SimulationResults(
            expected_results=expected_results,
            best_case_results=best_case_data.get("metrics", {}),
            worst_case_results=worst_case_data.get("metrics", {}),
            best_case_narrative=best_case_narrative,
            expected_case_narrative=expected_case_narrative,
            worst_case_narrative=worst_case_narrative,
            general_insights=general_insights,
            stability_probability=stability_prob,
            liquidity_shortfall_probability=liquidity_shortfall_prob,
            financial_stress_probability=financial_stress_prob,
            timeline=timeline,
            timeline_events=timeline_events,
            stress_metrics=stress_metrics,
            trajectory_analysis=self._analyze_overall_trajectory(),
            top_sensitive_variables=sensitivity_analysis,
            num_simulations=self.num_simulations,
            simulation_months=self.num_months
        )
    
    def _get_static_general_insights(self, stability_prob: float, expected_metrics: Dict) -> Dict[str, Any]:
        """Genera insights estáticos basados en métricas"""
        
        liquidity = expected_metrics.get('liquidity', 0)
        housing_ratio = expected_metrics.get('housing_ratio', 0)
        
        # Determinar el estado general
        if stability_prob > 0.7:
            main_insight = "Tu situación financiera muestra buena estabilidad. Las proyecciones indican que puedes mantener tus finanzas saludables."
            primary_severity = "positive"
        elif stability_prob > 0.4:
            main_insight = "Tu situación financiera es moderada. Hay áreas de mejora que podrían fortalecer tu estabilidad."
            primary_severity = "neutral"
        else:
            main_insight = "Tu situación financiera presenta riesgos significativos. Es importante revisar tus gastos y buscar mejorar tus ingresos."
            primary_severity = "warning"
        
        insights = []
        
        # Insight 1: Liquidez
        if liquidity > 1000000:
            insights.append({
                "id": "liquidez",
                "title": "Buena liquidez",
                "description": f"Tu liquidez de ${liquidity:,.0f} te da margen para enfrentar imprevistos.",
                "severity": "positive",
                "metric_reference": "liquidity"
            })
        elif liquidity > 0:
            insights.append({
                "id": "liquidez",
                "title": "Liquidez ajustada",
                "description": f"Tu liquidez de ${liquidity:,.0f} es positiva pero limitada. Considera aumentar tu margen.",
                "severity": "neutral",
                "metric_reference": "liquidity"
            })
        else:
            insights.append({
                "id": "liquidez",
                "title": "Liquidez negativa",
                "description": f"Tu liquidez es negativa (${liquidity:,.0f}). Necesitas reducir gastos o aumentar ingresos.",
                "severity": "warning",
                "metric_reference": "liquidity"
            })
        
        # Insight 2: Housing ratio
        if housing_ratio < 0.3:
            insights.append({
                "id": "vivienda",
                "title": "Costo de vivienda saludable",
                "description": f"Tu costo de vivienda representa el {housing_ratio:.1%} de tus ingresos, está dentro del rango recomendado.",
                "severity": "positive",
                "metric_reference": "housing_ratio"
            })
        elif housing_ratio < 0.4:
            insights.append({
                "id": "vivienda",
                "title": "Costo de vivienda moderado",
                "description": f"Tu costo de vivienda es del {housing_ratio:.1%} de tus ingresos. Está en el límite superior recomendado.",
                "severity": "neutral",
                "metric_reference": "housing_ratio"
            })
        else:
            insights.append({
                "id": "vivienda",
                "title": "Costo de vivienda alto",
                "description": f"Tu costo de vivienda es del {housing_ratio:.1%} de tus ingresos, supera el 30% recomendado.",
                "severity": "warning",
                "metric_reference": "housing_ratio"
            })
        
        # Insight 3: Estabilidad
        if stability_prob > 0.7:
            insights.append({
                "id": "estabilidad",
                "title": "Alta estabilidad",
                "description": f"Tienes un {stability_prob:.0%} de probabilidad de mantener estabilidad financiera.",
                "severity": "positive",
                "metric_reference": "stability"
            })
        elif stability_prob > 0.4:
            insights.append({
                "id": "estabilidad",
                "title": "Estabilidad moderada",
                "description": f"Tienes un {stability_prob:.0%} de probabilidad de mantener estabilidad financiera.",
                "severity": "neutral",
                "metric_reference": "stability"
            })
        else:
            insights.append({
                "id": "estabilidad",
                "title": "Baja estabilidad",
                "description": f"Solo tienes un {stability_prob:.0%} de probabilidad de mantener estabilidad financiera.",
                "severity": "warning",
                "metric_reference": "stability"
            })
        
        # Insight 4: Emergency fund
        emergency_months = expected_metrics.get('emergency_months', 0)
        if emergency_months >= 6:
            insights.append({
                "id": "emergencia",
                "title": "Fondo de emergencia sólido",
                "description": f"Tu fondo de emergencia cubre {emergency_months:.1f} meses de gastos, muy por encima del mínimo recomendado.",
                "severity": "positive",
                "metric_reference": "emergency_months"
            })
        elif emergency_months >= 3:
            insights.append({
                "id": "emergencia",
                "title": "Fondo de emergencia adecuado",
                "description": f"Tu fondo de emergencia cubre {emergency_months:.1f} meses de gastos, cumple con el mínimo recomendado.",
                "severity": "positive",
                "metric_reference": "emergency_months"
            })
        elif emergency_months > 0:
            insights.append({
                "id": "emergencia",
                "title": "Fondo de emergencia limitado",
                "description": f"Tu fondo de emergencia cubre solo {emergency_months:.1f} meses. Considera aumentarlo a 3-6 meses.",
                "severity": "warning",
                "metric_reference": "emergency_months"
            })
        else:
            insights.append({
                "id": "emergencia",
                "title": "Sin fondo de emergencia",
                "description": "No tienes fondo de emergencia. Es prioritario crear uno para imprevistos.",
                "severity": "warning",
                "metric_reference": "emergency_months"
            })
        
        # Insight 5: Debt ratio
        debt_ratio = expected_metrics.get('debt_ratio', 0)
        if debt_ratio < 0.3:
            insights.append({
                "id": "deuda",
                "title": "Nivel de deuda saludable",
                "description": f"Tu nivel de deuda ({debt_ratio:.1%} de ingresos) está dentro de lo recomendado.",
                "severity": "positive",
                "metric_reference": "debt_ratio"
            })
        elif debt_ratio < 0.4:
            insights.append({
                "id": "deuda",
                "title": "Nivel de deuda moderado",
                "description": f"Tu nivel de deuda ({debt_ratio:.1%} de ingresos) está cerca del límite recomendado.",
                "severity": "neutral",
                "metric_reference": "debt_ratio"
            })
        else:
            insights.append({
                "id": "deuda",
                "title": "Nivel de deuda alto",
                "description": f"Tu nivel de deuda ({debt_ratio:.1%} de ingresos) supera el 30% recomendado. Prioriza reducir deudas.",
                "severity": "warning",
                "metric_reference": "debt_ratio"
            })
        
        return {
            "main_insight": main_insight,
            "insights": insights[:5]
        }
    def _get_static_case_narrative(self, case_type: str, case_data: Dict, stress_metrics: Dict) -> Dict[str, Any]:
        """Genera narrativas estáticas para cada caso"""
        
        metrics = case_data.get("metrics", {})
        liquidity = metrics.get('liquidity', 0)
        housing_ratio = metrics.get('housing_ratio', 0)
        emergency_months = metrics.get('emergency_months', 0)
        
        # Calcular métricas adicionales del caso
        states = case_data.get("states", [])
        if states:
            # Calcular stability score (porcentaje de meses estables)
            stable_months = sum(1 for s in states if s.risk_status in [RiskStatus.SAFE, RiskStatus.MODERATE])
            stability_pct = (stable_months / len(states)) * 100 if states else 0
            
            # Calcular recovery score
            critical_periods = self._find_critical_periods(states)
            if critical_periods:
                avg_recovery = np.mean([p["duration"] for p in critical_periods])
                recovery_score = max(0, 100 - (avg_recovery / len(states) * 100))
            else:
                recovery_score = 100
            
            # Calcular stress score (porcentaje de meses en estrés)
            stress_months = sum(1 for s in states if s.risk_status == RiskStatus.CRITICAL)
            stress_pct = (stress_months / len(states)) * 100 if states else 0
            
            # Calcular volatility (desviación estándar de liquidez normalizada)
            liquidity_values = [s.liquidity for s in states]
            if liquidity_values and max(liquidity_values) > 0:
                volatility = (np.std(liquidity_values) / max(liquidity_values)) * 100
            else:
                volatility = 0
        else:
            stability_pct = 0
            recovery_score = 0
            stress_pct = 0
            volatility = 0
        
        if case_type == "best":
            if liquidity > 0:
                title = "Mejor escenario posible"
                financial_state = "Situación financiera sólida con liquidez positiva"
                summary = f"En el mejor escenario, tu liquidez alcanza ${liquidity:,.0f} y mantienes buena estabilidad."
                trajectory_type = "stable_growth"
                personality = "resilient"
                tone = "optimistic"
            else:
                title = "Escenario optimista"
                financial_state = "El mejor escenario muestra cierta mejoría pero aún hay desafíos"
                summary = f"Incluso en el mejor escenario, la liquidez es de ${liquidity:,.0f}, lo que indica presión financiera."
                trajectory_type = "volatile_recovery"
                personality = "sustainable"
                tone = "cautious"
            
            opportunities = [
                {"type": "growth", "description": "Potencial de crecimiento financiero", "potential": "high"},
                {"type": "stability", "description": "Posibilidad de alcanzar estabilidad", "potential": "medium"}
            ]
            risks = []
            
        elif case_type == "expected":
            if liquidity > 0:
                title = "Escenario más probable"
                financial_state = "Situación financiera estable según lo esperado"
                summary = f"En el escenario más probable, tu liquidez proyectada es de ${liquidity:,.0f}."
                trajectory_type = "stable_growth"
                personality = "sustainable"
                tone = "cautious"
            else:
                title = "Escenario esperado"
                financial_state = "El escenario más probable muestra desafíos financieros"
                summary = f"El escenario más probable muestra liquidez negativa de ${liquidity:,.0f}."
                trajectory_type = "fragile_stability"
                personality = "volatile"
                tone = "stressful"
            
            opportunities = [{"type": "improvement", "description": "Margen para mejorar", "potential": "medium"}]
            risks = [{"type": "liquidity", "description": "Posibles problemas de liquidez", "severity": "medium"}]
            
        else:  # worst
            if liquidity < 0:
                title = "Peor escenario posible"
                financial_state = "Situación financiera crítica en el peor escenario"
                summary = f"En el peor escenario, podrías enfrentar una liquidez negativa de ${liquidity:,.0f}."
                trajectory_type = "progressive_decline"
                personality = "high_risk"
                tone = "stressful"
            else:
                title = "Escenario de estrés"
                financial_state = "El peor escenario muestra presión financiera significativa"
                summary = f"El peor escenario muestra liquidez ajustada de ${liquidity:,.0f}."
                trajectory_type = "progressive_decline"
                personality = "fragile"
                tone = "stressful"
            
            opportunities = []
            risks = [{"type": "critical", "description": "Alta vulnerabilidad a shocks", "severity": "high"}]
        
        return {
            "title": title,
            "financial_state": financial_state,
            "summary": summary,
            "top_metrics": [
                {"metric": "Liquidez", "value": liquidity, "unit": "COP", "trend": "positive" if liquidity > 0 else "negative"},
                {"metric": "Ratio vivienda", "value": housing_ratio, "unit": "%", "trend": "positive" if housing_ratio < 0.3 else "negative"},
                {"metric": "Meses de emergencia", "value": emergency_months, "unit": "meses", "trend": "positive" if emergency_months >= 3 else "negative"},
                {"metric": "Estabilidad", "value": stability_pct, "unit": "%", "trend": "positive" if stability_pct > 70 else "negative"},
                {"metric": "Recuperación", "value": recovery_score, "unit": "%", "trend": "positive" if recovery_score > 70 else "negative"},
                {"metric": "Estrés", "value": stress_pct, "unit": "%", "trend": "negative" if stress_pct > 30 else "positive"},
                {"metric": "Volatilidad", "value": volatility, "unit": "%", "trend": "negative" if volatility > 30 else "positive"}
            ],
            "key_events": [],
            "risks": risks,
            "opportunities": opportunities,
            "trajectory": {"type": trajectory_type, "description": self._get_trajectory_description(trajectory_type)},
            "emotional_tone": tone,
            "scenario_personality": personality,
            "stress_exposure": stress_metrics,
            "recovery_metrics": {"months_to_recovery": 0, "recovery_quality": "moderate"}
        }
    
    def _get_trajectory_description(self, trajectory_type: str) -> str:
        """Obtiene descripción de trayectoria"""
        descriptions = {
            "stable_growth": "Crecimiento estable y sostenido de la salud financiera",
            "volatile_recovery": "Recuperación con altibajos, pero tendencia positiva",
            "progressive_decline": "Deterioro gradual de la situación financiera",
            "fragile_stability": "Estabilidad aparente pero con fragilidad subyacente"
        }
        return descriptions.get(trajectory_type, "Trayectoria proyectada")
    
    def _get_static_recommendation(self, variable: str, correlation: float) -> str:
        """Recomendación estática basada en variable y correlación"""
        
        var_names = {
            'monthly_income': 'ingresos mensuales',
            'fixed_expenses': 'gastos fijos',
            'variable_expenses': 'gastos variables',
            'housing_cost': 'costo de vivienda',
            'debt_payments': 'pagos de deuda'
        }
        var_name = var_names.get(variable, variable)
        
        if correlation > 0:
            if abs(correlation) > 0.3:
                return f"Tus {var_name} tienen un impacto significativo en tu estabilidad. Mantener o aumentar tus ingresos es clave para tu salud financiera."
            else:
                return f"Tus {var_name} tienen un impacto positivo en tu estabilidad. Busca formas de incrementarlos si es posible."
        else:
            if abs(correlation) > 0.3:
                return f"Tus {var_name} tienen un impacto negativo en tu estabilidad. Considera reducirlos o controlarlos mejor."
            else:
                return f"Tus {var_name} tienen un impacto negativo moderado. Revisa si puedes optimizar estos gastos."
    
    def _get_static_actionable_steps(self, variable: str, correlation: float) -> List[str]:
        """Pasos accionables estáticos"""
        
        if variable == 'monthly_income':
            return [
                "Busca oportunidades de aumento de ingresos",
                "Considera fuentes de ingreso adicionales",
                "Actualiza tu perfil profesional regularmente"
            ]
        elif variable in ['fixed_expenses', 'variable_expenses']:
            return [
                "Revisa tus gastos mensuales y elimina los innecesarios",
                "Compara precios de servicios antes de contratar",
                "Establece un presupuesto mensual y respétalo"
            ]
        elif variable == 'housing_cost':
            return [
                "Evalúa opciones de vivienda más económicas",
                "Considera renegociar el arriendo o la hipoteca",
                "Compara costos de vivienda en diferentes zonas"
            ]
        elif variable == 'debt_payments':
            return [
                "Prioriza el pago de deudas con mayor interés",
                "Considera consolidar tus deudas",
                "Evita adquirir nuevas deudas innecesarias"
            ]
        else:
            return [
                "Monitorea esta variable mensualmente",
                "Establece metas realistas para mejorarla",
                "Consulta con un asesor financiero"
            ]
    
    def _perform_static_sensitivity_analysis(self) -> List[SensitivityAnalysis]:
        """Análisis de sensibilidad con recomendaciones estáticas"""
        
        variables_data = self._calculate_real_correlations()
        sensitivity_results = []
        
        for var_data in variables_data:
            sensitivity_results.append(SensitivityAnalysis(
                variable=var_data["variable"],
                correlation=var_data["correlation"],
                impact_score=var_data["impact_score"],
                recommendation=self._get_static_recommendation(var_data["variable"], var_data["correlation"]),
                priority="high" if abs(var_data["correlation"]) > 0.3 else "medium",
                actionable_steps=self._get_static_actionable_steps(var_data["variable"], var_data["correlation"])
            ))
            
        return sorted(sensitivity_results, key=lambda x: x.impact_score, reverse=True)[:5]
    
    def _calculate_real_correlations(self) -> List[Dict[str, Any]]:
        """Calcula correlaciones reales entre variables y resultados de estabilidad"""
        
        correlations = []
        final_states = [sim[-1] for sim in self.simulations]
        
        variables = [
            {'name': 'monthly_income', 'key': 'monthly_income'},
            {'name': 'fixed_expenses', 'key': 'fixed_expenses'},
            {'name': 'variable_expenses', 'key': 'variable_expenses'},
            {'name': 'housing_cost', 'key': 'housing_cost'},
            {'name': 'debt_payments', 'key': 'monthly_debt_payments'}
        ]
        
        for var in variables:
            var_values = []
            stability_scores = []
            
            for simulation in self.simulations:
                if var['key'] == 'monthly_income':
                    var_value = simulation[0].monthly_income
                elif var['key'] == 'fixed_expenses':
                    var_value = simulation[0].fixed_expenses
                elif var['key'] == 'variable_expenses':
                    var_value = simulation[0].variable_expenses
                elif var['key'] == 'housing_cost':
                    var_value = simulation[0].housing_cost
                elif var['key'] == 'debt_payments':
                    var_value = simulation[0].monthly_debt_payments
                else:
                    var_value = 0
                
                stability_score = self._calculate_simulation_stability_score(simulation)
                var_values.append(var_value)
                stability_scores.append(stability_score)
            
            if len(var_values) > 1 and len(set(var_values)) > 1:
                correlation, _ = stats.pearsonr(var_values, stability_scores)
            else:
                correlation = 0.0
            
            impact_score = abs(correlation)
            current_value = np.mean(var_values) if var_values else 0
            
            correlations.append({
                "variable": var['name'],
                "correlation": correlation,
                "impact_score": impact_score,
                "current_value": current_value,
                "context": f"Valor actual promedio: ${current_value:,.0f}. Correlación: {correlation:.2f}"
            })
        
        return correlations
    
    def _calculate_simulation_stability_score(self, simulation: List[SimulationState]) -> float:
        """Calcula un score de estabilidad para una simulación individual"""
        
        if not simulation:
            return 0.0
        
        final_state = simulation[-1]
        
        risk_scores = {
            RiskStatus.SAFE: 1.0,
            RiskStatus.MODERATE: 0.7,
            RiskStatus.RISKY: 0.3,
            RiskStatus.CRITICAL: 0.0
        }
        risk_score = risk_scores.get(final_state.risk_status, 0.0)
        
        stable_months = sum(1 for s in simulation if s.risk_status in [RiskStatus.SAFE, RiskStatus.MODERATE])
        stability_ratio = stable_months / len(simulation) if simulation else 0
        
        liquidity_ratio = 0.0
        if final_state.monthly_income > 0:
            liquidity_ratio = min(1.0, max(0.0, final_state.liquidity / final_state.monthly_income))
        
        score = (risk_score * 0.5 + stability_ratio * 0.3 + liquidity_ratio * 0.2)
        return score
    
    def _find_meaningful_extreme_cases(self) -> Tuple[Dict, Dict, Dict]:
        """Encuentra casos extremos basado en health score, con desempate por liquidez"""
        
        simulation_scores = []
        
        for sim_id, simulation in enumerate(self.simulations):
            score = self._calculate_financial_health_score(simulation)
            # Usar liquidez final como desempate
            final_liquidity = simulation[-1].liquidity if simulation else 0
            
            simulation_scores.append({
                "simulation_id": sim_id,
                "score": score,
                "final_liquidity": final_liquidity,
                "states": simulation,
                "metrics": self._extract_simulation_metrics(simulation)
            })
        
        # Ordenar primero por score (descendente), luego por liquidez final (descendente)
        sorted_by_score = sorted(
            simulation_scores, 
            key=lambda x: (x["score"], x["final_liquidity"]), 
            reverse=True
        )
        
        # Mejor caso (score más alto, mejor liquidez)
        best_case = sorted_by_score[0]
        # Peor caso (score más bajo, peor liquidez)
        worst_case = sorted_by_score[-1]
        # Caso esperado (cercano a la mediana)
        median_idx = len(sorted_by_score) // 2
        expected_case = sorted_by_score[median_idx]
        
        return best_case, worst_case, expected_case
    
    def _calculate_financial_health_score(self, simulation: List[SimulationState]) -> float:
        """Calcula un score de salud financiera integral"""
        
        weights = {
            "stability_weight": 0.3,
            "recovery_weight": 0.2,
            "stress_penalty": 0.3,
            "volatility_penalty": 0.2
        }
        
        stability_scores = []
        for state in simulation:
            if state.risk_status in [RiskStatus.SAFE, RiskStatus.MODERATE]:
                stability_scores.append(1.0)
            elif state.risk_status == RiskStatus.RISKY:
                stability_scores.append(0.5)
            else:
                stability_scores.append(0.0)
        
        avg_stability = np.mean(stability_scores)
        
        recovery_score = 1.0
        critical_periods = self._find_critical_periods(simulation)
        if critical_periods:
            avg_recovery_months = np.mean([p["duration"] for p in critical_periods])
            recovery_score = max(0, 1 - (avg_recovery_months / 60))
        
        stress_months = sum(1 for s in simulation if s.risk_status == RiskStatus.CRITICAL)
        stress_penalty = 1 - min(1, stress_months / len(simulation))
        
        liquidity_values = [s.liquidity for s in simulation]
        volatility = np.std(liquidity_values) if len(liquidity_values) > 1 else 0
        volatility_penalty = 1 - min(1, volatility / abs(np.mean(liquidity_values))) if np.mean(liquidity_values) != 0 else 0.5
        
        score = (
            weights["stability_weight"] * avg_stability +
            weights["recovery_weight"] * recovery_score +
            weights["stress_penalty"] * stress_penalty +
            weights["volatility_penalty"] * volatility_penalty
        )
        
        return score
    
    def _find_critical_periods(self, simulation: List[SimulationState]) -> List[Dict]:
        """Encuentra periodos críticos en la simulación"""
        
        critical_periods = []
        in_critical = False
        start_month = 0
        
        for i, state in enumerate(simulation):
            if state.risk_status == RiskStatus.CRITICAL and not in_critical:
                in_critical = True
                start_month = state.month
            elif state.risk_status != RiskStatus.CRITICAL and in_critical:
                in_critical = False
                critical_periods.append({
                    "start": start_month,
                    "end": state.month,
                    "duration": state.month - start_month
                })
        
        if in_critical:
            critical_periods.append({
                "start": start_month,
                "end": simulation[-1].month,
                "duration": simulation[-1].month - start_month
            })
        
        return critical_periods
    
    def _calculate_stress_metrics(self) -> Dict[str, Any]:
        """Calcula métricas detalladas de estrés para cada tipo de caso"""
        
        best_sim, worst_sim, expected_sim = self._find_meaningful_extreme_cases()
        
        def extract_simulation_metrics(simulation):
            states = simulation.get("states", simulation) if isinstance(simulation, dict) else simulation
            
            critical_months = sum(1 for s in states if s.risk_status == RiskStatus.CRITICAL)
            risky_months = sum(1 for s in states if s.risk_status == RiskStatus.RISKY)
            
            periods = self._find_critical_periods(states)
            max_stress_duration = max([p["duration"] for p in periods]) if periods else 0
            
            recovery_months = 0
            if periods and periods[-1]["end"] < len(states):
                recovery_months = len(states) - periods[-1]["end"]
            
            return {
                "months_in_critical": critical_months,
                "months_in_risky": risky_months,
                "max_stress_duration": max_stress_duration,
                "months_to_recovery": recovery_months,
                "recovery_quality": "fast" if recovery_months < 12 else "moderate" if recovery_months < 24 else "slow"
            }
        
        return {
            "best": extract_simulation_metrics(best_sim),
            "expected": extract_simulation_metrics(expected_sim),
            "worst": extract_simulation_metrics(worst_sim)
        }
    
    def _extract_key_events(self) -> List[Dict]:
        """Extrae eventos clave del timeline"""
        
        events = []
        
        for month in range(self.num_months + 1):
            month_data = [sim[month] for sim in self.simulations]
            
            critical_ratio = sum(1 for s in month_data if s.risk_status == RiskStatus.CRITICAL) / self.num_simulations
            if critical_ratio > 0.3:
                events.append({
                    "month": month,
                    "type": "critical",
                    "title": "Estrés financiero generalizado",
                    "description": f"{critical_ratio*100:.0f}% de las simulaciones en estado crítico"
                })
            
            if month > 0:
                prev_critical = sum(1 for s in self.simulations if s[month-1].risk_status == RiskStatus.CRITICAL) / self.num_simulations
                if prev_critical > 0.3 and critical_ratio < 0.1:
                    events.append({
                        "month": month,
                        "type": "recovery",
                        "title": "Recuperación financiera",
                        "description": "La mayoría de los escenarios salen de la zona crítica"
                    })
            
            if month > 0 and month % 12 == 0:
                avg_liquidity = np.mean([s.liquidity for s in month_data])
                events.append({
                    "month": month,
                    "type": "milestone",
                    "title": f"Año {month//12} completado",
                    "description": f"Liquidez promedio: ${avg_liquidity:,.0f}"
                })
        
        events.sort(key=lambda x: x.get("month", 0))
        return events[:10]
    
    def _build_timeline(self) -> List[TimelinePoint]:
        """Construye timeline incluyendo todos los meses (0 a num_months)"""
        timeline = []
        
        for month in range(self.num_months + 1):
            month_data = [sim[month] for sim in self.simulations]
            
            liquidity_values = [state.liquidity for state in month_data]
            housing_ratio_values = [state.housing_ratio for state in month_data]
            
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
    
    def _calculate_expected_metrics(self) -> Dict[str, Any]:
        """Calcula métricas esperadas para insights"""
        final_month_data = [sim[-1] for sim in self.simulations]
        
        return {
            'liquidity': np.mean([s.liquidity for s in final_month_data]),
            'housing_ratio': np.mean([s.housing_ratio for s in final_month_data]),
            'debt_ratio': np.mean([s.debt_ratio for s in final_month_data]),
            'emergency_months': np.mean([s.emergency_months for s in final_month_data])
        }
    
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
    
    def _extract_simulation_metrics(self, simulation: List[SimulationState]) -> Dict[str, float]:
        """Extrae métricas finales de una simulación"""
        final_state = simulation[-1]
        return {
            'liquidity': final_state.liquidity,
            'housing_ratio': final_state.housing_ratio,
            'debt_ratio': final_state.debt_ratio,
            'emergency_months': final_state.emergency_months
        }
    
    def _calculate_stability_probability(self) -> float:
        """Probabilidad de mantener estabilidad financiera en el último mes"""
        final_month_data = [sim[-1] for sim in self.simulations]
        stable_count = sum(1 for state in final_month_data 
                          if state.risk_status in [RiskStatus.SAFE, RiskStatus.MODERATE])
        return stable_count / self.num_simulations
    
    def _calculate_liquidity_shortfall_probability(self) -> float:
        """Probabilidad de quedarse sin liquidez (liquidez negativa) en el último mes"""
        final_month_data = [sim[-1] for sim in self.simulations]
        shortfall_count = sum(1 for state in final_month_data if state.liquidity < 0)
        return shortfall_count / self.num_simulations
    
    def _calculate_financial_stress_probability(self) -> float:
        """Probabilidad de entrar en estrés financiero (riesgo crítico) en el último mes"""
        final_month_data = [sim[-1] for sim in self.simulations]
        stress_count = sum(1 for state in final_month_data if state.risk_status == RiskStatus.CRITICAL)
        return stress_count / self.num_simulations
    
    def _analyze_trajectory(self, simulation_data: Dict) -> Dict[str, Any]:
        """Analiza la trayectoria de una simulación específica"""
        
        states = simulation_data.get("states", [])
        if not states:
            return {"type": "stable_growth", "description": "Trayectoria no disponible"}
        
        liquidity_values = [s.liquidity for s in states]
        if len(liquidity_values) > 1:
            trend = (liquidity_values[-1] - liquidity_values[0]) / len(liquidity_values)
        else:
            trend = 0
        
        volatility = np.std(liquidity_values) if len(liquidity_values) > 1 else 0
        mean_liquidity = abs(np.mean(liquidity_values)) if np.mean(liquidity_values) != 0 else 1
        
        if trend > 0 and volatility / mean_liquidity < 0.2:
            trajectory_type = "stable_growth"
            description = "Crecimiento estable y sostenido de la salud financiera"
        elif trend > 0 and volatility / mean_liquidity >= 0.2:
            trajectory_type = "volatile_recovery"
            description = "Recuperación con altibajos, pero tendencia positiva"
        elif trend < 0 and volatility / mean_liquidity < 0.3:
            trajectory_type = "progressive_decline"
            description = "Deterioro gradual de la situación financiera"
        else:
            trajectory_type = "fragile_stability"
            description = "Estabilidad aparente pero con fragilidad subyacente"
        
        return {
            "type": trajectory_type,
            "description": description,
            "trend": trend,
            "volatility": volatility
        }
    
    def _analyze_overall_trajectory(self) -> Dict[str, Any]:
        """Analiza la trayectoria general de todas las simulaciones"""
        _, _, expected = self._find_meaningful_extreme_cases()
        return self._analyze_trajectory(expected)