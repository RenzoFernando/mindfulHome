import React, { useState } from 'react';
import Icon from './Icon';
import '../styles/save-scenario-modal.css';

const SaveScenarioModal = ({ isOpen, onClose, onSave, isLoading }) => {
    const [scenarioName, setScenarioName] = useState('');
    const [error, setError] = useState('');

    if (!isOpen) return null;

    const handleSave = () => {
        if (!scenarioName.trim()) {
            setError('Por favor ingresa un nombre para el escenario');
            return;
        }
        setError('');
        onSave(scenarioName.trim());
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter') {
            handleSave();
        }
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <Icon name="Save" size={20} color="#467599" />
                    <h3>Guardar escenario</h3>
                    <button className="modal-close" onClick={onClose}>
                        <Icon name="X" size={18} color="#999" />
                    </button>
                </div>
                <div className="modal-body">
                    <p>Ingresa un nombre para identificar este escenario:</p>
                    <input
                        type="text"
                        className="modal-input"
                        placeholder="Ej: Escenario optimista 2024"
                        value={scenarioName}
                        onChange={(e) => setScenarioName(e.target.value)}
                        onKeyPress={handleKeyPress}
                        autoFocus
                    />
                    {error && <div className="modal-error">{error}</div>}
                </div>
                <div className="modal-footer">
                    <button className="modal-btn modal-btn-cancel" onClick={onClose}>
                        Cancelar
                    </button>
                    <button 
                        className="modal-btn modal-btn-save" 
                        onClick={handleSave}
                        disabled={isLoading}
                    >
                        {isLoading ? 'Guardando...' : 'Guardar'}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default SaveScenarioModal;