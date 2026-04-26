import { apiFetch } from "./api";

export async function register(data) {
    const res = await apiFetch("/auth/register", {
        method: "POST",
        body: JSON.stringify(data),
    });

    localStorage.setItem("token", res.access_token);
    return res;
}

export async function login(data) {
    const res = await apiFetch("/auth/login", {
        method: "POST",
        body: JSON.stringify(data),
    });

    localStorage.setItem("token", res.access_token);
    return res;
}

export function logout() {
    localStorage.removeItem("token");
}