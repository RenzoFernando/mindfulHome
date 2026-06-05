import React, { useState, useEffect, useCallback, useRef } from "react";
import { ChevronDown, ChevronUp, Briefcase, ShoppingBag, Shield, CreditCard, Home, Check, AlertTriangle } from "lucide-react";
import { applyPlaygroundModifications, getWhatIfPresets, runSimulation } from "../services/simulation.service";
import "../styles/playground.css";
import Icon from "../components/Icon";
import SaveScenarioModal from './SaveScenarioModal';
import { saveScenario } from '../services/simulation.service';
import SavedScenariosPanel from './SavedScenariosPanel';

const USER_FIELDS = [
    'monthly_income', 'fixed_expenses', 'variable_expenses', 'total_savings',
    'emergency_fund', 'monthly_savings_goal', 'income_type', 'income_variability',
    'contract_type', 'job_seniority_months', 'monthly_debt_payments', 'total_debt',
    'is_renting', 'monthly_rent', 'rent_mortgage_overlap_months', 'dependents'
];

const formatCurrency = (value) => {
    const numericValue = Number(value || 0);
    return `$${new Intl.NumberFormat("es-CO").format(numericValue)}`;
};

const Playground = ({ userData, onSimulationUpdate, isLoading: externalLoading, simulationResults }) => {
    const [presets, setPresets] = useState([]);
    const [openCards, setOpenCards] = useState({});
    
    // ESTADO BASE (nunca cambia después de cargar)
    const [baseUserData, setBaseUserData] = useState({});
    const [basePropertyData, setBasePropertyData] = useState({});
    
    // ESTADO ACTUAL (cambia cuando se aplican modificaciones)
    const [currentUserData, setCurrentUserData] = useState({});
    const [currentPropertyData, setCurrentPropertyData] = useState({});
    
    // Modificaciones pendientes (no aplicadas aún)
    const [pendingUserModifications, setPendingUserModifications] = useState({});
    const [pendingPropertyModifications, setPendingPropertyModifications] = useState({});
    
    // HISTORIAL DE MODIFICACIONES APLICADAS (para guardar)
    const [appliedModifications, setAppliedModifications] = useState({});
    
    const [isLoading, setIsLoading] = useState(false);
    const [notification, setNotification] = useState(null);
    const notificationTimeoutRef = useRef(null);
    const [hasChanges, setHasChanges] = useState(false);
    const [isSaveModalOpen, setIsSaveModalOpen] = useState(false);
    const [isSaving, setIsSaving] = useState(false);

    const [isScenariosPanelOpen, setIsScenariosPanelOpen] = useState(false);
    const [isLoadingScenario, setIsLoadingScenario] = useState(false);

    const buildUserOverrides = useCallback((source = {}) => {
        return USER_FIELDS.reduce((acc, field) => {
            if (source[field] !== undefined && source[field] !== null) {
                acc[field] = source[field];
            }
            return acc;
        }, {});
    }, []);

    const buildPropertyInput = useCallback((source = {}) => {
        return {
            property_price: Number(source.property_price ?? 300000000),
            down_payment: Number(source.down_payment ?? 60000000),
            annual_interest_rate: Number(source.annual_interest_rate ?? 12.0),
            interest_rate_type: String(source.interest_rate_type || "FIJA"),
            loan_term_years: Number(source.loan_term_years ?? 20)
        };
    }, []);

    // Cargar presets y datos iniciales
    useEffect(() => {
        loadPresets();
        if (userData) {
            // Inicializar base y current con los mismos datos
            setBaseUserData(userData);
            setCurrentUserData(userData);
        }
        loadDefaultProperty();
    }, [userData]);

    const loadPresets = async () => {
        try {
            const presetsData = await getWhatIfPresets();
            setPresets(presetsData);
        } catch (error) {
            console.error("Error loading presets:", error);
        }
    };

    const loadDefaultProperty = async () => {
        try {
            const defaultProperty = {
                property_price: 300000000,
                down_payment: 60000000,
                annual_interest_rate: 12.0,
                interest_rate_type: "FIJA",
                loan_term_years: 20
            };
            setBasePropertyData(defaultProperty);
            setCurrentPropertyData(defaultProperty);
        } catch (error) {
            console.error("Error loading property:", error);
        }
    };

    // Acumular modificación (no enviar aún)
    const accumulateModification = useCallback((variable, value, isProperty = false) => {
        if (isProperty) {
            setPendingPropertyModifications(prev => ({ ...prev, [variable]: value }));
        } else {
            setPendingUserModifications(prev => ({ ...prev, [variable]: value }));
        }
        setHasChanges(true);
    }, []);

    // Aplicar todos los cambios acumulados
    const applyAllChanges = useCallback(async () => {
        if (!hasChanges) return;

        setIsLoading(true);
        try {
            const finalUserData = { ...currentUserData, ...pendingUserModifications };
            const finalPropertyData = { ...currentPropertyData, ...pendingPropertyModifications };

            // Convertir modificaciones al formato esperado por el backend
            const userModificationsList = Object.entries(pendingUserModifications).map(([variable, value]) => ({
                variable,
                new_value: value,
                percentage_change: null
            }));

            const propertyModificationsList = Object.entries(pendingPropertyModifications).map(([variable, value]) => ({
                variable,
                new_value: value,
                percentage_change: null
            }));

            // Enviar al backend
            const updatedScenario = await applyPlaygroundModifications(
                userModificationsList,
                propertyModificationsList,
                buildPropertyInput(finalPropertyData)
            );

            // ACTUALIZAR EL HISTORIAL DE MODIFICACIONES APLICADAS
            const updatedUserData = updatedScenario.user_data || finalUserData;
            const updatedPropertyData = updatedScenario.property_input || buildPropertyInput(finalPropertyData);
            const newAppliedModifications = buildUserOverrides(updatedUserData);
            
            setAppliedModifications(newAppliedModifications);

            // Actualizar SOLO el estado actual (NO el base)
            setCurrentUserData(updatedUserData);
            setCurrentPropertyData(updatedPropertyData);

            // Limpiar modificaciones pendientes
            setPendingUserModifications({});
            setPendingPropertyModifications({});
            setHasChanges(false);

            // Preparar input para simulación
            const simulationInput = {
                overrides: buildUserOverrides(updatedUserData),
                property_input: buildPropertyInput(updatedPropertyData),
                simulation_months: 360,
                num_simulations: 100
            };

            // Ejecutar simulación
            const results = await runSimulation(simulationInput);

            if (onSimulationUpdate) {
                onSimulationUpdate(results);
            }
        } catch (error) {
            console.error("Error applying modifications:", error);
        } finally {
            setIsLoading(false);
        }
    }, [hasChanges, pendingUserModifications, pendingPropertyModifications, currentUserData, currentPropertyData, buildUserOverrides, buildPropertyInput, onSimulationUpdate]);

    const toggleCard = (cardId) => {
        setOpenCards(prev => ({ ...prev, [cardId]: !prev[cardId] }));
    };

    // Obtener valor actual (current + pendiente)
    const getCurrentValue = (variable, isProperty = false, defaultValue = null) => {
        if (isProperty) {
            if (pendingPropertyModifications.hasOwnProperty(variable)) {
                return pendingPropertyModifications[variable];
            }
            return currentPropertyData[variable] !== undefined ? currentPropertyData[variable] : defaultValue;
        } else {
            if (pendingUserModifications.hasOwnProperty(variable)) {
                return pendingUserModifications[variable];
            }
            return currentUserData[variable] !== undefined ? currentUserData[variable] : defaultValue;
        }
    };

    const showNotification = useCallback((message, type = "success") => {
        setNotification({ message, type });
        window.clearTimeout(notificationTimeoutRef.current);
        notificationTimeoutRef.current = window.setTimeout(() => {
            setNotification(null);
        }, 3200);
    }, []);

    const loadSavedScenario = async (scenario) => {
        setIsLoadingScenario(true);
        try {
            // Preparar las modificaciones del escenario guardado
            const modifications = scenario.scenario_overrides || scenario.inputs?.overrides || {};
            const propertyInput = scenario.property_input || scenario.inputs?.property_input || buildPropertyInput(currentPropertyData);
            
            // Convertir modificaciones al formato esperado
            const userModificationsList = Object.entries(modifications).map(([variable, value]) => ({
                variable,
                new_value: value,
                percentage_change: null
            }));
            
            // Enviar al backend para aplicar el escenario
            const updatedScenario = await applyPlaygroundModifications(
                userModificationsList,
                [],
                buildPropertyInput(propertyInput)
            );
            
            // Actualizar estados
            const loadedUserData = updatedScenario.user_data || { ...currentUserData, ...modifications };
            const loadedPropertyData = updatedScenario.property_input || buildPropertyInput(propertyInput);
            setCurrentUserData(loadedUserData);
            setBaseUserData(loadedUserData);
            setCurrentPropertyData(loadedPropertyData);
            setBasePropertyData(loadedPropertyData);
            
            // Limpiar modificaciones pendientes
            setPendingUserModifications({});
            setPendingPropertyModifications({});
            setAppliedModifications(buildUserOverrides(loadedUserData));
            setHasChanges(false);
            
            // Preparar input para simulación
            const simulationInput = {
                overrides: buildUserOverrides(loadedUserData),
                property_input: buildPropertyInput(loadedPropertyData),
                simulation_months: 360,
                num_simulations: 100
            };
            
            // Ejecutar simulación
            const results = scenario.results_summary || await runSimulation(simulationInput);
            
            if (onSimulationUpdate) {
                onSimulationUpdate(results);
            }
            
            showNotification(`Escenario "${scenario.name}" cargado`);
        } catch (error) {
            console.error('Error loading scenario:', error);
            showNotification('No se pudo cargar el escenario', 'error');
        } finally {
            setIsLoadingScenario(false);
        }
    };

    // Función para guardar el escenario actual
    const handleSaveScenario = async (name) => {
        setIsSaving(true);
        try {
            const finalUserData = { ...currentUserData, ...appliedModifications, ...pendingUserModifications };
            const finalPropertyData = { ...currentPropertyData, ...pendingPropertyModifications };
            
            // Crear el escenario para guardar
            const scenarioToSave = {
                name: String(name),
                modifications: buildUserOverrides(finalUserData),
                property_input: buildPropertyInput(finalPropertyData),
                simulation_months: 360,
                num_simulations: 100,
                results_summary: hasChanges ? null : simulationResults || null
            };
            
            console.log('Enviando al backend:', JSON.stringify(scenarioToSave, null, 2));
            
            const response = await saveScenario(scenarioToSave);
            console.log('Respuesta del backend:', response);
            
            setAppliedModifications(buildUserOverrides(finalUserData));
            setCurrentUserData(finalUserData);
            setCurrentPropertyData(buildPropertyInput(finalPropertyData));
            showNotification('Escenario guardado correctamente');
            setIsSaveModalOpen(false);
        } catch (error) {
            console.error('Error saving scenario:', error);
            if (error.response?.data) {
                const errorData = error.response.data;
                if (typeof errorData === 'object') {
                    showNotification('Error: ' + JSON.stringify(errorData, null, 2), 'error');
                } else {
                    showNotification('Error: ' + errorData, 'error');
                }
            } else {
                showNotification('No se pudo guardar el escenario. Verifica los campos.', 'error');
            }
        } finally {
            setIsSaving(false);
        }
    };

    // Resetear todos los cambios pendientes
    const resetPendingChanges = () => {
        setPendingUserModifications({});
        setPendingPropertyModifications({});
        setHasChanges(false);
    };

    // Configuración de las cards del playground
    const playgroundSections = [
        {
            id: "income",
            title: "Ingresos y trabajo",
            icon: Briefcase,
            variables: [
                { name: "monthly_income", label: "Ingreso mensual", type: "slider", min: 0, max: 20000000, step: 100000, unit: "$", format: (v) => formatCurrency(v), defaultValue: 4000000 },
                { name: "job_seniority_months", label: "Antigüedad laboral", type: "slider", min: 0, max: 240, step: 6, unit: "meses", format: (v) => v ? `${v} meses` : "0 meses", defaultValue: 24 },
                { name: "income_type", label: "Tipo de ingreso", type: "segmented", options: ["EMPLEADO", "INDEPENDIENTE", "EMPRESARIO", "PENSIONADO"], defaultValue: "EMPLEADO" },
                { name: "contract_type", label: "Tipo de contrato", type: "segmented", options: ["INDEFINIDO", "FIJO", "PRESTACION_SERVICIOS", "NINGUNO"], defaultValue: "INDEFINIDO" },
                { name: "income_variability", label: "Variabilidad de ingresos", type: "segmented", options: ["FIJO", "VARIABLE", "MIXTO"], defaultValue: "FIJO" }
            ]
        },
        {
            id: "spending",
            title: "Gastos y estilo de vida",
            icon: ShoppingBag,
            variables: [
                { name: "fixed_expenses", label: "Gastos fijos", type: "slider", min: 0, max: 10000000, step: 50000, unit: "$", format: (v) => formatCurrency(v), defaultValue: 1500000 },
                { name: "variable_expenses", label: "Gastos variables", type: "slider", min: 0, max: 8000000, step: 50000, unit: "$", format: (v) => formatCurrency(v), defaultValue: 1000000 },
                { name: "monthly_savings_goal", label: "Meta de ahorro mensual", type: "slider", min: 0, max: 5000000, step: 50000, unit: "$", format: (v) => formatCurrency(v), defaultValue: 500000 },
                { name: "dependents", label: "Dependientes", type: "stepper", min: 0, max: 10, step: 1, unit: "", format: (v) => v === 1 ? `${v} dependiente` : `${v} dependientes`, defaultValue: 0 }
            ]
        },
        {
            id: "savings",
            title: "Ahorros y protección",
            icon: Shield,
            variables: [
                { name: "total_savings", label: "Ahorros totales", type: "slider", min: 0, max: 500000000, step: 1000000, unit: "$", format: (v) => formatCurrency(v), defaultValue: 10000000 },
                { name: "emergency_fund", label: "Fondo de emergencia", type: "slider", min: 0, max: 200000000, step: 1000000, unit: "$", format: (v) => formatCurrency(v), defaultValue: 5000000 }
            ]
        },
        {
            id: "debt",
            title: "Deudas y presión financiera",
            icon: CreditCard,
            variables: [
                { name: "total_debt", label: "Deuda total", type: "slider", min: 0, max: 200000000, step: 1000000, unit: "$", format: (v) => formatCurrency(v), defaultValue: 5000000 },
                { name: "monthly_debt_payments", label: "Pagos mensuales de deuda", type: "slider", min: 0, max: 5000000, step: 50000, unit: "$", format: (v) => formatCurrency(v), defaultValue: 300000 }
            ]
        },
        {
            id: "housing",
            title: "Condiciones de vivienda",
            icon: Home,
            variables: [
                { name: "monthly_rent", label: "Renta mensual (si aplica)", type: "slider", min: 0, max: 10000000, step: 100000, unit: "$", format: (v) => formatCurrency(v), defaultValue: 0 },
                { name: "rent_mortgage_overlap_months", label: "Meses de overlap (renta + hipoteca)", type: "stepper", min: 0, max: 12, step: 1, unit: "meses", format: (v) => `${v} meses`, defaultValue: 0 }
            ]
        },
        {
            id: "property",
            title: "Detalles de propiedad",
            icon: Home,
            variables: [
                { name: "property_price", label: "Precio de la propiedad", type: "slider", min: 0, max: 1000000000, step: 10000000, unit: "$", format: (v) => formatCurrency(v), defaultValue: 300000000 },
                { name: "down_payment", label: "Pago inicial", type: "slider", min: 0, max: 500000000, step: 5000000, unit: "$", format: (v) => formatCurrency(v), defaultValue: 60000000 },
                { name: "annual_interest_rate", label: "Tasa de interés anual", type: "slider", min: 0, max: 20, step: 0.1, unit: "%", format: (v) => v ? `${v}%` : "0%", defaultValue: 12.0 },
                { name: "loan_term_years", label: "Plazo del préstamo", type: "slider", min: 5, max: 30, step: 5, unit: "años", format: (v) => v ? `${v} años` : "0 años", defaultValue: 20 },
                { name: "interest_rate_type", label: "Tipo de tasa", type: "segmented", options: ["FIJA", "VARIABLE"], defaultValue: "FIJA" }
            ]
        }
    ];

    // Renderizar control según tipo
    const renderControl = (variable, config, currentValue) => {
        const value = currentValue !== undefined ? currentValue : config.defaultValue;
        const isLoadingState = isLoading || externalLoading;

        switch (config.type) {
            case "slider":
                return (
                    <div className="playground-control">
                        <input
                            type="range"
                            min={config.min}
                            max={config.max}
                            step={config.step}
                            value={value ?? config.defaultValue ?? 0}
                            onChange={(e) => accumulateModification(variable, parseFloat(e.target.value), config.isProperty || false)}
                            className="playground-slider"
                            disabled={isLoadingState}
                        />
                        <div className="playground-value">
                            {config.format ? config.format(value !== undefined ? value : config.defaultValue) : value}
                        </div>
                    </div>
                );
            case "segmented":
                return (
                    <div className="playground-segmented">
                        {config.options.map(opt => (
                            <button
                                key={opt}
                                className={`segmented-btn ${value === opt ? "active" : ""}`}
                                onClick={() => accumulateModification(variable, opt, config.isProperty || false)}
                                disabled={isLoadingState}
                            >
                                {opt}
                            </button>
                        ))}
                    </div>
                );
            case "stepper":
                return (
                    <div className="playground-stepper">
                        <button
                            className="stepper-btn"
                            onClick={() => accumulateModification(variable, Math.max(config.min, (value ?? config.defaultValue ?? 0) - config.step), config.isProperty || false)}
                            disabled={isLoadingState || (value ?? config.defaultValue ?? 0) <= config.min}
                        >
                            -
                        </button>
                        <span className="stepper-value">{config.format ? config.format(value !== undefined ? value : config.defaultValue) : value}</span>
                        <button
                            className="stepper-btn"
                            onClick={() => accumulateModification(variable, Math.min(config.max, (value ?? config.defaultValue ?? 0) + config.step), config.isProperty || false)}
                            disabled={isLoadingState || (value ?? config.defaultValue ?? 0) >= config.max}
                        >
                            +
                        </button>
                    </div>
                );
            default:
                return null;
        }
    };

    const isLoadingState = isLoading || externalLoading;

    return (
        <div className="playground-container">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <h3 className="playground-title" style={{ marginBottom: 0 }}>¡Experimenta ahora!</h3>
                <div style={{ display: 'flex', gap: '8px' }}>
                    <Icon
                        name="FolderOpen"
                        size={18}
                        color="#467599"
                        backgroundColor="#eef4f8"
                        padding={10}
                        borderRadius={12}
                        onPress={() => setIsScenariosPanelOpen(true)}
                        disabled={isLoadingState}
                    />
                    <Icon
                        name="Save"
                        size={18}
                        color="#467599"
                        backgroundColor="#eef4f8"
                        padding={10}
                        borderRadius={12}
                        onPress={() => setIsSaveModalOpen(true)}
                        disabled={isLoadingState}
                    />
                    <Icon
                        name="Check"
                        size={18}
                        color={hasChanges ? "#4CAF50" : "#cccccc"}
                        backgroundColor={hasChanges ? "#e8f5e9" : "#f5f5f5"}
                        padding={10}
                        borderRadius={12}
                        onPress={applyAllChanges}
                        disabled={!hasChanges || isLoadingState}
                    />
                </div>
            </div>

            {isLoadingState && (
                <div className="playground-loading">
                    <div className="loading-spinner"></div>
                    <span>Simulando...</span>
                </div>
            )}

            <div className="playground-sections">
                {playgroundSections.map(section => {
                    const isOpen = openCards[section.id] || false;
                    const IconComponent = section.icon;

                    if (section.showIf && !section.showIf()) return null;

                    return (
                        <div key={section.id} className="playground-card">
                            <div className="playground-card-header" onClick={() => toggleCard(section.id)}>
                                <div className="playground-card-header-left">
                                    <div className="playground-card-icon">
                                        <IconComponent size={18} />
                                    </div>
                                    <h4 className="playground-card-title">{section.title}</h4>
                                </div>
                                <div className="playground-card-header-right">
                                    {isOpen ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                                </div>
                            </div>
                            {isOpen && (
                                <div className="playground-card-body">
                                    {section.variables.map(variable => {
                                        const isPropertyVariable = section.id === "property";
                                        const currentValue = getCurrentValue(variable.name, isPropertyVariable, variable.defaultValue);
                                        return (
                                            <div key={variable.name} className="playground-variable">
                                                <label className="playground-label">{variable.label}</label>
                                                {renderControl(variable.name, { ...variable, isProperty: isPropertyVariable }, currentValue)}
                                            </div>
                                        );
                                    })}
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>
            {notification && (
                <div className={`playground-notification playground-notification-${notification.type}`}>
                    <Icon name={notification.type === "error" ? "AlertCircle" : "CheckCircle2"} size={16} color={notification.type === "error" ? "#b42318" : "#1f7a3f"} backgroundColor="transparent" padding={0} />
                    <span>{notification.message}</span>
                </div>
            )}

            <SaveScenarioModal
                isOpen={isSaveModalOpen}
                onClose={() => setIsSaveModalOpen(false)}
                onSave={handleSaveScenario}
                isLoading={isSaving}
            />
            <SavedScenariosPanel
                isOpen={isScenariosPanelOpen}
                onClose={() => setIsScenariosPanelOpen(false)}
                onLoadScenario={loadSavedScenario}
                isLoading={isLoadingScenario}
                onScenarioDeleted={(name) => showNotification(`Escenario "${name}" eliminado`)}
            />
        </div>
    );
};

export default Playground;