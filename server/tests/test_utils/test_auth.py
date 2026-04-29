import pytest
from app.utils.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)


def test_hash_and_verify_password():
    password = "MyPassword123"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword123", hashed) is False


def test_create_access_token():
    token = create_access_token(user_id="test-uuid", email="user@example.com")
    assert isinstance(token, str)
    payload = decode_token(token)
    assert payload["sub"] == "test-uuid"
    assert payload["email"] == "user@example.com"
    assert payload["type"] == "access"


def test_create_refresh_token():
    token = create_refresh_token(user_id="test-uuid")
    payload = decode_token(token)
    assert payload["sub"] == "test-uuid"
    assert payload["type"] == "refresh"


def test_decode_expired_token():
    token = create_access_token(
        user_id="test-uuid", email="user@example.com", expires_minutes=-1
    )
    with pytest.raises(ValueError):
        decode_token(token)


def test_decode_invalid_token():
    with pytest.raises(ValueError):
        decode_token("invalid.token.string")
