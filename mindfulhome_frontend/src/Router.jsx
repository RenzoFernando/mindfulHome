import React from "react";
import { createBrowserRouter, Navigate, Outlet } from "react-router-dom";
import Auth from "./pages/Auth";
import Home from "./pages/Home";
import CompleteProfile from "./pages/CompleteProfile";
import ProtectedRoute from "./components/ProtectedRoute";
import PublicRoute from "./components/PublicRoute";
import Sidebar from "./components/Sidebar";
import UpdateProfile from "./pages/UpdateProfile";
import Simulations from "./pages/Simulations";

// Layout con sidebar (para páginas protegidas)
function ProtectedLayout() {
    return (
        <ProtectedRoute>
            <div style={{ display: "flex" }}>
                <Sidebar />
                <div className="main-content">
                    <Outlet />
                </div>
            </div>
        </ProtectedRoute>
    );
}

// Layout sin sidebar (para CompleteProfile)
function NoSidebarLayout() {
    return (
        <ProtectedRoute>
            <Outlet />
        </ProtectedRoute>
    );
}

// Layout público (sin protección, sin sidebar)
function PublicLayout() {
    return (
        <PublicRoute>
            <Outlet />
        </PublicRoute>
    );
}

const router = createBrowserRouter([
    {
        path: "/",
        Component: () => <Navigate to="/home" replace />,
    },
    {
        path: "/auth",
        Component: PublicLayout,
        children: [{ index: true, Component: Auth }],
    },
    {
        path: "/complete-profile",
        Component: NoSidebarLayout,
        children: [{ index: true, Component: CompleteProfile }],
    },
    {
        path: "/",
        Component: ProtectedLayout,
        children: [
            { path: "home", Component: Home },
            { path: "profile", Component: UpdateProfile },
            { path: "simulations", Component: Simulations},
        ],
    },
], { basename: "/mindfulhome" });

export default router;