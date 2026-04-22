from pydantic import BaseModel, field_validator
from typing import Optional, Any
from app.models.analysis import InterestRateType, RiskStatus


class PropertyInput(BaseModel):
    property_price: float
    down_payment: float
    annual_interest_rate: float
    interest_rate_type: InterestRateType
    loan_term_years: int

    @field_validator("down_payment")
    @classmethod
    def down_payment_must_be_less_than_price(cls, v, info):
        if "property_price" in info.data and v >= info.data["property_price"]:
            raise ValueError("El pago inicial debe ser menor al precio de la propiedad")
        return v

    @field_validator("annual_interest_rate")
    @classmethod
    def rate_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("La tasa de interés debe ser positiva")
        return v

    @field_validator("loan_term_years")
    @classmethod
    def term_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("El plazo debe ser mayor a 0")
        return v


class MortgageResult(BaseModel):
    loan_amount: float
    monthly_rate: float
    num_payments: int
    monthly_payment: float
    total_paid: float
    total_interest: float


class CashflowResult(BaseModel):
    income: float
    expenses: float
    debt: float
    housing_cost: float
    liquidity: float
    liquidity_after_savings: float
    status: RiskStatus


class RatiosResult(BaseModel):
    mortgage_ratio: float
    debt_ratio: float
    housing_ratio: float
    emergency_months: float
    free_cash_flow_ratio: float
    discretionary_income_ratio: float


class AnalysisResponse(BaseModel):
    id: int
    status: Optional[RiskStatus] = None
    mortgage: Optional[Any] = None
    cashflow: Optional[Any] = None
    ratios: Optional[Any] = None
    llm_analysis: Optional[Any] = None

    class Config:
        from_attributes = True
