const API_URL = "http://localhost:8000";
const API_PREFIX = "/mindfulhome";

export async function apiFetch(endpoint, options = {}) {
    const token = localStorage.getItem("token");
    
    const url = `${API_URL}${API_PREFIX}${endpoint}`;
    
    const res = await fetch(url, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...(token && { Authorization: `Bearer ${token}` }),
            ...options.headers,
        },
    });

    if (!res.ok) {
        const error = await res.json().catch(() => ({}));
        throw new Error(error.detail || "Error en la petición");
    }

    return res.json();
}