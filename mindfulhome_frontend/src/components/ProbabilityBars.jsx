import React from 'react';
import ProgressBar from './ProgressBar';
import '../styles/probability-bars.css';

const ProbabilityBars = ({ 
    stabilityProbability = 0, 
    liquidityShortfallProbability = 0, 
    financialStressProbability = 0 
}) => {
    // Tooltips explicativos
    const tooltips = {
        stability: "Porcentaje de simulaciones donde tus finanzas se mantienen estables. Un valor alto (>70%) indica buena salud financiera.",
        liquidity: "Porcentaje de simulaciones donde podrías quedarte sin liquidez (gastos mayores a ingresos). Un valor bajo (<20%) es deseable.",
        financialStress: "Porcentaje de simulaciones donde entras en estrés financiero crítico (deuda insostenible). Idealmente debe ser lo más bajo posible (<10%)."
    };
    
    return (
        <div className="probability-bars-container">
            <div className="probability-bars-list">
                <ProgressBar 
                    title="Estabilidad financiera"
                    percentage={stabilityProbability}
                    color="#7ADE5D"
                    tooltip={tooltips.stability}
                />
                
                <ProgressBar 
                    title="Déficit de liquidez"
                    percentage={liquidityShortfallProbability}
                    color="#ffc107"
                    tooltip={tooltips.liquidity}
                />
                
                <ProgressBar 
                    title="Estrés financiero"
                    percentage={financialStressProbability}
                    color="#dc3545"
                    tooltip={tooltips.financialStress}
                />
            </div>
        </div>
    );
};

export default ProbabilityBars;