import React, { useState } from "react";
import {
    Lightbulb,
    AlertTriangle,
    TrendingUp,
    ChevronDown,
    ChevronUp,
    Shield,
    Target
} from "lucide-react";
import "../styles/tabs-section.css";

const TabsSection = ({ insights, risks, recommendations }) => {
    const [activeTab, setActiveTab] = useState("analysis");
    const [openCards, setOpenCards] = useState({});

    const toggleCard = (id, type) => {
        // Solo permitir toggle para análisis
        if (type === "analysis") {
            const key = `${type}-${id}`;
            setOpenCards(prev => ({ ...prev, [key]: !prev[key] }));
        }
    };

    const tabs = [
        { id: "analysis", label: "Análisis", icon: Lightbulb, count: insights?.length || 0 },
        { id: "risks", label: "Riesgos", icon: AlertTriangle, count: risks?.length || 0 },
        { id: "recommendations", label: "Recomendaciones", icon: TrendingUp, count: recommendations?.length || 0 }
    ];

    const getCardContent = (item, type) => {
        if (type === "analysis") {
            return {
                title: item.label,
                icon: Lightbulb,
                severity: item.severity,
                details: (
                    <>
                        <p className="card-detail"><strong>{item.interpretation?.what_it_means}</strong></p>
                        <p className="card-detail">{item.interpretation?.why_it_matters}. {item.interpretation.context}</p>
                    </>
                )
            };
        } else if (type === "risks") {
            return {
                title: item.type,
                icon: AlertTriangle,
                urgency: item.urgency,
                details: (
                    <p className="card-detail">{item.explanation}</p>
                )
            };
        } else {
            return {
                title: item.action,
                icon: TrendingUp,
                priority: item.priority,
                details: (
                    <p className="card-detail">{item.reason}</p>
                )
            };
        }
    };

    const renderContent = () => {
        let items = [];
        let type = activeTab;

        if (activeTab === "analysis") items = insights || [];
        else if (activeTab === "risks") items = risks || [];
        else items = recommendations || [];

        if (items.length === 0) {
            return (
                <div className="empty-tab">
                    <p>No hay {activeTab === "analysis" ? "análisis" : activeTab === "risks" ? "riesgos" : "recomendaciones"} disponibles</p>
                </div>
            );
        }

        return items.map((item, idx) => {
            const content = getCardContent(item, activeTab);
            const IconComponent = content.icon;
            
            if (activeTab === "analysis") {
                const isOpen = openCards[`analysis-${idx}`] || false;
                return (
                    <div key={idx} className="collapsible-card">
                        <div className="card-header" onClick={() => toggleCard(idx, "analysis")}>
                            <div className="card-header-left">
                                <div className={`card-icon-circle severity-${content.severity?.toLowerCase() || 'info'}`}>
                                    <IconComponent size={20} />
                                </div>
                                <div className="card-title">
                                    <h4>{content.title}</h4>
                                </div>
                            </div>
                            <div className="card-header-right">
                                {isOpen ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                            </div>
                        </div>
                        {isOpen && (
                            <div className="card-body">
                                {content.details}
                            </div>
                        )}
                    </div>
                );
            } 
            
            else if (activeTab === "risks") {
                return (
                    <div key={idx} className="static-card">
                        <div className="card-header-static">
                            <div className="card-header-left">
                                <div className={`card-icon-circle urgency-${content.urgency || 'medium'}`}>
                                    <IconComponent size={20} />
                                </div>
                                <div className="card-title">
                                    <h4>{content.title}</h4>
                            {content.details}

                                </div>
                            </div>
                        </div>
                    </div>
                );
            }
            
            else {
                return (
                    <div key={idx} className="static-card">
                        <div className="card-header-static">
                            <div className="card-header-left">
                                <div className="card-icon-circle">
                                    <IconComponent size={20} />
                                </div>
                                <div className="card-title">
                                    <h4>{content.title}</h4>
                            {content.details}
                                </div>
                            </div>
                        </div>
                    </div>
                );
            }
        });
    };

    return (
        <div className="tabs-section">
            <div className="tabs-header">
                {tabs.map(tab => (
                    <button
                        key={tab.id}
                        className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
                        onClick={() => setActiveTab(tab.id)}
                    >
                        <span>{tab.label}</span>
                        {tab.count > 0 && <span className="tab-count">{tab.count}</span>}
                    </button>
                ))}
            </div>
            <div className="tabs-content">
                {renderContent()}
            </div>
        </div>
    );
};

export default TabsSection;