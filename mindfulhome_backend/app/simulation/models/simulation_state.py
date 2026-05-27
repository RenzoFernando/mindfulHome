from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
from enum import Enum


class RiskStatus(str, Enum):
    SAFE = "SAFE"
    MODERATE = "MODERATE"
    RISKY = "RISKY"
    CRITICAL = "CRITICAL"


class SimulationState(BaseModel):
    """Estado financiero en un mes específico"""
    month: int
    date: date
    
    # Variables financieras
    monthly_income: float = 0.0
    fixed_expenses: float = 0.0
    variable_expenses: float = 0.0
    monthly_debt_payments: float = 0.0
    housing_cost: float = 0.0
    total_savings: float = 0.0
    emergency_fund: float = 0.0
    
    # Métricas calculadas
    liquidity: float = 0.0
    liquidity_after_savings: float = 0.0
    housing_ratio: float = 0.0
    debt_ratio: float = 0.0
    emergency_months: float = 0.0
    risk_status: RiskStatus = RiskStatus.MODERATE
    
    # Estado de cuenta
    has_emergency_usage: bool = False
    months_since_recovery: Optional[int] = None
    
    # Campos para manejo de vivienda y overlap
    is_renting: bool = False
    monthly_rent: float = 0.0
    rent_overlap_months_remaining: int = 0
    has_mortgage: bool = False
    base_mortgage_payment: float = 0.0
    base_monthly_rent: float = 0.0

    def calculate_metrics(self):
        """Calcula métricas basadas en el estado actual"""
        
        # Asegurar valores numéricos
        monthly_income = float(self.monthly_income or 0)
        fixed_expenses = float(self.fixed_expenses or 0)
        variable_expenses = float(self.variable_expenses or 0)
        monthly_debt_payments = float(self.monthly_debt_payments or 0)
        emergency_fund = float(self.emergency_fund or 0)
        
        # Calcular el housing cost real considerando overlap
        effective_housing_cost = self.housing_cost
        
        # Si hay overlap activo, usar hipoteca + renta
        if self.is_renting and self.rent_overlap_months_remaining > 0:
            effective_housing_cost = self.base_mortgage_payment + self.base_monthly_rent
        elif self.has_mortgage:
            effective_housing_cost = self.base_mortgage_payment
        
        # Calcular liquidez
        self.liquidity = monthly_income - (
            fixed_expenses + variable_expenses + 
            monthly_debt_payments + effective_housing_cost
        )
        self.liquidity_after_savings = self.liquidity
        
        # Calcular ratios
        if monthly_income > 0:
            self.housing_ratio = effective_housing_cost / monthly_income
            self.debt_ratio = monthly_debt_payments / monthly_income
        else:
            self.housing_ratio = 1.0 if effective_housing_cost > 0 else 0.0
            self.debt_ratio = 1.0 if monthly_debt_payments > 0 else 0.0
        
        # Calcular meses de emergencia
        base_expenses = fixed_expenses + variable_expenses
        if base_expenses > 0:
            self.emergency_months = emergency_fund / base_expenses
        else:
            self.emergency_months = 0
        
        # Clasificar riesgo
        if monthly_income > 0:
            liquidity_ratio = self.liquidity / monthly_income
            if liquidity_ratio > 0.20:
                self.risk_status = RiskStatus.SAFE
            elif liquidity_ratio > 0.05:
                self.risk_status = RiskStatus.MODERATE
            elif liquidity_ratio > 0:
                self.risk_status = RiskStatus.RISKY
            else:
                self.risk_status = RiskStatus.CRITICAL
        else:
            if self.liquidity > 0:
                self.risk_status = RiskStatus.RISKY
            else:
                self.risk_status = RiskStatus.CRITICAL