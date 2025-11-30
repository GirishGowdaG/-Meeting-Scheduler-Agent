"""
Basic Tests
Simple tests to verify setup and core functionality
"""
import pytest
from fastapi.testclient import TestClient
import sys
sys.path.append(".")

from main import app
from app.utils.encryption import encryption_service
from app.utils.jwt import create_access_token, decode_access_token
from uuid import uuid4


client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint returns healthy status"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_encryption_roundtrip():
    """Test encryption and decryption"""
    original = "test_secret_token_12345"
    encrypted = encryption_service.encrypt(original)
    decrypted = encryption_service.decrypt(encrypted)
    
    assert encrypted != original
    assert decrypted == original


def test_jwt_roundtrip():
    """Test JWT creation and validation"""
    user_id = uuid4()
    token = create_access_token(user_id)
    decoded_id = decode_access_token(token)
    
    assert decoded_id == user_id


def test_invalid_jwt():
    """Test invalid JWT returns None"""
    invalid_token = "invalid.jwt.token"
    result = decode_access_token(invalid_token)
    
    assert result is None


def test_google_login_endpoint():
    """Test Google login endpoint returns auth URL"""
    response = client.get("/auth/google/login")
    assert response.status_code == 200
    assert "auth_url" in response.json()
    assert "accounts.google.com" in response.json()["auth_url"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
