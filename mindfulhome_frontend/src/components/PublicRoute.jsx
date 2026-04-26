import React from "react";

import { Navigate } from "react-router-dom";
import { useSelector } from "react-redux";

export default function PublicRoute({ children }) {
    const token = useSelector((state) => state.user.token);

    console.log(token);
    if (token) {
        // Si hay token, redirige a home
        return <Navigate to="/home" replace />;
    }

    // Si no hay token, muestra la página pública
    return children;
}
