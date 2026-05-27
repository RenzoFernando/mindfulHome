// components/SimulationHeader.jsx
import React from 'react';
import Icon from './Icon';
import '../styles/simulation-header.css';

// Derivar personalidad del main insight o del score
const derivePersonalityFromData = (stabilityScore, mainInsight) => {
    if (stabilityScore === 0 || stabilityScore < 20) return 'high_risk';
    if (stabilityScore < 40) return 'fragile';
    if (stabilityScore < 70) return 'volatile';
    if (stabilityScore >= 70) return 'resilient';
    return 'sustainable';
};

const getPersonalityIcon = (personality) => {
    const icons = {
        resilient: 'Shield',
        fragile: 'AlertTriangle',
        volatile: 'TrendingUp',
        sustainable: 'Leaf',
        high_risk: 'Flame'
    };
    return icons[personality] || 'TrendingUp';
};

const getPersonalityDisplayName = (personality) => {
    const names = {
        resilient: 'Resiliente',
        fragile: 'Frágil',
        volatile: 'Volátil',
        sustainable: 'Sostenible',
        high_risk: 'Alto riesgo'
    };
    return names[personality] || personality;
};

const SimulationHeader = ({ personality, mainInsight, stabilityScore, generalInsights }) => {
    // Usar generalInsights si está disponible, sino los props directos
    const effectiveMainInsight = generalInsights?.main_insight || mainInsight;
    const effectiveStabilityScore = stabilityScore !== undefined ? stabilityScore :
        (generalInsights?.stability_probability !== undefined ? Math.round(generalInsights.stability_probability * 100) : 0);

    // Derivar personalidad del score real
    const derivedPersonality = derivePersonalityFromData(effectiveStabilityScore, effectiveMainInsight);
    const displayPersonality = getPersonalityDisplayName(derivedPersonality);
    const iconName = getPersonalityIcon(derivedPersonality);

    const scoreColor = effectiveStabilityScore >= 70 ? '#7ADE5D' :
        effectiveStabilityScore >= 40 ? '#ffc107' : '#dc3545';

    const displayScore = !isNaN(effectiveStabilityScore) && effectiveStabilityScore !== undefined ?
        effectiveStabilityScore : '—';

    return (
        <div className="simulation-header">
            <div className="header-top">
                <div className="header-left">
                    <Icon
                        name={iconName}
                        size={24}
                        color="#467599"
                        backgroundColor="#f0f0f0"
                        borderRadius={12}
                        padding={10}
                    />
                    <h2 className="personality-title">
                        {displayPersonality}
                    </h2>
                </div>
                <div className="header-right">
                    <div className="stability-score">
                        <span className="score-number" style={{ color: scoreColor }}>
                            {displayScore}
                        </span>
                        <span className="score-max">/100</span>
                    </div>
                    <p className="score-label">Estabilidad financiera</p>
                </div>
            </div>
            <div className="header-bottom">
                <p className="main-insight">{effectiveMainInsight || 'Ajusta las variables para ver el análisis'}</p>
            </div>
        </div>
    );
};

export default SimulationHeader;