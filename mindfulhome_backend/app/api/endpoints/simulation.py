from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.api import deps
from app.models.user import User
from app.schemas.simulation import ScenarioCreate, ScenarioResponse, SimulationResponse
from app.services.scenario_service import ScenarioService
from app.simulation.models.scenario import ScenarioInput
from app.simulation.scenarios.playground import PlaygroundManager, PlaygroundModification, WhatIfLibrary

router = APIRouter()

@router.post("/simulate", response_model=SimulationResponse)
async def run_simulation(scenario_input: ScenarioInput, background_tasks: BackgroundTasks, db: Session = Depends(deps.get_db), current_user: User = Depends(deps.get_current_user)):
    """Ejecuta una simulación Monte Carlo para un escenario"""
    service = ScenarioService(db)
    
    # Ejecutar simulación (podría ser pesada, usar background)
    results = service.run_scenario(scenario_input)
    
    return SimulationResponse(
        scenario_id=scenario_input.id if hasattr(scenario_input, 'id') else None,
        results=results.dict(),
        status="completed"
    )

@router.post("/scenarios", response_model=ScenarioResponse)
async def save_scenario(scenario: ScenarioCreate, db: Session = Depends(deps.get_db), current_user: User = Depends(deps.get_current_user)):
    """Guarda un escenario personalizado"""
    service = ScenarioService(db)
    
    scenario_input = ScenarioInput(
        overrides=scenario.modifications,
        property_input=scenario.property_input
    )
    
    saved = service.save_scenario(current_user, scenario.name, scenario_input)
    return ScenarioResponse.from_orm(saved)

@router.get("/whatif/presets")
async def get_whatif_presets():
    """Retorna los presets de What-If disponibles"""
    return WhatIfLibrary.get_presets()

@router.post("/playground/apply")
async def apply_playground_modifications(modifications: List[PlaygroundModification], current_user: User = Depends(deps.get_current_user)):
    """Aplica modificaciones temporales al escenario base del usuario"""
    user_data = current_user.dict()
    playground = PlaygroundManager(user_data)
    
    for mod in modifications:
        playground.apply_modification(mod)
    
    return playground.get_current_scenario()