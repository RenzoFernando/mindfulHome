import React, { useState } from "react";
import "../styles/progress-bar.css";

const ProgressBar = ({ title, percentage, color, tooltip }) => {
    const [showTooltip, setShowTooltip] = useState(false);
    
    // percentage puede ser 0-1 o 0-100
    const normalizedPercentage = typeof percentage === 'number' && percentage <= 1 
        ? percentage * 100 
        : Math.min(100, Math.max(0, percentage));
    
    const displayPercentage = normalizedPercentage.toFixed(1);
    
    const getDefaultColor = (value) => {
        if (value < 30) return "#7ADE5D";
        if (value < 60) return "#ffc107";
        return "#dc3545";
    };
    
    const barColor = color || getDefaultColor(normalizedPercentage);

    return (
        <div 
            className="progress-bar-container"
            onMouseEnter={() => setShowTooltip(true)}
            onMouseLeave={() => setShowTooltip(false)}
        >
            <div className="progress-bar-header">
                <span className="progress-bar-title">
                    {title}
                    {tooltip && (
                        <span className="progress-bar-help-icon" title={tooltip}>ⓘ</span>
                    )}
                </span>
                <span className="progress-bar-percentage">{displayPercentage}%</span>
            </div>
            <div className="progress-bar-track">
                <div 
                    className="progress-bar-fill"
                    style={{ 
                        width: `${normalizedPercentage}%`,
                        backgroundColor: barColor
                    }}
                />
            </div>
            {showTooltip && tooltip && (
                <div className="progress-bar-tooltip">
                    {tooltip}
                </div>
            )}
        </div>
    );
};

export default ProgressBar;