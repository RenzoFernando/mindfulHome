import React, { useState } from "react";
import "../styles/forms.css";

const CURRENCY_FIELDS = new Set([
    "monthly_income",
    "fixed_expenses",
    "variable_expenses",
    "total_savings",
    "emergency_fund",
    "monthly_savings_goal",
    "monthly_debt_payments",
    "total_debt",
    "monthly_rent",
    "property_price",
    "down_payment"
]);

function FloatingInput({
    type = "text",
    id,
    name,
    label,
    value,
    onChange,
    required = false,
}) {
    const [error, setError] = useState("");
    const [touched, setTouched] = useState(false);
    const isCurrency = type === "number" && CURRENCY_FIELDS.has(name);

    const getRawCurrencyValue = (val) => {
        if (val === undefined || val === null) return "";
        return String(val).replace(/\D/g, "");
    };

    const formatCurrencyValue = (val) => {
        const raw = getRawCurrencyValue(val);
        if (raw === "") return "";
        return new Intl.NumberFormat("es-CO").format(Number(raw));
    };

    const validateAndCorrect = (val) => {
        if (type === "number" && val !== "") {
            const numValue = parseFloat(val);
            if (!isNaN(numValue) && numValue < 0) {
                setError("El valor no puede ser negativo");
                return "0";
            }
        }
        setError("");
        return val;
    };

    const handleChange = (e) => {
        if (isCurrency) {
            const rawValue = getRawCurrencyValue(e.target.value);
            const rawEvent = {
                ...e,
                target: { ...e.target, name, value: rawValue }
            };
            onChange(rawEvent);
            setError("");
            return;
        }

        let newValue = e.target.value;
        
        onChange(e);
        
        if (touched && type === "number") {
            const correctedValue = validateAndCorrect(newValue);
            if (correctedValue !== newValue) {
                const correctedEvent = {
                    ...e,
                    target: { ...e.target, value: correctedValue }
                };
                onChange(correctedEvent);
            }
        }
    };

    const handleBlur = () => {
        setTouched(true);
        
        if (type === "number" && value !== "") {
            const numValue = parseFloat(value);
            if (!isNaN(numValue) && numValue < 0) {
                const correctedEvent = {
                    target: { name, value: "0" }
                };
                onChange(correctedEvent);
                setError("");
            } else {
                validateAndCorrect(value);
            }
        }
    };

    return (
        <div className="input-group">
            <input
                type={isCurrency ? "text" : type}
                id={id}
                name={name}
                className={`form_input ${error ? "error" : ""}`}
                placeholder=" "
                value={isCurrency ? formatCurrencyValue(value) : value}
                onChange={handleChange}
                onBlur={handleBlur}
                required={required}
                step={!isCurrency && type === "number" ? "any" : undefined}
                inputMode={isCurrency ? "numeric" : type === "number" ? "decimal" : undefined}
            />
            <label htmlFor={id} className="form_label">
                {label}
            </label>
            {error && <div className="input-error-message">{error}</div>}
        </div>
    );
}

export default FloatingInput;
