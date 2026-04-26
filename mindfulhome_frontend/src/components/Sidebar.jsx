import React from "react";
import { useNavigate } from "react-router-dom";
import { useDispatch } from "react-redux";
import { Home, AlignEndHorizontal, Settings2, LogOut, Activity } from "lucide-react";
import { logout } from "../features/userSlice";
import "../styles/sidebar.css";

import logo from "../assets/logo.png";

export default function Sidebar() {
    const dispatch = useDispatch();
    const navigate = useNavigate();

    const handleLogout = () => {
        dispatch(logout());
        localStorage.removeItem("token");
        navigate("/auth");
    };

    return (
        <div className="sidebar">
            {/* Rectángulo superior */}
            <div className="sidebar-top">
                <div className="logo-container">
                    <img src={logo} alt="Logo" className="sidebar-logo" />
                </div>
                <div className="nav-icons">
                    <Home
                        className="sidebar-icon"
                        onClick={() => navigate("/home")}
                        strokeWidth={2.7}
                        fill="currentColor"
                    />
                    <AlignEndHorizontal
                        className="sidebar-icon"
                        onClick={() => navigate("/simulations")}
                        strokeWidth={2.7}
                        fill="currentColor"
                    />
                </div>
            </div>

            {/* Rectángulo inferior */}
            <div className="sidebar-bottom">
                <div className="nav-icons-bottom">
                    <Settings2
                        className="sidebar-icon"
                        onClick={() => navigate("/profile")}
                        strokeWidth={2.7}
                        fill="currentColor"
                    />
                    <LogOut
                        className="sidebar-icon"
                        onClick={handleLogout}
                        strokeWidth={2.7}
                    />
                </div>
            </div>
        </div>
    );
}