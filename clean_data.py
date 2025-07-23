#!/usr/bin/env python3
"""
Clean Database Data
This script will delete all data from all tables but keep the database structure intact.
Much faster than dropping and recreating tables.
"""

from sqlalchemy.orm import sessionmaker
from app.database import engine
from app.models import *

def clean_data():
    """Delete all data from all tables"""
    print("🧹 Cleaning all data from database...")
    
    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Delete in order to respect foreign key constraints
        print("📝 Deleting notifications...")
        session.query(Notification).delete()
        
        print("💬 Deleting comments...")
        session.query(Comment).delete()
        
        print("⭐ Deleting ratings...")
        session.query(Rating).delete()
        
        print("🎨 Deleting paintings...")
        session.query(Painting).delete()
        
        print("📂 Deleting categories...")
        session.query(Category).delete()
        
        print("👤 Deleting users...")
        session.query(User).delete()
        
        # Commit all deletions
        session.commit()
        
        # Clean upload files
        print("🗂️ Cleaning upload files...")
        import os
        
        # Clean paintings
        paintings_dir = "uploads/paintings"
        if os.path.exists(paintings_dir):
            for filename in os.listdir(paintings_dir):
                if filename != "thumbnails":
                    file_path = os.path.join(paintings_dir, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
        
        # Clean thumbnails
        thumbnails_dir = "uploads/paintings/thumbnails"
        if os.path.exists(thumbnails_dir):
            for filename in os.listdir(thumbnails_dir):
                file_path = os.path.join(thumbnails_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        
        # Clean profiles
        profiles_dir = "uploads/profiles"
        if os.path.exists(profiles_dir):
            for filename in os.listdir(profiles_dir):
                file_path = os.path.join(profiles_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        
        print("✅ Database cleaned successfully!")
        print("🚀 All tables are empty and ready for fresh data")
        
    except Exception as e:
        print(f"❌ Error cleaning data: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    clean_data()
