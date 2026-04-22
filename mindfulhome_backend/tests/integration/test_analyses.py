"""Integration tests for analyses endpoints."""
import pytest
from unittest.mock import patch

PROPERTY_PAYLOAD = {
    "property_price": 300_000_000,
    "down_payment": 60_000_000,
    "annual_interest_rate": 12.0,
    "interest_rate_type": "FIJA",
    "loan_term_years": 20,
}

MOCK_LLM = {
    "summary": {"status": "MODERATE", "message": "Análisis de prueba"},
    "global_analysis": {"financial_health_score": 55, "main_problem": "test", "secondary_problems": []},
    "insights": [],
    "risks": [],
    "recommendations": [],
    "uiHints": {"primaryMetric": "housingRatio", "attentionAreas": []},
}


class TestCreateAnalysis:
    @patch("app.services.llm.analyze_with_llm", return_value=MOCK_LLM)
    def test_create_analysis_success(self, mock_llm, client, user_with_profile):
        resp = client.post("/api/analyses", json=PROPERTY_PAYLOAD, headers=user_with_profile)
        assert resp.status_code == 201
        data = resp.json()
        assert "mortgage" in data
        assert "cashflow" in data
        assert "ratios" in data
        assert data["mortgage"]["loan_amount"] == 240_000_000

    def test_create_analysis_without_profile_fails(self, client, auth_headers):
        resp = client.post("/api/analyses", json=PROPERTY_PAYLOAD, headers=auth_headers)
        assert resp.status_code == 422

    def test_create_analysis_unauthenticated(self, client):
        resp = client.post("/api/analyses", json=PROPERTY_PAYLOAD)
        assert resp.status_code == 403

    def test_down_payment_exceeds_price_fails(self, client, user_with_profile):
        bad = {**PROPERTY_PAYLOAD, "down_payment": 400_000_000}
        resp = client.post("/api/analyses", json=bad, headers=user_with_profile)
        assert resp.status_code == 422

    def test_negative_rate_fails(self, client, user_with_profile):
        bad = {**PROPERTY_PAYLOAD, "annual_interest_rate": -5.0}
        resp = client.post("/api/analyses", json=bad, headers=user_with_profile)
        assert resp.status_code == 422


class TestListAnalyses:
    @patch("app.services.llm.analyze_with_llm", return_value=MOCK_LLM)
    def test_list_returns_only_own_analyses(self, mock_llm, client, user_with_profile):
        client.post("/api/analyses", json=PROPERTY_PAYLOAD, headers=user_with_profile)
        client.post("/api/analyses", json=PROPERTY_PAYLOAD, headers=user_with_profile)
        resp = client.get("/api/analyses", headers=user_with_profile)
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_list_empty_for_new_user(self, client, auth_headers):
        resp = client.get("/api/analyses", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []


class TestGetAnalysis:
    @patch("app.services.llm.analyze_with_llm", return_value=MOCK_LLM)
    def test_get_by_id(self, mock_llm, client, user_with_profile):
        create_resp = client.post("/api/analyses", json=PROPERTY_PAYLOAD, headers=user_with_profile)
        analysis_id = create_resp.json()["id"]
        resp = client.get(f"/api/analyses/{analysis_id}", headers=user_with_profile)
        assert resp.status_code == 200
        assert resp.json()["id"] == analysis_id

    def test_get_nonexistent_returns_404(self, client, auth_headers):
        resp = client.get("/api/analyses/9999", headers=auth_headers)
        assert resp.status_code == 404


class TestDeleteAnalysis:
    @patch("app.services.llm.analyze_with_llm", return_value=MOCK_LLM)
    def test_delete_analysis(self, mock_llm, client, user_with_profile):
        create_resp = client.post("/api/analyses", json=PROPERTY_PAYLOAD, headers=user_with_profile)
        analysis_id = create_resp.json()["id"]
        del_resp = client.delete(f"/api/analyses/{analysis_id}", headers=user_with_profile)
        assert del_resp.status_code == 204
        get_resp = client.get(f"/api/analyses/{analysis_id}", headers=user_with_profile)
        assert get_resp.status_code == 404
