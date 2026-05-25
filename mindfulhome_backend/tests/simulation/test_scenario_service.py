import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.services.scenario_service import ScenarioService
from app.simulation.models.scenario import ScenarioInput
from app.simulation.models.rules import SimulationRules
from app.models.user import User, IncomeType, IncomeVariability, ContractType
from app.schemas.analysis import PropertyInput, InterestRateType

class TestScenarioService:
    """Pruebas del servicio de escenarios"""
    
    @pytest.fixture
    def db_session(self):
        """Base de datos en memoria para pruebas"""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        return Session()
    
    @pytest.fixture
    def test_user(self, db_session):
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="fakehash",
            monthly_income=5000000,
            fixed_expenses=1500000,
            variable_expenses=1000000,
            total_savings=10000000,
            emergency_fund=5000000,
            income_type=IncomeType.EMPLEADO,
            income_variability=IncomeVariability.FIJO,
            contract_type=ContractType.INDEFINIDO,
            job_seniority_months=24,
            monthly_debt_payments=500000,
            total_debt=10000000,
            dependents=2
        )
        db_session.add(user)
        db_session.commit()
        return user
    
    @pytest.fixture
    def property_input(self):
        return PropertyInput(
            property_price=300000000,
            down_payment=60000000,
            annual_interest_rate=12.0,
            interest_rate_type=InterestRateType.FIJA,
            loan_term_years=20
        )
    
    def test_run_scenario_basic(self, db_session, test_user, property_input):
        """Ejecutar escenario básico"""
        service = ScenarioService(db_session)
        
        scenario_input = ScenarioInput(
            property_input=property_input,
            simulation_months=60,  # 5 años
            num_simulations=50  # Pocas para pruebas rápidas
        )
        
        results = service.run_scenario(scenario_input)
        
        # Verificar resultados
        assert results.num_simulations == 50
        assert results.simulation_months == 60
        assert len(results.timeline) == 61
        assert 0 <= results.stability_probability <= 1
        
    def test_run_scenario_with_overrides(self, db_session, test_user, property_input):
        """Ejecutar escenario con modificaciones"""
        service = ScenarioService(db_session)
        
        scenario_input = ScenarioInput(
            property_input=property_input,
            overrides={
                'monthly_income': 3000000,  # Menos ingresos
                'variable_expenses': 2000000  # Más gastos
            },
            simulation_months=120,
            num_simulations=50
        )
        
        results = service.run_scenario(scenario_input)
        
        # La probabilidad de estabilidad debería ser menor que en escenario base
        assert results.stability_probability <= 0.8
        
    def test_save_and_retrieve_scenario(self, db_session, test_user, property_input):
        """Guardar y recuperar escenario"""
        service = ScenarioService(db_session)
        
        scenario_input = ScenarioInput(
            property_input=property_input,
            overrides={'monthly_income': 4000000},
            simulation_months=60,
            num_simulations=50
        )
        
        saved = service.save_scenario(test_user, "Test Scenario", scenario_input)
        
        assert saved.id is not None
        assert saved.name == "Test Scenario"
        assert saved.user_id == test_user.id
        
    def test_rules_generation_consistency(self, db_session, test_user, property_input):
        """Verificar consistencia en generación de reglas"""
        service = ScenarioService(db_session)
        
        scenario_input = ScenarioInput(
            property_input=property_input,
            simulation_months=12,
            num_simulations=10
        )
        
        results1 = service.run_scenario(scenario_input)
        results2 = service.run_scenario(scenario_input)
        
        # Con mismas semillas, resultados deberían ser similares
        # (No idénticos por random, pero estadísticamente similares)
        assert abs(results1.stability_probability - results2.stability_probability) < 0.3