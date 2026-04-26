import React from "react";

import "../styles/forms.css";

function FloatingInput({
    type = "text",
    id,
    name,
    label,
    value,
    onChange,
    required = false
}) {
    return (
        <div className="input-group">
            <input
                type={type}
                id={id}
                name={name}
                className="form_input"
                placeholder=" "
                value={value}
                onChange={onChange}
                required={required}
            />
            <label htmlFor={id} className="form_label">
                {label}
            </label>
        </div>
    );
}

export default FloatingInput;
