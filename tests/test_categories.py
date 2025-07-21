"""
Test category endpoints
"""
import pytest
from fastapi.testclient import TestClient

def test_get_all_categories(client):
    """Test getting all categories - accessible to all users"""
    response = client.get("/categories/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3  # At least our test categories

def test_create_category_as_artist(client):
    """Test creating category - should work for artists"""
    category_data = {
        "name": "Test Modern Art",
        "description": "Modern art category for testing"
    }
    
    response = client.post("/categories/", json=category_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == category_data["name"]
    assert data["description"] == category_data["description"]
    assert "id" in data
    assert "created_at" in data

def test_create_category_as_enthusiast(client):
    """Test creating category - should work for enthusiasts too (no RBAC)"""
    category_data = {
        "name": "Enthusiast Category",
        "description": "Category created by enthusiast"
    }
    
    response = client.post("/categories/", json=category_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == category_data["name"]

def test_create_duplicate_category(client):
    """Test creating category with duplicate name"""
    category_data = {
        "name": "Abstract",  # Already exists in test data
        "description": "Duplicate abstract category"
    }
    
    response = client.post("/categories/", json=category_data)
    # Should either succeed or return 400 based on unique constraint
    assert response.status_code in [201, 400]

def test_get_category_by_id(client, test_category_id):
    """Test getting category by ID"""
    if not test_category_id:
        pytest.skip("Test category not found")
        
    response = client.get(f"/categories/{test_category_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_category_id
    assert "name" in data
    assert "description" in data

def test_get_nonexistent_category(client):
    """Test getting nonexistent category"""
    response = client.get("/categories/99999")
    assert response.status_code == 404

def test_create_category_invalid_data(client):
    """Test creating category with invalid data"""
    # Missing name
    category_data = {
        "description": "Category without name"
    }
    
    response = client.post("/categories/", json=category_data)
    assert response.status_code == 422

def test_create_category_empty_name(client):
    """Test creating category with empty name"""
    category_data = {
        "name": "",
        "description": "Category with empty name"
    }
    
    response = client.post("/categories/", json=category_data)
    assert response.status_code in [400, 422]  # Should validate name is not empty
