"""
Database connection and initialization for the inventory system.

Provides database connection management and initialization with migrations.
"""

import sqlite3
from sqlite3 import Error
from typing import Optional

from config.settings import settings
from database.migrations import run_migrations
from database.backup import create_backup, cleanup_old_backups
from utils.logging_config import logger


def get_connection() -> Optional[sqlite3.Connection]:
    """
    Get database connection with row factory for dict access.
    
    Returns:
        Database connection or None if connection fails.
    """
    try:
        conn = sqlite3.connect(settings.DB_PATH)
        conn.row_factory = sqlite3.Row  # access columns by name
        return conn
    except Error as e:
        logger.error(f"Database connection error: {e}")
        return None


def initialize_db() -> None:
    """
    Initialize database with migrations and backup.
    
    Runs migrations on startup and creates daily backup.
    """
    try:
        # Run migrations
        run_migrations()
        
        # Create daily backup
        create_backup()
        
        # Cleanup old backups (keep last 30)
        cleanup_old_backups(keep_count=30)
        
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise