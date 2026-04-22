from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey, JSON, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum


class InterestRateType(str, enum.Enum):
    FIJA = "FIJA"
    VARIABLE = "VARIABLE"


class RiskStatus(str, enum.Enum):
    SAFE = "SAFE"
    MODERATE = "MODERATE"
    RISKY = "RISKY"
    CRITICAL = "CRITICAL"


class PropertyAnalysis(Base):
    __tablename__ = "property_analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Property input
    property_price = Column(Float, nullable=False)
    down_payment = Column(Float, nullable=False)
    annual_interest_rate = Column(Float, nullable=False)
    interest_rate_type = Column(SAEnum(InterestRateType), nullable=False)
    loan_term_years = Column(Integer, nullable=False)

    # Computed results stored as JSON
    mortgage_result = Column(JSON, nullable=True)
    cashflow_result = Column(JSON, nullable=True)
    ratios_result = Column(JSON, nullable=True)
    llm_analysis = Column(JSON, nullable=True)

    status = Column(SAEnum(RiskStatus), nullable=True)

    user = relationship("User", back_populates="analyses")
