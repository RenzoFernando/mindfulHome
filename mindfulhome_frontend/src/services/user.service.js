import { apiFetch } from "./api";

export async function getMe() {
    return apiFetch<User>("/users/me");
}

export async function updateProfile(data) {
    return apiFetch<User>("/users/me", {
        method: "PATCH",
        body: JSON.stringify(data),
    });
}