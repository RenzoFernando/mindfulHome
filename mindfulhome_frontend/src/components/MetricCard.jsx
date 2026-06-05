import React from 'react';
import Icon from './Icon';
import '../styles/metric-card.css';

const MetricCard = ({ 
    title, 
    value, 
    unit, 
    description, 
    iconName, 
    iconColor = '#467599',
    backgroundColor = '#f9f9f9',
    chartData = null,
    chartType = 'donut' // 'donut' or 'icon'
}) => {
    
    // Renderizar el gráfico circular (donut)
    const renderDonutChart = () => {
        if (!chartData) return null;
        
        const percentage = chartData.percentage || 0;
        const radius = 30;
        const circumference = 2 * Math.PI * radius;
        const offset = circumference - (percentage / 100) * circumference;
        
        return (
            <div className="metric-card-chart">
                <svg width="40" height="40" viewBox="0 0 80 80">
                    <circle
                        cx="40"
                        cy="40"
                        r={radius}
                        fill="none"
                        stroke="#e8e8e8"
                        strokeWidth="8"
                    />
                    <circle
                        cx="40"
                        cy="40"
                        r={radius}
                        fill="none"
                        stroke={iconColor}
                        strokeWidth="8"
                        strokeDasharray={circumference}
                        strokeDashoffset={offset}
                        strokeLinecap="round"
                        transform="rotate(-90 40 40)"
                        style={{ transition: 'stroke-dashoffset 0.3s ease' }}
                    />
                </svg>
            </div>
        );
    };
    
    return (
        <div className="metric-card" style={{ backgroundColor }}>
            <div className="metric-card-left">
                {chartType === 'donut' && chartData ? (
                    renderDonutChart()
                ) : (
                    <div className="metric-card-icon">
                        <Icon 
                            name={iconName}
                            size={28}
                            color={iconColor}
                            backgroundColor="white"
                            borderRadius={16}
                            padding={12}
                        />
                    </div>
                )}
            </div>
            
            <div className="metric-card-center">
                <h4 className="metric-card-title">{title}</h4>
                <p className="metric-card-description">{description}</p>
            </div>
            
            <div className="metric-card-right">
                <div className="metric-card-value">
                    {typeof value === 'number' ? value.toLocaleString("es-CO") : value}
                    {unit && <span className="metric-card-unit">{unit}</span>}
                </div>
            </div>
        </div>
    );
};

export default MetricCard;