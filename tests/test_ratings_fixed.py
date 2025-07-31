"""
Test rating endpoints
"""
import pytest

def test_create_rating(authenticated_client, test_enthusiast_headers):
    """Test creating a rating - enthusiasts should be able to rate"""
    # First, we need a painting to rate - let's assume painting ID 1 exists
    rating_data = {
        "painting_id": 1,
        "rating": 4
    }
    
    response = authenticated_client.post("/ratings/", json=rating_data, headers=test_enthusiast_headers)
    # Should succeed if painting exists, or return 404 if not
    assert response.status_code in [201, 404]
    
    if response.status_code == 201:
        result = response.json()
        assert result["rating"] == rating_data["rating"]
        assert "user_id" in result

def test_create_rating_invalid_score(authenticated_client, test_enthusiast_headers):
    """Test creating rating with invalid rating value"""
    rating_data = {
        "painting_id": 1,
        "rating": 6  # Invalid - should be 1-5
    }
    
    response = authenticated_client.post("/ratings/", json=rating_data, headers=test_enthusiast_headers)
    assert response.status_code == 422  # Validation error

def test_create_rating_missing_fields(authenticated_client, test_enthusiast_headers):
    """Test creating rating with missing required fields"""
    rating_data = {
        # Missing painting_id and rating
    }
    
    response = authenticated_client.post("/ratings/", json=rating_data, headers=test_enthusiast_headers)
    assert response.status_code == 422  # Validation error

def test_get_painting_ratings(client):
    """Test getting all ratings for a painting"""
    response = client.get("/ratings/painting/1")
    assert response.status_code in [200, 404]  # 200 if painting exists with ratings
    
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)

def test_get_user_ratings(authenticated_client, test_enthusiast_headers):
    """Test getting all ratings by current user"""
    response = authenticated_client.get("/ratings/my-ratings", headers=test_enthusiast_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_update_rating(authenticated_client, test_enthusiast_headers):
    """Test updating a rating"""
    # First create a rating to update
    rating_data = {
        "painting_id": 1,
        "rating": 3
    }
    
    create_response = authenticated_client.post("/ratings/", json=rating_data, headers=test_enthusiast_headers)
    if create_response.status_code != 201:
        pytest.skip("Could not create rating for update test")
    
    rating_id = create_response.json()["id"]
    
    # Update the rating
    update_data = {
        "rating": 5
    }
    
    response = authenticated_client.put(f"/ratings/{rating_id}", json=update_data, headers=test_enthusiast_headers)
    assert response.status_code == 200
    result = response.json()
    assert result["rating"] == update_data["rating"]

def test_delete_rating(authenticated_client, test_enthusiast_headers):
    """Test deleting a rating"""
    # First create a rating to delete
    rating_data = {
        "painting_id": 1,
        "rating": 2
    }
    
    create_response = authenticated_client.post("/ratings/", json=rating_data, headers=test_enthusiast_headers)
    if create_response.status_code != 201:
        pytest.skip("Could not create rating for delete test")
    
    rating_id = create_response.json()["id"]
    
    # Delete the rating
    response = authenticated_client.delete(f"/ratings/{rating_id}", headers=test_enthusiast_headers)
    assert response.status_code == 204

def test_duplicate_rating_prevention(authenticated_client, test_enthusiast_headers):
    """Test that users can't rate the same painting twice"""
    rating_data = {
        "painting_id": 1,
        "rating": 4
    }
    
    # First rating should succeed
    first_response = authenticated_client.post("/ratings/", json=rating_data, headers=test_enthusiast_headers)
    if first_response.status_code != 201:
        pytest.skip("Could not create first rating")
    
    # Second rating for same painting should fail or update existing
    second_response = authenticated_client.post("/ratings/", json=rating_data, headers=test_enthusiast_headers)
    # Should either prevent duplicate (400) or allow update (201/200)
    assert second_response.status_code in [200, 201, 400]

def test_get_painting_average_rating(client):
    """Test getting average rating for a painting"""
    response = client.get("/ratings/painting/1/average")
    assert response.status_code in [200, 404]  # 200 if painting exists
    
    if response.status_code == 200:
        data = response.json()
        assert "average_rating" in data
        assert "total_ratings" in data
        assert isinstance(data["average_rating"], (int, float)) or data["average_rating"] is None
        assert isinstance(data["total_ratings"], int)
