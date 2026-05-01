"""
Database migration engine for the inventory system.

Tracks applied migrations and auto-runs on startup.
"""

import sqlite3
from pathlib import Path
from typing import List

from config.settings import settings
from utils.logging_config import logger


class Migration:
    """Represents a database migration."""
    
    def __init__(self, version: int, name: str, up_sql: str):
        self.version = version
        self.name = name
        self.up_sql = up_sql


# Define migrations
MIGRATIONS: List[Migration] = [
    Migration(
        version=1,
        name="initial_schema",
        up_sql="""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            purchase_price REAL NOT NULL CHECK(purchase_price >= 0),
            selling_price REAL NOT NULL CHECK(selling_price >= 0),
            quantity INTEGER NOT NULL CHECK(quantity >= 0),
            expiration_date TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            quantity INTEGER NOT NULL CHECK(quantity > 0),
            total_price REAL NOT NULL,
            profit REAL NOT NULL,
            date TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE
        );
        """
    ),
    Migration(
        version=2,
        name="add_indexes",
        up_sql="""
        CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);
        CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(date);
        CREATE INDEX IF NOT EXISTS idx_sales_product_id ON sales(product_id);
        """
    ),
    Migration(
        version=3,
        name="add_migration_tracking",
        up_sql="""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            applied_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """
    ),
]


def get_connection() -> sqlite3.Connection:
    """Get database connection."""
    return sqlite3.connect(settings.DB_PATH)


def ensure_migration_table() -> None:
    """Ensure migration tracking table exists."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            applied_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    conn.commit()
    conn.close()


def get_applied_migrations() -> List[int]:
    """Get list of applied migration versions."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT version FROM schema_migrations ORDER BY version")
    rows = cursor.fetchall()
    
    conn.close()
    return [row[0] for row in rows]


def apply_migration(migration: Migration) -> None:
    """
    Apply a single migration.
    
    Args:
        migration: Migration to apply.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        # Execute migration SQL
        cursor.executescript(migration.up_sql)
        
        # Record migration
        cursor.execute(
            "INSERT INTO schema_migrations (version, name) VALUES (?, ?)",
            (migration.version, migration.name)
        )
        
        conn.commit()
        logger.info(f"Applied migration {migration.version}: {migration.name}")
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to apply migration {migration.version}: {e}")
        raise
    finally:
        conn.close()


def run_migrations() -> None:
    """Run all pending migrations."""
    logger.info("Checking for pending migrations...")
    
    # Ensure migration table exists
    ensure_migration_table()
    
    # Get applied migrations
    applied = get_applied_migrations()
    
    # Apply pending migrations
    for migration in MIGRATIONS:
        if migration.version not in applied:
            logger.info(f"Applying migration {migration.version}: {migration.name}")
            apply_migration(migration)
        else:
            logger.debug(f"Migration {migration.version} already applied")
    
    logger.info("Migration check complete")
