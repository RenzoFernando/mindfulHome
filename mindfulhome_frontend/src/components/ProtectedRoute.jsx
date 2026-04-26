import React from "react";
import { Navigate } from "react-router-dom";
import { useSelector } from "react-redux";

export default function ProtectedRoute({ children }) {
    const { isAuthenticated, user } = useSelector(state => state.user);
    
    if (!isAuthenticated) {
        return <Navigate to="/auth" replace />;
    }
    
    // Verificar si tiene monthly_income
    const hasMonthlyIncome = user?.monthly_income && user?.monthly_income > 0;
    const currentPath = window.location.pathname;
    
    // Si está en home y no tiene monthly_income, redirigir a complete-profile
    if (currentPath === "/home" && !hasMonthlyIncome) {
        return <Navigate to="/complete-profile" replace />;
    }
    
    // Si está en complete-profile y ya tiene monthly_income, redirigir a home
    if (currentPath === "/complete-profile" && hasMonthlyIncome) {
        return <Navigate to="/home" replace />;
    }
    
    return children;
}