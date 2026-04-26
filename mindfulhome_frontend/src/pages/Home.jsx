import React, { useState, useEffect } from "react";
import { useSelector, useDispatch } from "react-redux";
import { Home as HomeIcon, Plus, TrendingUp, TrendingDown, AlertCircle, ChevronRight, Ban, AlertTriangle, Shield, Clock, DollarSign, Home as HomeIcon2, Activity, Smile, Meh, Frown } from "lucide-react";
import { getAnalyses } from "../services/analysis.service";
import PropertyModal from "../components/PropertyModal";
import "../styles/home.css";
import TabsSection from "../components/TabsSection";
import MetricsCard from "../components/MetricsCard";
import DonutChart from "../components/DonutChart";
import "../styles/donut-chart.css";
import { useUserData } from "../hooks/useUserData";
import RatiosSection from "../components/RatiosSection";

const getProblemIcon = (index) => {
    const icons = [AlertTriangle, DollarSign, Clock, Activity, Shield, HomeIcon2, TrendingDown, AlertCircle, Smile, Meh, Frown
    ];
    return icons[index % icons.length];
};

export default function Home() {
    const dispatch = useDispatch();
    const { userData, refetch: refetchUserData } = useUserData();
    const [analysis, setAnalysis] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const token = useSelector(state => state.user.token);

    useEffect(() => {
        loadLatestAnalysis();
    }, []);

    const refreshAllData = async () => {
        await refetchUserData();
        await loadLatestAnalysis();
    };

    const loadLatestAnalysis = async () => {
        setLoading(true);

        try {
            await refetchUserData();

            await new Promise(resolve => setTimeout(resolve, 500));

            const analyses = await getAnalyses();

            if (analyses && analyses.length > 0) {
                const sortedAnalyses = [...analyses].sort((a, b) => b.id - a.id);
                const latestAnalysis = sortedAnalyses[0];

                const llmData = latestAnalysis.llm_analysis || {};
                const globalAnalysis = llmData.global_analysis || {};
                const insights = llmData.insights || [];
                const risks = llmData.risks || [];
                const recommendations = llmData.recommendations || [];
                const uiHints = llmData.uiHints || {};

                const enrichedAnalysis = {
                    ...latestAnalysis,
                    global_analysis: globalAnalysis,
                    insights: insights,
                    risks: risks,
                    recommendations: recommendations,
                    uiHints: uiHints
                };

                setAnalysis(enrichedAnalysis);
            } else {
                setAnalysis(null);
            }
        } catch (err) {
            console.error("[DEBUG Home] Error:", err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleAnalysisSuccess = async (newAnalysis) => {
        const llmData = newAnalysis.llm_analysis || {};
        const globalAnalysis = llmData.global_analysis || {};
        const insights = llmData.insights || [];
        const risks = llmData.risks || [];
        const recommendations = llmData.recommendations || [];
        const uiHints = llmData.uiHints || {};

        const enrichedAnalysis = {
            ...newAnalysis,
            global_analysis: globalAnalysis,
            insights: insights,
            risks: risks,
            recommendations: recommendations,
            uiHints: uiHints
        };

        setAnalysis(enrichedAnalysis);

        await refetchUserData();

        setTimeout(async () => {
            await loadLatestAnalysis();
        }, 1000);
    };

    const getScoreColor = (score) => {
        if (score === null || score === undefined) return "#ccc";
        if (score < 40) return "#dc3545";
        if (score < 70) return "#ffc107";
        return "#7ADE5D";
    };

    const getBoxBorderColor = (score) => {
        if (score === null || score === undefined) return "#e0e0e0";
        if (score < 40) return "#ffebee";
        if (score < 70) return "#fff9e6";
        return "#e8f5e9";
    };

    const getStatusText = (score) => {
        if (score === null || score === undefined) return "Sin análisis";
        if (score < 40) return "Riesgo crítico";
        if (score < 70) return "Riesgo moderado";
        return "Buena salud financiera";
    };

    if (loading) {
        return (
            <div className="home-container full-center">
                <div className="empty-state">
                    <div>Cargando análisis...</div>
                </div>
            </div>
        );
    }

    if (!analysis && !loading) {
        return (
            <>
                <div className="home-container full-center">
                    <div className="empty-state">
                        <Ban size={80} strokeWidth={1.5} className="empty-icon" />
                        <h2>No hay propiedades analizadas</h2>
                        <p>Comienza analizando tu primera propiedad para obtener recomendaciones personalizadas</p>
                        <button className="add-btn" onClick={() => setIsModalOpen(true)}>
                            <Plus size={20} />
                            <span>Añadir propiedad</span>
                        </button>
                    </div>
                </div>
                <PropertyModal
                    isOpen={isModalOpen}
                    onClose={() => setIsModalOpen(false)}
                    onSuccess={handleAnalysisSuccess}
                />
            </>
        );
    }

    const getStatusEmoji = (score) => {
        if (score === null || score === undefined) return <Meh size={20} />;
        if (score < 40) return <Frown size={20} />;
        if (score < 70) return <Meh size={20} />;
        return <Smile size={20} />;
    };

    // Extraer los valores para mostrarlos
    const financialScore = analysis?.global_analysis?.financial_health_score;
    const mainProblem = analysis?.global_analysis?.main_problem;
    const secondaryProblems = analysis?.global_analysis?.secondary_problems || [];
    const scoreColor = getScoreColor(financialScore);
    const boxBorderColor = getBoxBorderColor(financialScore);
    const statusText = getStatusText(financialScore);

    // Formatear valores monetarios
    const formatCurrency = (value) => {
        if (value === undefined || value === null) return "N/A";
        return new Intl.NumberFormat('es-CO', {
            style: 'currency',
            currency: 'COP',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(value);
    };

    // Formatear porcentajes
    const formatPercentage = (value) => {
        if (value === undefined || value === null) return "N/A";
        return `${value}%`;
    };

    // Formatear años
    const formatYears = (value) => {
        if (value === undefined || value === null) return "N/A";
        return `${value} años`;
    };

    const getCashflowMetrics = (analysis) => {
        const cashflow = analysis?.cashflow || {};
        return [
            { label: "Ingresos", value: formatCurrency(cashflow.income) },
            { label: "Gastos", value: formatCurrency(cashflow.expenses) },
            { label: "Deudas", value: formatCurrency(cashflow.debt) },
            { label: "Costo vivienda", value: formatCurrency(cashflow.housing_cost) }
        ];
    };

    const getPropertyMetrics = (analysis) => {
        return [
            { label: "Precio propiedad", value: formatCurrency(analysis?.property_price) },
            { label: "Cuota inicial", value: formatCurrency(analysis?.down_payment) },
            { label: "Tasa interés", value: formatPercentage(analysis?.annual_interest_rate) },
            { label: "Plazo", value: formatYears(analysis?.loan_term_years) }
        ];
    };

    const getMortgageMetrics = (analysis) => {
        const mortgage = analysis?.mortgage || {};
        return [
            { label: "Monto préstamo", value: formatCurrency(mortgage.loan_amount) },
            { label: "Cuota mensual", value: formatCurrency(mortgage.monthly_payment) },
            { label: "Total a pagar", value: formatCurrency(mortgage.total_paid) },
            { label: "Intereses totales", value: formatCurrency(mortgage.total_interest) }
        ];
    };

    const prepareChartData = (analysis) => {
        if (!analysis) return [];

        const cashflow = analysis.cashflow || {};
        const mortgage = analysis.mortgage || {};

        // Datos importantes para el gráfico
        const chartData = [
            {
                name: "Ingresos",
                value: cashflow.income || 0,
                color: "#7ADE5D"
            },
            {
                name: "Gastos",
                value: cashflow.expenses || 0,
                color: "#dc3545"
            },
            {
                name: "Deudas",
                value: cashflow.debt || 0,
                color: "#ffc107"
            },
            {
                name: "Costo vivienda",
                value: cashflow.housing_cost || 0,
                color: "#467599"
            },
            {
                name: "Cuota hipoteca",
                value: mortgage.monthly_payment || 0,
                color: "#9ed8d8"
            }
        ];

        return chartData.filter(item => item.value > 0);
    };

    // Preparar el total para mostrar en el centro
    const getTotalAmount = (analysis) => {
        const cashflow = analysis?.cashflow || {};
        const mortgage = analysis?.mortgage || {};

        const total = (cashflow.income || 0) +
            (cashflow.expenses || 0) +
            (cashflow.debt || 0) +
            (cashflow.housing_cost || 0) +
            (mortgage.monthly_payment || 0);

        return formatCurrency(total);
    };

    const chartData = prepareChartData(analysis);
    const totalAmount = getTotalAmount(analysis);

    const getLiquidityData = (analysis) => {
        const cashflow = analysis?.cashflow || {};
        return [
            {
                title: "Liquidez",
                value: formatCurrency(cashflow.liquidity),
                icon: DollarSign,
                color: "#28a745"
            },
            {
                title: "Liquidez después de ahorros",
                value: formatCurrency(cashflow.liquidity_after_savings),
                icon: TrendingUp,
                color: cashflow.liquidity_after_savings >= 0 ? "#28a745" : "#dc3545"
            }
        ];
    };

    const liquidityData = getLiquidityData(analysis);


    return (
        <>
            <div className="home-container">
                {/* Lado izquierdo */}
                <div className="home-left">
                    <div className="top-rectangle" style={{ backgroundColor: 'white' }}>
                        <div className="top-rectangle-grid">
                            <div className="grid-col-left">
                                <div className="status-indicator">
                                    <div className="status-emoji" style={{ color: scoreColor }}>
                                        {getStatusEmoji(financialScore)}
                                    </div>
                                    <span className="status-text">{statusText}</span>
                                </div>

                                <div className="main-problem-text">
                                    <p className="problem-label">Principal hallazgo</p>
                                    <h3 className="problem-description">
                                        {mainProblem || "No hay problema principal identificado"}
                                    </h3>
                                </div>

                                <div className="analyze-button-container">
                                    <button className="analyze-property-btn" onClick={() => setIsModalOpen(true)}>
                                        <Plus size={20} />
                                        <span>Analizar otra propiedad</span>
                                    </button>
                                </div>
                            </div>

                            <div className="grid-col-right">
                                <div className="financial-score">
                                    <div className="score-value" style={{ color: scoreColor }}>
                                        {financialScore !== undefined ? financialScore : "N/A"}
                                        <span className="score-max">/100</span>
                                    </div>
                                    <p className="score-label">Puntuación financiera</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Problemas secundarios */}
                    {secondaryProblems.length > 0 && (
                        <div className="secondary-problems-container">
                            <div className="secondary-problems-scroll">
                                {liquidityData.map((item, idx) => (
                                    <div key={`liquidity-${idx}`} className="liquidity-card">
                                        <div className="secondary-problem-header">
                                            <div className="liquidity-icon-circle" style={{ backgroundColor: item.color === "#28a745" ? "#e8f5e9" : "#ffebee" }}>
                                                <item.icon strokeWidth={2.5} style={{ color: item.color }} />
                                            </div>
                                            <p className="liquidity-title">{item.title}</p>
                                        </div>
                                        <p className="liquidity-value">{item.value}</p>
                                    </div>
                                ))}

                                {secondaryProblems.map((problem, idx) => {
                                    const IconComponent = getProblemIcon(idx);
                                    return (
                                        <div key={idx} className="secondary-problem-card">
                                            <div className="secondary-problem-header">
                                                <div className="problem-icon-circle">
                                                    <IconComponent strokeWidth={5} />
                                                </div>
                                                <p className="problem-number">Problema #{idx + 1}</p>
                                            </div>
                                            <p className="problem-description-text">{problem}</p>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    )}
                    <div className="metrics-grid-container">
                        <MetricsCard
                            title="Detalles de la propiedad"
                            metrics={getPropertyMetrics(analysis)}
                        />
                        <MetricsCard
                            title="Detalles de hipoteca"
                            metrics={getMortgageMetrics(analysis)}
                        />
                    </div>
                    <TabsSection
                        insights={analysis?.insights || []}
                        risks={analysis?.risks || []}
                        recommendations={analysis?.recommendations || []}
                    />
                </div>

                {/* Lado derecho */}
                <div className="home-right">

                    <MetricsCard
                        title="Flujo de Caja"
                        metrics={getCashflowMetrics(analysis)}
                    />
                    <DonutChart
                        data={chartData}
                        title="Distribución Financiera"
                        centerLabel={totalAmount}
                    />

                    <RatiosSection ratios={analysis?.ratios} />
                </div>
            </div>
            <PropertyModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onSuccess={handleAnalysisSuccess}
            />
        </>
    );
}