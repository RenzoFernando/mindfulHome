from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class SimulationResponse(BaseModel):
    scenario_id: Optional[int]
    results: Dict[str, Any]
    status: str
    created_at: datetime = datetime.now()

class ScenarioCreate(BaseModel):
    name: str
    description: Optional[str] = None
    modifications: Dict[str, Any]
    property_input: Optional[Dict[str, Any]]

class ScenarioResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    results_summary: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True

class TimelineDataPoint(BaseModel):
    month: int
    liquidity_p50: float
    liquidity_p10: float
    liquidity_p90: float
    stability_probability: float
    housing_ratio: float