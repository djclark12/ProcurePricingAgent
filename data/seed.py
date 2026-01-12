"""
Database seeding script.

Creates SQLite tables and populates them with sample data for the demo.
Run with: python -m data.seed
"""

import sqlite3
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent / "procurement.db"
FIXTURES_PATH = Path(__file__).parent / "fixtures.sql"


def create_database() -> None:
    """Create the database and seed with sample data."""
    print(f"Creating database at: {DB_PATH}")

    # Remove existing database
    if DB_PATH.exists():
        DB_PATH.unlink()
        print("Removed existing database")

    # Create new database
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # Read and execute fixtures
    print(f"Loading fixtures from: {FIXTURES_PATH}")
    with open(FIXTURES_PATH, "r", encoding="utf-8") as f:
        fixtures_sql = f.read()

    cursor.executescript(fixtures_sql)
    conn.commit()

    # Verify data
    print("\nData verification:")
    tables = ["items", "vendors", "price_lists", "cost_basis", "competitor_prices", "demand_notes"]
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {table}: {count} rows")

    conn.close()
    print("\n✓ Database seeded successfully!")


if __name__ == "__main__":
    create_database()
