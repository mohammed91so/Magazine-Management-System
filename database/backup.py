"""
Database backup utilities for the inventory system.

Provides automatic daily backup and versioned backup management.
"""

import shutil
from datetime import datetime
from pathlib import Path

from config.settings import settings
from utils.logging_config import logger


def create_backup() -> Path:
    """
    Create a timestamped backup of the database.
    
    Returns:
        Path to the backup file.
    """
    # Ensure backup directory exists
    settings.ensure_directories()
    
    # Generate backup filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"inventory_{timestamp}.db"
    backup_path = settings.BACKUP_PATH / backup_filename
    
    # Copy database file
    try:
        shutil.copy2(settings.DB_PATH, backup_path)
        logger.info(f"Database backup created: {backup_path}")
        return backup_path
    except FileNotFoundError:
        logger.error(f"Database file not found: {settings.DB_PATH}")
        raise
    except Exception as e:
        logger.error(f"Failed to create backup: {e}")
        raise


def cleanup_old_backups(keep_count: int = 30) -> None:
    """
    Remove old backups, keeping only the most recent ones.
    
    Args:
        keep_count: Number of backups to keep.
    """
    if not settings.BACKUP_PATH.exists():
        return
    
    # Get all backup files
    backup_files = sorted(
        settings.BACKUP_PATH.glob("inventory_*.db"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    
    # Remove old backups
    for backup_file in backup_files[keep_count:]:
        try:
            backup_file.unlink()
            logger.info(f"Removed old backup: {backup_file}")
        except Exception as e:
            logger.error(f"Failed to remove backup {backup_file}: {e}")


def restore_backup(backup_path: Path) -> None:
    """
    Restore database from a backup file.
    
    Args:
        backup_path: Path to the backup file.
    """
    if not backup_path.exists():
        raise FileNotFoundError(f"Backup file not found: {backup_path}")
    
    try:
        # Create backup of current database before restoring
        current_backup = create_backup()
        logger.info(f"Created pre-restore backup: {current_backup}")
        
        # Restore from backup
        shutil.copy2(backup_path, settings.DB_PATH)
        logger.info(f"Database restored from: {backup_path}")
    except Exception as e:
        logger.error(f"Failed to restore backup: {e}")
        raise


def get_backup_list() -> list[Path]:
    """
    Get list of available backup files.
    
    Returns:
        List of backup file paths, sorted by date (newest first).
    """
    if not settings.BACKUP_PATH.exists():
        return []
    
    return sorted(
        settings.BACKUP_PATH.glob("inventory_*.db"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
