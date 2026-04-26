import React from "react";
import "../styles/progress-bar.css";

const ProgressBar = ({ title, percentage, color }) => {
    const normalizedPercentage = Math.min(100, Math.max(0, percentage * 100));
    const displayPercentage = (percentage * 100).toFixed(1);
    
    const getDefaultColor = (value) => {
        if (value < 30) return "#7ADE5D";
        if (value < 60) return "#ffc107";
        return "#dc3545";
    };
    
    const barColor = color || getDefaultColor(normalizedPercentage);

    return (
        <div className="progress-bar-container">
            <div className="progress-bar-header">
                <span className="progress-bar-title">{title}</span>
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
        </div>
    );
};

export default ProgressBar;