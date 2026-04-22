from sqlalchemy import Column, Integer, String, Float, Boolean, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum


class IncomeType(str, enum.Enum):
    EMPLEADO = "EMPLEADO"
    INDEPENDIENTE = "INDEPENDIENTE"
    EMPRESARIO = "EMPRESARIO"
    PENSIONADO = "PENSIONADO"


class IncomeVariability(str, enum.Enum):
    FIJO = "FIJO"
    VARIABLE = "VARIABLE"
    MIXTO = "MIXTO"


class ContractType(str, enum.Enum):
    INDEFINIDO = "INDEFINIDO"
    FIJO = "FIJO"
    PRESTACION_SERVICIOS = "PRESTACION_SERVICIOS"
    NINGUNO = "NINGUNO"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Perfil financiero
    monthly_income = Column(Float, nullable=True)
    fixed_expenses = Column(Float, nullable=True)
    variable_expenses = Column(Float, nullable=True)
    total_savings = Column(Float, nullable=True)
    emergency_fund = Column(Float, nullable=True)
    monthly_savings_goal = Column(Float, nullable=True)

    # Perfil laboral
    income_type = Column(SAEnum(IncomeType), nullable=True)
    income_variability = Column(SAEnum(IncomeVariability), nullable=True)
    contract_type = Column(SAEnum(ContractType), nullable=True)
    job_seniority_months = Column(Integer, nullable=True)

    # Perfil de deudas
    monthly_debt_payments = Column(Float, nullable=True)
    total_debt = Column(Float, nullable=True)

    # Perfil de vivienda
    is_renting = Column(Boolean, default=False)
    monthly_rent = Column(Float, nullable=True)
    rent_mortgage_overlap_months = Column(Integer, default=0)

    # Perfil del hogar
    dependents = Column(Integer, default=0)

    analyses = relationship("PropertyAnalysis", back_populates="user")
