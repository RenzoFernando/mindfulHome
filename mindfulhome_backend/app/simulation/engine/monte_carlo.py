from typing import List, Dict, Any
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.simulation.engine.single_simulation import SingleSimulation
from app.simulation.models.simulation_state import SimulationState
from app.simulation.models.rules import SimulationRules

class MonteCarloEngine:
    def __init__(self, rules: SimulationRules, initial_state: SimulationState, num_simulations: int, months: int):
        self.rules = rules
        self.initial_state = initial_state
        self.num_simulations = num_simulations
        self.months = months
        
    def run(self, parallel: bool = True) -> List[List[SimulationState]]:
        """Ejecuta múltiples simulaciones en paralelo"""
        all_simulations = []
        
        if parallel:
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = []
                for i in range(self.num_simulations):
                    sim = SingleSimulation(self.rules, self.initial_state.copy(deep=True), self.months)
                    futures.append(executor.submit(sim.run, seed=i))
                
                for future in as_completed(futures):
                    all_simulations.append(future.result())
        else:
            for i in range(self.num_simulations):
                sim = SingleSimulation(self.rules, self.initial_state.copy(deep=True), self.months)
                all_simulations.append(sim.run(seed=i))
                
        return all_simulations