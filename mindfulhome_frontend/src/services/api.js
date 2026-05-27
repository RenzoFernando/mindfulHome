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
        const message = typeof error.detail === "string" ? error.detail : "Error en la petición";
        const requestError = new Error(message);
        requestError.response = { data: error };
        throw requestError;
    }

    if (res.status === 204) {
        return null;
    }

    return res.json();
}
