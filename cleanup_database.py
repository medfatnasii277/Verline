#!/usr/bin/env python3
"""
Database cleanup script for Verlin Art Gallery
This script will:
1. Delete all paintings and their associated files
2. Delete all ratings and comments
3. Keep only the two demo accounts (admin and art_lover)
4. Delete all other user accounts
"""

import sys
import os
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent / "app"))

from sqlalchemy.orm import Session
from app.database import get_db, engine
from app.models import User, Painting, Rating, Comment, Category
from app.utils import delete_image_files

def cleanup_database():
    """Clean up the database keeping only demo accounts"""
    
    # Get database session
    db = next(get_db())
    
    try:
        print("🧹 Starting database cleanup...")
        
        # 1. Delete all comments
        print("📝 Deleting all comments...")
        comment_count = db.query(Comment).count()
        db.query(Comment).delete()
        print(f"   ✅ Deleted {comment_count} comments")
        
        # 2. Delete all ratings
        print("⭐ Deleting all ratings...")
        rating_count = db.query(Rating).count()
        db.query(Rating).delete()
        print(f"   ✅ Deleted {rating_count} ratings")
        
        # 3. Delete all painting images and records
        print("🖼️  Deleting all paintings and their images...")
        paintings = db.query(Painting).all()
        painting_count = len(paintings)
        
        # Delete image files for each painting
        for painting in paintings:
            try:
                if painting.image_url:
                    # Extract filename from URL and delete file
                    filename = painting.image_url.split('/')[-1]
                    image_path = Path("static/images/paintings") / filename
                    if image_path.exists():
                        image_path.unlink()
                        print(f"   🗑️  Deleted image: {filename}")
                
                if painting.thumbnail_url:
                    # Delete thumbnail if it exists
                    thumbnail_filename = painting.thumbnail_url.split('/')[-1]
                    thumbnail_path = Path("static/images/paintings") / thumbnail_filename
                    if thumbnail_path.exists():
                        thumbnail_path.unlink()
                        print(f"   🗑️  Deleted thumbnail: {thumbnail_filename}")
                        
            except Exception as e:
                print(f"   ⚠️  Error deleting images for painting {painting.id}: {e}")
        
        # Delete all painting records
        db.query(Painting).delete()
        print(f"   ✅ Deleted {painting_count} paintings")
        
        # 4. Keep only demo accounts and delete others
        print("👥 Cleaning up user accounts...")
        
        # Get demo accounts
        demo_accounts = ['admin', 'art_lover']
        demo_users = db.query(User).filter(User.username.in_(demo_accounts)).all()
        
        # Delete all other users
        other_users = db.query(User).filter(~User.username.in_(demo_accounts)).all()
        other_user_count = len(other_users)
        
        for user in other_users:
            db.delete(user)
        
        print(f"   ✅ Deleted {other_user_count} non-demo user accounts")
        print(f"   ✅ Kept {len(demo_users)} demo accounts: {[u.username for u in demo_users]}")
        
        # 5. Reset demo accounts to clean state
        print("🔄 Resetting demo accounts...")
        for user in demo_users:
            if user.username == 'admin':
                user.full_name = 'Admin Artist'
                user.email = 'admin@verlin.com'
                user.bio = 'Professional artist and gallery administrator'
                user.role = 'artist'
            elif user.username == 'art_lover':
                user.full_name = 'Art Enthusiast'
                user.email = 'enthusiast@verlin.com'
                user.bio = 'Passionate art lover and collector'
                user.role = 'enthusiast'
        
        # 6. Optionally clean up categories (keep some basic ones)
        print("📁 Cleaning up categories...")
        # Keep only basic categories
        basic_categories = ['Abstract', 'Landscape', 'Portrait', 'Still Life', 'Modern']
        
        # Delete categories not in basic list
        db.query(Category).filter(~Category.name.in_(basic_categories)).delete()
        
        # Create basic categories if they don't exist
        existing_categories = db.query(Category).all()
        existing_names = [cat.name for cat in existing_categories]
        
        for cat_name in basic_categories:
            if cat_name not in existing_names:
                new_category = Category(
                    name=cat_name,
                    description=f"{cat_name} artworks"
                )
                db.add(new_category)
        
        print(f"   ✅ Set up {len(basic_categories)} basic categories")
        
        # Commit all changes
        db.commit()
        
        print("\n🎉 Database cleanup completed successfully!")
        print("📊 Final state:")
        print(f"   • Users: {db.query(User).count()} (demo accounts only)")
        print(f"   • Paintings: {db.query(Painting).count()}")
        print(f"   • Ratings: {db.query(Rating).count()}")
        print(f"   • Comments: {db.query(Comment).count()}")
        print(f"   • Categories: {db.query(Category).count()}")
        
        print("\n✨ Your Verlin gallery is now fresh and ready!")
        print("🚀 You can now start adding paintings and testing the application.")
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("🎨 Verlin Art Gallery Database Cleanup")
    print("="*50)
    
    # Confirm before cleanup
    confirm = input("⚠️  This will delete ALL paintings, ratings, comments, and non-demo accounts. Continue? (y/N): ")
    
    if confirm.lower() != 'y':
        print("❌ Cleanup cancelled.")
        sys.exit(0)
    
    try:
        cleanup_database()
    except Exception as e:
        print(f"💥 Cleanup failed: {e}")
        sys.exit(1)
