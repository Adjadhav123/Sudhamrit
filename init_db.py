#!/usr/bin/env python3
"""
Database initialization script for Sudhamrit Dairy Farm application.
This script creates all database tables and can optionally add sample data.
"""

from app import app, db
from models import User, Admin, Product, Cart, Payment, Order, OrderItem
from werkzeug.security import generate_password_hash
import os

def init_database():
    """Initialize the database with all tables."""
    with app.app_context():
        try:
            # Drop all tables (if you want a fresh start)
            # db.drop_all()
            
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Check if any data exists
            user_count = User.query.count()
            admin_count = Admin.query.count()
            product_count = Product.query.count()
            
            print(f"📊 Current data count:")
            print(f"   Users: {user_count}")
            print(f"   Admins: {admin_count}")
            print(f"   Products: {product_count}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating database tables: {e}")
            return False

def add_sample_admin():
    """Add a sample admin user for testing."""
    with app.app_context():
        try:
            # Check if admin already exists
            existing_admin = Admin.query.filter_by(admin_email="admin@sudhamrit.com").first()
            if existing_admin:
                print("🔄 Sample admin already exists!")
                return True
                
            # Create sample admin
            hashed_password = generate_password_hash("admin123", method="pbkdf2:sha256", salt_length=16)
            sample_admin = Admin(
                admin_name="Admin",
                admin_email="admin@sudhamrit.com",
                admin_password=hashed_password
            )
            
            db.session.add(sample_admin)
            db.session.commit()
            
            print("✅ Sample admin created successfully!")
            print("   Email: admin@sudhamrit.com")
            print("   Password: admin123")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating sample admin: {e}")
            return False

def add_sample_products():
    """Add sample products for testing."""
    with app.app_context():
        try:
            # Check if products already exist
            existing_products = Product.query.count()
            if existing_products > 0:
                print("🔄 Sample products already exist!")
                return True
                
            sample_products = [
                {
                    "product_name": "Fresh Milk",
                    "description": "Pure and fresh cow milk, rich in nutrients",
                    "category": "Dairy",
                    "price": 60.0,
                    "stock": 100,
                    "product_image": "milk.jpg"
                },
                {
                    "product_name": "Paneer",
                    "description": "Fresh homemade paneer, perfect for cooking",
                    "category": "Dairy",
                    "price": 250.0,
                    "stock": 50,
                    "product_image": "paneer.jpg"
                },
                {
                    "product_name": "Butter",
                    "description": "Creamy fresh butter made from pure milk",
                    "category": "Dairy",
                    "price": 120.0,
                    "stock": 75,
                    "product_image": "butter.jpg"
                },
                {
                    "product_name": "Yogurt",
                    "description": "Thick and creamy yogurt, naturally fermented",
                    "category": "Dairy",
                    "price": 45.0,
                    "stock": 80,
                    "product_image": "yogurt.jpg"
                },
                {
                    "product_name": "Cheese",
                    "description": "Artisanal cheese with rich flavor",
                    "category": "Dairy",
                    "price": 300.0,
                    "stock": 30,
                    "product_image": "cheese.jpg"
                }
            ]
            
            for product_data in sample_products:
                product = Product(**product_data)
                db.session.add(product)
            
            db.session.commit()
            print(f"✅ Added {len(sample_products)} sample products successfully!")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating sample products: {e}")
            return False

if __name__ == "__main__":
    print("🚀 Initializing Sudhamrit Dairy Farm Database...")
    print("=" * 50)
    
    # Initialize database
    if init_database():
        print("\n🎯 Database initialization completed!")
        
        # Ask user if they want to add sample data
        print("\n" + "=" * 50)
        add_samples = input("Do you want to add sample admin and products? (y/N): ").lower().strip()
        
        if add_samples in ['y', 'yes']:
            print("\n📦 Adding sample data...")
            add_sample_admin()
            add_sample_products()
            print("\n🎉 Sample data added successfully!")
        
        print("\n" + "=" * 50)
        print("✅ Setup completed! Your application is ready to use.")
        print("\nYou can now:")
        print("1. Start your Flask application")
        print("2. Register users and admins")
        print("3. Add products through admin panel")
        print("4. Test the complete e-commerce flow")
        
    else:
        print("\n❌ Database initialization failed!")