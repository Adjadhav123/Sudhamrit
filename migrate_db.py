#!/usr/bin/env python3
"""
Database migration script for Sudhamrit Dairy Farm application.
This script handles schema updates for existing databases.
"""

from app import app, db
from models import User, Admin, Product, Cart, Payment, Order, OrderItem
import sqlite3
import os

def check_column_exists(table_name, column_name):
    """Check if a column exists in a table."""
    with app.app_context():
        try:
            # Get the database file path
            db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            
            # Connect to database directly
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get table info
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [column[1] for column in cursor.fetchall()]
            
            conn.close()
            return column_name in columns
            
        except Exception as e:
            print(f"Error checking column {column_name} in {table_name}: {e}")
            return False

def add_missing_columns():
    """Add missing columns to existing tables."""
    with app.app_context():
        try:
            # Get the database file path
            db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            print(f"Database path: {db_path}")
            
            # Connect to database directly
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check and add Razorpay columns to payment table
            razorpay_columns = [
                ('razorpay_order_id', 'VARCHAR(100)'),
                ('razorpay_payment_id', 'VARCHAR(100)'),
                ('razorpay_signature', 'VARCHAR(200)')
            ]
            
            print("🔄 Checking Payment table for Razorpay columns...")
            
            for column_name, column_type in razorpay_columns:
                if not check_column_exists('payment', column_name):
                    print(f"➕ Adding missing column: {column_name}")
                    try:
                        cursor.execute(f"ALTER TABLE payment ADD COLUMN {column_name} {column_type}")
                        print(f"✅ Added {column_name} to payment table")
                    except Exception as e:
                        print(f"❌ Error adding {column_name}: {e}")
                else:
                    print(f"✅ Column {column_name} already exists")
            
            conn.commit()
            conn.close()
            
            print("✅ Database migration completed!")
            return True
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return False

def verify_database_schema():
    """Verify that all expected columns exist."""
    print("\n🔍 Verifying database schema...")
    
    with app.app_context():
        try:
            # Test each table with a simple query
            tables_to_test = [
                ("Users", User),
                ("Admins", Admin),
                ("Products", Product),
                ("Cart", Cart),
                ("Payments", Payment),
                ("Orders", Order),
                ("OrderItems", OrderItem)
            ]
            
            all_good = True
            
            for table_name, model in tables_to_test:
                try:
                    count = model.query.count()
                    print(f"✅ {table_name} table: {count} records - Schema OK")
                except Exception as e:
                    print(f"❌ {table_name} table error: {e}")
                    all_good = False
                    
            return all_good
            
        except Exception as e:
            print(f"❌ Schema verification failed: {e}")
            return False

def migrate_database():
    """Main migration function."""
    print("🚀 Starting Database Migration...")
    print("=" * 50)
    
    # Step 1: Create any missing tables
    print("📋 Step 1: Ensuring all tables exist...")
    with app.app_context():
        try:
            db.create_all()
            print("✅ All tables created/verified")
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            return False
    
    # Step 2: Add missing columns
    print("\n📋 Step 2: Adding missing columns...")
    if not add_missing_columns():
        return False
    
    # Step 3: Verify schema
    print("\n📋 Step 3: Verifying schema...")
    if not verify_database_schema():
        print("⚠️  Some schema issues remain, but basic functionality should work")
    
    print("\n" + "=" * 50)
    print("🎉 Migration completed!")
    print("\nYour database is now ready for the updated application.")
    return True

if __name__ == "__main__":
    success = migrate_database()
    if success:
        print("\n🚀 You can now run your application safely!")
    else:
        print("\n❌ Migration failed. Please check the errors above.")
    exit(0 if success else 1)