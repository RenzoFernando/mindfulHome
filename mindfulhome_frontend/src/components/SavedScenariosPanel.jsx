// components/SavedScenariosPanel.jsx
import React, { useState, useEffect } from 'react';
import Icon from './Icon';
import { deleteScenario, getUserScenarios } from '../services/simulation.service';
import '../styles/saved-scenarios-panel.css';

const SavedScenariosPanel = ({ isOpen, onClose, onLoadScenario, onScenarioDeleted, isLoading }) => {
    const [scenarios, setScenarios] = useState([]);
    const [loading, setLoading] = useState(false);
    const [deletingId, setDeletingId] = useState(null);
    const [panelMessage, setPanelMessage] = useState('');

    useEffect(() => {
        if (isOpen) {
            loadScenarios();
        }
    }, [isOpen]);

    const loadScenarios = async () => {
        setLoading(true);
        setPanelMessage('');
        try {
            const data = await getUserScenarios();
            setScenarios(data);
        } catch (error) {
            console.error('Error loading scenarios:', error);
            setPanelMessage('No se pudieron cargar los escenarios guardados.');
        } finally {
            setLoading(false);
        }
    };

    const handleScenarioClick = (scenario) => {
        if (isLoading || deletingId) return;
        if (onLoadScenario) {
            onLoadScenario(scenario);
            onClose();
        }
    };

    const handleDeleteScenario = async (event, scenario) => {
        event.stopPropagation();
        if (isLoading || deletingId) return;
        setDeletingId(scenario.id);
        setPanelMessage('');
        try {
            await deleteScenario(scenario.id);
            setScenarios(prev => prev.filter(item => item.id !== scenario.id));
            if (onScenarioDeleted) {
                onScenarioDeleted(scenario.name);
            }
        } catch (error) {
            console.error('Error deleting scenario:', error);
            setPanelMessage('No se pudo eliminar el escenario.');
        } finally {
            setDeletingId(null);
        }
    };

    const getScenarioIcon = (index) => {
        const icons = ['Folder', 'FileText', 'Bookmark', 'Star', 'Heart'];
        return icons[index % icons.length];
    };

    const formatScenarioDate = (value) => {
        if (!value) return '';
        return new Date(value).toLocaleDateString('es-CO', {
            day: '2-digit',
            month: 'short',
            year: 'numeric'
        });
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
                    <div className="scenarios-panel-heading">
                        <h3 className="scenarios-panel-title">Escenarios guardados</h3>
                        <span className="scenarios-panel-subtitle">Carga o elimina escenarios anteriores</span>
                    </div>
                </div>
                
                <div className="scenarios-panel-content">
                    {panelMessage && <div className="scenarios-panel-message">{panelMessage}</div>}
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
                            {scenarios.map((scenario, index) => {
                                const isDeleting = deletingId === scenario.id;
                                return (
                                    <div 
                                        key={scenario.id} 
                                        className={`scenario-item ${isDeleting ? 'scenario-item-deleting' : ''}`}
                                        onClick={() => handleScenarioClick(scenario)}
                                    >
                                        <div className="scenario-item-left">
                                            <div className="scenario-icon">
                                                <Icon name={getScenarioIcon(index)} size={18} color="#467599" />
                                            </div>
                                            <div className="scenario-info">
                                                <div className="scenario-name">{scenario.name}</div>
                                                <div className="scenario-date">
                                                    {formatScenarioDate(scenario.created_at)}
                                                </div>
                                            </div>
                                        </div>
                                        <div className="scenario-item-right">
                                            <span className="scenario-load-hint">Cargar</span>
                                            <button
                                                type="button"
                                                className="scenario-delete-btn"
                                                onClick={(event) => handleDeleteScenario(event, scenario)}
                                                disabled={isDeleting || isLoading}
                                                aria-label={`Eliminar ${scenario.name}`}
                                            >
                                                {isDeleting ? (
                                                    <span className="scenario-delete-spinner"></span>
                                                ) : (
                                                    <Icon 
                                                        name="Trash2" 
                                                        size={16} 
                                                        color="#b42318" 
                                                        backgroundColor="transparent"
                                                        padding={0}
                                                    />
                                                )}
                                            </button>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default SavedScenariosPanel;
