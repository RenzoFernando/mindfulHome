"""Integration tests for auth endpoints."""
import pytest


class TestRegister:
    def test_register_success(self, client):
        resp = client.post("/api/auth/register", json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "Pass1234!",
        })
        assert resp.status_code == 201
        assert "access_token" in resp.json()

    def test_register_duplicate_email(self, client):
        payload = {"username": "user1", "email": "dup@example.com", "password": "Pass1234!"}
        client.post("/api/auth/register", json=payload)
        payload["username"] = "user2"
        resp = client.post("/api/auth/register", json=payload)
        assert resp.status_code == 400

    def test_register_duplicate_username(self, client):
        payload = {"username": "sameuser", "email": "a@example.com", "password": "Pass1234!"}
        client.post("/api/auth/register", json=payload)
        payload["email"] = "b@example.com"
        resp = client.post("/api/auth/register", json=payload)
        assert resp.status_code == 400


class TestLogin:
    def test_login_success(self, client):
        client.post("/api/auth/register", json={
            "username": "loginuser",
            "email": "login@example.com",
            "password": "Pass1234!",
        })
        resp = client.post("/api/auth/login", json={
            "email": "login@example.com",
            "password": "Pass1234!",
        })
        assert resp.status_code == 200
        assert resp.json()["token_type"] == "bearer"

    def test_login_wrong_password(self, client):
        client.post("/api/auth/register", json={
            "username": "loginuser2",
            "email": "login2@example.com",
            "password": "Pass1234!",
        })
        resp = client.post("/api/auth/login", json={
            "email": "login2@example.com",
            "password": "WrongPass!",
        })
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client):
        resp = client.post("/api/auth/login", json={
            "email": "ghost@example.com",
            "password": "Any1234!",
        })
        assert resp.status_code == 401
