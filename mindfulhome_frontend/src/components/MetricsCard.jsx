import React from "react";
import "../styles/metrics-card.css";

const MetricsCard = ({ title, metrics }) => {
    return (
        <div className="metrics-section">
            <div className="metrics-card-title">{title}</div>
            <div className="metrics-card">
                <div className="metrics-grid">
                    {metrics.map((metric, idx) => (
                        <div key={idx} className="metric-item">
                            <div className="metric-label">{metric.label}</div>
                            <div className="metric-value">{metric.value}</div>
                        </div>
                    ))}
                </div>
            </div>
        </div>

    );
};

export default MetricsCard;