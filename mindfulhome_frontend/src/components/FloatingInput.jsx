import React, { useState } from "react";
import "../styles/forms.css";

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
                type={type}
                id={id}
                name={name}
                className={`form_input ${error ? "error" : ""}`}
                placeholder=" "
                value={value}
                onChange={handleChange}
                onBlur={handleBlur}
                required={required}
                step={type === "number" ? "any" : undefined}
            />
            <label htmlFor={id} className="form_label">
                {label}
            </label>
            {error && <div className="input-error-message">{error}</div>}
        </div>
    );
}

export default FloatingInput;