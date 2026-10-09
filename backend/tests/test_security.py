"""
Tests for Security Module
"""
import pytest
from datetime import timedelta
from unittest.mock import patch, MagicMock

from backend.app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_token,
)
from backend.app.config import settings


class TestPasswordHashing:
    """Test password hashing and verification."""

    def test_hash_and_verify(self):
        """Test password hashing and verification."""
        password = "TestPassword123!"
        hashed = get_password_hash(password)

        assert hashed != password
        assert verify_password(password, hashed) is True
        assert verify_password("WrongPassword", hashed) is False

    def test_different_hashes_for_same_password(self):
        """Test that bcrypt generates different hashes for same password."""
        password = "TestPassword123!"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        assert hash1 != hash2  # Different salts
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestJWTTokens:
    """Test JWT token creation and decoding."""

    def test_create_access_token(self):
        """Test creating an access token."""
        data = {"sub": "user-id", "role": "USER"}
        token = create_access_token(data, expires_delta=timedelta(minutes=15))

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_valid_token(self):
        """Test decoding a valid token."""
        data = {"sub": "user-id", "role": "USER"}
        token = create_access_token(data)

        payload = decode_token(token)

        assert payload["sub"] == "user-id"
        assert payload["role"] == "USER"
        assert "exp" in payload

    def test_decode_expired_token(self):
        """Test decoding an expired token raises error."""
        data = {"sub": "user-id", "role": "USER"}
        token = create_access_token(data, expires_delta=timedelta(seconds=-1))

        with pytest.raises(Exception):  # HTTPException from decode_token
            decode_token(token)

    def test_decode_invalid_token(self):
        """Test decoding an invalid token raises error."""
        with pytest.raises(Exception):
            decode_token("invalid.token.string")

    def test_decode_tampered_token(self):
        """Test decoding a tampered token raises error."""
        data = {"sub": "user-id", "role": "USER"}
        token = create_access_token(data)

        # Tamper with the token
        tampered = token[:-5] + "xxxxx"

        with pytest.raises(Exception):
            decode_token(tampered)


class TestTokenExpiry:
    """Test token expiry behavior."""

    def test_custom_expiry(self):
        """Test custom expiry time."""
        data = {"sub": "user-id"}
        token = create_access_token(data, expires_delta=timedelta(hours=1))

        payload = decode_token(token)

        # Should expire in about 1 hour
        import time
        now = int(time.time())
        assert payload["exp"] > now + 3500  # ~1 hour
        assert payload["exp"] < now + 3700

    def test_default_expiry(self):
        """Test default expiry from settings."""
        data = {"sub": "user-id"}
        token = create_access_token(data)

        payload = decode_token(token)

        import time
        now = int(time.time())
        expected = now + settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        assert abs(payload["exp"] - expected) < 10  # Within 10 seconds