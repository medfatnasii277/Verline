#!/usr/bin/env python3
"""
Script to create a test painting with a valid image for testing purposes
"""
import os
import io
from PIL import Image
from app.database import get_db
from app.models import User, Category, Painting, PaintingStatus
from app.schemas import PaintingCreate
from app.crud import PaintingService, CategoryService

def create_test_image(format='PNG', size=(400, 300), color='lightblue'):
    """Create a test image and save it"""
    image = Image.new('RGB', size, color=color)
    
    # Create uploads directory if it doesn't exist
    os.makedirs("uploads/paintings", exist_ok=True)
    os.makedirs("uploads/paintings/thumbnails", exist_ok=True)
    
    # Save main image
    image_path = "uploads/paintings/test_painting.png"
    image.save(image_path, format=format)
    
    # Create and save thumbnail
    thumbnail = image.copy()
    thumbnail.thumbnail((150, 150))
    thumbnail_path = "uploads/paintings/thumbnails/test_painting_thumb.png"
    thumbnail.save(thumbnail_path, format=format)
    
    return image_path, thumbnail_path

def create_test_data():
    """Create test painting with valid image"""
    db = next(get_db())
    
    try:
        # Check if test category exists, create if not
        test_category = db.query(Category).filter(Category.name == "Abstract").first()
        if not test_category:
            print("Creating test category...")
            from app.schemas import CategoryCreate
            category_data = CategoryCreate(name="Abstract", description="Abstract art category")
            test_category = CategoryService.create_category(db, category_data)
            print(f"Created category: {test_category.name} (ID: {test_category.id})")
        else:
            print(f"Using existing category: {test_category.name} (ID: {test_category.id})")
        
        # Check if test artist exists
        test_artist = db.query(User).filter(User.role == "artist").first()
        if not test_artist:
            print("No artist found in database. Please ensure there's at least one artist user.")
            return
        
        print(f"Using artist: {test_artist.username} (ID: {test_artist.id})")
        
        # Create test image
        print("Creating test image...")
        image_path, thumbnail_path = create_test_image()
        print(f"Image saved to: {image_path}")
        print(f"Thumbnail saved to: {thumbnail_path}")
        
        # Check if test painting already exists
        existing_painting = db.query(Painting).filter(Painting.title == "Test Painting for API Testing").first()
        if existing_painting:
            print(f"Test painting already exists (ID: {existing_painting.id})")
            return
        
        # Create painting data
        painting_data = PaintingCreate(
            title="Test Painting for API Testing",
            description="A beautiful test painting created for API testing purposes",
            category_id=test_category.id,
            price=125.50,
            year_created=2024,
            dimensions="24x18 inches",
            medium="Digital Art",
            tags="test,abstract,colorful,api"
        )
        
        # Create the painting
        print("Creating test painting...")
        test_painting = PaintingService.create_painting(
            db=db,
            painting=painting_data,
            artist_id=test_artist.id,
            image_url=f"/{image_path}",  # Relative path for API
            thumbnail_url=f"/{thumbnail_path}"
        )
        
        print(f"✅ Test painting created successfully!")
        print(f"   ID: {test_painting.id}")
        print(f"   Title: {test_painting.title}")
        print(f"   Artist: {test_artist.username}")
        print(f"   Category: {test_category.name}")
        print(f"   Status: {test_painting.status}")
        print(f"   Image URL: {test_painting.image_url}")
        
    except Exception as e:
        print(f"❌ Error creating test painting: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_data()
