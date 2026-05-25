# app/api/v1/endpoints/comparison.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.api import deps
from app.models.user import User
from app.services.comparator_service import ComparatorService
from app.simulation.models.scenario import ScenarioInput
from app.simulation.models.comparison import ComparisonResponse

router = APIRouter()

@router.post("/compare", response_model=ComparisonResponse)
async def compare_scenarios(
    scenario_a_id: Optional[int] = Query(None, description="ID del primer escenario guardado"),
    scenario_b_id: Optional[int] = Query(None, description="ID del segundo escenario guardado"),
    temporal_scenario: Optional[ScenarioInput] = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Compara dos escenarios financieros
    
    Puede comparar:
    - Dos escenarios guardados (proveer ambos IDs)
    - Escenario guardado vs temporal (proveer un ID y temporal_scenario)
    - Dos escenarios temporales (proveer temporal_scenario con overrides diferentes)
    """
    
    if not (scenario_a_id or scenario_b_id or temporal_scenario):
        raise HTTPException(
            status_code=400,
            detail="Debe proporcionar al menos un escenario (guardado o temporal)"
        )
    
    service = ComparatorService(db)
    
    # Para comparar dos temporales, necesitamos un enfoque diferente
    if not scenario_a_id and not scenario_b_id and temporal_scenario:
        # Comparar escenario base (usuario actual) vs temporal
        return await service.compare_scenarios(
            scenario_a=None,
            scenario_b=None,
            temporal_scenario=temporal_scenario,
            user_id=current_user.id
        )
    elif scenario_a_id and scenario_b_id:
        # Comparar dos guardados
        return await service.compare_scenarios(
            scenario_a=scenario_a_id,
            scenario_b=scenario_b_id,
            user_id=current_user.id
        )
    elif scenario_a_id and not scenario_b_id:
        # Comparar guardado vs temporal
        return await service.compare_scenarios(
            scenario_a=scenario_a_id,
            scenario_b=None,
            temporal_scenario=temporal_scenario,
            user_id=current_user.id
        )
    else:
        raise HTTPException(
            status_code=400,
            detail="Combinación de parámetros no válida"
        )

@router.get("/compare/{scenario_a_id}/{scenario_b_id}")
async def compare_saved_scenarios(
    scenario_a_id: int,
    scenario_b_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Compara dos escenarios guardados por ID"""
    
    service = ComparatorService(db)
    
    return await service.compare_scenarios(
        scenario_a=scenario_a_id,
        scenario_b=scenario_b_id,
        user_id=current_user.id
    )

@router.post("/compare/current")
async def compare_with_current(
    scenario_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Compara un escenario guardado con el estado actual del usuario"""
    
    temporal = ScenarioInput(
        overrides={},
        simulation_months=360,
        num_simulations=1000
    )
    
    service = ComparatorService(db)
    
    return await service.compare_scenarios(
        scenario_a=scenario_id,
        scenario_b=None,
        temporal_scenario=temporal,
        user_id=current_user.id
    )