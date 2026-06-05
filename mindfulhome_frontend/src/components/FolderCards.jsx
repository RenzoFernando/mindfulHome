import React, { useState } from 'react';
import Icon from './Icon';
import MetricsCard from './MetricsCard';
import { LineChart, Line, XAxis, ResponsiveContainer } from 'recharts';
import '../styles/folder-cards.css';

const FolderCards = ({ bestCase, expectedCase, worstCase, timelineData = [] }) => {
    const [expandedCard, setExpandedCard] = useState(null);

    const getScoreForCase = (caseData) => {
        if (!caseData) return { value: 0, label: 'Sin datos' };
        
        const liquidity = caseData.top_metrics?.find(m => m.metric === 'Liquidez')?.value || 0;
        const housingRatio = caseData.top_metrics?.find(m => m.metric === 'Ratio vivienda')?.value || 1;
        
        let score = 0;
        if (liquidity > 0) score += 50;
        if (housingRatio < 0.3) score += 50;
        else if (housingRatio < 0.4) score += 30;
        else score += 10;
        
        return { value: score, label: 'Puntaje' };
    };

    const getDiagnosticTitle = (caseData) => {
        return caseData?.title || 'Sin diagnóstico';
    };

    const formatMetricValue = (metric) => {
        const value = metric.value || 0;
        
        switch(metric.metric) {
            case 'Ratio vivienda':
                return `${Math.round(value * 100)}%`;
            case 'Estabilidad':
            case 'Recuperación':
            case 'Estrés':
            case 'Volatilidad':
                return `${Math.round(value)}%`;
            default:
                return metric.unit === 'COP' 
                    ? `$${Math.round(value).toLocaleString("es-CO")}`
                    : `${Math.round(value)}${metric.unit === '%' ? '%' : ''}`;
        }
    };

    const getTopMetricsForCard = (caseData) => {
        if (!caseData?.top_metrics) return [];
        
        const allowedMetrics = ['Ratio vivienda', 'Estabilidad', 'Recuperación', 'Estrés', 'Volatilidad'];
        
        return caseData.top_metrics
            .filter(metric => allowedMetrics.includes(metric.metric))
            .map(metric => ({
                label: metric.metric,
                value: formatMetricValue(metric)
            }));
    };

    const getLiquidityData = (timeline) => {
        if (!timeline || timeline.length === 0) return [];
        return timeline.slice(0, 60).map(point => ({
            month: point.month,
            liquidity: Math.round(point.liquidity?.p50 || 0) // Redondear liquidez
        }));
    };

    const cards = [
        {
            id: 'best',
            type: 'best',
            data: bestCase,
            icon: 'TrendingUp',
            color: '#7ADE5D',
            bgGradient: '#a4e093',
            score: getScoreForCase(bestCase),
            diagnostic: getDiagnosticTitle(bestCase),
            topMetrics: getTopMetricsForCard(bestCase)
        },
        {
            id: 'expected',
            type: 'expected',
            data: expectedCase,
            icon: 'Target',
            color: '#467599',
            bgGradient: '#a4c8e6',
            score: getScoreForCase(expectedCase),
            diagnostic: getDiagnosticTitle(expectedCase),
            topMetrics: getTopMetricsForCard(expectedCase)
        },
        {
            id: 'worst',
            type: 'worst',
            data: worstCase,
            icon: 'AlertTriangle',
            color: '#ff6b6b',
            bgGradient: '#facfcf',
            score: getScoreForCase(worstCase),
            diagnostic: getDiagnosticTitle(worstCase),
            topMetrics: getTopMetricsForCard(worstCase)
        }
    ];

    const handleToggle = (cardId) => {
        if (expandedCard === cardId) {
            setExpandedCard(null);
        } else {
            setExpandedCard(cardId);
        }
    };

    const liquidityData = getLiquidityData(timelineData);

    return (
        <div className="folder-cards-container">
            {cards.map((card) => (
                <div 
                    key={card.id}
                    className={`folder-card ${expandedCard === card.id ? 'expanded' : 'collapsed'}`}
                    onClick={() => handleToggle(card.id)}
                >
                    <div className="folder-card-inner" style={{ background: card.bgGradient }}>
                        {/* Header */}
                        <div className="folder-header">
                            <div className="folder-header-left">
                                <div className="folder-icon">
                                    <Icon name={card.icon} size={16} color="#696969" />
                                </div>
                                <div className="folder-header-text">
                                    <div className="folder-type-label">
                                        {card.id === 'best' ? 'Mejor Escenario' : card.id === 'expected' ? 'Escenario Esperado' : 'Peor Escenario'}
                                    </div>
                                    <div className="folder-diagnostic">{card.diagnostic}</div>
                                </div>
                            </div>
                            <div className="folder-header-right">
                                <div className="folder-score">{card.score.value}</div>
                                <div className="folder-score-unit">%</div>
                            </div>
                        </div>
                        
                        {/* Contenido */}
                        <div className="folder-content">
                            <div className="folder-content-inner">
                                {expandedCard === card.id ? (
                                    <div className="folder-expanded">
                                        {/* Top metrics usando MetricsCard */}
                                        {card.topMetrics.length > 0 && (
                                            <MetricsCard 
                                                metrics={card.topMetrics}
                                            />
                                        )}
                                        
                                        {/* Gráfico de liquidez */}
                                        {liquidityData.length > 0 && (
                                            <div className="liquidity-chart-section">
                                                <div className="chart-header">
                                                    <span>Trayectoria de liquidez</span>
                                                </div>
                                                <ResponsiveContainer width="100%" height={80}>
                                                    <LineChart data={liquidityData}>
                                                        <XAxis dataKey="month" hide />
                                                        <Line 
                                                            type="monotone" 
                                                            dataKey="liquidity" 
                                                            stroke={card.color} 
                                                            strokeWidth={3}
                                                            dot={false}
                                                            isAnimationActive={false}
                                                        />
                                                    </LineChart>
                                                </ResponsiveContainer>
                                            </div>
                                        )}
                                        
                                        {/* Resumen del caso */}
                                        {card.data?.summary && (
                                            <div className="case-summary">
                                                <p>{card.data.summary}</p>
                                            </div>
                                        )}
                                        
                                        {/* Riesgos y oportunidades */}
                                        {card.data?.risks?.length > 0 && (
                                            <div className="risks-section">
                                                <div className="section-subtitle">Riesgos</div>
                                                {card.data.risks.map((risk, idx) => (
                                                    <div key={idx} className="risk-item">
                                                        <Icon name="AlertCircle" size={15} color="#696969" backgroundColor='transparent' padding={2}/>
                                                        <span>{risk.description}</span>
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                        
                                        {card.data?.opportunities?.length > 0 && (
                                            <div className="opportunities-section">
                                                <div className="section-subtitle">Oportunidades</div>
                                                {card.data.opportunities.map((opp, idx) => (
                                                    <div key={idx} className="opportunity-item">
                                                        <Icon name="Zap" size={15} color="#696969" backgroundColor='transparent' padding={2}/>
                                                        <span>{opp.description}</span>
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                ) : (
                                    <div className="folder-collapsed">
                                        <div className="folder-preview">
                                            <Icon name="Eye" size={20} color="#999" />
                                            <p className="preview-text">Haz clic para expandir</p>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            ))}
        </div>
    );
};

export default FolderCards;