"""Integration tests for user profile endpoints."""
import pytest


class TestGetMe:
    def test_get_me_authenticated(self, client, auth_headers):
        resp = client.get("/api/users/me", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["email"] == "test@example.com"

    def test_get_me_unauthenticated(self, client):
        resp = client.get("/api/users/me")
        assert resp.status_code == 403

    def test_get_me_invalid_token(self, client):
        resp = client.get("/api/users/me", headers={"Authorization": "Bearer bad.token"})
        assert resp.status_code == 401


class TestUpdateProfile:
    def test_update_financial_profile(self, client, auth_headers):
        resp = client.patch("/api/users/me", json={
            "financial": {"monthly_income": 5_000_000, "fixed_expenses": 800_000, "variable_expenses": 400_000}
        }, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["monthly_income"] == 5_000_000
        assert data["fixed_expenses"] == 800_000

    def test_update_labor_profile(self, client, auth_headers):
        resp = client.patch("/api/users/me", json={
            "labor": {"income_type": "EMPLEADO", "contract_type": "INDEFINIDO", "job_seniority_months": 24}
        }, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["income_type"] == "EMPLEADO"

    def test_update_debt_profile(self, client, auth_headers):
        resp = client.patch("/api/users/me", json={
            "debt": {"monthly_debt_payments": 400_000, "total_debt": 8_000_000}
        }, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["monthly_debt_payments"] == 400_000

    def test_update_housing_renting(self, client, auth_headers):
        resp = client.patch("/api/users/me", json={
            "housing": {"is_renting": True, "monthly_rent": 1_200_000, "rent_mortgage_overlap_months": 2}
        }, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["is_renting"] is True

    def test_update_household(self, client, auth_headers):
        resp = client.patch("/api/users/me", json={
            "household": {"dependents": 3}
        }, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["dependents"] == 3

    def test_partial_update_preserves_other_fields(self, client, auth_headers):
        client.patch("/api/users/me", json={
            "financial": {"monthly_income": 6_000_000, "fixed_expenses": 900_000, "variable_expenses": 400_000}
        }, headers=auth_headers)
        client.patch("/api/users/me", json={
            "household": {"dependents": 2}
        }, headers=auth_headers)
        resp = client.get("/api/users/me", headers=auth_headers)
        assert resp.json()["monthly_income"] == 6_000_000
        assert resp.json()["dependents"] == 2
