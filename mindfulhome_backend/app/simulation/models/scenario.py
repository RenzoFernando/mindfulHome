from pydantic import BaseModel, Field
from typing import Any, Dict, Optional

from app.schemas.analysis import PropertyInput


class ScenarioInput(BaseModel):
    """Input completo para una simulación"""
    user_snapshot_id: Optional[int] = None
    overrides: Dict[str, Any] = Field(default_factory=dict)
    property_input: Optional['PropertyInput'] = None
    simulation_months: int = 360  # 30 años por defecto
    num_simulations: int = 1000
    
    class Config:
        arbitrary_types_allowed = True