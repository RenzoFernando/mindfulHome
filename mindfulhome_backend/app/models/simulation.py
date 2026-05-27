from app.models.user import ContractType, IncomeType, IncomeVariability, User
from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey, JSON, DateTime, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum
from datetime import datetime

class ScenarioStatus(str, enum.Enum):
    TEMPORAL = "TEMPORAL"
    SAVED = "SAVED"

class SimulationType(str, enum.Enum):
    DETERMINISTIC = "DETERMINISTIC"
    MONTE_CARLO = "MONTE_CARLO"

class SavedScenario(Base):
    __tablename__ = "saved_scenarios"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(SAEnum(ScenarioStatus), default=ScenarioStatus.SAVED)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Snapshot de variables del usuario en el momento de creación
    user_snapshot_id = Column(Integer, ForeignKey("user_snapshots.id"), nullable=False)
    
    # Modificaciones específicas del escenario (override)
    scenario_overrides = Column(JSON, nullable=True)
    
    # Metadata de la simulación
    simulation_config = Column(JSON, nullable=True)
    results_summary = Column(JSON, nullable=True)
    
    user = relationship("User", back_populates="scenarios")
    user_snapshot = relationship("UserSnapshot", back_populates="scenarios")

    @property
    def property_input(self):
        config = self.simulation_config or {}
        return config.get("property_input")

    @property
    def inputs(self):
        snapshot = None
        if self.user_snapshot:
            snapshot = {
                "monthly_income": self.user_snapshot.monthly_income,
                "fixed_expenses": self.user_snapshot.fixed_expenses,
                "variable_expenses": self.user_snapshot.variable_expenses,
                "total_savings": self.user_snapshot.total_savings,
                "emergency_fund": self.user_snapshot.emergency_fund,
                "monthly_savings_goal": self.user_snapshot.monthly_savings_goal,
                "income_type": self.user_snapshot.income_type.value if self.user_snapshot.income_type else None,
                "income_variability": self.user_snapshot.income_variability.value if self.user_snapshot.income_variability else None,
                "contract_type": self.user_snapshot.contract_type.value if self.user_snapshot.contract_type else None,
                "job_seniority_months": self.user_snapshot.job_seniority_months,
                "monthly_debt_payments": self.user_snapshot.monthly_debt_payments,
                "total_debt": self.user_snapshot.total_debt,
                "is_renting": self.user_snapshot.is_renting,
                "monthly_rent": self.user_snapshot.monthly_rent,
                "rent_mortgage_overlap_months": self.user_snapshot.rent_mortgage_overlap_months,
                "dependents": self.user_snapshot.dependents
            }
        return {
            "user": snapshot,
            "overrides": self.scenario_overrides or {},
            "property_input": self.property_input
        }

class UserSnapshot(Base):
    __tablename__ = "user_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Copia completa del perfil del usuario
    monthly_income = Column(Float, nullable=True)
    fixed_expenses = Column(Float, nullable=True)
    variable_expenses = Column(Float, nullable=True)
    total_savings = Column(Float, nullable=True)
    emergency_fund = Column(Float, nullable=True)
    monthly_savings_goal = Column(Float, nullable=True)
    
    income_type = Column(SAEnum(IncomeType), nullable=True)
    income_variability = Column(SAEnum(IncomeVariability), nullable=True)
    contract_type = Column(SAEnum(ContractType), nullable=True)
    job_seniority_months = Column(Integer, nullable=True)
    
    monthly_debt_payments = Column(Float, nullable=True)
    total_debt = Column(Float, nullable=True)
    
    is_renting = Column(Boolean, default=False)
    monthly_rent = Column(Float, nullable=True)
    rent_mortgage_overlap_months = Column(Integer, default=0)
    dependents = Column(Integer, default=0)
    
    scenarios = relationship("SavedScenario", back_populates="user_snapshot")

class SimulationCache(Base):
    __tablename__ = "simulation_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    cache_key = Column(String, unique=True, index=True)  # Hash de los inputs
    results = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

# Actualizar relación en User
User.scenarios = relationship("SavedScenario", back_populates="user")
