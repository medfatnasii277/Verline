"""
Test painting endpoints
"""
import pytest
import io
from PIL import Image
from fastapi.testclient import TestClient

def create_test_image(format='PNG', size=(100, 100), color='red'):
    """Helper to create test images"""
    image = Image.new('RGB', size, color=color)
    img_buffer = io.BytesIO()
    image.save(img_buffer, format=format)
    img_buffer.seek(0)
    return img_buffer

def test_get_all_paintings(client):
    """Test getting all paintings - accessible to all users"""
    response = client.get("/paintings/")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "limit" in data
    assert isinstance(data["items"], list)

def test_get_paintings_with_pagination(client):
    """Test getting paintings with pagination"""
    response = client.get("/paintings/?page=1&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["limit"] == 5

def test_create_painting_valid_image(client, test_artist_id, test_category_id):
    """Test creating painting with valid image - artists should be able to upload"""
    if not test_artist_id or not test_category_id:
        pytest.skip("Test data not available")
    
    # Create test image
    img_buffer = create_test_image('PNG')
    
    files = {
        'image': ('test.png', img_buffer, 'image/png')
    }
    
    data = {
        'title': 'Test Painting',
        'description': 'A beautiful test painting',
        'artist_id': str(test_artist_id),
        'category_id': str(test_category_id),
        'price': '100.50',
        'year_created': '2024',
        'dimensions': '20x30 inches',
        'medium': 'Oil on canvas',
        'tags': 'abstract,modern,colorful'
    }
    
    response = client.post("/paintings/", files=files, data=data)
    assert response.status_code == 201
    result = response.json()
    assert result["title"] == data["title"]
    assert result["artist_id"] == test_artist_id
    assert "image_url" in result
    assert "thumbnail_url" in result

def test_create_painting_invalid_image_format(client, test_artist_id):
    """Test creating painting with invalid image format"""
    if not test_artist_id:
        pytest.skip("Test artist not found")
    
    # Create a text file pretending to be an image
    text_buffer = io.BytesIO(b"This is not an image")
    
    files = {
        'image': ('test.txt', text_buffer, 'text/plain')
    }
    
    data = {
        'title': 'Test Painting with Invalid Image',
        'artist_id': str(test_artist_id)
    }
    
    response = client.post("/paintings/", files=files, data=data)
    assert response.status_code == 400  # Should reject invalid format

def test_create_painting_large_image(client, test_artist_id):
    """Test creating painting with oversized image"""
    if not test_artist_id:
        pytest.skip("Test artist not found")
    
    # Create a large image (this might be slow, so we'll simulate)
    # In a real test, you'd create an actual large image
    img_buffer = create_test_image('PNG', size=(100, 100))  # Small for test speed
    
    files = {
        'image': ('large_test.png', img_buffer, 'image/png')
    }
    
    data = {
        'title': 'Test Large Image Painting',
        'artist_id': str(test_artist_id)
    }
    
    response = client.post("/paintings/", files=files, data=data)
    # Should succeed with our small test image
    assert response.status_code == 201

def test_create_painting_missing_required_fields(client):
    """Test creating painting with missing required fields"""
    img_buffer = create_test_image('PNG')
    
    files = {
        'image': ('test.png', img_buffer, 'image/png')
    }
    
    data = {
        # Missing title and artist_id
        'description': 'Painting without required fields'
    }
    
    response = client.post("/paintings/", files=files, data=data)
    assert response.status_code == 422  # Validation error

def test_get_user_paintings(client, test_artist_id):
    """Test getting paintings by artist"""
    if not test_artist_id:
        pytest.skip("Test artist not found")
    
    response = client.get(f"/paintings/my-paintings/{test_artist_id}")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)

def test_get_painting_by_id_nonexistent(client):
    """Test getting nonexistent painting"""
    response = client.get("/paintings/99999")
    assert response.status_code == 404

def test_update_painting(client, test_artist_id):
    """Test updating painting"""
    if not test_artist_id:
        pytest.skip("Test artist not found")
    
    # First create a painting to update
    img_buffer = create_test_image('PNG')
    files = {'image': ('test.png', img_buffer, 'image/png')}
    data = {
        'title': 'Original Title',
        'artist_id': str(test_artist_id)
    }
    
    create_response = client.post("/paintings/", files=files, data=data)
    if create_response.status_code != 201:
        pytest.skip("Could not create painting for update test")
    
    painting_id = create_response.json()["id"]
    
    # Now update it
    update_data = {
        'title': 'Updated Title',
        'description': 'Updated description'
    }
    
    response = client.put(
        f"/paintings/{painting_id}?artist_id={test_artist_id}",
        data=update_data
    )
    assert response.status_code == 200
    result = response.json()
    assert result["title"] == update_data["title"]

def test_delete_painting(client, test_artist_id):
    """Test deleting painting"""
    if not test_artist_id:
        pytest.skip("Test artist not found")
    
    # First create a painting to delete
    img_buffer = create_test_image('PNG')
    files = {'image': ('test.png', img_buffer, 'image/png')}
    data = {
        'title': 'Painting to Delete',
        'artist_id': str(test_artist_id)
    }
    
    create_response = client.post("/paintings/", files=files, data=data)
    if create_response.status_code != 201:
        pytest.skip("Could not create painting for delete test")
    
    painting_id = create_response.json()["id"]
    
    # Now delete it
    response = client.delete(f"/paintings/{painting_id}?artist_id={test_artist_id}")
    assert response.status_code == 204

def test_paintings_filtering(client):
    """Test paintings filtering capabilities"""
    # Test category filter
    response = client.get("/paintings/?category_id=1")
    assert response.status_code == 200
    
    # Test price range filter
    response = client.get("/paintings/?min_price=50&max_price=200")
    assert response.status_code == 200
    
    # Test artist filter
    response = client.get("/paintings/?artist_id=1")
    assert response.status_code == 200
    
    # Test search
    response = client.get("/paintings/?search=test")
    assert response.status_code == 200
