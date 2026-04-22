import { apiFetch } from "./api";
import type { User } from "../types/user";

export async function getMe() {
    return apiFetch<User>("/users/me");
}

export async function updateProfile(data: any) {
    return apiFetch<User>("/users/me", {
        method: "PATCH",
        body: JSON.stringify(data),
    });
}