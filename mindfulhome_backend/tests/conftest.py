# tests/conftest.py
"""
Shared pytest fixtures.
Uses an in-memory SQLite database to avoid needing a real PostgreSQL instance.
"""
import pytest
import os
import sys
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["TESTING"] = "True"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app.db.base import Base
from app.main import app
from app.api import deps

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Fixture que proporciona una sesión de BD para tests"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()  # Rollback cualquier transacción pendiente
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Fixture para cliente de pruebas FastAPI"""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[deps.get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def registered_user(client):
    """Creates a user and returns their auth token."""
    client.post("/api/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "Test1234!",
    })
    resp = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "Test1234!",
    })
    return resp.json()["access_token"]


@pytest.fixture
def auth_headers(registered_user):
    """Headers con token de autenticación"""
    return {"Authorization": f"Bearer {registered_user}"}


@pytest.fixture
def user_with_profile(client, auth_headers):
    """Creates a user and patches a complete financial profile."""
    client.patch("/api/users/me", json={
        "financial": {
            "monthly_income": 8_000_000,
            "fixed_expenses": 1_000_000,
            "variable_expenses": 600_000,
            "total_savings": 20_000_000,
            "emergency_fund": 10_000_000,
            "monthly_savings_goal": 500_000,
        },
        "labor": {
            "income_type": "EMPLEADO",
            "income_variability": "FIJO",
            "contract_type": "INDEFINIDO",
            "job_seniority_months": 36,
        },
        "debt": {
            "monthly_debt_payments": 300_000,
            "total_debt": 5_000_000,
        },
        "housing": {
            "is_renting": False,
            "monthly_rent": None,
            "rent_mortgage_overlap_months": 0,
        },
        "household": {"dependents": 1},
    }, headers=auth_headers)
    return auth_headers