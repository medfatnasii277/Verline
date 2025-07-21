"""
Test user endpoints
"""
import pytest
from fastapi.testclient import TestClient

def test_get_all_users(client):
    """Test getting all users - accessible to all"""
    response = client.get("/users/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2  # At least test_artist and test_enthusiast

def test_get_all_users_filter_by_role(client):
    """Test getting users filtered by role"""
    # Test getting only artists
    response = client.get("/users/?role=artist")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for user in data:
        assert user["role"] == "artist"

    # Test getting only enthusiasts  
    response = client.get("/users/?role=enthusiast")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for user in data:
        assert user["role"] == "enthusiast"

def test_get_artists_only(client):
    """Test getting artists only endpoint"""
    response = client.get("/users/artists")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for user in data:
        assert user["role"] == "artist"

def test_get_user_by_id(client, test_artist_id):
    """Test getting user by ID"""
    if not test_artist_id:
        pytest.skip("Test artist not found")
        
    response = client.get(f"/users/{test_artist_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_artist_id
    assert "email" in data
    assert "username" in data

def test_get_user_profile(client, test_artist_id):
    """Test getting user profile (me endpoint)"""
    if not test_artist_id:
        pytest.skip("Test artist not found")
        
    response = client.get(f"/users/me/{test_artist_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_artist_id

def test_update_user_profile(client, test_artist_id):
    """Test updating user profile"""
    if not test_artist_id:
        pytest.skip("Test artist not found")
        
    update_data = {
        "full_name": "Updated Test Artist",
        "bio": "Updated bio for testing"
    }
    
    response = client.put(f"/users/me/{test_artist_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == update_data["full_name"]
    assert data["bio"] == update_data["bio"]

def test_get_user_paintings(client, test_artist_id):
    """Test getting user's paintings"""
    if not test_artist_id:
        pytest.skip("Test artist not found")
        
    response = client.get(f"/users/{test_artist_id}/paintings")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)

def test_get_nonexistent_user(client):
    """Test getting nonexistent user"""
    response = client.get("/users/99999")
    assert response.status_code == 404
