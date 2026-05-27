# app/simulation/models/results.py (actualizado)

from typing import Dict, List, Any, Optional
from pydantic import BaseModel

class MetricPercentiles(BaseModel):
    p10: float
    p50: float
    p90: float
    mean: float
    std: float

class TimelinePoint(BaseModel):
    month: int
    liquidity: MetricPercentiles
    stability_probability: float
    housing_ratio: MetricPercentiles
    risk_distribution: Dict[str, float]

class SensitivityAnalysis(BaseModel):
    variable: str
    correlation: float
    impact_score: float
    recommendation: str
    priority: Optional[str] = "medium"
    actionable_steps: Optional[List[str]] = []

class SimulationResults(BaseModel):
    # Resultados base
    expected_results: Dict[str, MetricPercentiles]
    best_case_results: Dict[str, float]
    worst_case_results: Dict[str, float]
    
    # Narrativas
    best_case_narrative: Dict[str, Any]
    expected_case_narrative: Dict[str, Any]
    worst_case_narrative: Dict[str, Any]
    
    # NUEVO: Insights generales
    general_insights: Dict[str, Any]
    
    # Métricas de probabilidad
    stability_probability: float
    liquidity_shortfall_probability: float
    financial_stress_probability: float
    
    # Timeline y eventos
    timeline: List[TimelinePoint]
    timeline_events: List[Dict[str, Any]]
    
    # Métricas de estrés y trayectoria
    stress_metrics: Dict[str, Any]
    trajectory_analysis: Dict[str, Any]
    
    # Análisis de sensibilidad mejorado
    top_sensitive_variables: List[SensitivityAnalysis]
    
    # Metadata
    num_simulations: int
    simulation_months: int
    convergence_checked: bool = False