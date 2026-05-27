import { apiFetch } from "./api";

export async function runSimulation(scenarioInput) {
    const res = await apiFetch("/simulations/simulate", {
        method: "POST",
        body: JSON.stringify(scenarioInput),
    });
    return res;
}

export async function saveScenario(scenario) {
    const res = await apiFetch("/simulations/scenarios", {
        method: "POST",
        body: JSON.stringify(scenario),
    });
    return res;
}

export async function getWhatIfPresets() {
    const res = await apiFetch("/simulations/whatif/presets", {
        method: "GET",
    });
    return res;
}

export async function applyPlaygroundModifications(modifications, propertyModifications = [], propertyInput = null) {
    const body = {
        modifications: modifications || [],
        property_modifications: propertyModifications || []
    };
    if (propertyInput) {
        body.property_input = propertyInput;
    }
    
    const res = await apiFetch("/simulations/playground/apply", {
        method: "POST",
        body: JSON.stringify(body),
    });
    return res;
}

export async function getScenario(scenarioId) {
    const res = await apiFetch(`/simulations/scenarios/${scenarioId}`, {
        method: "GET",
    });
    return res;
}

export async function getUserScenarios() {
    const res = await apiFetch("/simulations/scenarios", {
        method: "GET",
    });
    return res;
}

export async function deleteScenario(scenarioId) {
    const res = await apiFetch(`/simulations/scenarios/${scenarioId}`, {
        method: "DELETE",
    });
    return res;
}

export async function updateScenario(scenarioId, updates) {
    const res = await apiFetch(`/simulations/scenarios/${scenarioId}`, {
        method: "PATCH",
        body: JSON.stringify(updates),
    });
    return res;
}