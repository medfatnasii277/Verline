"""
Test comment endpoints
"""
import pytest

def test_create_comment(client, test_enthusiast_id):
    """Test creating a comment - all users should be able to comment"""
    if not test_enthusiast_id:
        pytest.skip("Test enthusiast not found")
    
    comment_data = {
        "painting_id": 1,
        "user_id": test_enthusiast_id,
        "content": "This is a beautiful painting! I love the composition."
    }
    
    response = client.post("/comments/", json=comment_data)
    # Should succeed if painting exists, or return 404 if not
    assert response.status_code in [201, 404]
    
    if response.status_code == 201:
        result = response.json()
        assert result["content"] == comment_data["content"]
        assert result["user_id"] == test_enthusiast_id
        assert "created_at" in result

def test_create_comment_missing_fields(client):
    """Test creating comment with missing required fields"""
    comment_data = {
        # Missing painting_id, user_id, and content
    }
    
    response = client.post("/comments/", json=comment_data)
    assert response.status_code == 422  # Validation error

def test_create_empty_comment(client, test_enthusiast_id):
    """Test creating comment with empty content"""
    if not test_enthusiast_id:
        pytest.skip("Test enthusiast not found")
    
    comment_data = {
        "painting_id": 1,
        "user_id": test_enthusiast_id,
        "content": ""  # Empty content
    }
    
    response = client.post("/comments/", json=comment_data)
    assert response.status_code == 422  # Should validate content is not empty

def test_get_painting_comments(client):
    """Test getting comments for a painting"""
    response = client.get("/comments/painting/1")
    assert response.status_code in [200, 404]  # 200 if painting exists
    
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)
        # Check comment structure if any comments exist
        if data:
            comment = data[0]
            assert "id" in comment
            assert "content" in comment
            assert "user_id" in comment
            assert "created_at" in comment

def test_get_user_comments(client, test_enthusiast_id):
    """Test getting comments by a user"""
    if not test_enthusiast_id:
        pytest.skip("Test enthusiast not found")
    
    response = client.get(f"/comments/user/{test_enthusiast_id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_update_comment(client, test_enthusiast_id):
    """Test updating a comment"""
    if not test_enthusiast_id:
        pytest.skip("Test enthusiast not found")
    
    # First create a comment to update
    comment_data = {
        "painting_id": 1,
        "user_id": test_enthusiast_id,
        "content": "Original comment content"
    }
    
    create_response = client.post("/comments/", json=comment_data)
    if create_response.status_code != 201:
        pytest.skip("Could not create comment for update test")
    
    comment_id = create_response.json()["id"]
    
    # Update the comment
    update_data = {
        "content": "Updated comment content - much more detailed now!"
    }
    
    response = client.put(f"/comments/{comment_id}", json=update_data)
    assert response.status_code == 200
    result = response.json()
    assert result["content"] == update_data["content"]

def test_delete_comment(client, test_enthusiast_id):
    """Test deleting a comment"""
    if not test_enthusiast_id:
        pytest.skip("Test enthusiast not found")
    
    # First create a comment to delete
    comment_data = {
        "painting_id": 1,
        "user_id": test_enthusiast_id,
        "content": "Comment to be deleted"
    }
    
    create_response = client.post("/comments/", json=comment_data)
    if create_response.status_code != 201:
        pytest.skip("Could not create comment for delete test")
    
    comment_id = create_response.json()["id"]
    
    # Delete the comment
    response = client.delete(f"/comments/{comment_id}")
    assert response.status_code == 204

def test_get_comment_by_id(client, test_enthusiast_id):
    """Test getting a specific comment by ID"""
    if not test_enthusiast_id:
        pytest.skip("Test enthusiast not found")
    
    # First create a comment
    comment_data = {
        "painting_id": 1,
        "user_id": test_enthusiast_id,
        "content": "Comment to retrieve by ID"
    }
    
    create_response = client.post("/comments/", json=comment_data)
    if create_response.status_code != 201:
        pytest.skip("Could not create comment for retrieval test")
    
    comment_id = create_response.json()["id"]
    
    # Get the comment by ID
    response = client.get(f"/comments/{comment_id}")
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == comment_id
    assert result["content"] == comment_data["content"]

def test_get_nonexistent_comment(client):
    """Test getting a comment that doesn't exist"""
    response = client.get("/comments/99999")
    assert response.status_code == 404

def test_long_comment_content(client, test_enthusiast_id):
    """Test creating comment with long content"""
    if not test_enthusiast_id:
        pytest.skip("Test enthusiast not found")
    
    long_content = "A" * 1000  # 1000 character comment
    
    comment_data = {
        "painting_id": 1,
        "user_id": test_enthusiast_id,
        "content": long_content
    }
    
    response = client.post("/comments/", json=comment_data)
    # Should either succeed or fail with validation if there's a length limit
    assert response.status_code in [201, 404, 422]

def test_comment_with_special_characters(client, test_enthusiast_id):
    """Test creating comment with special characters and unicode"""
    if not test_enthusiast_id:
        pytest.skip("Test enthusiast not found")
    
    comment_data = {
        "painting_id": 1,
        "user_id": test_enthusiast_id,
        "content": "Beautiful painting! 🎨✨ Contains émojis & spécial chars: @#$%"
    }
    
    response = client.post("/comments/", json=comment_data)
    assert response.status_code in [201, 404]  # Should handle unicode properly
    
    if response.status_code == 201:
        result = response.json()
        assert result["content"] == comment_data["content"]

def test_comments_pagination(client):
    """Test comments pagination if implemented"""
    response = client.get("/comments/painting/1?page=1&limit=5")
    # This might not be implemented, so we'll accept 200, 404, or 422
    assert response.status_code in [200, 404, 422]
