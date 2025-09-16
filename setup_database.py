#!/usr/bin/env python3
"""
Database Setup Script for Production Deployment
This script helps set up the database for production use with MySQL
"""

import os
from app import app, db, User
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_database():
    """Create all database tables"""
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("✅ Database tables created successfully!")

def create_default_users():
    """Create default admin and user accounts"""
    with app.app_context():
        print("Creating default users...")
        
        # Create admin user if not exists
        if not User.query.filter_by(username='admin').first():
            admin_user = User(username='admin', role='admin')
            admin_user.set_password('admin123')  # Change this in production!
            db.session.add(admin_user)
            print("✅ Admin user created (username: admin, password: admin123)")
        else:
            print("ℹ️  Admin user already exists")
        
        # Create normal user if not exists
        if not User.query.filter_by(username='user').first():
            normal_user = User(username='user', role='normal')
            normal_user.set_password('user123')  # Change this in production!
            db.session.add(normal_user)
            print("✅ Normal user created (username: user, password: user123)")
        else:
            print("ℹ️  Normal user already exists")
        
        db.session.commit()
        print("✅ Default users setup completed!")

def test_connection():
    """Test database connection"""
    try:
        with app.app_context():
            # Try to query the database
            user_count = User.query.count()
            print(f"✅ Database connection successful! Found {user_count} users.")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

def main():
    """Main setup function"""
    print("🚀 Starting database setup for production...")
    print(f"Database URL: {os.environ.get('DATABASE_URL', 'Not set')}")
    
    # Test connection first
    if not test_connection():
        print("\n❌ Please check your database configuration in .env file")
        return
    
    # Create tables
    create_database()
    
    # Create default users
    create_default_users()
    
    print("\n🎉 Database setup completed successfully!")
    print("\n⚠️  IMPORTANT SECURITY NOTES:")
    print("1. Change default passwords immediately in production")
    print("2. Create strong passwords for admin accounts")
    print("3. Consider removing default users after creating your own")

if __name__ == '__main__':
    main()