#!/usr/bin/env python3
"""
Migration script to update user roles from old values to new values.
This script will:
1. First expand the ENUM to include both old and new values
2. Update VISITOR -> ENTHUSIAST
3. Update PAINTER -> ARTIST  
4. Update ADMIN -> ARTIST (since we only have 2 roles now)
5. Remove old ENUM values to enforce new schema
"""

import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from sqlalchemy import create_engine, text
from app.config import settings

def migrate_user_roles():
    """Migrate old user roles to new role system"""
    engine = create_engine(settings.database_url)
    
    try:
        with engine.connect() as connection:
            # First, let's see what roles exist in the database
            result = connection.execute(text("SELECT DISTINCT role FROM users;"))
            existing_roles = [row[0] for row in result.fetchall()]
            print(f"Existing roles in database: {existing_roles}")
            
            # Step 1: Expand ENUM to include both old and new values
            print("\n🔄 Step 1: Adding new enum values to the role column...")
            connection.execute(text("""
                ALTER TABLE users MODIFY COLUMN role 
                ENUM('VISITOR', 'PAINTER', 'ADMIN', 'ENTHUSIAST', 'ARTIST') 
                NOT NULL DEFAULT 'ENTHUSIAST';
            """))
            connection.commit()
            print("✅ Successfully added new enum values")
            
            # Step 2: Update roles using raw SQL 
            print("\n🔄 Step 2: Updating user roles...")
            
            # Update VISITOR -> ENTHUSIAST
            result = connection.execute(text("UPDATE users SET role = 'ENTHUSIAST' WHERE role = 'VISITOR';"))
            visitor_count = result.rowcount
            print(f"✅ Updated {visitor_count} VISITOR users to ENTHUSIAST")
            
            # Update PAINTER -> ARTIST
            result = connection.execute(text("UPDATE users SET role = 'ARTIST' WHERE role = 'PAINTER';"))
            painter_count = result.rowcount
            print(f"✅ Updated {painter_count} PAINTER users to ARTIST")
            
            # Update ADMIN -> ARTIST
            result = connection.execute(text("UPDATE users SET role = 'ARTIST' WHERE role = 'ADMIN';"))
            admin_count = result.rowcount
            print(f"✅ Updated {admin_count} ADMIN users to ARTIST")
            
            connection.commit()
            
            # Step 3: Remove old enum values to enforce the new schema
            print("\n🔄 Step 3: Removing old enum values...")
            connection.execute(text("""
                ALTER TABLE users MODIFY COLUMN role 
                ENUM('ENTHUSIAST', 'ARTIST') 
                NOT NULL DEFAULT 'ENTHUSIAST';
            """))
            connection.commit()
            print("✅ Successfully removed old enum values")
            
            # Verify the changes
            print("\n🔍 Verification:")
            result = connection.execute(text("SELECT DISTINCT role FROM users;"))
            new_roles = [row[0] for row in result.fetchall()]
            print(f"New roles in database: {new_roles}")
            
            result = connection.execute(text("SELECT role, COUNT(*) FROM users GROUP BY role;"))
            role_counts = result.fetchall()
            for role, count in role_counts:
                print(f"  {role}: {count} users")
            
            total_updated = visitor_count + painter_count + admin_count
            print(f"\n🎉 Migration completed successfully! Updated {total_updated} users total.")
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Starting user role migration...")
    success = migrate_user_roles()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("You can now restart your FastAPI server and try registration again.")
    else:
        print("\n💥 Migration failed. Please check the error messages above.")
        sys.exit(1)
