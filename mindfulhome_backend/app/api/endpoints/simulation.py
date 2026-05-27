from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.api import deps
import logging
from app.models.user import User
from app.schemas.analysis import PropertyInput
from app.schemas.simulation import ScenarioCreate, ScenarioResponse, ScenarioUpdate, SimulationResponse
from app.services.scenario_service import ScenarioService
from app.simulation.models.scenario import ScenarioInput
from app.simulation.scenarios.playground import PlaygroundManager, PlaygroundModification, PlaygroundState, WhatIfLibrary

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

router = APIRouter(prefix="/simulations", tags=["simulations"])

@router.post("/simulate", response_model=SimulationResponse)
async def run_simulation(
    scenario_input: ScenarioInput,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Ejecuta una simulación Monte Carlo para un escenario"""
    service = ScenarioService(db)
    
    if scenario_input.property_input:
        if not scenario_input.property_input.property_price:
            raise HTTPException(status_code=400, detail="Falta property_price")
        if not scenario_input.property_input.down_payment:
            raise HTTPException(status_code=400, detail="Falta down_payment")
        if not scenario_input.property_input.annual_interest_rate:
            raise HTTPException(status_code=400, detail="Falta annual_interest_rate")
        if not scenario_input.property_input.loan_term_years:
            raise HTTPException(status_code=400, detail="Falta loan_term_years")
    
    results = service.run_scenario(scenario_input, current_user)
    
    return SimulationResponse(
        scenario_id=scenario_input.id if hasattr(scenario_input, 'id') else None,
        results=results.dict(),
        status="completed"
    )

@router.post("/scenarios", response_model=ScenarioResponse)
async def save_scenario(
    scenario: ScenarioCreate, 
    db: Session = Depends(deps.get_db), 
    current_user: User = Depends(deps.get_current_user)
):
    """Guarda un escenario personalizado"""
    service = ScenarioService(db)
    
    scenario_input = ScenarioInput(
        overrides=scenario.modifications,
        property_input=scenario.property_input,
        simulation_months=scenario.simulation_months,
        num_simulations=scenario.num_simulations
    )
    
    saved = service.save_scenario(
        current_user,
        scenario.name,
        scenario_input,
        scenario.description,
        scenario.results_summary
    )
    return ScenarioResponse.model_validate(saved)

@router.post("/playground/apply", response_model=PlaygroundState)
async def apply_playground_modifications(
    modifications: List[PlaygroundModification] = [],
    property_modifications: List[PlaygroundModification] = [],
    property_input: Optional[PropertyInput] = None,
    current_user: User = Depends(deps.get_current_user)
):
    """Aplica modificaciones temporales al escenario base del usuario"""
    
    # DEBUG: Imprimir lo que llega
    logger.debug("=" * 50)
    logger.debug("PLAYGROUND APPLY REQUEST RECEIVED")
    logger.debug(f"modifications: {modifications}")
    logger.debug(f"property_modifications: {property_modifications}")
    logger.debug(f"property_input: {property_input}")
    logger.debug(f"current_user.id: {current_user.id}")
    logger.debug("=" * 50)
    
    # Datos base del usuario
    user_data = {
        "monthly_income": current_user.monthly_income,
        "fixed_expenses": current_user.fixed_expenses,
        "variable_expenses": current_user.variable_expenses,
        "total_savings": current_user.total_savings,
        "emergency_fund": current_user.emergency_fund,
        "monthly_savings_goal": current_user.monthly_savings_goal,
        "income_type": current_user.income_type,
        "income_variability": current_user.income_variability,
        "contract_type": current_user.contract_type,
        "job_seniority_months": current_user.job_seniority_months,
        "monthly_debt_payments": current_user.monthly_debt_payments,
        "total_debt": current_user.total_debt,
        "is_renting": current_user.is_renting,
        "monthly_rent": current_user.monthly_rent,
        "rent_mortgage_overlap_months": current_user.rent_mortgage_overlap_months,
        "dependents": current_user.dependents
    }
    
    logger.debug(f"Datos base del usuario: {user_data}")
    
    # Si el usuario tiene una propiedad analizada, usarla como base
    if not property_input:
        logger.debug("No se recibió property_input, buscando última propiedad analizada...")
        from app.models.analysis import PropertyAnalysis
        last_analysis = current_user.analyses[-1] if current_user.analyses else None
        if last_analysis:
            logger.debug(f"Última propiedad encontrada: ID={last_analysis.id}")
            property_input = PropertyInput(
                property_price=last_analysis.property_price,
                down_payment=last_analysis.down_payment,
                annual_interest_rate=last_analysis.annual_interest_rate,
                interest_rate_type=last_analysis.interest_rate_type,
                loan_term_years=last_analysis.loan_term_years
            )
            logger.debug(f"Property input creado: {property_input}")
        else:
            logger.debug("No se encontraron propiedades analizadas para el usuario")
    else:
        logger.debug(f"Property input recibido: {property_input}")
        logger.debug(f"  - property_price: {property_input.property_price}")
        logger.debug(f"  - down_payment: {property_input.down_payment}")
        logger.debug(f"  - annual_interest_rate: {property_input.annual_interest_rate}")
        logger.debug(f"  - loan_term_years: {property_input.loan_term_years}")
    
    playground = PlaygroundManager(user_data, property_input)
    logger.debug("PlaygroundManager creado")
    
    # Aplicar modificaciones
    logger.debug(f"Aplicando {len(modifications)} modificaciones de usuario...")
    for mod in modifications:
        logger.debug(f"  - Usuario: {mod.variable} = {mod.new_value} (cambio: {mod.percentage_change}%)")
        playground.apply_modification(mod, is_property=False)
    
    logger.debug(f"Aplicando {len(property_modifications)} modificaciones de propiedad...")
    for mod in property_modifications:
        logger.debug(f"  - Propiedad: {mod.variable} = {mod.new_value} (cambio: {mod.percentage_change}%)")
        playground.apply_modification(mod, is_property=True)
    
    result = playground.get_current_scenario()
    logger.debug(f"Resultado final - user_data keys: {list(result.user_data.keys())}")
    logger.debug(f"Resultado final - property_input: {result.property_input}")
    logger.debug("=" * 50)
    
    return result

@router.get("/whatif/presets")
async def get_whatif_presets():
    """Retorna los presets de What-If disponibles"""
    return WhatIfLibrary.get_presets()

@router.get("/scenarios", response_model=List[ScenarioResponse])
async def get_user_scenarios(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Obtiene todos los escenarios guardados del usuario"""
    service = ScenarioService(db)
    scenarios = service.get_user_scenarios(current_user)
    return [ScenarioResponse.model_validate(s) for s in scenarios]

@router.get("/scenarios/{scenario_id}", response_model=ScenarioResponse)
async def get_saved_scenario(
    scenario_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    service = ScenarioService(db)
    scenario = service.get_scenario(current_user, scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Escenario no encontrado")
    return ScenarioResponse.model_validate(scenario)

@router.patch("/scenarios/{scenario_id}", response_model=ScenarioResponse)
async def update_saved_scenario(
    scenario_id: int,
    updates: ScenarioUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    service = ScenarioService(db)
    scenario = service.update_scenario(
        current_user,
        scenario_id,
        updates.model_dump(exclude_unset=True)
    )
    if not scenario:
        raise HTTPException(status_code=404, detail="Escenario no encontrado")
    return ScenarioResponse.model_validate(scenario)

@router.delete("/scenarios/{scenario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_saved_scenario(
    scenario_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    service = ScenarioService(db)
    deleted = service.delete_scenario(current_user, scenario_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Escenario no encontrado")
    return None
