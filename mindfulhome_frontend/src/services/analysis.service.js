import { apiFetch } from "./api";

export async function createAnalysis(data) {
    return apiFetch("/analyses", {
        method: "POST",
        body: JSON.stringify(data),
    });
}

export async function getAnalyses() {
    return apiFetch("/analyses");
}

export async function getAnalysis(id) {
    return apiFetch(`/analyses/${id}`);
}

export async function deleteAnalysis(id) {
    return apiFetch(`/analyses/${id}`, {
        method: "DELETE",
    });
}