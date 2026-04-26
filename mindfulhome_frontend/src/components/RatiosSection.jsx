import React from "react";
import ProgressBar from "./ProgressBar";
import "../styles/ratios-section.css";

const RatiosSection = ({ ratios }) => {
    if (!ratios) return null;

const ratioItems = [
    { 
        key: "mortgage_ratio", 
        label: "Esfuerzo Hipotecario", 
        description: "Porcentaje del ingreso destinado a la cuota de la hipoteca",
        recommendedMax: 30,
        unit: "%"
    },
    { 
        key: "debt_ratio", 
        label: "Nivel de Endeudamiento", 
        description: "Porcentaje del ingreso destinado a pagar deudas (sin incluir hipoteca)",
        recommendedMax: 40,
        unit: "%"
    },
    { 
        key: "housing_ratio", 
        label: "Carga de Vivienda", 
        description: "Porcentaje del ingreso destinado a gastos de vivienda (cuota + servicios básicos estimados)",
        recommendedMax: 35,
        unit: "%"
    },
    { 
        key: "emergency_months", 
        label: "Respaldo de Emergencia", 
        description: "Meses que puedes cubrir tus gastos con tu fondo de emergencia",
        recommendedMin: 3,
        unit: "meses"
    },
    { 
        key: "free_cash_flow_ratio", 
        label: "Capacidad de Ahorro", 
        description: "Porcentaje del ingreso que queda después de gastos esenciales y deuda",
        recommendedMin: 20,
        unit: "%"
    },
    { 
        key: "discretionary_income_ratio", 
        label: "Libertad Financiera", 
        description: "Porcentaje del ingreso disponible para gastos no esenciales, ahorro o inversión",
        recommendedMin: 15,
        unit: "%"
    }
];

    return (
        <div className="ratios-section">
            <div className="ratios-list">
                {ratioItems.map((item) => {
                    const value = ratios[item.key];
                    if (value === undefined || value === null) return null;
                    
                    return (
                        <div key={item.key} className="ratio-item">
                            <ProgressBar 
                                title={item.label}
                                percentage={value}
                            />
                            <p className="ratio-description">{item.description}</p>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default RatiosSection;