from datetime import datetime
from typing import Any, Dict, List

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
        
        # Obtener valores base
        monthly_income = float(user_data.get('monthly_income', 0))
        fixed_expenses = float(user_data.get('fixed_expenses', 0))
        variable_expenses = float(user_data.get('variable_expenses', 0))
        monthly_debt_payments = float(user_data.get('monthly_debt_payments', 0))
        monthly_rent = user_data.get('monthly_rent', 0)
        rent_overlap_months = int(user_data.get('rent_mortgage_overlap_months', 0))
        
        # Inicializar variables
        housing_cost = 0.0
        base_mortgage_payment = 0.0
        base_monthly_rent = float(monthly_rent) if monthly_rent else 0.0
        has_mortgage = False
        is_renting = False
        rent_overlap_remaining = 0
        
        if property_input:
            # Escenario de compra
            has_mortgage = True
            try:
                from app.services.mortgage import calculate_mortgage
                mortgage_result = calculate_mortgage(property_input)
                base_mortgage_payment = float(mortgage_result.monthly_payment) if mortgage_result else 0.0
                print(f"DEBUG: Cuota hipoteca = {base_mortgage_payment:,.0f}")
            except Exception as e:
                print(f"Error calculando mortgage: {e}")
                base_mortgage_payment = 0.0
            
            # Verificar si hay período de overlap (renta durante los primeros meses)
            if monthly_rent and rent_overlap_months > 0:
                is_renting = True
                rent_overlap_remaining = rent_overlap_months
                housing_cost = base_mortgage_payment + base_monthly_rent
                print(f"DEBUG: Overlap activo - Hipoteca + Renta = {housing_cost:,.0f} durante {rent_overlap_months} meses")
            else:
                housing_cost = base_mortgage_payment
                print(f"DEBUG: Solo hipoteca = {housing_cost:,.0f}")
        else:
            # Sin compra: si hay renta, pagar renta
            if monthly_rent:
                is_renting = True
                housing_cost = base_monthly_rent
                print(f"DEBUG: Solo renta = {housing_cost:,.0f}")
            else:
                housing_cost = 0.0
                print(f"DEBUG: Sin costo de vivienda")
        
        print(f"DEBUG _build_initial_state: property_input={property_input is not None}, housing_cost={housing_cost:,.0f}")
        
        state = SimulationState(
            month=0,
            date=datetime.now().date(),
            monthly_income=monthly_income,
            fixed_expenses=fixed_expenses,
            variable_expenses=variable_expenses,
            monthly_debt_payments=monthly_debt_payments,
            housing_cost=housing_cost,
            total_savings=float(user_data.get('total_savings', 0)),
            emergency_fund=float(user_data.get('emergency_fund', 0)),
            # Campos de vivienda
            is_renting=is_renting,
            monthly_rent=base_monthly_rent,
            rent_overlap_months_remaining=rent_overlap_remaining,
            has_mortgage=has_mortgage,
            base_mortgage_payment=base_mortgage_payment,
            base_monthly_rent=base_monthly_rent
        )
        state.calculate_metrics()
        return state
    
    def run_scenario(self, scenario_input: ScenarioInput, current_user: User) -> SimulationResults:
        """Orquesta la ejecución completa de un escenario"""
        
        # 1. Obtener snapshot del usuario
        user_snapshot = self._get_or_create_snapshot(scenario_input, current_user)
        
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
        user_snapshot = self._get_or_create_snapshot(scenario_input, user)
        
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
    
    def _get_or_create_snapshot(self, scenario_input: ScenarioInput, current_user: User) -> UserSnapshot:
        """Obtiene un snapshot existente o crea uno nuevo con los datos del usuario actual"""
        
        # Si se proporciona un snapshot_id, intentar obtenerlo
        if scenario_input.user_snapshot_id:
            snapshot = self.db.query(UserSnapshot).filter(
                UserSnapshot.id == scenario_input.user_snapshot_id
            ).first()
            if snapshot:
                return snapshot
        
        # Crear snapshot con los datos del usuario actual
        snapshot = UserSnapshot(
            user_id=current_user.id,  # Usar el ID del usuario autenticado
            created_at=datetime.utcnow(),
            # Datos del perfil del usuario
            monthly_income=float(current_user.monthly_income or 0),
            fixed_expenses=float(current_user.fixed_expenses or 0),
            variable_expenses=float(current_user.variable_expenses or 0),
            total_savings=float(current_user.total_savings or 0),
            emergency_fund=float(current_user.emergency_fund or 0),
            monthly_savings_goal=float(current_user.monthly_savings_goal or 0),
            income_type=current_user.income_type,
            income_variability=current_user.income_variability,
            contract_type=current_user.contract_type,
            job_seniority_months=int(current_user.job_seniority_months or 0),
            monthly_debt_payments=float(current_user.monthly_debt_payments or 0),
            total_debt=float(current_user.total_debt or 0),
            is_renting=bool(current_user.is_renting or False),
            monthly_rent=float(current_user.monthly_rent or 0) if current_user.monthly_rent else None,
            rent_mortgage_overlap_months=int(current_user.rent_mortgage_overlap_months or 0),
            dependents=int(current_user.dependents or 0)
        )
        
        # Aplicar overrides del escenario si existen
        if scenario_input.overrides:
            for key, value in scenario_input.overrides.items():
                if hasattr(snapshot, key) and value is not None:
                    setattr(snapshot, key, value)
        
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
        
    def get_user_scenarios(self, user: User) -> List[SavedScenario]:
        """Obtiene todos los escenarios guardados del usuario"""
        return self.db.query(SavedScenario).filter(
            SavedScenario.user_id == user.id
        ).order_by(SavedScenario.created_at.desc()).all()