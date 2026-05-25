# app/simulation/models/simulation_state.py
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
    monthly_income: float
    fixed_expenses: float
    variable_expenses: float
    monthly_debt_payments: float
    housing_cost: float
    total_savings: float
    emergency_fund: float
    
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
    
    def calculate_metrics(self):
        """Calcula métricas basadas en el estado actual"""
        # Calcular liquidez básica
        self.liquidity = self.monthly_income - (
            self.fixed_expenses + self.variable_expenses + 
            self.monthly_debt_payments + self.housing_cost
        )
        
        if self.monthly_income > 0:
            self.housing_ratio = self.housing_cost / self.monthly_income
            self.debt_ratio = self.monthly_debt_payments / self.monthly_income
        else:
            self.housing_ratio = 1.0 if self.housing_cost > 0 else 0.0
            self.debt_ratio = 1.0 if self.monthly_debt_payments > 0 else 0.0
        
        total_expenses = self.fixed_expenses + self.variable_expenses
        if total_expenses > 0:
            self.emergency_months = self.emergency_fund / total_expenses
        else:
            self.emergency_months = 0
        
        if self.monthly_income > 0:
            liquidity_ratio = self.liquidity / self.monthly_income
            if liquidity_ratio > 0.20:
                self.risk_status = RiskStatus.SAFE
            elif liquidity_ratio > 0.05:
                self.risk_status = RiskStatus.MODERATE
            elif liquidity_ratio > 0:
                self.risk_status = RiskStatus.RISKY
            else:
                self.risk_status = RiskStatus.CRITICAL
        else:
            # Sin ingresos, clasificar según liquidez absoluta
            if self.liquidity > 0:
                self.risk_status = RiskStatus.RISKY
            else:
                self.risk_status = RiskStatus.CRITICAL