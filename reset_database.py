#!/usr/bin/env python3
"""
Database Reset Script - Drops and recreates all tables
USE WITH CAUTION: This will delete all existing data!
"""

import os
from app import app, db
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def reset_database():
    """Drop all tables and recreate them"""
    with app.app_context():
        print("⚠️  WARNING: This will delete ALL existing data!")
        response = input("Are you sure you want to continue? (yes/no): ")
        
        if response.lower() != 'yes':
            print("❌ Operation cancelled.")
            return False
            
        print("🗑️  Dropping all existing tables...")
        db.drop_all()
        print("✅ All tables dropped successfully!")
        
        print("🔨 Creating new tables with updated schema...")
        db.create_all()
        print("✅ New tables created successfully!")
        
        return True

if __name__ == '__main__':
    print("🚀 Database Reset Tool")
    print(f"Database URL: {os.environ.get('DATABASE_URL', 'Not set')}")
    
    if reset_database():
        print("\n🎉 Database reset completed successfully!")
        print("\n💡 Next steps:")
        print("1. Run 'python setup_database.py' to create default users")
        print("2. Test your application")
    else:
        print("\n❌ Database reset was cancelled.")