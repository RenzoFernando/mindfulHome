# app/services/scenario_narrator.py
import json
from typing import List, Dict, Any, Optional
from groq import Groq
from app.core.config import settings
from app.simulation.models.simulation_state import SimulationState, RiskStatus

CASE_NARRATIVE_SCHEMA = {
    "title": "string - Título atractivo del escenario",
    "financial_state": "string - Descripción general del estado financiero",
    "summary": "string - Resumen ejecutivo de 1-2 oraciones",
    "top_metrics": [
        {
            "metric": "string - Nombre de la métrica",
            "value": "number",
            "unit": "string",
            "trend": "positive | negative | neutral"
        }
    ],
    "key_events": [
        {
            "month": "number",
            "type": "critical | recovery | milestone | warning",
            "title": "string",
            "description": "string"
        }
    ],
    "risks": [
        {
            "type": "string",
            "description": "string",
            "severity": "low | medium | high | critical"
        }
    ],
    "opportunities": [
        {
            "type": "string",
            "description": "string",
            "potential": "low | medium | high"
        }
    ],
    "trajectory": {
        "type": "stable_growth | volatile_recovery | progressive_decline | fragile_stability",
        "description": "string"
    },
    "emotional_tone": "string - optimistic | cautious | stressful | resilient",
    "scenario_personality": "resilient | fragile | volatile | sustainable | high_risk",
    "stress_exposure": {
        "months_in_critical": "number",
        "months_in_risky": "number",
        "max_stress_duration": "number"
    },
    "recovery_metrics": {
        "months_to_recovery": "number",
        "recovery_quality": "fast | moderate | slow | none"
    }
}

COMPARISON_NARRATIVE_SCHEMA = {
    "comparison_summary": "string - Resumen de la comparación",
    "winning_aspects": [
        {
            "aspect": "string",
            "advantage": "string",
            "magnitude": "small | moderate | large"
        }
    ],
    "losing_aspects": [
        {
            "aspect": "string",
            "disadvantage": "string",
            "magnitude": "small | moderate | large"
        }
    ],
    "tradeoff_explanation": "string - Explicación narrativa de los tradeoffs",
    "recommendation": "string - Recomendación final",
    "risk_warning": "string - Advertencia si aplica"
}

GENERAL_INSIGHTS_SCHEMA = {
    "main_insight": "string - Insight principal de 1-2 oraciones que resume la situación financiera",
    "insights": [
        {
            "id": "string",
            "title": "string - Título corto del insight",
            "description": "string - Explicación detallada en lenguaje natural",
            "severity": "positive | neutral | warning",
            "metric_reference": "string - Métrica relacionada (opcional)"
        }
    ]
}

SENSITIVITY_RECOMMENDATION_SCHEMA = {
    "recommendation": "string - Recomendación concisa pero útil (máximo 2 oraciones)",
    "priority": "high | medium | low",
    "actionable_steps": ["string - Pasos concretos que el usuario puede tomar"]
}

TRADEOFF_EXPLANATION_SCHEMA = {
    "explanation": "string - Explicación clara y concisa de este tradeoff específico (2-3 oraciones)"
}

SYSTEM_PROMPT = """Eres un analista financiero experto en comunicación clara y empática.

Tu tarea es transformar datos financieros complejos de simulaciones Monte Carlo en narrativas humanas y comprensibles.

REGLAS IMPORTANTES:
- Usa lenguaje simple, cálido pero profesional
- Sé empático con la situación del usuario
- Explica conceptos financieros complejos de forma sencilla
- Destaca tanto los aspectos positivos como los riesgos
- Sé honesto pero no alarmista
- Usa ejemplos de la vida real cuando sea útil
- Devuelve SOLO JSON válido, sin markdown, sin backticks
- RESPONDE SIEMPRE en español

Para cada caso (mejor, esperado, peor) debes:
1. Dar un título descriptivo y atractivo
2. Explicar el estado financiero general
3. Destacar las 3-4 métricas más relevantes con su tendencia
4. Identificar eventos clave en el timeline
5. Señalar riesgos y oportunidades
6. Clasificar la trayectoria y personalidad del escenario

Recuerda: NO estás dando consejos financieros, solo interpretando los datos de la simulación."""

INSIGHTS_SYSTEM_PROMPT = """Eres un analista financiero experto en comunicación clara.

Tu tarea es generar insights claros y accionables a partir de datos financieros de simulaciones Monte Carlo.

REGLAS:
- Sé conciso pero informativo
- Usa lenguaje simple y directo
- Cada insight debe tener un título claro y una descripción útil
- Identifica el insight principal que resume la situación
- Clasifica la severidad de cada insight (positive, neutral, warning)
- Devuelve SOLO JSON válido
- RESPONDE SIEMPRE en español"""

SENSITIVITY_SYSTEM_PROMPT = """Eres un asesor financiero experto.

Tu tarea es generar una recomendación concisa pero útil basada en el análisis de sensibilidad de variables financieras.

REGLAS:
- La recomendación debe ser de máximo 2 oraciones
- Sé específico y accionable
- Prioriza la recomendación según su importancia
- Ofrece 2-3 pasos concretos que el usuario puede tomar
- Devuelve SOLO JSON válido
- RESPONDE SIEMPRE en español"""

TRADEOFF_SYSTEM_PROMPT = """Eres un analista financiero experto.

Tu tarea es explicar de forma clara y concisa un tradeoff específico entre dos escenarios financieros.

REGLAS:
- La explicación debe ser de 2-3 oraciones
- Usa lenguaje simple y directo
- Enfócate en la compensación (qué se gana y qué se pierde)
- Sé específico para este tradeoff en particular
- Devuelve SOLO JSON válido
- RESPONDE SIEMPRE en español"""


class LLMScenarioNarrator:
    """Genera narrativas dinámicas para escenarios financieros usando LLM"""
    
    def __init__(self):
        self.client = None
        if settings.GROQ_API_KEY:
            self.client = Groq(api_key=settings.GROQ_API_KEY)
    
    def generate_case_narrative(
        self,
        case_type: str,
        simulation_data: Dict[str, Any],
        timeline_events: List[Dict],
        metrics: Dict[str, Any],
        stress_metrics: Dict[str, Any],
        trajectory_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Genera narrativa para un caso específico (mejor, esperado, peor)"""
        
        if not self.client:
            return self._get_fallback_narrative(case_type)
        
        # Serializar simulation_data para evitar errores JSON
        serialized_data = self._serialize_simulation_data(simulation_data)
        
        prompt = self._build_case_prompt(
            case_type, serialized_data, timeline_events, 
            metrics, stress_metrics, trajectory_data
        )
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.7,
                max_tokens=4096,
                response_format={"type": "json_object"}
            )
            
            raw_text = response.choices[0].message.content.strip()
            if raw_text.startswith("```"):
                raw_text = raw_text.split("```")[1]
                if raw_text.startswith("json"):
                    raw_text = raw_text[4:]
                raw_text = raw_text.strip()
            
            return json.loads(raw_text)
        
        except Exception as e:
            print(f"Error generando narrativa para {case_type}: {e}")
            return self._get_fallback_narrative(case_type)
    
    def generate_comparison_narrative(
        self,
        scenario_a_name: str,
        scenario_b_name: str,
        comparison_metrics: Dict[str, Any],
        tradeoffs: List[Dict],
        sensitivity_changes: List[Dict]
    ) -> Dict[str, Any]:
        """Genera narrativa comparativa entre dos escenarios"""
        
        if not self.client:
            return self._get_fallback_comparison(scenario_a_name, scenario_b_name)
        
        prompt = self._build_comparison_prompt(
            scenario_a_name, scenario_b_name, comparison_metrics, 
            tradeoffs, sensitivity_changes
        )
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.7,
                max_tokens=4096,
                response_format={"type": "json_object"}
            )
            
            raw_text = response.choices[0].message.content.strip()
            if raw_text.startswith("```"):
                raw_text = raw_text.split("```")[1]
                if raw_text.startswith("json"):
                    raw_text = raw_text[4:]
                raw_text = raw_text.strip()
            
            return json.loads(raw_text)
        
        except Exception as e:
            print(f"Error generando narrativa comparativa: {e}")
            return self._get_fallback_comparison(scenario_a_name, scenario_b_name)
    
    def generate_general_insights(
        self,
        scenario_name: str,
        stability_probability: float,
        expected_metrics: Dict[str, Any],
        timeline_events: List[Dict],
        trajectory_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Genera insights generales para un escenario"""
        
        if not self.client:
            return self._get_fallback_insights()
        
        prompt = self._build_insights_prompt(
            scenario_name, stability_probability, expected_metrics,
            timeline_events, trajectory_data
        )
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": INSIGHTS_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.7,
                max_tokens=2048,
                response_format={"type": "json_object"}
            )
            
            raw_text = response.choices[0].message.content.strip()
            if raw_text.startswith("```"):
                raw_text = raw_text.split("```")[1]
                if raw_text.startswith("json"):
                    raw_text = raw_text[4:]
                raw_text = raw_text.strip()
            
            return json.loads(raw_text)
        
        except Exception as e:
            print(f"Error generando insights: {e}")
            return self._get_fallback_insights()
    
    def generate_sensitivity_recommendation(
        self,
        variable: str,
        correlation: float,
        impact_score: float,
        current_value: Optional[float] = None,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Genera recomendación para una variable sensible"""
        
        if not self.client:
            return self._get_fallback_sensitivity_recommendation(variable, correlation)
        
        prompt = self._build_sensitivity_prompt(
            variable, correlation, impact_score, current_value, context
        )
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": SENSITIVITY_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.7,
                max_tokens=1024,
                response_format={"type": "json_object"}
            )
            
            raw_text = response.choices[0].message.content.strip()
            if raw_text.startswith("```"):
                raw_text = raw_text.split("```")[1]
                if raw_text.startswith("json"):
                    raw_text = raw_text[4:]
                raw_text = raw_text.strip()
            
            return json.loads(raw_text)
        
        except Exception as e:
            print(f"Error generando recomendación para {variable}: {e}")
            return self._get_fallback_sensitivity_recommendation(variable, correlation)
    
    def generate_tradeoff_explanation(
        self,
        variable: str,
        benefit: str,
        cost: str,
        impact_score: float,
        scenario_a_name: str,
        scenario_b_name: str
    ) -> str:
        """Genera una explicación individual para un tradeoff específico"""
        
        if not self.client:
            return self._get_fallback_tradeoff_explanation(variable, benefit, cost)
        
        prompt = self._build_tradeoff_prompt(
            variable, benefit, cost, impact_score, scenario_a_name, scenario_b_name
        )
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": TRADEOFF_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.7,
                max_tokens=512,
                response_format={"type": "json_object"}
            )
            
            raw_text = response.choices[0].message.content.strip()
            if raw_text.startswith("```"):
                raw_text = raw_text.split("```")[1]
                if raw_text.startswith("json"):
                    raw_text = raw_text[4:]
                raw_text = raw_text.strip()
            
            result = json.loads(raw_text)
            return result.get("explanation", self._get_fallback_tradeoff_explanation(variable, benefit, cost))
        
        except Exception as e:
            print(f"Error generando explicación para tradeoff de {variable}: {e}")
            return self._get_fallback_tradeoff_explanation(variable, benefit, cost)
    
    def _serialize_simulation_data(self, simulation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Serializa simulation_data para que sea JSON compatible"""
        
        serialized = {}
        
        for key, value in simulation_data.items():
            if key == "states" and isinstance(value, list):
                serialized[key] = []
                for state in value:
                    if hasattr(state, 'dict'):
                        serialized[key].append(state.dict())
                    elif hasattr(state, '__dict__'):
                        state_dict = {}
                        for attr in ['month', 'monthly_income', 'fixed_expenses', 'variable_expenses', 
                                     'monthly_debt_payments', 'housing_cost', 'total_savings', 
                                     'emergency_fund', 'liquidity', 'housing_ratio', 'debt_ratio', 
                                     'emergency_months', 'risk_status']:
                            if hasattr(state, attr):
                                val = getattr(state, attr)
                                if hasattr(val, 'value'):
                                    val = val.value
                                state_dict[attr] = val
                        serialized[key].append(state_dict)
            elif key == "metrics" and isinstance(value, dict):
                serialized[key] = {k: float(v) if v is not None else 0 for k, v in value.items()}
            elif isinstance(value, (list, dict)):
                serialized[key] = self._make_serializable(value)
            else:
                serialized[key] = value
        
        return serialized
    
    def _make_serializable(self, obj: Any) -> Any:
        """Convierte objetos no serializables a formatos serializables"""
        if obj is None:
            return None
        elif isinstance(obj, (str, int, float, bool)):
            return obj
        elif isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._make_serializable(item) for item in obj]
        elif hasattr(obj, 'value'):
            return obj.value
        elif hasattr(obj, 'dict'):
            return self._make_serializable(obj.dict())
        elif hasattr(obj, '__dict__'):
            return self._make_serializable(obj.__dict__)
        else:
            return str(obj)
    
    def _build_case_prompt(
        self,
        case_type: str,
        simulation_data: Dict[str, Any],
        timeline_events: List[Dict],
        metrics: Dict[str, Any],
        stress_metrics: Dict[str, Any],
        trajectory_data: Dict[str, Any]
    ) -> str:
        """Construye el prompt para un caso específico"""
        
        prompt = f"""Eres un analista financiero. Genera una narrativa para el **{case_type.upper()} CASE** de una simulación financiera.

FORMATO OBLIGATORIO (JSON):
{json.dumps(CASE_NARRATIVE_SCHEMA, ensure_ascii=False, indent=2)}

DATOS DE LA SIMULACIÓN:
- Tipo de caso: {case_type}
- Métricas finales: {json.dumps(metrics, ensure_ascii=False, indent=2, default=str)}
- Métricas de estrés: {json.dumps(stress_metrics, ensure_ascii=False, indent=2, default=str)}
- Eventos clave: {json.dumps(timeline_events[:5], ensure_ascii=False, indent=2, default=str)}
- Trayectoria: {json.dumps(trajectory_data, ensure_ascii=False, indent=2, default=str)}
- Datos simulados: {json.dumps(simulation_data, ensure_ascii=False, indent=2, default=str)}

INSTRUCCIONES ESPECÍFICAS POR TIPO DE CASO:

**MEJOR CASO (Optimistic):**
- Enfócate en el potencial y las oportunidades
- Destaca cómo se logró la estabilidad
- Usa un tono esperanzador pero realista
- El título debe ser inspirador

**CASO ESPERADO (Expected):**
- Sé equilibrado y realista
- Muestra tanto fortalezas como áreas de mejora
- Usa un tono neutral pero útil
- El título debe reflejar la realidad más probable

**PEOR CASO (Worst):**
- Sé honesto pero no alarmista
- Enfócate en lecciones y áreas de atención
- Usa un tono constructivo, no catastrófico
- El título debe ser descriptivo pero no aterrador

Devuelve SOLO el JSON, sin texto adicional."""
        
        return prompt
    
    def _build_comparison_prompt(
        self,
        scenario_a_name: str,
        scenario_b_name: str,
        comparison_metrics: Dict[str, Any],
        tradeoffs: List[Dict],
        sensitivity_changes: List[Dict]
    ) -> str:
        """Construye el prompt para comparación"""
        
        prompt = f"""Compara dos escenarios financieros y genera una narrativa.

FORMATO OBLIGATORIO (JSON):
{json.dumps(COMPARISON_NARRATIVE_SCHEMA, ensure_ascii=False, indent=2)}

DATOS DE COMPARACIÓN:
- Escenario A: {scenario_a_name}
- Escenario B: {scenario_b_name}
- Métricas comparadas: {json.dumps(comparison_metrics, ensure_ascii=False, indent=2, default=str)}
- Tradeoffs identificados: {json.dumps(tradeoffs, ensure_ascii=False, indent=2, default=str)}
- Cambios en sensibilidad: {json.dumps(sensitivity_changes, ensure_ascii=False, indent=2, default=str)}

INSTRUCCIONES:
1. Sé imparcial - ambos escenarios tienen pros y contras
2. Explica los tradeoffs de forma clara y útil
3. La recomendación debe ser práctica y accionable
4. Usa un tono consultivo, no directivo
5. Destaca qué escenario es mejor para diferentes prioridades del usuario

Devuelve SOLO el JSON, sin texto adicional."""
        
        return prompt
    
    def _build_insights_prompt(
        self,
        scenario_name: str,
        stability_probability: float,
        expected_metrics: Dict[str, Any],
        timeline_events: List[Dict],
        trajectory_data: Dict[str, Any]
    ) -> str:
        """Construye el prompt para insights generales"""
        
        prompt = f"""Genera insights financieros para un escenario de simulación.

FORMATO OBLIGATORIO (JSON):
{json.dumps(GENERAL_INSIGHTS_SCHEMA, ensure_ascii=False, indent=2)}

DATOS DEL ESCENARIO:
- Nombre: {scenario_name}
- Probabilidad de estabilidad: {stability_probability:.1%}
- Métricas esperadas: {json.dumps(expected_metrics, ensure_ascii=False, indent=2, default=str)}
- Eventos clave en timeline: {json.dumps(timeline_events[:3], ensure_ascii=False, indent=2, default=str)}
- Trayectoria: {json.dumps(trajectory_data, ensure_ascii=False, indent=2, default=str)}

INSTRUCCIONES:
1. El insight principal debe resumir la situación financiera general
2. Genera 4-5 insights específicos que ayuden al usuario a entender su situación
3. Cada insight debe tener un título claro y una descripción útil
4. Clasifica cada insight como positive, neutral, o warning según corresponda
5. Si aplica, referencia la métrica relacionada

Devuelve SOLO el JSON, sin texto adicional."""
        
        return prompt
    
    def _build_sensitivity_prompt(
        self,
        variable: str,
        correlation: float,
        impact_score: float,
        current_value: Optional[float],
        context: Optional[str]
    ) -> str:
        """Construye el prompt para recomendación de sensibilidad"""
        
        variable_names = {
            'monthly_income': 'ingresos mensuales',
            'fixed_expenses': 'gastos fijos',
            'variable_expenses': 'gastos variables',
            'housing_cost': 'costo de vivienda',
            'debt_payments': 'pagos de deuda'
        }
        var_name = variable_names.get(variable, variable)
        
        impact_type = "positivo" if correlation > 0 else "negativo"
        
        if correlation > 0:
            impact_description = f"aumentar tus {var_name} tiene un efecto positivo en tu estabilidad financiera"
        else:
            impact_description = f"aumentar tus {var_name} tiene un efecto negativo en tu estabilidad financiera"
        
        prompt = f"""Genera una recomendación financiera basada en análisis de sensibilidad.

FORMATO OBLIGATORIO (JSON):
{json.dumps(SENSITIVITY_RECOMMENDATION_SCHEMA, ensure_ascii=False, indent=2)}

DATOS DEL ANÁLISIS:
- Variable analizada: {var_name}
- Correlación con estabilidad: {correlation:.2f}
- Impacto score: {impact_score:.2f}
- Tipo de impacto: {impact_type}
- Contexto: {impact_description}
- Valor actual: {current_value if current_value else "No especificado"}
- Información adicional: {context if context else "No disponible"}

INSTRUCCIONES:
1. La recomendación debe ser concisa (máximo 2 oraciones)
2. Sé específico y accionable
3. Ofrece 2-3 pasos concretos que el usuario puede tomar
4. Prioriza según la importancia del impacto

Devuelve SOLO el JSON, sin texto adicional."""
        
        return prompt
    
    def _build_tradeoff_prompt(
        self,
        variable: str,
        benefit: str,
        cost: str,
        impact_score: float,
        scenario_a_name: str,
        scenario_b_name: str
    ) -> str:
        """Construye el prompt para explicación de tradeoff"""
        
        variable_names = {
            'monthly_income': 'ingresos mensuales',
            'fixed_expenses': 'gastos fijos',
            'variable_expenses': 'gastos variables',
            'housing_cost': 'costo de vivienda',
            'debt_payments': 'pagos de deuda'
        }
        var_name = variable_names.get(variable, variable)
        
        prompt = f"""Explica este tradeoff financiero de forma clara y concisa.

FORMATO OBLIGATORIO (JSON):
{json.dumps(TRADEOFF_EXPLANATION_SCHEMA, ensure_ascii=False, indent=2)}

DATOS DEL TRADEOFF:
- Variable: {var_name}
- Beneficio en escenario B: {benefit}
- Costo en escenario B: {cost}
- Impacto: {impact_score:.2f}
- Escenario A: {scenario_a_name}
- Escenario B: {scenario_b_name}

INSTRUCCIONES:
1. Explica qué significa este tradeoff para el usuario
2. Menciona qué se gana (beneficio) y qué se pierde (costo)
3. Sé específico y práctico
4. Máximo 2-3 oraciones

Devuelve SOLO el JSON, sin texto adicional."""
        
        return prompt
    
    def _get_fallback_narrative(self, case_type: str) -> Dict[str, Any]:
        """Narrativa de respaldo en caso de error del LLM"""
        
        templates = {
            "best": {
                "title": "Futuro Financiero Optimista",
                "financial_state": "Situación financiera sólida y en crecimiento",
                "summary": "Las condiciones favorables permiten construir un futuro estable",
                "top_metrics": [],
                "key_events": [],
                "risks": [],
                "opportunities": [{"type": "growth", "description": "Potencial de crecimiento sostenido", "potential": "high"}],
                "trajectory": {"type": "stable_growth", "description": "Crecimiento estable proyectado"},
                "emotional_tone": "optimistic",
                "scenario_personality": "resilient",
                "stress_exposure": {"months_in_critical": 0, "months_in_risky": 0, "max_stress_duration": 0},
                "recovery_metrics": {"months_to_recovery": 0, "recovery_quality": "fast"}
            },
            "expected": {
                "title": "Futuro Financiero Esperado",
                "financial_state": "Situación financiera equilibrada",
                "summary": "El escenario más probable muestra estabilidad moderada",
                "top_metrics": [],
                "key_events": [],
                "risks": [{"type": "moderate", "description": "Alguna vulnerabilidad a shocks", "severity": "medium"}],
                "opportunities": [{"type": "improvement", "description": "Margen para mejorar", "potential": "medium"}],
                "trajectory": {"type": "fragile_stability", "description": "Estabilidad con cierta fragilidad"},
                "emotional_tone": "cautious",
                "scenario_personality": "sustainable",
                "stress_exposure": {"months_in_critical": 0, "months_in_risky": 6, "max_stress_duration": 3},
                "recovery_metrics": {"months_to_recovery": 12, "recovery_quality": "moderate"}
            },
            "worst": {
                "title": "Futuro Financiero de Estrés",
                "financial_state": "Situación financiera bajo presión",
                "summary": "El escenario muestra periodos significativos de estrés financiero",
                "top_metrics": [],
                "key_events": [],
                "risks": [{"type": "critical", "description": "Alta vulnerabilidad a shocks", "severity": "high"}],
                "opportunities": [],
                "trajectory": {"type": "progressive_decline", "description": "Deterioro progresivo de la salud financiera"},
                "emotional_tone": "stressful",
                "scenario_personality": "fragile",
                "stress_exposure": {"months_in_critical": 18, "months_in_risky": 24, "max_stress_duration": 12},
                "recovery_metrics": {"months_to_recovery": 36, "recovery_quality": "slow"}
            }
        }
        
        return templates.get(case_type, templates["expected"])
    
    def _get_fallback_comparison(self, scenario_a: str, scenario_b: str) -> Dict[str, Any]:
        """Comparación de respaldo"""
        
        return {
            "comparison_summary": f"Comparación entre {scenario_a} y {scenario_b}",
            "winning_aspects": [],
            "losing_aspects": [],
            "tradeoff_explanation": "Cada escenario tiene ventajas y desventajas según tus prioridades",
            "recommendation": "Revisa las métricas detalladas para tomar una decisión informada",
            "risk_warning": None
        }
    
    def _get_fallback_insights(self) -> Dict[str, Any]:
        """Insights de respaldo en caso de error"""
        
        return {
            "main_insight": "Tu situación financiera muestra estabilidad moderada, con áreas de mejora identificadas.",
            "insights": [
                {
                    "id": "insight_1",
                    "title": "Liquidez disponible",
                    "description": "Tu liquidez mensual te da margen de maniobra, pero es importante monitorearla.",
                    "severity": "neutral",
                    "metric_reference": "liquidity"
                },
                {
                    "id": "insight_2",
                    "title": "Carga de vivienda",
                    "description": "El costo de vivienda representa una porción significativa de tus ingresos.",
                    "severity": "warning",
                    "metric_reference": "housing_ratio"
                },
                {
                    "id": "insight_3",
                    "title": "Fondo de emergencia",
                    "description": "Tu fondo de emergencia te protege ante imprevistos, pero considera aumentarlo.",
                    "severity": "positive",
                    "metric_reference": "emergency_fund"
                }
            ]
        }
    
    def _get_fallback_sensitivity_recommendation(self, variable: str, correlation: float) -> Dict[str, Any]:
        """Recomendación de respaldo en caso de error"""
        
        var_names = {
            'monthly_income': 'ingresos mensuales',
            'fixed_expenses': 'gastos fijos',
            'variable_expenses': 'gastos variables',
            'housing_cost': 'costo de vivienda',
            'debt_payments': 'pagos de deuda'
        }
        var_name = var_names.get(variable, variable)
        
        if correlation > 0:
            return {
                "recommendation": f"Mantener o aumentar tus {var_name} es clave para tu estabilidad financiera.",
                "priority": "high" if abs(correlation) > 0.3 else "medium",
                "actionable_steps": [
                    f"Monitorea tus {var_name} mensualmente",
                    "Busca oportunidades para incrementar ingresos si es posible"
                ]
            }
        else:
            return {
                "recommendation": f"Controlar tus {var_name} es importante para mantener tu estabilidad financiera.",
                "priority": "high" if abs(correlation) > 0.3 else "medium",
                "actionable_steps": [
                    f"Revisa y optimiza tus {var_name}",
                    "Identifica áreas donde puedas reducir gastos"
                ]
            }
    
    def _get_fallback_tradeoff_explanation(self, variable: str, benefit: str, cost: str) -> str:
        """Explicación de respaldo para tradeoff"""
        
        return f"{benefit}, pero {cost.lower()}. Considera cómo esto se alinea con tus prioridades financieras."