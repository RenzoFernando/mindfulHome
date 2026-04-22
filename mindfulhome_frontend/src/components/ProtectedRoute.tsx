import React from "react";
import { Navigate } from "react-router-dom";
import { useSelector } from "react-redux";
import { RootState } from "./store";

interface ProtectedRouteProps {
    children: React.ReactNode;
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
    const token = useSelector((state: RootState) => state.user.token);

    if (!token) {
        // Si no está autenticado, redirige a login
        return <Navigate to="/auth" replace />;
    }

    // Si está autenticado, muestra el contenido
    return <>{children}</>;
}