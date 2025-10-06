#!/usr/bin/env python3
"""
Script to initialize the SQLite database for the Medical Data Management System.
This creates all necessary tables based on the SQLAlchemy models.
"""

import os
import sys

# Add parent directory to path to import utils module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from utils.database import get_engine, init_database


def main():
    # Load environment variables from .env file
    load_dotenv()

    # Check if DATABASE_URL is set
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("❌ ERROR: DATABASE_URL not found in environment variables")
        print("Please ensure .env file exists and contains DATABASE_URL")
        return

    print(f"📊 Database URL: {database_url}")
    print("🔧 Initializing database...")

    try:
        # Initialize the database (creates all tables)
        init_database()
        print("✅ Database initialized successfully!")

        # Verify the database was created
        engine = get_engine()
        print(f"✅ Database engine created: {engine.url}")

        # List the tables that were created
        from sqlalchemy import inspect

        inspector = inspect(engine)
        tables = inspector.get_table_names()

        print(f"\n📋 Created {len(tables)} tables:")
        for table in tables:
            print(f"   • {table}")

        print("\n🎉 Database setup complete! You can now run the application.")

    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
