import React from 'react';
import Icon from './Icon';
import '../styles/secondary-insights.css';

const SecondaryInsights = ({ insights = [] }) => {
    if (!insights || insights.length === 0) {
        return null;
    }

    const getSeverityIcon = (severity) => {
        switch(severity) {
            case 'positive':
                return { name: 'ThumbsUp', color: '#7ADE5D' };
            case 'warning':
                return { name: 'AlertTriangle', color: '#ff6b6b' };
            default:
                return { name: 'Info', color: '#ffc107' };
        }
    };

    const getSeverityClass = (severity) => {
        switch(severity) {
            case 'positive': return 'insight-positive';
            case 'warning': return 'insight-warning';
            default: return 'insight-neutral';
        }
    };

    return (
        <div className="secondary-insights-container">
            <div className="secondary-insights-header">
                <Icon name="Lightbulb" size={18} color="#666" backgroundColor='transparent' padding={0}/>
                <span>Análisis detallado</span>
            </div>
            <div className="secondary-insights-grid">
                {insights.map((insight, index) => {
                    const icon = getSeverityIcon(insight.severity);
                    return (
                        <div key={index} className={`insight-card ${getSeverityClass(insight.severity)}`}>
                            <div className="insight-content">
                                <div className="insight-title">{insight.title}</div>
                                <div className="insight-description">{insight.description}</div>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default SecondaryInsights;