"""
Database initialization script
Creates all tables and initial data
"""

from app.database import engine, Base
from app.models import User, Category, Painting, Rating, Comment
from app.auth import get_password_hash
from app.config import settings
from sqlalchemy.orm import sessionmaker

def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully")

def create_initial_data():
    """Create initial categories and admin user"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Create categories
        categories = [
            {"name": "Abstract", "description": "Abstract art and non-representational works"},
            {"name": "Landscape", "description": "Natural scenery and outdoor scenes"},
            {"name": "Portrait", "description": "Human figures and facial representations"},
            {"name": "Still Life", "description": "Inanimate objects and compositions"},
            {"name": "Contemporary", "description": "Modern and contemporary artworks"},
            {"name": "Classical", "description": "Traditional and classical art styles"},
            {"name": "Digital Art", "description": "Digital and computer-generated artworks"},
            {"name": "Mixed Media", "description": "Artworks using multiple artistic mediums"}
        ]
        
        for cat_data in categories:
            existing = db.query(Category).filter(Category.name == cat_data["name"]).first()
            if not existing:
                category = Category(**cat_data)
                db.add(category)
        
        # Create admin user
        admin_email = "admin@artgallery.com"
        existing_admin = db.query(User).filter(User.email == admin_email).first()
        if not existing_admin:
            admin_user = User(
                email=admin_email,
                username="admin",
                full_name="Gallery Administrator",
                hashed_password=get_password_hash("admin123"),
                role="admin",
                bio="Art Gallery System Administrator"
            )
            db.add(admin_user)
        
        # Create sample painter
        painter_email = "painter@artgallery.com"
        existing_painter = db.query(User).filter(User.email == painter_email).first()
        if not existing_painter:
            painter_user = User(
                email=painter_email,
                username="painter1",
                full_name="Sample Artist",
                hashed_password=get_password_hash("painter123"),
                role="painter",
                bio="Professional artist specializing in contemporary works"
            )
            db.add(painter_user)
        
        db.commit()
        print("✅ Initial data created successfully")
        print("Admin credentials: admin / admin123")
        print("Painter credentials: painter1 / painter123")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating initial data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_tables()
    create_initial_data()
