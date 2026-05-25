from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import numpy as np

from app.models.analysis import RiskStatus

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
    risk_distribution: Dict[RiskStatus, float]

class SensitivityAnalysis(BaseModel):
    variable: str
    correlation: float
    impact_score: float
    recommendation: str

class SimulationResults(BaseModel):
    # Resultados agregados
    expected_results: Dict[str, MetricPercentiles]
    best_case_results: Dict[str, float]
    worst_case_results: Dict[str, float]
    
    # Probabilidades
    stability_probability: float
    liquidity_shortfall_probability: float
    financial_stress_probability: float
    
    # Timeline
    timeline: List[TimelinePoint]
    
    # Análisis de sensibilidad
    top_sensitive_variables: List[SensitivityAnalysis]
    
    # Metadata
    num_simulations: int
    simulation_months: int
    convergence_checked: bool = False