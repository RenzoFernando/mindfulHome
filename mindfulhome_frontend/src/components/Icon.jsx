import React from 'react';
import * as LucideIcons from 'lucide-react';

const Icon = ({
    name,
    size = 20,
    color = '#252525',
    backgroundColor = '#ffffff',
    borderRadius = 20,
    padding = 8,
    onPress,
    disabled = false,
    style,
    strokeWidth = 2.5,
    fill = 'none',
}) => {
    // Obtener el componente del ícono de Lucide
    const LucideIcon = LucideIcons[name];
    
    if (!LucideIcon) {
        console.warn(`Icon "${name}" not found in Lucide`);
        return null;
    }

    const iconElement = (
        <div
            style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                backgroundColor,
                borderRadius,
                padding,
                ...style,
            }}
        >
            <LucideIcon 
                size={size} 
                color={color}
                strokeWidth={strokeWidth}
                fill={fill}
            />
        </div>
    );

    if (onPress) {
        return (
            <button
                onClick={onPress}
                disabled={disabled}
                style={{
                    background: 'none',
                    border: 'none',
                    cursor: disabled ? 'not-allowed' : 'pointer',
                    padding: 0,
                    opacity: disabled ? 0.5 : 1,
                }}
            >
                {iconElement}
            </button>
        );
    }

    return iconElement;
};

export default Icon;