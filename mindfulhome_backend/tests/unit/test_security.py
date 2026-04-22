"""Unit tests for JWT security utilities."""
import pytest
from datetime import timedelta
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_token,
)


class TestPasswordHashing:
    def test_hash_is_different_from_plain(self):
        hashed = get_password_hash("mysecret")
        assert hashed != "mysecret"

    def test_verify_correct_password(self):
        hashed = get_password_hash("mysecret")
        assert verify_password("mysecret", hashed) is True

    def test_verify_wrong_password(self):
        hashed = get_password_hash("mysecret")
        assert verify_password("wrongpassword", hashed) is False

    def test_two_hashes_of_same_password_differ(self):
        h1 = get_password_hash("mysecret")
        h2 = get_password_hash("mysecret")
        assert h1 != h2  # bcrypt uses random salt


class TestJWT:
    def test_create_and_decode_token(self):
        token = create_access_token({"sub": "42"})
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "42"

    def test_invalid_token_returns_none(self):
        assert decode_token("not.a.valid.token") is None

    def test_expired_token_returns_none(self):
        token = create_access_token({"sub": "1"}, expires_delta=timedelta(seconds=-1))
        assert decode_token(token) is None

    def test_token_contains_exp(self):
        token = create_access_token({"sub": "1"})
        payload = decode_token(token)
        assert "exp" in payload
