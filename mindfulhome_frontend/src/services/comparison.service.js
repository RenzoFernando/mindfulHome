import { apiFetch } from "./api";

export async function compareScenarios({ scenario_a_id, scenario_b_id, temporal_scenario }) {
    const queryParams = new URLSearchParams();
    if (scenario_a_id) queryParams.append("scenario_a_id", scenario_a_id);
    if (scenario_b_id) queryParams.append("scenario_b_id", scenario_b_id);
    
    const queryString = queryParams.toString();
    const url = queryString ? `/comparison/compare?${queryString}` : "/comparison/compare";
    
    const res = await apiFetch(url, {
        method: "POST",
        body: temporal_scenario ? JSON.stringify(temporal_scenario) : undefined,
    });
    return res;
}

export async function compareSavedScenarios(scenario_a_id, scenario_b_id) {
    const res = await apiFetch(`/comparison/compare/${scenario_a_id}/${scenario_b_id}`, {
        method: "GET",
    });
    return res;
}

export async function compareWithCurrent(scenario_id) {
    const res = await apiFetch(`/comparison/compare/current?scenario_id=${scenario_id}`, {
        method: "POST",
    });
    return res;
}

export async function compareWithTemporal(temporal_scenario) {
    const res = await apiFetch("/comparison/compare", {
        method: "POST",
        body: JSON.stringify(temporal_scenario),
    });
    return res;
}

export async function compareMultipleScenarios(scenarioIds) {
    const res = await apiFetch("/comparison/compare/multiple", {
        method: "POST",
        body: JSON.stringify({ scenario_ids: scenarioIds }),
    });
    return res;
}

export async function getComparisonSummary(scenario_a_id, scenario_b_id) {
    const res = await apiFetch(`/comparison/summary/${scenario_a_id}/${scenario_b_id}`, {
        method: "GET",
    });
    return res;
}

export async function exportComparison(comparisonResult, format = "pdf") {
    const res = await apiFetch(`/comparison/export?format=${format}`, {
        method: "POST",
        body: JSON.stringify(comparisonResult),
        headers: {
            "Accept": format === "pdf" ? "application/pdf" : "text/csv",
        },
    });
    return res.blob();
}