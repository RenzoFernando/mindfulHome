# app/simulation/scenarios/playground.py
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from app.schemas.analysis import PropertyInput

class PlaygroundModification(BaseModel):
    variable: str
    new_value: Any = None
    percentage_change: Optional[float] = None

class WhatIfPreset(BaseModel):
    name: str
    description: str
    modifications: List[PlaygroundModification]
    property_modifications: Optional[List[PlaygroundModification]] = None

class PlaygroundState(BaseModel):
    """Estado completo del playground incluyendo datos de usuario y propiedad"""
    user_data: Dict[str, Any]
    property_input: Optional[Dict[str, Any]] = None

class WhatIfLibrary:
    """Librería de presets rápidos"""
    
    @staticmethod
    def get_presets() -> List[WhatIfPreset]:
        return [
            WhatIfPreset(
                name="Pérdida de empleo",
                description="Simula una pérdida temporal de ingresos",
                modifications=[
                    PlaygroundModification(
                        variable="monthly_income", 
                        new_value=0,
                        percentage_change=-1.0
                    ),
                    PlaygroundModification(
                        variable="job_seniority_months", 
                        new_value=0,
                        percentage_change=None
                    )
                ],
                property_modifications=None
            ),
            WhatIfPreset(
                name="Aumento de tasas",
                description="Escenario con tasas de interés más altas",
                modifications=[],
                property_modifications=[
                    PlaygroundModification(
                        variable="annual_interest_rate", 
                        new_value=None,
                        percentage_change=0.02
                    )
                ]
            ),
            WhatIfPreset(
                name="Gastos imprevistos",
                description="Incremento temporal de gastos",
                modifications=[
                    PlaygroundModification(
                        variable="variable_expenses", 
                        new_value=None,
                        percentage_change=0.3
                    )
                ],
                property_modifications=None
            ),
            WhatIfPreset(
                name="Mejor ingreso",
                description="Escenario optimista de ingresos",
                modifications=[
                    PlaygroundModification(
                        variable="monthly_income", 
                        new_value=None,
                        percentage_change=0.2
                    )
                ],
                property_modifications=None
            ),
            WhatIfPreset(
                name="Comprar casa más cara",
                description="Aumenta el precio de la propiedad",
                modifications=[],
                property_modifications=[
                    PlaygroundModification(
                        variable="property_price", 
                        new_value=None,
                        percentage_change=0.25
                    )
                ]
            ),
            WhatIfPreset(
                name="Mejores condiciones hipoteca",
                description="Reduce la tasa de interés",
                modifications=[],
                property_modifications=[
                    PlaygroundModification(
                        variable="annual_interest_rate", 
                        new_value=None,
                        percentage_change=-0.02
                    )
                ]
            )
        ]

class PlaygroundManager:
    """Maneja modificaciones temporales de escenarios"""
    
    def __init__(self, user_data: Dict[str, Any], property_input: Optional[PropertyInput] = None):
        self.user_data = user_data
        self.property_input = property_input
        self.user_modifications: List[PlaygroundModification] = []
        self.property_modifications: List[PlaygroundModification] = []
        
    def apply_modification(self, mod: PlaygroundModification, is_property: bool = False):
        """Aplica una modificación (de usuario o de propiedad)"""
        if is_property:
            self.property_modifications.append(mod)
        else:
            self.user_modifications.append(mod)
    
    def get_current_scenario(self) -> PlaygroundState:
        """Retorna los datos actuales del playground con modificaciones aplicadas"""
        
        # Aplicar modificaciones a datos de usuario
        user_result = self.user_data.copy()
        for mod in self.user_modifications:
            if mod.percentage_change is not None and mod.new_value is None:
                original = user_result.get(mod.variable, 0)
                user_result[mod.variable] = original * (1 + mod.percentage_change)
            elif mod.new_value is not None:
                user_result[mod.variable] = mod.new_value
        
        # Aplicar modificaciones a property_input
        property_result = None
        if self.property_input:
            property_result = self.property_input.dict()
            for mod in self.property_modifications:
                if mod.percentage_change is not None and mod.new_value is None:
                    original = property_result.get(mod.variable, 0)
                    property_result[mod.variable] = original * (1 + mod.percentage_change)
                elif mod.new_value is not None:
                    property_result[mod.variable] = mod.new_value
        
        return PlaygroundState(
            user_data=user_result,
            property_input=property_result
        )
    
    def apply_preset(self, preset: WhatIfPreset):
        """Aplica un preset completo"""
        for mod in preset.modifications:
            self.apply_modification(mod, is_property=False)
        if preset.property_modifications:
            for mod in preset.property_modifications:
                self.apply_modification(mod, is_property=True)
    
    def reset_user_modifications(self):
        """Resetea solo las modificaciones de usuario"""
        self.user_modifications = []
    
    def reset_property_modifications(self):
        """Resetea solo las modificaciones de propiedad"""
        self.property_modifications = []
    
    def reset_all(self):
        """Resetea todas las modificaciones"""
        self.user_modifications = []
        self.property_modifications = []