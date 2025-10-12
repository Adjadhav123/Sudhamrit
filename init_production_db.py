#!/usr/bin/env python3
"""
Simple database initialization script for production deployment.
This script should be run once after deployment to create database tables.
"""

from app import app, db
import os

def initialize_production_db():
    """Initialize database for production environment."""
    print("🚀 Initializing Production Database...")
    
    with app.app_context():
        try:
            # Create all database tables
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Verify tables were created
            from models import User, Admin, Product, Cart, Payment, Order, OrderItem
            
            # Test each table with error handling
            tables = [
                ("Users", User),
                ("Admins", Admin), 
                ("Products", Product),
                ("Cart", Cart),
                ("Payments", Payment),
                ("Orders", Order),
                ("OrderItems", OrderItem)
            ]
            
            for table_name, model in tables:
                try:
                    count = model.query.count()
                    print(f"✅ {table_name} table: {count} records")
                except Exception as e:
                    print(f"⚠️  {table_name} table warning: {e}")
                    # For Payment table, this might be a column issue
                    if "payment" in str(e).lower() and "razorpay" in str(e).lower():
                        print(f"🔧 Payment table needs migration for Razorpay columns")
                        print(f"   This is expected for existing databases")
                    
            print("\n🎉 Database initialization completed!")
            print("🚀 Application is ready to accept users!")
            
            # Additional notes for production
            print("\n📝 Notes:")
            print("   - If you see Payment table warnings about Razorpay columns,")
            print("     run 'python migrate_db.py' to update the schema")
            print("   - The application will still work for basic functionality")
            
            return True
            
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            return False

if __name__ == "__main__":
    success = initialize_production_db()
    exit(0 if success else 1)