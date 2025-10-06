#!/usr/bin/env python3
"""
Quick test to verify database connection and tables.
"""

import os
import sys

# Add the parent directory to sys path to import utils module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from sqlalchemy import inspect
from utils.database import get_engine


def main():
    # Load environment variables
    load_dotenv()

    print("🔍 Testing database connection...")

    try:
        # Get database engine
        engine = get_engine()
        print(f"✅ Connected to: {engine.url}")

        # Test connection
        with engine.connect() as conn:
            print("✅ Database connection successful!")

        # Inspect tables
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        print(f"\n📊 Found {len(tables)} tables:")
        for table in tables:
            columns = inspector.get_columns(table)
            print(f"\n  📋 {table} ({len(columns)} columns):")
            for col in columns[:5]:  # Show the first 5 columns
                print(f"     - {col['name']}: {col['type']}")
            if len(columns) > 5:
                print(f"     ... and {len(columns) - 5} more columns")

        print("\n✅ Database is ready to use!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
