"""
Test configuration and fixtures
"""
import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base
from app.models import User, Category, Painting
from app.auth import get_password_hash
import os
import tempfile
from PIL import Image
import io

# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite:///./test.db"

# Create test database engine
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session")
def test_app():
    """Create test FastAPI app"""
    return app

@pytest.fixture(scope="session")
def client():
    """Create test client"""
    with TestClient(app) as client:
        yield client

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Setup test database"""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create test data
    db = TestingSessionLocal()
    
    # Create test categories
    if not db.query(Category).filter(Category.name == "Abstract").first():
        categories = [
            Category(name="Abstract", description="Abstract art"),
            Category(name="Portrait", description="Portrait paintings"),
            Category(name="Landscape", description="Landscape paintings")
        ]
        for category in categories:
            db.add(category)
    
    # Create test users
    if not db.query(User).filter(User.username == "test_artist").first():
        artist = User(
            username="test_artist",
            email="artist@test.com",
            full_name="Test Artist",
            hashed_password=get_password_hash("testpass123"),
            role="artist",
            bio="Test artist for API testing"
        )
        db.add(artist)
    
    if not db.query(User).filter(User.username == "test_enthusiast").first():
        enthusiast = User(
            username="test_enthusiast",
            email="enthusiast@test.com",
            full_name="Test Enthusiast",
            hashed_password=get_password_hash("testpass123"),
            role="enthusiast",
            bio="Test enthusiast for API testing"
        )
        db.add(enthusiast)
    
    db.commit()
    db.close()
    
    yield
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_image():
    """Create a test image file"""
    # Create a simple test image
    image = Image.new('RGB', (100, 100), color='red')
    img_buffer = io.BytesIO()
    image.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    return ("test_image.png", img_buffer, "image/png")

@pytest.fixture
def invalid_image():
    """Create an invalid file that's not an image"""
    text_buffer = io.BytesIO(b"This is not an image")
    return ("test.txt", text_buffer, "text/plain")

@pytest.fixture
def db_session():
    """Create a database session for testing"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def test_artist_id(db_session):
    """Get test artist ID"""
    artist = db_session.query(User).filter(User.username == "test_artist").first()
    return artist.id if artist else None

@pytest.fixture
def test_enthusiast_id(db_session):
    """Get test enthusiast ID"""
    enthusiast = db_session.query(User).filter(User.username == "test_enthusiast").first()
    return enthusiast.id if enthusiast else None

@pytest.fixture
def test_category_id(db_session):
    """Get test category ID"""
    category = db_session.query(Category).filter(Category.name == "Abstract").first()
    return category.id if category else None

@pytest.fixture
def authenticated_client():
    """TestClient instance that can use authentication headers"""
    return client

@pytest.fixture
def test_artist_token(client):
    """Get authentication token for test artist"""
    login_data = {
        "username": "test_artist",
        "password": "testpass123"
    }
    response = client.post("/auth/login", data=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

@pytest.fixture
def test_enthusiast_token(client):
    """Get authentication token for test enthusiast"""
    login_data = {
        "username": "test_enthusiast",
        "password": "testpass123"
    }
    response = client.post("/auth/login", data=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

@pytest.fixture
def test_artist_headers(test_artist_token):
    """Get authentication headers for test artist"""
    if test_artist_token:
        return {"Authorization": f"Bearer {test_artist_token}"}
    return {}

@pytest.fixture
def test_enthusiast_headers(test_enthusiast_token):
    """Get authentication headers for test enthusiast"""
    if test_enthusiast_token:
        return {"Authorization": f"Bearer {test_enthusiast_token}"}
    return {}
