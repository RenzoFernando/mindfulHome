// components/SavedScenariosPanel.jsx
import React, { useState, useEffect } from 'react';
import Icon from './Icon';
import { getUserScenarios } from '../services/simulation.service';
import '../styles/saved-scenarios-panel.css';

const SavedScenariosPanel = ({ isOpen, onClose, onLoadScenario, isLoading }) => {
    const [scenarios, setScenarios] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (isOpen) {
            loadScenarios();
        }
    }, [isOpen]);

    const loadScenarios = async () => {
        setLoading(true);
        try {
            const data = await getUserScenarios();
            setScenarios(data);
        } catch (error) {
            console.error('Error loading scenarios:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleScenarioClick = (scenario) => {
        if (onLoadScenario) {
            onLoadScenario(scenario);
            onClose();
        }
    };

    const getScenarioIcon = (index) => {
        const icons = ['Folder', 'FileText', 'Bookmark', 'Star', 'Heart'];
        return icons[index % icons.length];
    };

    if (!isOpen) return null;

    return (
        <div className="scenarios-panel-overlay">
            <div className="scenarios-panel">
                <div className="scenarios-panel-header">
                    <Icon 
                        name="X" 
                        size={20} 
                        color="#666" 
                        backgroundColor="#f5f5f5"
                        borderRadius={12}
                        padding={8}
                        onPress={onClose}
                    />
                    <h3 className="scenarios-panel-title">Escenarios guardados</h3>
                </div>
                
                <div className="scenarios-panel-content">
                    {loading ? (
                        <div className="scenarios-loading">
                            <div className="loading-spinner-small"></div>
                            <span>Cargando escenarios...</span>
                        </div>
                    ) : scenarios.length === 0 ? (
                        <div className="scenarios-empty">
                            <Icon name="FolderOpen" size={48} color="#ccc" />
                            <p>No hay escenarios guardados</p>
                            <p className="scenarios-empty-sub">Guarda tu primer escenario usando el botón de guardar</p>
                        </div>
                    ) : (
                        <div className="scenarios-list">
                            {scenarios.map((scenario, index) => (
                                <div 
                                    key={scenario.id} 
                                    className="scenario-item"
                                    onClick={() => handleScenarioClick(scenario)}
                                >
                                    <div className="scenario-item-left">
                                        <div className="scenario-icon">
                                            <Icon name={getScenarioIcon(index)} size={18} color="#467599" />
                                        </div>
                                        <div className="scenario-info">
                                            <div className="scenario-name">{scenario.name}</div>
                                            <div className="scenario-date">
                                                {new Date(scenario.created_at).toLocaleDateString()}
                                            </div>
                                        </div>
                                    </div>
                                    <div className="scenario-item-right">
                                        <Icon 
                                            name="GitCompare" 
                                            size={18} 
                                            color="#999" 
                                            backgroundColor="transparent"
                                            padding={4}
                                            onPress={(e) => {
                                                e.stopPropagation();
                                                // TODO: implementar comparación
                                                console.log('Comparar escenario:', scenario);
                                            }}
                                        />
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default SavedScenariosPanel;