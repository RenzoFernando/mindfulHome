from datetime import datetime
from typing import Any, Dict

from sqlalchemy.orm import Session
from app.models.user import User
from app.models.simulation import SavedScenario, SimulationCache, UserSnapshot
from app.simulation.models.results import SimulationResults
from app.simulation.models.scenario import ScenarioInput
from app.simulation.models.rules import SimulationRules
from app.simulation.models.simulation_state import SimulationState
from app.simulation.engine.monte_carlo import MonteCarloEngine
from app.simulation.engine.aggregator import SimulationAggregator
from app.simulation.rules.debt_rules import DebtRulesGenerator
from app.simulation.rules.income_rules import IncomeRulesGenerator
from app.simulation.rules.expense_rules import ExpenseRulesGenerator
from app.services.mortgage import calculate_mortgage
from app.simulation.rules.savings_rules import SavingsRulesGenerator

class ScenarioService:
    def __init__(self, db: Session):
        self.db = db
        
    def run_scenario(self, scenario_input: ScenarioInput) -> SimulationResults:
        """Orquesta la ejecución completa de un escenario"""
        
        # 1. Obtener snapshot del usuario
        user_snapshot = self._get_or_create_snapshot(scenario_input)
        
        # 2. Aplicar overrides del escenario
        merged_input = self._merge_overrides(user_snapshot, scenario_input.overrides)
        
        # 3. Generar reglas según perfil
        rules = self._generate_rules(merged_input)
        
        # 4. Construir estado inicial
        initial_state = self._build_initial_state(merged_input, scenario_input.property_input)
        
        # 5. Ejecutar simulaciones
        monte_carlo = MonteCarloEngine(
            rules=rules,
            initial_state=initial_state,
            num_simulations=scenario_input.num_simulations,
            months=scenario_input.simulation_months
        )
        simulation_results = monte_carlo.run()
        
        # 6. Agregar resultados
        aggregator = SimulationAggregator(simulation_results)
        results = aggregator.aggregate_results()
        
        # 7. Cachear resultados si es necesario
        self._cache_results(scenario_input, results)
        
        return results
    
    def save_scenario(self, user: User, name: str, scenario_input: ScenarioInput) -> SavedScenario:
        """Guarda un escenario para el usuario"""
        user_snapshot = self._get_or_create_snapshot(scenario_input)
        
        saved_scenario = SavedScenario(
            user_id=user.id,
            name=name,
            user_snapshot_id=user_snapshot.id,
            scenario_overrides=scenario_input.overrides,
            simulation_config={
                'num_simulations': scenario_input.num_simulations,
                'simulation_months': scenario_input.simulation_months
            }
        )
        
        self.db.add(saved_scenario)
        self.db.commit()
        self.db.refresh(saved_scenario)
        
        return saved_scenario
    
    def _generate_rules(self, user_data: dict) -> SimulationRules:
        """Genera reglas personalizadas según perfil"""
        temp_user = User(**{k: v for k, v in user_data.items() if hasattr(User, k)})
        
        return SimulationRules(
            income=IncomeRulesGenerator.generate_rules(temp_user),
            expenses=ExpenseRulesGenerator.generate_rules(temp_user),
            savings=SavingsRulesGenerator.generate_rules(temp_user),
            debt=DebtRulesGenerator.generate_rules(temp_user)
    )
    
    def _build_initial_state(self, user_data: dict, property_input) -> SimulationState:
        """Construye el estado inicial del mes 0"""
        # Calcular housing cost basado en propiedad
        mortgage_result = calculate_mortgage(property_input) if property_input else None
        housing_cost = mortgage_result.monthly_payment if mortgage_result else (user_data.get('monthly_rent', 0))
        
        state = SimulationState(
            month=0,
            date=datetime.now().date(),
            monthly_income=user_data.get('monthly_income', 0),
            fixed_expenses=user_data.get('fixed_expenses', 0),
            variable_expenses=user_data.get('variable_expenses', 0),
            monthly_debt_payments=user_data.get('monthly_debt_payments', 0),
            housing_cost=housing_cost,
            total_savings=user_data.get('total_savings', 0),
            emergency_fund=user_data.get('emergency_fund', 0)
        )
        state.calculate_metrics()
        return state
    
    def _get_or_create_snapshot(self, scenario_input: ScenarioInput) -> UserSnapshot:
        """Obtiene un snapshot existente o crea uno nuevo"""
        
        # Si se proporciona un snapshot_id, intentar obtenerlo
        if scenario_input.user_snapshot_id:
            snapshot = self.db.query(UserSnapshot).filter(
                UserSnapshot.id == scenario_input.user_snapshot_id
            ).first()
            if snapshot:
                return snapshot
            
        snapshot = UserSnapshot(
            user_id=1,  # TODO: Obtener del usuario actual
            created_at=datetime.utcnow(),
            monthly_income=scenario_input.overrides.get('monthly_income', 0),
            fixed_expenses=scenario_input.overrides.get('fixed_expenses', 0),
            variable_expenses=scenario_input.overrides.get('variable_expenses', 0),
            total_savings=scenario_input.overrides.get('total_savings', 0),
            emergency_fund=scenario_input.overrides.get('emergency_fund', 0),
            monthly_savings_goal=scenario_input.overrides.get('monthly_savings_goal', 0),
            income_type=scenario_input.overrides.get('income_type'),
            income_variability=scenario_input.overrides.get('income_variability'),
            contract_type=scenario_input.overrides.get('contract_type'),
            job_seniority_months=scenario_input.overrides.get('job_seniority_months', 0),
            monthly_debt_payments=scenario_input.overrides.get('monthly_debt_payments', 0),
            total_debt=scenario_input.overrides.get('total_debt', 0),
            is_renting=scenario_input.overrides.get('is_renting', False),
            monthly_rent=scenario_input.overrides.get('monthly_rent'),
            rent_mortgage_overlap_months=scenario_input.overrides.get('rent_mortgage_overlap_months', 0),
            dependents=scenario_input.overrides.get('dependents', 0)
        )
        
        self.db.add(snapshot)
        self.db.commit()
        self.db.refresh(snapshot)
        
        return snapshot
    
    def _merge_overrides(self, snapshot: UserSnapshot, overrides: Dict[str, Any]) -> Dict[str, Any]:
        """Combina los datos del snapshot con los overrides del escenario"""
        
        snapshot_data = {
            'monthly_income': snapshot.monthly_income,
            'fixed_expenses': snapshot.fixed_expenses,
            'variable_expenses': snapshot.variable_expenses,
            'total_savings': snapshot.total_savings,
            'emergency_fund': snapshot.emergency_fund,
            'monthly_savings_goal': snapshot.monthly_savings_goal,
            'income_type': snapshot.income_type,
            'income_variability': snapshot.income_variability,
            'contract_type': snapshot.contract_type,
            'job_seniority_months': snapshot.job_seniority_months,
            'monthly_debt_payments': snapshot.monthly_debt_payments,
            'total_debt': snapshot.total_debt,
            'is_renting': snapshot.is_renting,
            'monthly_rent': snapshot.monthly_rent,
            'rent_mortgage_overlap_months': snapshot.rent_mortgage_overlap_months,
            'dependents': snapshot.dependents
        }
        
        merged = {**snapshot_data, **overrides}
        
        return merged
    
    def _cache_results(self, scenario_input: ScenarioInput, results: SimulationResults) -> None:
        """Cachea los resultados de la simulación"""
        import hashlib
        import json
        
        cache_key_data = {
            'user_snapshot_id': scenario_input.user_snapshot_id,
            'overrides': scenario_input.overrides,
            'property_input': scenario_input.property_input.dict() if scenario_input.property_input else None,
            'simulation_months': scenario_input.simulation_months,
            'num_simulations': scenario_input.num_simulations
        }
        
        # Generar hash
        key_string = json.dumps(cache_key_data, sort_keys=True)
        cache_key = hashlib.md5(key_string.encode()).hexdigest()
        
        # Verificar si ya existe
        existing = self.db.query(SimulationCache).filter(
            SimulationCache.cache_key == cache_key
        ).first()
        
        if existing:
            # Actualizar existente
            existing.results = results.dict()
            existing.expires_at = datetime.utcnow()
        else:
            # Crear nuevo cache
            cache = SimulationCache(
                cache_key=cache_key,
                results=results.dict(),
                expires_at=datetime.utcnow()
            )
            self.db.add(cache)
        
        self.db.commit()