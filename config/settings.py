"""
Configuration management for the inventory system.

Loads environment variables and provides application settings.
"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Database
    DB_NAME: str = os.getenv("DB_NAME", "inventory.db")
    DB_BACKUP_DIR: str = os.getenv("DB_BACKUP_DIR", "backups")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR: str = os.getenv("LOG_DIR", "logs")
    
    # Application
    APP_NAME: str = os.getenv("APP_NAME", "Inventory System")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    DB_PATH: Path = BASE_DIR / DB_NAME
    BACKUP_PATH: Path = BASE_DIR / DB_BACKUP_DIR
    LOG_PATH: Path = BASE_DIR / LOG_DIR
    
    @classmethod
    def ensure_directories(cls) -> None:
        """Ensure required directories exist."""
        cls.BACKUP_PATH.mkdir(parents=True, exist_ok=True)
        cls.LOG_PATH.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production mode."""
        return cls.ENVIRONMENT.lower() == "production"


# Global settings instance
settings = Settings()
