import pytest
from pydantic import ValidationError

from app.schemas.auth import RegisterRequest, LoginRequest


def test_register_request_valid():
    req = RegisterRequest(
        email="user@example.com",
        username="testuser",
        password="Password123",
    )
    assert req.email == "user@example.com"
    assert req.username == "testuser"


def test_register_request_invalid_email():
    with pytest.raises(ValidationError):
        RegisterRequest(email="not-an-email", username="testuser", password="Password123")


def test_register_request_short_username():
    with pytest.raises(ValidationError):
        RegisterRequest(email="user@example.com", username="ab", password="Password123")


def test_register_request_invalid_username_chars():
    with pytest.raises(ValidationError):
        RegisterRequest(email="user@example.com", username="user!@#", password="Password123")


def test_register_request_weak_password():
    with pytest.raises(ValidationError):
        RegisterRequest(email="user@example.com", username="testuser", password="weak")


def test_login_request_valid():
    req = LoginRequest(email="user@example.com", password="Password123")
    assert req.email == "user@example.com"


def test_login_request_invalid_email():
    with pytest.raises(ValidationError):
        LoginRequest(email="not-email", password="Password123")
