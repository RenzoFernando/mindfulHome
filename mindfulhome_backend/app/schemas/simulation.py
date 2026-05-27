from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.schemas.analysis import PropertyInput

class SimulationResponse(BaseModel):
    scenario_id: Optional[int]
    results: Dict[str, Any]
    status: str
    created_at: datetime = datetime.now()

class ScenarioCreate(BaseModel):
    name: str
    description: Optional[str] = None
    modifications: Dict[str, Any] = {}
    property_input: Optional[PropertyInput] = None
    simulation_months: int = 360
    num_simulations: int = 100
    results_summary: Optional[Dict[str, Any]] = None

class ScenarioUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    modifications: Optional[Dict[str, Any]] = None
    property_input: Optional[PropertyInput] = None
    simulation_months: Optional[int] = None
    num_simulations: Optional[int] = None
    results_summary: Optional[Dict[str, Any]] = None

class ScenarioResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    scenario_overrides: Optional[Dict[str, Any]]
    property_input: Optional[Dict[str, Any]]
    simulation_config: Optional[Dict[str, Any]]
    inputs: Optional[Dict[str, Any]]
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
