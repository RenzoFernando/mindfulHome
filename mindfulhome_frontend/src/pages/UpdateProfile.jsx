import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import { Wallet, Briefcase, CreditCard, Home, Save } from "lucide-react";
import { updateUserProfile, setUser } from "../features/userSlice";
import FloatingInput from "../components/FloatingInput";
import "../styles/update-profile.css";
import logo from "../assets/logo.png";

export default function UpdateProfile() {
    const dispatch = useDispatch();
    const navigate = useNavigate();
    const user = useSelector(state => state.user.user);
    const token = useSelector(state => state.user.token);

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [isLoading, setIsLoading] = useState(true);
    const [hasChanges, setHasChanges] = useState(false);
    const [originalData, setOriginalData] = useState({});

    // Datos del formulario
    const [formData, setFormData] = useState({
        // Perfil financiero
        monthly_income: "",
        fixed_expenses: "",
        variable_expenses: "",
        total_savings: "",
        emergency_fund: "",
        monthly_savings_goal: "",

        // Perfil laboral
        income_type: "",
        income_variability: "",
        contract_type: "",
        job_seniority_months: "",

        // Perfil de deudas
        monthly_debt_payments: "",
        total_debt: "",

        // Perfil de vivienda
        is_renting: false,
        monthly_rent: "",
        rent_mortgage_overlap_months: 0,
        dependents: 0,
    });

    // Cargar usuario
    useEffect(() => {
        let isMounted = true;

        const loadUser = async () => {
            const localToken = localStorage.getItem("token");
            const currentToken = token || localToken;

            if (!currentToken) {
                navigate("/auth");
                return;
            }

            if (user) {
                const userData = {
                    monthly_income: user.monthly_income || "",
                    fixed_expenses: user.fixed_expenses || "",
                    variable_expenses: user.variable_expenses || "",
                    total_savings: user.total_savings || "",
                    emergency_fund: user.emergency_fund || "",
                    monthly_savings_goal: user.monthly_savings_goal || "",
                    income_type: user.income_type || "",
                    income_variability: user.income_variability || "",
                    contract_type: user.contract_type || "",
                    job_seniority_months: user.job_seniority_months || "",
                    monthly_debt_payments: user.monthly_debt_payments || "",
                    total_debt: user.total_debt || "",
                    is_renting: user.is_renting || false,
                    monthly_rent: user.monthly_rent || "",
                    rent_mortgage_overlap_months: user.rent_mortgage_overlap_months || 0,
                    dependents: user.dependents || 0,
                };
                setFormData(userData);
                setOriginalData(userData);
                setIsLoading(false);
                return;
            }

            try {
                const response = await fetch("http://localhost:8000/mindfulhome/users/me", {
                    headers: { Authorization: `Bearer ${currentToken}` }
                });
                if (!response.ok) throw new Error(`Error ${response.status}`);

                const userData = await response.json();
                if (isMounted) {
                    dispatch(setUser(userData));
                    const formDataObj = {
                        monthly_income: userData.monthly_income || "",
                        fixed_expenses: userData.fixed_expenses || "",
                        variable_expenses: userData.variable_expenses || "",
                        total_savings: userData.total_savings || "",
                        emergency_fund: userData.emergency_fund || "",
                        monthly_savings_goal: userData.monthly_savings_goal || "",
                        income_type: userData.income_type || "",
                        income_variability: userData.income_variability || "",
                        contract_type: userData.contract_type || "",
                        job_seniority_months: userData.job_seniority_months || "",
                        monthly_debt_payments: userData.monthly_debt_payments || "",
                        total_debt: userData.total_debt || "",
                        is_renting: userData.is_renting || false,
                        monthly_rent: userData.monthly_rent || "",
                        rent_mortgage_overlap_months: userData.rent_mortgage_overlap_months || 0,
                        dependents: userData.dependents || 0,
                    };
                    setFormData(formDataObj);
                    setOriginalData(formDataObj);
                    setIsLoading(false);
                }
            } catch (err) {
                console.error("Error:", err);
                if (isMounted) navigate("/auth");
            }
        };

        loadUser();
        return () => { isMounted = false; };
    }, []);

    // Detectar cambios
    useEffect(() => {
        const hasChanged = JSON.stringify(formData) !== JSON.stringify(originalData);
        setHasChanges(hasChanged);
    }, [formData, originalData]);

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({ ...prev, [name]: type === "checkbox" ? checked : value }));
    };

    const handleSubmit = async () => {
        if (!hasChanges) return;

        setLoading(true);
        setError("");

        try {
            const currentToken = localStorage.getItem("token");
            const updateData = {
                financial: {
                    monthly_income: parseFloat(formData.monthly_income) || 0,
                    fixed_expenses: parseFloat(formData.fixed_expenses) || 0,
                    variable_expenses: parseFloat(formData.variable_expenses) || 0,
                    total_savings: parseFloat(formData.total_savings) || 0,
                    emergency_fund: parseFloat(formData.emergency_fund) || 0,
                    monthly_savings_goal: parseFloat(formData.monthly_savings_goal) || 0,
                },
                labor: {
                    income_type: formData.income_type,
                    income_variability: formData.income_variability,
                    contract_type: formData.contract_type,
                    job_seniority_months: parseInt(formData.job_seniority_months) || 0,
                },
                debt: {
                    monthly_debt_payments: parseFloat(formData.monthly_debt_payments) || 0,
                    total_debt: parseFloat(formData.total_debt) || 0,
                },
                housing: {
                    is_renting: formData.is_renting,
                    monthly_rent: parseFloat(formData.monthly_rent) || 0,
                    rent_mortgage_overlap_months: parseInt(formData.rent_mortgage_overlap_months) || 0,
                },
                household: { dependents: parseInt(formData.dependents) || 0 }
            };

            const response = await fetch("http://localhost:8000/mindfulhome/users/me", {
                method: "PATCH",
                headers: { "Content-Type": "application/json", Authorization: `Bearer ${currentToken}` },
                body: JSON.stringify(updateData)
            });

            if (!response.ok) throw new Error(`Error ${response.status}`);

            const updatedUser = await response.json();
            dispatch(updateUserProfile(updatedUser));

            navigate("/home");
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    if (isLoading) {
        return (
            <div className="update-profile-container">
                <div className="update-profile-card">
                    <div style={{ textAlign: "center", padding: "40px" }}>Cargando tu información...</div>
                </div>
            </div>
        );
    }

    // Definición de secciones
    const sections = {
        financial: {
            title: "Perfil financiero",
            icon: Wallet,
            fields: [
                { name: "monthly_income", label: "Ingreso mensual (COP)", type: "number", description: "Tu ingreso total mensual después de impuestos" },
                { name: "fixed_expenses", label: "Gastos fijos mensuales (COP)", type: "number", description: "Gastos que no cambian mes a mes" },
                { name: "variable_expenses", label: "Gastos variables mensuales (COP)", type: "number", description: "Gastos que varían mes a mes" },
                { name: "total_savings", label: "Ahorros totales (COP)", type: "number", description: "Total de tus ahorros" },
                { name: "emergency_fund", label: "Fondo de emergencia (COP)", type: "number", description: "Ahorros para emergencias" },
                { name: "monthly_savings_goal", label: "Meta de ahorro mensual (COP)", type: "number", description: "Cuánto quieres ahorrar cada mes" },
            ]
        },
        labor: {
            title: "Perfil laboral",
            icon: Briefcase,
            fields: [
                {
                    name: "income_type", label: "Tipo de ingreso", type: "select",
                    description: "Cómo recibes tus ingresos",
                    options: [
                        { value: "EMPLEADO", label: "Empleado" },
                        { value: "INDEPENDIENTE", label: "Independiente" },
                        { value: "EMPRESARIO", label: "Empresario" },
                        { value: "PENSIONADO", label: "Pensionado" }
                    ]
                },
                {
                    name: "income_variability", label: "Variabilidad del ingreso", type: "select",
                    description: "Qué tan predecibles son tus ingresos",
                    options: [
                        { value: "FIJO", label: "Fijo" },
                        { value: "VARIABLE", label: "Variable" },
                        { value: "MIXTO", label: "Mixto" }
                    ]
                },
                {
                    name: "contract_type", label: "Tipo de contrato", type: "select",
                    description: "Tu situación contractual",
                    options: [
                        { value: "INDEFINIDO", label: "Indefinido" },
                        { value: "FIJO", label: "Fijo" },
                        { value: "PRESTACION_SERVICIOS", label: "Prestación de servicios" },
                        { value: "NINGUNO", label: "Ninguno" }
                    ]
                },
                { name: "job_seniority_months", label: "Antigüedad laboral (meses)", type: "number", description: "Tiempo en tu trabajo actual" },
            ]
        },
        debt: {
            title: "Perfil de deudas",
            icon: CreditCard,
            fields: [
                { name: "monthly_debt_payments", label: "Pagos mensuales de deudas (COP)", type: "number", description: "Total que pagas cada mes en deudas" },
                { name: "total_debt", label: "Deuda total (COP)", type: "number", description: "Monto total de tus deudas" },
            ]
        },
        housing: {
            title: "Perfil de vivienda",
            icon: Home,
            fields: [
                { name: "is_renting", label: "¿Vives en arriendo?", type: "checkbox", description: "Si pagas arriendo actualmente" },
                { name: "monthly_rent", label: "Arriendo mensual (COP)", type: "number", description: "Monto de tu arriendo" },
                { name: "rent_mortgage_overlap_months", label: "Meses de superposición", type: "number", description: "Meses que pagarías renta e hipoteca" },
                { name: "dependents", label: "Número de dependientes", type: "number", description: "Personas que dependen de ti" },
            ]
        }
    };

    return (
        <div className="update-profile-card">
            <div className="profile-header">
                <img src={logo} alt="Logo" className="profile-logo" width="80" height="80" />
                <div className="profile-divider"></div>
                <h1>Actualizar perfil</h1>
            </div>

            <div className="two-column-layout">
                {/* Columna izquierda */}
                <div className="left-column">
                    <div className="section-card">
                        <div className="section-header">
                            <Wallet size={24} className="section-icon" />
                            <h2>{sections.financial.title}</h2>
                        </div>
                        <div className="section-fields">
                            {sections.financial.fields.map((field) => (
                                <div key={field.name} className="form-field">
                                    <FloatingInput
                                        type={field.type}
                                        name={field.name}
                                        label={field.label}
                                        value={formData[field.name]}
                                        onChange={handleChange}
                                    />
                                    <p className="field-description">{field.description}</p>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="section-card">
                        <div className="section-header">
                            <Briefcase size={24} className="section-icon" />
                            <h2>{sections.labor.title}</h2>
                        </div>
                        <div className="section-fields">
                            {sections.labor.fields.map((field) => (
                                <div key={field.name} className="form-field">
                                    {field.type === "select" ? (
                                        <>
                                            <select
                                                name={field.name}
                                                value={formData[field.name]}
                                                onChange={handleChange}
                                                className="floating-select"
                                            >
                                                <option value="">Selecciona {field.label.toLowerCase()}</option>
                                                {field.options.map(opt => (
                                                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                                                ))}
                                            </select>
                                            <p className="field-description">{field.description}</p>
                                        </>
                                    ) : (
                                        <>
                                            <FloatingInput
                                                type={field.type}
                                                name={field.name}
                                                label={field.label}
                                                value={formData[field.name]}
                                                onChange={handleChange}
                                            />
                                            <p className="field-description">{field.description}</p>
                                        </>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Columna derecha */}
                <div className="right-column">
                    <div className="section-card">
                        <div className="section-header">
                            <CreditCard size={24} className="section-icon" />
                            <h2>{sections.debt.title}</h2>
                        </div>
                        <div className="section-fields">
                            {sections.debt.fields.map((field) => (
                                <div key={field.name} className="form-field">
                                    <FloatingInput
                                        type={field.type}
                                        name={field.name}
                                        label={field.label}
                                        value={formData[field.name]}
                                        onChange={handleChange}
                                    />
                                    <p className="field-description">{field.description}</p>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="section-card">
                        <div className="section-header">
                            <Home size={24} className="section-icon" />
                            <h2>{sections.housing.title}</h2>
                        </div>
                        <div className="section-fields">
                            {sections.housing.fields.map((field) => (
                                <div key={field.name} className="form-field">
                                    {field.type === "checkbox" ? (
                                        <>
                                            <label className="checkbox-label">
                                                <input
                                                    type="checkbox"
                                                    name={field.name}
                                                    checked={formData[field.name]}
                                                    onChange={handleChange}
                                                />
                                                {field.label}
                                            </label>
                                            <p className="field-description">{field.description}</p>
                                        </>
                                    ) : (
                                        <>
                                            <FloatingInput
                                                type={field.type}
                                                name={field.name}
                                                label={field.label}
                                                value={formData[field.name]}
                                                onChange={handleChange}
                                            />
                                            <p className="field-description">{field.description}</p>
                                        </>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>

            {error && <div className="error-message">{error}</div>}

            <div className="update-button-container">
                <button
                    onClick={handleSubmit}
                    className={`update-btn ${hasChanges ? 'active' : ''}`}
                    disabled={loading || !hasChanges}
                >
                    {loading ? "Guardando..." : (
                        <>
                            <span>Actualizar perfil</span>
                        </>
                    )}
                </button>
            </div>
        </div>
    );
}