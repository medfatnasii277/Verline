"""
Test authentication endpoints
"""
import pytest
from fastapi.testclient import TestClient

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["version"] == "1.0.0"

def test_register_artist(client):
    """Test user registration - artist"""
    user_data = {
        "username": "new_artist",
        "email": "new_artist@test.com",
        "password": "testpass123",
        "full_name": "New Test Artist",
        "role": "artist",
        "bio": "New artist registration test"
    }
    
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert data["role"] == "artist"

def test_register_enthusiast(client):
    """Test user registration - enthusiast"""
    user_data = {
        "username": "new_enthusiast",
        "email": "new_enthusiast@test.com",
        "password": "testpass123",
        "full_name": "New Test Enthusiast",
        "role": "enthusiast",
        "bio": "New enthusiast registration test"
    }
    
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["role"] == "enthusiast"

def test_register_duplicate_username(client):
    """Test registration with duplicate username"""
    user_data = {
        "username": "test_artist",  # Already exists
        "email": "duplicate@test.com",
        "password": "testpass123",
        "full_name": "Duplicate User"
    }
    
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 400

def test_register_duplicate_email(client):
    """Test registration with duplicate email"""
    user_data = {
        "username": "unique_user",
        "email": "artist@test.com",  # Already exists
        "password": "testpass123",
        "full_name": "Duplicate Email"
    }
    
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 400

def test_login_success(client):
    """Test successful login"""
    login_data = {
        "username": "test_artist",
        "password": "testpass123"
    }
    
    response = client.post("/auth/login", data=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client):
    """Test login with invalid credentials"""
    login_data = {
        "username": "test_artist",
        "password": "wrongpassword"
    }
    
    response = client.post("/auth/login", data=login_data)
    assert response.status_code == 401

def test_login_nonexistent_user(client):
    """Test login with nonexistent user"""
    login_data = {
        "username": "nonexistent",
        "password": "testpass123"
    }
    
    response = client.post("/auth/login", data=login_data)
    assert response.status_code == 401
