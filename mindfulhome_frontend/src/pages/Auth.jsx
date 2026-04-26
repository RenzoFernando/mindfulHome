import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import { jwtDecode } from "jwt-decode";
import { setToken, setUser, clearUserData } from "../features/userSlice";
import { login as loginService, register as registerService } from "../services/auth.service";
import "../styles/auth.css";
import FloatingInput from "../components/FloatingInput";
import HorizontalCarousel from "../components/HorizontalCarousel";

import imagen1 from "../assets/slide1.png";
import imagen2 from "../assets/slide2.png";
import imagen3 from "../assets/slide3.png";

export default function Auth() {
    // Estado para el formulario activo (registro/login)
    const [isActive, setIsActive] = useState(false);

    // Estados para alertas
    const [signupAlert, setSignupAlert] = useState({
        type: "",
        message: "",
        show: false
    });

    const [loginAlert, setLoginAlert] = useState({
        type: "",
        message: "",
        show: false
    });

    // Estados para los formularios
    const [signUpData, setSignUpData] = useState({
        username: "",
        email: "",
        password: "",
    });

    const [loginData, setLoginData] = useState({
        email: "",
        password: ""
    });

    const dispatch = useDispatch();
    const navigate = useNavigate();
    const user = useSelector(state => state.user);

    // Efecto para limpiar alertas automáticamente
    useEffect(() => {
        if (signupAlert.show) {
            const timer = setTimeout(() => {
                setSignupAlert({ ...signupAlert, show: false });
            }, 9000);
            return () => clearTimeout(timer);
        }
    }, [signupAlert]);

    useEffect(() => {
        if (loginAlert.show) {
            const timer = setTimeout(() => {
                setLoginAlert({ ...loginAlert, show: false });
            }, 9000);
            return () => clearTimeout(timer);
        }
    }, [loginAlert]);

    // Verificar si ya hay un token al cargar el componente
    useEffect(() => {
        const token = localStorage.getItem("token");
        if (token) {
            try {
                const decoded = jwtDecode(token);
                if (decoded.exp && decoded.exp * 1000 > Date.now()) {
                    // CORREGIDO: Usa setToken y setUser separadamente
                    dispatch(setToken(token));
                    dispatch(setUser({
                        id: decoded.sub || decoded.id,
                        username: decoded.username || decoded.name,
                        email: decoded.email,
                        role: decoded.role || decoded.authorities?.[0]
                    }));
                    navigate("/home");
                } else {
                    localStorage.removeItem("token");
                    dispatch(clearUserData());
                }
            } catch (error) {
                console.error("Error decodificando token:", error);
                localStorage.removeItem("token");
            }
        }
    }, [dispatch, navigate]);

    const handleRegisterClick = () => setIsActive(true);
    const handleLoginClick = () => setIsActive(false);

const handleSignup = async (e) => {
    e.preventDefault();

    try {
        const response = await registerService({
            username: signUpData.username,
            email: signUpData.email,
            password: signUpData.password,
        });

        const decoded = jwtDecode(response.access_token);
        
        dispatch(setToken(response.access_token));
        
        // Obtener datos del usuario después del registro
        const res = await fetch("http://localhost:8000/mindfulhome/users/me", {
            headers: {
                Authorization: `Bearer ${response.access_token}`
            }
        });

        const userData = await res.json();
        dispatch(setUser(userData));
        
        // Verificar si tiene monthly_income
        const hasMonthlyIncome = userData.monthly_income && userData.monthly_income > 0;
        
        setSignupAlert({
            type: "success",
            message: hasMonthlyIncome 
                ? "¡Cuenta creada con éxito! Redirigiendo..."
                : "¡Cuenta creada con éxito! Completa tus datos financieros para continuar",
            show: true
        });

        setTimeout(() => {
            if (!hasMonthlyIncome) {
                navigate("/complete-profile");
            } else {
                navigate("/home");
            }
        }, 1500);

    } catch (error) {
        console.error("Error en registro:", error);
        setSignupAlert({
            type: "error",
            message: error.message || "¡Algo salió mal! Vuelve a intentarlo más tarde",
            show: true
        });
    }
};

const handleLogin = async (e) => {
    e.preventDefault();

    try {
        const response = await loginService(loginData);
        dispatch(setToken(response.access_token));

        const res = await fetch("http://localhost:8000/mindfulhome/users/me", {
            headers: {
                Authorization: `Bearer ${response.access_token}`
            }
        });

        const userData = await res.json();
        dispatch(setUser(userData));
        
        // Verificar si tiene monthly_income
        const hasMonthlyIncome = userData.monthly_income && userData.monthly_income > 0;
        
        if (!hasMonthlyIncome) {
            navigate("/complete-profile");
        } else {
            navigate("/home");
        }

    } catch (error) {
        setLoginAlert({
            type: "error",
            message: "Credenciales inválidas",
            show: true
        });
    }
};


    return (
        <div className={`container ${isActive ? "active" : ""}`} id="container">
            {/* SIGN UP */}
            <div className="form-container sign-up">
                <form onSubmit={handleSignup}>
                    <h1>Tu hogar, bien pensado</h1>
                <div className="form-section">
                    <FloatingInput
                        type="text"
                        id="username"
                        name="username"
                        label="Nombre de usuario"
                        value={signUpData.username}
                        onChange={(e) => setSignUpData({ ...signUpData, username: e.target.value })}
                        required
                    />
                    <FloatingInput
                        type="email"
                        id="email"
                        name="email"
                        label="Correo electrónico"
                        value={signUpData.email}
                        onChange={(e) => setSignUpData({ ...signUpData, email: e.target.value })}
                        required
                    />
                    <FloatingInput
                        type="password"
                        id="password"
                        name="password"
                        label="Contraseña"
                        value={signUpData.password}
                        onChange={(e) => setSignUpData({ ...signUpData, password: e.target.value })}
                        required
                    />
                    </div>

                    {signupAlert.show && (
                        <div className={`form-alert ${signupAlert.type}`}>
                            {signupAlert.message}
                        </div>
                    )}

                    <button type="submit">Regístrate</button>
                    <a href="#" onClick={(e) => { e.preventDefault(); handleLoginClick(); }}>
                        ¿Ya tienes una cuenta? Inicia sesión
                    </a>
                </form>
            </div>

            {/* SIGN IN */}
            <div className="form-container sign-in">
                <form onSubmit={handleLogin}>
                    <h1>Sigue construyendo tu hogar</h1>
                <div className="form-section">

                    <FloatingInput
                        type="email"
                        id="email"
                        name="email"
                        label="Correo electrónico"
                        value={loginData.email}
                        onChange={(e) => setLoginData({ ...loginData, email: e.target.value })}
                        required
                    />
                    <FloatingInput
                        type="password"
                        id="password"
                        name="password"
                        label="Contraseña"
                        value={loginData.password}
                        onChange={(e) => setLoginData({ ...loginData, password: e.target.value })}
                        required
                    />
                        </div>

                    {loginAlert.show && (
                        <div className={`form-alert ${loginAlert.type}`}>
                            {loginAlert.message}
                        </div>
                    )}

                    <button type="submit">Ingresar</button>
                    <a href="#" onClick={(e) => { e.preventDefault(); handleRegisterClick(); }}>
                        ¿No tienes una cuenta? Regístrate
                    </a>
                </form>
            </div>

            {/* TOGGLE */}
            <div className="toggle-container">
                <div className="toggle">
                    <HorizontalCarousel>
                        {/* Slide 1 */}
                        <div className="carousel-content">
                            <img
                                src={imagen1}
                                alt="Bienvenido a Tu Hogar"
                                className="carousel-image"
                            />
                            <div className="carousel-text">
                                <h2>Construye tu hogar con confianza</h2>
                            </div>
                        </div>

                        {/* Slide 2 */}
                        <div className="carousel-content">
                            <img
                                src={imagen2}
                                alt="Ofertas Especiales"
                                className="carousel-image"
                            />
                            <div className="carousel-text">
                                <h2>Decide con claridad, vive con tranquilidad</h2>
                            </div>
                        </div>
                    </HorizontalCarousel>
                </div>
            </div>
        </div>
    );
}