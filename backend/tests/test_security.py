"""
Tests for security utilities.
"""

import pytest
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token,
    generate_secure_token,
    generate_api_key,
)


class TestPasswordHashing:
    """Tests for password hashing functions."""

    def test_hash_password_returns_hash(self):
        """Test that hashing returns a bcrypt hash."""
        password = "test-password-123"
        hashed = get_password_hash(password)

        assert hashed is not None
        assert hashed != password
        assert hashed.startswith("$2b$")  # bcrypt prefix

    def test_verify_correct_password(self):
        """Test that correct password verification succeeds."""
        password = "test-password-123"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_incorrect_password(self):
        """Test that incorrect password verification fails."""
        password = "test-password-123"
        wrong_password = "wrong-password"
        hashed = get_password_hash(password)

        assert verify_password(wrong_password, hashed) is False

    def test_different_hashes_for_same_password(self):
        """Test that same password produces different hashes (salt)."""
        password = "test-password-123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        assert hash1 != hash2
        # But both should verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestTokens:
    """Tests for JWT token functions."""

    def test_create_access_token(self):
        """Test access token creation."""
        data = {"sub": "testuser"}
        secret = "test-secret"
        token = create_access_token(data, secret)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_valid_token(self):
        """Test decoding a valid token."""
        data = {"sub": "testuser"}
        secret = "test-secret"
        token = create_access_token(data, secret)

        decoded = decode_access_token(token, secret)

        assert decoded is not None
        assert decoded.username == "testuser"

    def test_decode_invalid_token(self):
        """Test decoding an invalid token returns None."""
        secret = "test-secret"
        invalid_token = "invalid.token.here"

        decoded = decode_access_token(invalid_token, secret)

        assert decoded is None

    def test_decode_wrong_secret(self):
        """Test decoding with wrong secret returns None."""
        data = {"sub": "testuser"}
        token = create_access_token(data, "correct-secret")

        decoded = decode_access_token(token, "wrong-secret")

        assert decoded is None


class TestSecureTokens:
    """Tests for random token generation."""

    def test_generate_secure_token_default_length(self):
        """Test secure token generation with default length."""
        token = generate_secure_token()

        assert token is not None
        assert len(token) == 64  # 32 bytes = 64 hex chars

    def test_generate_secure_token_custom_length(self):
        """Test secure token generation with custom length."""
        token = generate_secure_token(16)

        assert len(token) == 32  # 16 bytes = 32 hex chars

    def test_generate_unique_tokens(self):
        """Test that generated tokens are unique."""
        token1 = generate_secure_token()
        token2 = generate_secure_token()

        assert token1 != token2

    def test_generate_api_key_format(self):
        """Test API key has correct format."""
        api_key = generate_api_key()

        assert api_key.startswith("ca_")
        assert len(api_key) > 10
