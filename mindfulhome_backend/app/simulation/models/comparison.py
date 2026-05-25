# app/simulation/models/comparison.py
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime

class ComparisonMetric(str, Enum):
    STABILITY_PROBABILITY = "stability_probability"
    LIQUIDITY_SHORTFALL = "liquidity_shortfall_probability"
    FINANCIAL_STRESS = "financial_stress_probability"
    HOUSING_RATIO = "housing_ratio"
    DEBT_RATIO = "debt_ratio"
    EMERGENCY_MONTHS = "emergency_months"

class ScenarioComparison(BaseModel):
    """Comparación entre dos escenarios"""
    scenario_a_id: Optional[int]
    scenario_a_name: str
    scenario_b_id: Optional[int]
    scenario_b_name: str
    comparison_date: datetime = Field(default_factory=datetime.now)
    
    # Métricas principales
    stability_probability_a: float
    stability_probability_b: float
    stability_improvement: float  # positivo si B mejora A
    
    # Métricas secundarias
    metrics_comparison: Dict[str, Dict[str, float]]
    
    # Top 3 ratios relevantes para cada escenario
    top_ratios_a: List[Dict[str, Any]]
    top_ratios_b: List[Dict[str, Any]]
    
    # Tradeoffs entre escenarios
    tradeoffs: List['Tradeoff']
    
    # Metadata
    recommendation: str
    risk_warning: Optional[str] = None

class TimelineComparisonPoint(BaseModel):
    """Punto del timeline comparativo"""
    month: int
    stability_probability_a: float
    stability_probability_b: float
    liquidity_p50_a: float
    liquidity_p50_b: float
    housing_ratio_a: float
    housing_ratio_b: float
    confidence_interval_a: Optional[Dict[str, float]] = None
    confidence_interval_b: Optional[Dict[str, float]] = None

class Tradeoff(BaseModel):
    """Tradeoff identificado entre escenarios"""
    variable: str
    benefit: str
    cost: str
    impact_score: float
    confidence: float
    
    correlation_a: float
    correlation_b: float
    delta_sensitivity: float
    
    recommendation: str

class ComparisonResponse(BaseModel):
    """Respuesta completa de comparación"""
    comparison: ScenarioComparison
    timeline: List[TimelineComparisonPoint]
    tradeoff_analysis: Dict[str, Any]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }