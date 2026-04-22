import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import { jwtDecode } from "jwt-decode";
import { setUserData, clearUserData } from "../features/userSlice";
import { login as loginService, register as registerService } from "../services/auth";
import "../styles/auth.css";
import FloatingInput from "../components/FloatingInput";
import VerticalCarousel from "../components/VerticalCarousel";

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
                // Verificar si el token no ha expirado
                if (decoded.exp && decoded.exp * 1000 > Date.now()) {
                    dispatch(setUserData({
                        token: token,
                        id: decoded.sub || decoded.id,
                        username: decoded.username || decoded.name,
                        email: decoded.email,
                        role: decoded.role || decoded.authorities?.[0]
                    }));
                    navigate("/home");
                } else {
                    // Token expirado, limpiar
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
            
            // Decodificar el token para obtener la información del usuario
            const decoded = jwtDecode(response.access_token);
            
            dispatch(setUserData({
                token: response.access_token,
                id: decoded.sub || decoded.id,
                username: signUpData.username,
                email: signUpData.email,
                role: decoded.role || "user"
            }));
            
            setSignupAlert({
                type: "success",
                message: "¡Cuenta creada con éxito! Redirigiendo...",
                show: true
            });
            
            // Redirigir después de 1.5 segundos
            setTimeout(() => {
                navigate("/home");
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
            const response = await loginService({
                email: loginData.email,
                password: loginData.password,
            });
            
            // Decodificar el token
            const decoded = jwtDecode(response.access_token);
            
            dispatch(setUserData({
                token: response.access_token,
                id: decoded.sub || decoded.id,
                username: decoded.username,
                email: loginData.email,
                role: decoded.role || "user"
            }));
            
            setLoginAlert({
                type: "success",
                message: "¡Inicio de sesión exitoso! Redirigiendo...",
                show: true
            });
            
            // Redirigir después de 1 segundo
            setTimeout(() => {
                navigate("/home");
            }, 1000);
            
        } catch (error) {
            console.error("Error en login:", error);
            setLoginAlert({
                type: "error",
                message: error.message || "Credenciales inválidas. Verifica tu correo y contraseña.",
                show: true
            });
        }
    };

    return (
        <div className={`container ${isActive ? "active" : ""}`} id="container">
            {/* SIGN UP */}
            <div className="form-container sign-up">
                <form onSubmit={handleSignup}>
                    <h1>Hoy es un buen día para empezar</h1>

                    <FloatingInput
                        type="text"
                        id="username"
                        name="username"
                        label="Nombre de usuario"
                        value={signUpData.username}
                        onChange={(e) => setSignUpData({...signUpData, username: e.target.value})}
                        required
                    />

                    <FloatingInput
                        type="email"
                        id="email"
                        name="email"
                        label="Correo electrónico"
                        value={signUpData.email}
                        onChange={(e) => setSignUpData({...signUpData, email: e.target.value})}
                        required
                    />

                    <FloatingInput
                        type="password"
                        id="password"
                        name="password"
                        label="Contraseña"
                        value={signUpData.password}
                        onChange={(e) => setSignUpData({...signUpData, password: e.target.value})}
                        required
                    />

                    {signupAlert.show && (
                        <div className={`form-alert ${signupAlert.type}`}>
                            {signupAlert.message}
                        </div>
                    )}

                    <button type="submit">Regístrate</button>
                    <a href="#" onClick={(e) => {e.preventDefault(); handleLoginClick();}}>
                        ¿Ya tienes una cuenta? Inicia sesión
                    </a>
                </form>
            </div>

            {/* SIGN IN */}
            <div className="form-container sign-in">
                <form onSubmit={handleLogin}>
                    <h1>¡Vamos a movernos!</h1>
                    
                    <FloatingInput
                        type="email"
                        id="email"
                        name="email"
                        label="Correo electrónico"
                        value={loginData.email}
                        onChange={(e) => setLoginData({...loginData, email: e.target.value})}
                        required
                    />

                    <FloatingInput
                        type="password"
                        id="password"
                        name="password"
                        label="Contraseña"
                        value={loginData.password}
                        onChange={(e) => setLoginData({...loginData, password: e.target.value})}
                        required
                    />

                    {loginAlert.show && (
                        <div className={`form-alert ${loginAlert.type}`}>
                            {loginAlert.message}
                        </div>
                    )}

                    <button type="submit">Ingresar</button>
                    <a href="#" onClick={(e) => {e.preventDefault(); handleRegisterClick();}}>
                        ¿No tienes una cuenta? Regístrate
                    </a>
                </form>
            </div>

            {/* TOGGLE */}
            <div className="toggle-container">
                <div className="toggle">
                    <VerticalCarousel />
                </div>
            </div>
        </div>
    );
}