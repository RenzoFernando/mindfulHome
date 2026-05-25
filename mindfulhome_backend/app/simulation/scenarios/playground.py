from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class PlaygroundModification(BaseModel):
    variable: str
    new_value: Any
    percentage_change: Optional[float] = None

class WhatIfPreset(BaseModel):
    name: str
    description: str
    modifications: List[PlaygroundModification]
    icon: str

class WhatIfLibrary:
    """Librería de presets rápidos"""
    
    @staticmethod
    def get_presets() -> List[WhatIfPreset]:
        return [
            WhatIfPreset(
                name="Pérdida de empleo",
                description="Simula una pérdida temporal de ingresos",
                modifications=[
                    PlaygroundModification(variable="monthly_income", percentage_change=-1.0),
                    PlaygroundModification(variable="job_seniority_months", new_value=0)
                ]
            ),
            WhatIfPreset(
                name="Aumento de tasas",
                description="Escenario con tasas de interés más altas",
                modifications=[
                    PlaygroundModification(variable="annual_interest_rate", percentage_change=0.02)
                ]
            ),
            WhatIfPreset(
                name="Gastos imprevistos",
                description="Incremento temporal de gastos",
                modifications=[
                    PlaygroundModification(variable="variable_expenses", percentage_change=0.3)
                ],
            ),
            WhatIfPreset(
                name="Mejor ingreso",
                description="Escenario optimista de ingresos",
                modifications=[
                    PlaygroundModification(variable="monthly_income", percentage_change=0.2)
                ],
            )
        ]

class PlaygroundManager:
    """Maneja modificaciones temporales de escenarios"""
    
    def __init__(self, base_user_data: Dict[str, Any]):
        self.base_data = base_user_data
        self.modifications: List[PlaygroundModification] = []
        
    def apply_modification(self, mod: PlaygroundModification):
        self.modifications.append(mod)
        
    def get_current_scenario(self) -> Dict[str, Any]:
        """Retorna los datos del usuario con modificaciones aplicadas"""
        result = self.base_data.copy()
        
        for mod in self.modifications:
            if mod.percentage_change:
                original = result.get(mod.variable, 0)
                result[mod.variable] = original * (1 + mod.percentage_change)
            else:
                result[mod.variable] = mod.new_value
                
        return result
    
    def apply_preset(self, preset: WhatIfPreset):
        for mod in preset.modifications:
            self.apply_modification(mod)