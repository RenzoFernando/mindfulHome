from typing import List
from app.simulation.engine.month_simulator import MonthSimulator
from app.simulation.models.simulation_state import SimulationState
from app.simulation.models.rules import SimulationRules

class SingleSimulation:
    def __init__(self, rules: SimulationRules, initial_state: SimulationState, months: int):
        self.rules = rules
        self.initial_state = initial_state
        self.months = months
        self.simulator = MonthSimulator(rules)
        
    def run(self, seed: int = None) -> List[SimulationState]:
        """Ejecuta una simulación individual de varios meses"""
        states = [self.initial_state]
        current_state = self.initial_state
        
        for month in range(1, self.months + 1):
            next_state = self.simulator.transition(current_state, seed + month if seed else None)
            states.append(next_state)
            current_state = next_state
            
            # Si llega a estado crítico y no hay recuperación, continuar pero marcar
            if current_state.risk_status == "CRITICAL" and current_state.liquidity < -current_state.monthly_income:
                # Quiebra técnica, pero continuamos para ver recuperación
                pass
                
        return states