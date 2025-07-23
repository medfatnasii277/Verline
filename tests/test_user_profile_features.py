import pytest
import os
import io
from fastapi.testclient import TestClient
from fastapi import UploadFile
from PIL import Image
from app.main import app
from app.database import get_db
from app.models import User
from app.schemas import UserUpdate
from app.crud import UserService
import tempfile

client = TestClient(app)

@pytest.fixture
def test_user_data():
    return {
        "email": "testuser@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "password": "testpassword123",
        "role": "enthusiast",
        "bio": "Test bio"
    }

@pytest.fixture
def test_artist_data():
    return {
        "email": "testartist@example.com", 
        "username": "testartist",
        "full_name": "Test Artist",
        "password": "testpassword123",
        "role": "artist",
        "bio": "Test artist bio"
    }

@pytest.fixture
def create_test_image():
    """Create a test image file for upload testing."""
    def _create_image(format="JPEG", size=(100, 100), mode="RGB"):
        image = Image.new(mode, size, color="red")
        image_bytes = io.BytesIO()
        image.save(image_bytes, format=format)
        image_bytes.seek(0)
        return image_bytes
    return _create_image

class TestUserProfileFields:
    """Test the new location and website fields in user profiles."""
    
    def test_user_creation_with_location_and_website(self, db_session):
        """Test creating a user with location and website fields."""
        user_data = {
            "email": "user@example.com",
            "username": "testuser",
            "full_name": "Test User", 
            "password": "testpass123",
            "role": "enthusiast",
            "bio": "Test bio",
            "location": "New York, USA",
            "website": "https://example.com"
        }
        
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 200
        user = response.json()
        
        # Note: Registration endpoint doesn't include location/website in response
        # So we fetch the user profile to verify
        user_response = client.get(f"/users/{user['id']}")
        assert user_response.status_code == 200
        profile = user_response.json()
        
        assert profile["location"] is None  # Registration doesn't set these
        assert profile["website"] is None   # They need to be updated via profile update

    def test_update_user_profile_with_location_and_website(self, db_session):
        """Test updating user profile with location and website."""
        # First create a user
        user_data = {
            "email": "user2@example.com",
            "username": "testuser2",
            "full_name": "Test User 2",
            "password": "testpass123",
            "role": "enthusiast"
        }
        
        reg_response = client.post("/auth/register", json=user_data)
        assert reg_response.status_code == 200
        user = reg_response.json()
        
        # Login to get token
        login_response = client.post("/auth/login", data={
            "username": "testuser2",
            "password": "testpass123"
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Update profile with location and website
        update_data = {
            "location": "San Francisco, CA",
            "website": "https://myportfolio.com",
            "bio": "Updated bio"
        }
        
        response = client.put(f"/users/me/{user['id']}", 
                            json=update_data, 
                            headers=headers)
        assert response.status_code == 200
        updated_user = response.json()
        
        assert updated_user["location"] == "San Francisco, CA"
        assert updated_user["website"] == "https://myportfolio.com"
        assert updated_user["bio"] == "Updated bio"

    def test_update_profile_location_only(self, db_session):
        """Test updating only the location field."""
        # Create and login user
        user_data = {
            "email": "user3@example.com",
            "username": "testuser3", 
            "full_name": "Test User 3",
            "password": "testpass123",
            "role": "artist"
        }
        
        reg_response = client.post("/auth/register", json=user_data)
        user = reg_response.json()
        
        login_response = client.post("/auth/login", data={
            "username": "testuser3",
            "password": "testpass123"
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Update only location
        update_data = {"location": "Tokyo, Japan"}
        
        response = client.put(f"/users/me/{user['id']}", 
                            json=update_data, 
                            headers=headers)
        assert response.status_code == 200
        updated_user = response.json()
        
        assert updated_user["location"] == "Tokyo, Japan"
        assert updated_user["website"] is None
        assert updated_user["full_name"] == "Test User 3"  # Other fields unchanged

    def test_update_profile_website_only(self, db_session):
        """Test updating only the website field."""
        # Create and login user
        user_data = {
            "email": "user4@example.com",
            "username": "testuser4",
            "full_name": "Test User 4", 
            "password": "testpass123",
            "role": "enthusiast"
        }
        
        reg_response = client.post("/auth/register", json=user_data)
        user = reg_response.json()
        
        login_response = client.post("/auth/login", data={
            "username": "testuser4", 
            "password": "testpass123"
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Update only website
        update_data = {"website": "https://artblog.example.com"}
        
        response = client.put(f"/users/me/{user['id']}", 
                            json=update_data, 
                            headers=headers)
        assert response.status_code == 200
        updated_user = response.json()
        
        assert updated_user["website"] == "https://artblog.example.com"
        assert updated_user["location"] is None
        assert updated_user["email"] == "user4@example.com"  # Other fields unchanged

class TestProfilePictureUpload:
    """Test profile picture upload functionality."""
    
    def test_upload_valid_profile_picture(self, db_session, create_test_image):
        """Test uploading a valid profile picture."""
        # Create and login user
        user_data = {
            "email": "picuser@example.com",
            "username": "picuser",
            "full_name": "Picture User",
            "password": "testpass123", 
            "role": "artist"
        }
        
        reg_response = client.post("/auth/register", json=user_data)
        user = reg_response.json()
        
        login_response = client.post("/auth/login", data={
            "username": "picuser",
            "password": "testpass123"
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create test image
        image_data = create_test_image(format="JPEG", size=(200, 200))
        
        # Upload profile picture
        files = {"file": ("test_profile.jpg", image_data, "image/jpeg")}
        response = client.post(f"/users/me/{user['id']}/profile-picture",
                             files=files,
                             headers=headers)
        
        assert response.status_code == 200
        updated_user = response.json()
        
        assert updated_user["profile_picture"] is not None
        assert updated_user["profile_picture"].startswith("/uploads/profiles/")
        assert "profile_" in updated_user["profile_picture"]
        
        # Verify file was created
        file_path = updated_user["profile_picture"].replace("/uploads/", "uploads/")
        assert os.path.exists(file_path)
        
        # Clean up
        if os.path.exists(file_path):
            os.remove(file_path)

    def test_upload_png_profile_picture(self, db_session, create_test_image):
        """Test uploading a PNG profile picture."""
        # Create and login user
        user_data = {
            "email": "pnguser@example.com",
            "username": "pnguser", 
            "full_name": "PNG User",
            "password": "testpass123",
            "role": "enthusiast"
        }
        
        reg_response = client.post("/auth/register", json=user_data)
        user = reg_response.json()
        
        login_response = client.post("/auth/login", data={
            "username": "pnguser",
            "password": "testpass123"
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create test PNG image
        image_data = create_test_image(format="PNG", size=(150, 150))
        
        # Upload profile picture
        files = {"file": ("test_profile.png", image_data, "image/png")}
        response = client.post(f"/users/me/{user['id']}/profile-picture",
                             files=files,
                             headers=headers)
        
        assert response.status_code == 200
        updated_user = response.json()
        
        assert updated_user["profile_picture"] is not None
        
        # Verify file was created and converted to JPEG
        file_path = updated_user["profile_picture"].replace("/uploads/", "uploads/")
        assert os.path.exists(file_path)
        assert file_path.endswith(".jpg")  # PNG should be converted to JPEG
        
        # Clean up
        if os.path.exists(file_path):
            os.remove(file_path)

    def test_upload_profile_picture_unauthorized(self, db_session, create_test_image):
        """Test uploading profile picture without authentication."""
        image_data = create_test_image()
        files = {"file": ("test.jpg", image_data, "image/jpeg")}
        
        response = client.post("/users/me/1/profile-picture", files=files)
        assert response.status_code == 401

    def test_upload_profile_picture_wrong_user(self, db_session, create_test_image):
        """Test uploading profile picture for another user."""
        # Create two users
        user1_data = {
            "email": "user1@example.com",
            "username": "user1",
            "full_name": "User 1",
            "password": "testpass123",
            "role": "artist"
        }
        
        user2_data = {
            "email": "user2@example.com", 
            "username": "user2",
            "full_name": "User 2",
            "password": "testpass123",
            "role": "enthusiast"
        }
        
        # Register both users
        reg1_response = client.post("/auth/register", json=user1_data)
        user1 = reg1_response.json()
        
        reg2_response = client.post("/auth/register", json=user2_data)
        user2 = reg2_response.json()
        
        # Login as user1
        login_response = client.post("/auth/login", data={
            "username": "user1",
            "password": "testpass123"
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to upload profile picture for user2
        image_data = create_test_image()
        files = {"file": ("test.jpg", image_data, "image/jpeg")}
        
        response = client.post(f"/users/me/{user2['id']}/profile-picture",
                             files=files,
                             headers=headers)
        
        assert response.status_code == 403
        assert "can only update your own" in response.json()["detail"]

    def test_upload_invalid_file_type(self, db_session):
        """Test uploading an invalid file type."""
        # Create and login user
        user_data = {
            "email": "invaliduser@example.com",
            "username": "invaliduser",
            "full_name": "Invalid User",
            "password": "testpass123",
            "role": "artist"
        }
        
        reg_response = client.post("/auth/register", json=user_data)
        user = reg_response.json()
        
        login_response = client.post("/auth/login", data={
            "username": "invaliduser",
            "password": "testpass123"
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Try to upload text file
        text_data = io.BytesIO(b"This is not an image")
        files = {"file": ("test.txt", text_data, "text/plain")}
        
        response = client.post(f"/users/me/{user['id']}/profile-picture",
                             files=files,
                             headers=headers)
        
        assert response.status_code == 400
        assert "Invalid file type" in response.json()["detail"]

    def test_upload_large_file(self, db_session, create_test_image):
        """Test uploading a file that's too large."""
        # Create and login user
        user_data = {
            "email": "largeuser@example.com",
            "username": "largeuser",
            "full_name": "Large User",
            "password": "testpass123",
            "role": "artist"
        }
        
        reg_response = client.post("/auth/register", json=user_data)
        user = reg_response.json()
        
        login_response = client.post("/auth/login", data={
            "username": "largeuser",
            "password": "testpass123"
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create large image (simulate by creating large data)
        large_data = io.BytesIO(b"x" * (6 * 1024 * 1024))  # 6MB
        files = {"file": ("large.jpg", large_data, "image/jpeg")}
        
        response = client.post(f"/users/me/{user['id']}/profile-picture",
                             files=files,
                             headers=headers)
        
        assert response.status_code == 400
        assert "File size too large" in response.json()["detail"]

    def test_replace_existing_profile_picture(self, db_session, create_test_image):
        """Test replacing an existing profile picture."""
        # Create and login user
        user_data = {
            "email": "replaceuser@example.com",
            "username": "replaceuser",
            "full_name": "Replace User",
            "password": "testpass123",
            "role": "artist"
        }
        
        reg_response = client.post("/auth/register", json=user_data)
        user = reg_response.json()
        
        login_response = client.post("/auth/login", data={
            "username": "replaceuser",
            "password": "testpass123"
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Upload first profile picture
        image_data1 = create_test_image(format="JPEG", size=(100, 100))
        files1 = {"file": ("test1.jpg", image_data1, "image/jpeg")}
        
        response1 = client.post(f"/users/me/{user['id']}/profile-picture",
                              files=files1,
                              headers=headers)
        assert response1.status_code == 200
        first_pic = response1.json()["profile_picture"]
        first_pic_path = first_pic.replace("/uploads/", "uploads/")
        
        # Verify first picture exists
        assert os.path.exists(first_pic_path)
        
        # Upload second profile picture
        image_data2 = create_test_image(format="JPEG", size=(200, 200))
        files2 = {"file": ("test2.jpg", image_data2, "image/jpeg")}
        
        response2 = client.post(f"/users/me/{user['id']}/profile-picture",
                              files=files2,
                              headers=headers)
        assert response2.status_code == 200
        second_pic = response2.json()["profile_picture"]
        second_pic_path = second_pic.replace("/uploads/", "uploads/")
        
        # Verify old picture was deleted and new one exists
        assert not os.path.exists(first_pic_path)  # Old file should be deleted
        assert os.path.exists(second_pic_path)     # New file should exist
        assert first_pic != second_pic             # URLs should be different
        
        # Clean up
        if os.path.exists(second_pic_path):
            os.remove(second_pic_path)

class TestUserProfileCRUD:
    """Test the UserService CRUD operations with new fields."""
    
    def test_user_service_update_location_website(self, db_session):
        """Test UserService.update_user with location and website."""
        from app.crud import UserService
        from app.schemas import UserCreate, UserUpdate
        
        # Create user via service
        user_create = UserCreate(
            email="serviceuser@example.com",
            username="serviceuser",
            full_name="Service User",
            password="testpass123",
            role="artist"
        )
        
        created_user = UserService.create_user(db_session, user_create)
        assert created_user.location is None
        assert created_user.website is None
        
        # Update with location and website
        user_update = UserUpdate(
            location="Berlin, Germany",
            website="https://artgallery.berlin"
        )
        
        updated_user = UserService.update_user(db_session, created_user.id, user_update)
        
        assert updated_user is not None
        assert updated_user.location == "Berlin, Germany"
        assert updated_user.website == "https://artgallery.berlin"
        assert updated_user.email == "serviceuser@example.com"  # Other fields unchanged

    def test_user_service_partial_update(self, db_session):
        """Test partial updates with UserService."""
        from app.crud import UserService
        from app.schemas import UserCreate, UserUpdate
        
        # Create user
        user_create = UserCreate(
            email="partialuser@example.com",
            username="partialuser",
            full_name="Partial User",
            password="testpass123",
            role="enthusiast",
            bio="Original bio"
        )
        
        created_user = UserService.create_user(db_session, user_create)
        
        # Update only location
        user_update = UserUpdate(location="London, UK")
        updated_user = UserService.update_user(db_session, created_user.id, user_update)
        
        assert updated_user.location == "London, UK"
        assert updated_user.website is None
        assert updated_user.bio == "Original bio"
        
        # Update only website
        user_update2 = UserUpdate(website="https://london-art.co.uk")
        updated_user2 = UserService.update_user(db_session, created_user.id, user_update2)
        
        assert updated_user2.location == "London, UK"  # Should remain from previous update
        assert updated_user2.website == "https://london-art.co.uk"
        assert updated_user2.bio == "Original bio"

if __name__ == "__main__":
    pytest.main([__file__])
