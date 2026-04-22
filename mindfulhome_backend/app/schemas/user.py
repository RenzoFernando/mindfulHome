from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models.user import IncomeType, IncomeVariability, ContractType


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class FinancialProfile(BaseModel):
    monthly_income: Optional[float] = None
    fixed_expenses: Optional[float] = None
    variable_expenses: Optional[float] = None
    total_savings: Optional[float] = None
    emergency_fund: Optional[float] = None
    monthly_savings_goal: Optional[float] = None


class LaborProfile(BaseModel):
    income_type: Optional[IncomeType] = None
    income_variability: Optional[IncomeVariability] = None
    contract_type: Optional[ContractType] = None
    job_seniority_months: Optional[int] = None


class DebtProfile(BaseModel):
    monthly_debt_payments: Optional[float] = None
    total_debt: Optional[float] = None


class HousingProfile(BaseModel):
    is_renting: Optional[bool] = None
    monthly_rent: Optional[float] = None
    rent_mortgage_overlap_months: Optional[int] = None


class HouseholdProfile(BaseModel):
    dependents: Optional[int] = None


class UserProfileUpdate(BaseModel):
    financial: Optional[FinancialProfile] = None
    labor: Optional[LaborProfile] = None
    debt: Optional[DebtProfile] = None
    housing: Optional[HousingProfile] = None
    household: Optional[HouseholdProfile] = None


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    monthly_income: Optional[float] = None
    fixed_expenses: Optional[float] = None
    variable_expenses: Optional[float] = None
    total_savings: Optional[float] = None
    emergency_fund: Optional[float] = None
    monthly_savings_goal: Optional[float] = None
    income_type: Optional[IncomeType] = None
    income_variability: Optional[IncomeVariability] = None
    contract_type: Optional[ContractType] = None
    job_seniority_months: Optional[int] = None
    monthly_debt_payments: Optional[float] = None
    total_debt: Optional[float] = None
    is_renting: Optional[bool] = None
    monthly_rent: Optional[float] = None
    rent_mortgage_overlap_months: Optional[int] = None
    dependents: Optional[int] = None

    class Config:
        from_attributes = True
