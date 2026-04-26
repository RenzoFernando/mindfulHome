import React, { useState } from "react";
import { X, Home, TrendingUp, Percent, Calendar, DollarSign } from "lucide-react";
import FloatingInput from "./FloatingInput";
import { createAnalysis } from "../services/analysis.service";
import "../styles/property-modal.css";
import logo from "../assets/logo.png";

export default function PropertyModal({ isOpen, onClose, onSuccess }) {
    const [formData, setFormData] = useState({
        property_price: "",
        down_payment: "",
        annual_interest_rate: "",
        interest_rate_type: "FIJA",
        loan_term_years: "",
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    if (!isOpen) return null;

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError("");

        try {
            const data = {
                property_price: parseFloat(formData.property_price),
                down_payment: parseFloat(formData.down_payment),
                annual_interest_rate: parseFloat(formData.annual_interest_rate),
                interest_rate_type: formData.interest_rate_type,
                loan_term_years: parseInt(formData.loan_term_years),
            };

            // Validaciones
            if (data.property_price <= 0) throw new Error("El precio de la propiedad debe ser mayor a 0");
            if (data.down_payment < 0) throw new Error("La cuota inicial no puede ser negativa");
            if (data.down_payment > data.property_price) throw new Error("La cuota inicial no puede ser mayor al precio");
            if (data.annual_interest_rate <= 0) throw new Error("La tasa de interés debe ser mayor a 0");
            if (data.loan_term_years <= 0) throw new Error("El plazo debe ser mayor a 0");

            const response = await createAnalysis(data);
            onSuccess(response);
            onClose();
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-container" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <div className="modal-title">
                <img src={logo} alt="Logo" className="profile-logo" width="80" height="80" />
                <div className="profile-divider"></div>
                                        <h2>Analizar propiedad</h2>
                    </div>
                    <button className="modal-close" onClick={onClose}>
                        <X size={24} />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="modal-form">
                    <div className="form-fields">
                        <div className="form-field">
                            <FloatingInput
                                type="number"
                                name="property_price"
                                label="Precio de la propiedad (COP)"
                                value={formData.property_price}
                                onChange={handleChange}
                                required
                            />
                            <p className="field-description">Valor total de la propiedad que deseas adquirir</p>
                        </div>

                        <div className="form-field">
                            <FloatingInput
                                type="number"
                                name="down_payment"
                                label="Cuota inicial (COP)"
                                value={formData.down_payment}
                                onChange={handleChange}
                                required
                            />
                            <p className="field-description">Monto que pagarás como cuota inicial</p>
                        </div>

                        <div className="form-field">
                            <FloatingInput
                                type="number"
                                name="annual_interest_rate"
                                label="Tasa de interés anual (%)"
                                value={formData.annual_interest_rate}
                                onChange={handleChange}
                                required
                                step="0.1"
                            />
                            <p className="field-description">Tasa de interés anual del préstamo hipotecario</p>
                        </div>

                        <div className="form-field">
                            <label className="select-label">Tipo de tasa de interés</label>
                            <select
                                name="interest_rate_type"
                                value={formData.interest_rate_type}
                                onChange={handleChange}
                                className="floating-select"
                                required
                            >
                                <option value="FIJA">Fija</option>
                                <option value="VARIABLE">Variable</option>
                            </select>
                            <p className="field-description">Si la tasa es fija o variable durante el préstamo</p>
                        </div>

                        <div className="form-field">
                            <FloatingInput
                                type="number"
                                name="loan_term_years"
                                label="Plazo del préstamo (años)"
                                value={formData.loan_term_years}
                                onChange={handleChange}
                                required
                            />
                            <p className="field-description">Número de años para pagar el préstamo</p>
                        </div>
                    </div>

                    {error && <div className="error-message">{error}</div>}

                    <div className="modal-buttons">
                        <button type="button" onClick={onClose} className="cancel-btn">
                            Cancelar
                        </button>
                        <button type="submit" className="submit-btn" disabled={loading}>
                            {loading ? "Analizando..." : "Analizar"}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}