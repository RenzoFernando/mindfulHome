import React, { useState, useEffect, useCallback } from "react";
import { Zap } from "lucide-react";
import Playground from "../components/Playground";
import SimulationHeader from "../components/SimulationHeader";
import ProbabilityBars from "../components/ProbabilityBars";
import MetricCard from "../components/MetricCard";
import TimelineChart from "../components/TimelineChart";
import SecondaryInsights from "../components/SecondaryInsights";
import { useUserData } from "../hooks/useUserData";
import { runSimulation } from "../services/simulation.service";
import "../styles/simulations.css";
import FolderCards from "../components/FolderCards"; 

const Simulations = () => {
    const { userData } = useUserData();
    const [simulationResults, setSimulationResults] = useState(null);
    const [isLoading, setIsLoading] = useState(false);

    // Función para ejecutar la simulación con los datos actuales
    const executeSimulation = useCallback(async (userDataParam, propertyDataParam = null) => {
        if (!userDataParam) return;
        
        setIsLoading(true);
        try {
            // Construir el objeto de overrides con los datos del usuario
            const overrides = {};
            
            // Campos a incluir del usuario
            const userFields = [
                'monthly_income', 'fixed_expenses', 'variable_expenses', 'total_savings',
                'emergency_fund', 'monthly_savings_goal', 'income_type', 'income_variability',
                'contract_type', 'job_seniority_months', 'monthly_debt_payments', 'total_debt',
                'is_renting', 'monthly_rent', 'rent_mortgage_overlap_months', 'dependents'
            ];
            
            userFields.forEach(field => {
                if (userDataParam[field] !== undefined && userDataParam[field] !== null) {
                    overrides[field] = userDataParam[field];
                }
            });
            
            // Configurar propiedad por defecto si no existe
            let propertyInput = propertyDataParam;
            if (!propertyInput) {
                propertyInput = {
                    property_price: 300000000,
                    down_payment: 60000000,
                    annual_interest_rate: 12.0,
                    interest_rate_type: "FIJA",
                    loan_term_years: 20
                };
            }
            
            // Preparar input para simulación
            const simulationInput = {
                overrides: overrides,
                property_input: propertyInput,
                simulation_months: 360,
                num_simulations: 100
            };
            
            console.log('Ejecutando simulación inicial con:', simulationInput);
            
            // Ejecutar simulación
            const results = await runSimulation(simulationInput);
            
            // Normalizar resultados
            let normalizedResults = results;
            if (results?.results) {
                normalizedResults = results.results;
            }
            
            setSimulationResults(normalizedResults);
        } catch (error) {
            console.error("Error en simulación inicial:", error);
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Ejecutar simulación cuando userData esté disponible
    useEffect(() => {
        if (userData) {
            executeSimulation(userData);
        }
    }, [userData, executeSimulation]);

    const handleSimulationUpdate = (results) => {
        console.log('=== Simulation Results Received ===');
        
        // Normalizar la estructura de datos
        let normalizedResults = results;
        
        // Si los datos están anidados en results.results, extraerlos
        if (results?.results) {
            console.log('Detectada estructura anidada, normalizando...');
            normalizedResults = results.results;
        }
        
        console.log('timeline length:', normalizedResults?.timeline?.length);
        console.log('timeline_events:', normalizedResults?.timeline_events);
        
        setSimulationResults(normalizedResults);
        setIsLoading(false);
    };

    // Extraer datos normalizados
    const results = simulationResults;
    
    const stabilityScore = results ? Math.round((results.stability_probability || 0) * 100) : 0;
    const mainInsight = results?.general_insights?.main_insight;
    const generalInsights = results?.general_insights;
    const secondaryInsights = results?.general_insights?.insights || [];
    
    // Extraer probabilidades
    const stabilityProbability = results?.stability_probability || 0;
    const liquidityShortfallProbability = results?.liquidity_shortfall_probability || 0;
    const financialStressProbability = results?.financial_stress_probability || 0;
    
    // Extraer métricas para las cards
    const resilienceScore = results ? Math.round(
        (results.stability_probability || 0) * 0.6 + 
        (1 - (results.financial_stress_probability || 0)) * 0.4
    ) * 100 : 0;
    
    const stressMetrics = results?.stress_metrics?.expected || {};
    const totalMonths = results?.simulation_months || 360;
    const stressExposure = Math.round(
        (stressMetrics.months_in_critical || 0) / totalMonths * 100
    );
    
    const recoveryLikelihood = results ? Math.round((1 - (results.financial_stress_probability || 0)) * 100) : 0;
    const emergencyMonths = Math.round(results?.expected_results?.emergency_months?.p50 || 0);
    
    const housingRatioRaw = (results?.expected_results?.housing_ratio?.p50 || 0) * 100;
    const housingRatio = Math.min(100, Math.max(0, Math.round(housingRatioRaw)));
    const housingRatioChart = Math.max(0, housingRatio);

    return (
        <div className="simulations-container">
            <div className="simulations-left">
                <div className="left-inner-column">
                    <SimulationHeader 
                        personality={results?.expected_case_narrative?.scenario_personality}
                        mainInsight={mainInsight}
                        stabilityScore={stabilityScore}
                        generalInsights={generalInsights}
                    />
                    
                    {/* Barras de probabilidad */}
                    <ProbabilityBars 
                        stabilityProbability={stabilityProbability}
                        liquidityShortfallProbability={liquidityShortfallProbability}
                        financialStressProbability={financialStressProbability}
                    />
                    
                    {/* Métricas en tarjetas */}
                    <div className="metrics-cards-container">
                        <MetricCard 
                            title="Capacidad de recuperación"
                            value={resilienceScore}
                            unit="%"
                            description="Mide tu capacidad para resistir y recuperarte de shocks financieros."
                            iconName="Shield"
                            iconColor="#7ADE5D"
                            backgroundColor="#f9f9f9"
                            chartData={{ percentage: resilienceScore }}
                            chartType="donut"
                        />
                        
                        <MetricCard 
                            title="Nivel de presión financiera"
                            value={stressExposure}
                            unit="%"
                            description="Porcentaje del tiempo total de simulación que pasarías en situación de estrés financiero crítico."
                            iconName="AlertTriangle"
                            iconColor="#ffc107"
                            backgroundColor="#f9f9f9"
                            chartData={{ percentage: stressExposure }}
                            chartType="donut"
                        />
                        
                        <MetricCard 
                            title="Probabilidad de recuperación"
                            value={recoveryLikelihood}
                            unit="%"
                            description="Probabilidad de recuperarte después de un período de estrés financiero. Un valor alto indica que incluso si enfrentas dificultades, es probable que tu situación mejore."
                            iconName="TrendingUp"
                            iconColor="#467599"
                            backgroundColor="#f9f9f9"
                            chartData={{ percentage: recoveryLikelihood }}
                            chartType="donut"
                        />

                        <MetricCard 
                            title="Carga de vivienda"
                            value={housingRatio}
                            unit="%"
                            description="Porcentaje de tus ingresos mensuales destinado al costo de vivienda (incluye renta o cuota hipotecaria). El límite recomendado es 30%."
                            iconName="Home"
                            iconColor="#77BABA"
                            backgroundColor="#f9f9f9"
                            chartData={{ percentage: housingRatioChart }}
                            chartType="donut"
                        />
                    </div>

                    <SecondaryInsights insights={secondaryInsights} />
                </div>

                <div className="right-inner-column">
                    {simulationResults ? (
                        <div className="results-container">
                            <TimelineChart 
                                timelineData={simulationResults.timeline || []}
                                events={simulationResults.timeline_events || []}
                                showComparison={false}
                            />
                            <FolderCards 
                                bestCase={simulationResults.best_case_narrative}
                                expectedCase={simulationResults.expected_case_narrative}
                                worstCase={simulationResults.worst_case_narrative}
                                timelineData={simulationResults.timeline || []}
                            />
                        </div>
                    ) : (
                        <div className="empty-results">
                            {isLoading ? (
                                <>
                                    <div className="loading-spinner"></div>
                                    <p>Cargando simulación inicial...</p>
                                </>
                            ) : (
                                <>
                                    <Zap size={48} strokeWidth={1.5} />
                                    <p>Ajusta las variables del panel derecho para ver los resultados</p>
                                </>
                            )}
                        </div>
                    )}
                </div>
            </div>

            <div className="simulations-right">
                <Playground 
                    userData={userData}
                    onSimulationUpdate={handleSimulationUpdate}
                    isLoading={isLoading}
                />
            </div>
        </div>
    );
};

export default Simulations;