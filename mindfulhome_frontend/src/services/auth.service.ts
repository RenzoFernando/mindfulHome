import { apiFetch } from "./api";
import type { LoginPayload, RegisterPayload, TokenResponse } from "../types/auth";

export async function register(data: RegisterPayload) {
    const res = await apiFetch<TokenResponse>("/auth/register", {
        method: "POST",
        body: JSON.stringify(data),
    });

    localStorage.setItem("token", res.access_token);
    return res;
}

export async function login(data: LoginPayload) {
    const res = await apiFetch<TokenResponse>("/auth/login", {
        method: "POST",
        body: JSON.stringify(data),
    });

    localStorage.setItem("token", res.access_token);
    return res;
}

export function logout() {
    localStorage.removeItem("token");
}