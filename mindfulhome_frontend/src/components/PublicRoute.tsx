import React from "react";
import { Navigate } from "react-router-dom";
import { useSelector } from "react-redux";

interface PublicRouteProps {
    children: React.ReactNode;
}

export default function PublicRoute({ children }: PublicRouteProps) {
    const token = useSelector((state: { user: { token: string | null } }) => state.user.token);

    console.log(token);
    
    if (token) {
        return <Navigate to="/routines" replace />;
    }

    return <>{children}</>;
}