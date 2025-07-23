#!/usr/bin/env python3
"""
Database Reset Script
This script will completely clean the database and recreate all tables fresh.
All data will be lost, but the schema and logic remain intact.
"""

import os
import sys
from sqlalchemy import create_engine, text
from app.database import Base, engine
from app.models import *  # Import all models to ensure they're registered

def reset_database():
    """Drop all tables and recreate them fresh"""
    print("🗑️  Starting database reset...")
    
    try:
        # Drop all tables
        print("📋 Dropping all existing tables...")
        Base.metadata.drop_all(bind=engine)
        print("✅ All tables dropped successfully")
        
        # Recreate all tables
        print("🏗️  Creating fresh tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully")
        
        # Clean up upload directories but keep the folders
        print("🧹 Cleaning upload directories...")
        
        # Clean paintings uploads
        paintings_dir = "uploads/paintings"
        if os.path.exists(paintings_dir):
            for filename in os.listdir(paintings_dir):
                if filename != "thumbnails":  # Keep the thumbnails folder
                    file_path = os.path.join(paintings_dir, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        print(f"   Removed: {file_path}")
        
        # Clean thumbnails
        thumbnails_dir = "uploads/paintings/thumbnails"
        if os.path.exists(thumbnails_dir):
            for filename in os.listdir(thumbnails_dir):
                file_path = os.path.join(thumbnails_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"   Removed: {file_path}")
        
        # Clean profile pictures
        profiles_dir = "uploads/profiles"
        if os.path.exists(profiles_dir):
            for filename in os.listdir(profiles_dir):
                file_path = os.path.join(profiles_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"   Removed: {file_path}")
        
        print("✅ Upload directories cleaned")
        
        print("\n🎉 Database reset completed successfully!")
        print("📝 All tables are now empty and ready for fresh data")
        print("🚀 You can now restart your application and create new accounts")
        
    except Exception as e:
        print(f"❌ Error during database reset: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("⚠️  WARNING: This will completely erase all data!")
    print("   - All user accounts will be deleted")
    print("   - All paintings will be deleted") 
    print("   - All ratings and comments will be deleted")
    print("   - All notifications will be deleted")
    print("   - All uploaded files will be removed")
    print()
    
    confirm = input("Are you sure you want to proceed? Type 'YES' to confirm: ")
    
    if confirm == "YES":
        reset_database()
    else:
        print("❌ Database reset cancelled")
        sys.exit(0)
