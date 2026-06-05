const API_URL = "http://localhost:8000";
const API_PREFIX = "/mindfulhome";

export async function apiFetch(endpoint, options = {}) {
    const token = localStorage.getItem("token");

    const url = `${API_URL}${API_PREFIX}${endpoint}`;

    let res;
    try {
        res = await fetch(url, {
            ...options,
            headers: {
                "Content-Type": "application/json",
                ...(token && { Authorization: `Bearer ${token}` }),
                ...options.headers,
            },
        });
    } catch (error) {
        throw new Error("No fue posible conectar con el servidor. Verifica que el backend siga encendido e intenta nuevamente.");
    }

    if (!res.ok) {
        const error = await res.json().catch(() => ({}));
        const detail = error.detail;
        const message = typeof detail === "string"
            ? detail
            : Array.isArray(detail)
                ? detail.map(item => item.msg).join(", ")
                : `Error del servidor (${res.status})`;
        const requestError = new Error(message);
        requestError.response = { data: error, status: res.status };
        throw requestError;
    }

    if (res.status === 204) {
        return null;
    }

    return res.json();
}
