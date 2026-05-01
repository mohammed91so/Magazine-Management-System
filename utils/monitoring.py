"""
Monitoring and telemetry utilities for the inventory system.

Provides error tracking, metrics collection, and health checks.
"""

import traceback
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from utils.logging_config import logger
from config.settings import settings


class MonitoringService:
    """Service for monitoring application health and collecting metrics."""
    
    def __init__(self):
        """Initialize monitoring service."""
        self.metrics: Dict[str, Any] = {
            "start_time": datetime.now().isoformat(),
            "error_count": 0,
            "warning_count": 0,
            "operation_count": 0
        }
    
    def log_error(self, error: Exception, context: str = "") -> None:
        """
        Log an error with context.
        
        Args:
            error: The exception that occurred.
            context: Additional context about where the error occurred.
        """
        self.metrics["error_count"] += 1
        error_info = {
            "timestamp": datetime.now().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "traceback": traceback.format_exc()
        }
        logger.error(f"Error in {context}: {error}\n{traceback.format_exc()}")
    
    def log_warning(self, message: str, context: str = "") -> None:
        """
        Log a warning with context.
        
        Args:
            message: Warning message.
            context: Additional context.
        """
        self.metrics["warning_count"] += 1
        logger.warning(f"Warning in {context}: {message}")
    
    def log_operation(self, operation: str) -> None:
        """
        Log an operation.
        
        Args:
            operation: Description of the operation.
        """
        self.metrics["operation_count"] += 1
        logger.debug(f"Operation: {operation}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current metrics.
        
        Returns:
            Dictionary of current metrics.
        """
        uptime = datetime.now() - datetime.fromisoformat(self.metrics["start_time"])
        self.metrics["uptime_seconds"] = uptime.total_seconds()
        return self.metrics.copy()
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on system components.
        
        Returns:
            Dictionary with health status of each component.
        """
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "status": "healthy",
            "components": {}
        }
        
        # Check database
        try:
            from database.db import get_connection
            conn = get_connection()
            if conn:
                conn.close()
                health_status["components"]["database"] = {"status": "healthy"}
            else:
                health_status["components"]["database"] = {"status": "unhealthy", "message": "Connection failed"}
                health_status["status"] = "degraded"
        except Exception as e:
            health_status["components"]["database"] = {"status": "unhealthy", "message": str(e)}
            health_status["status"] = "unhealthy"
        
        # Check logs directory
        try:
            if settings.LOG_PATH.exists():
                health_status["components"]["logs"] = {"status": "healthy"}
            else:
                health_status["components"]["logs"] = {"status": "unhealthy", "message": "Logs directory missing"}
                health_status["status"] = "degraded"
        except Exception as e:
            health_status["components"]["logs"] = {"status": "unhealthy", "message": str(e)}
            health_status["status"] = "unhealthy"
        
        # Check backup directory
        try:
            if settings.BACKUP_PATH.exists():
                health_status["components"]["backups"] = {"status": "healthy"}
            else:
                health_status["components"]["backups"] = {"status": "unhealthy", "message": "Backup directory missing"}
                health_status["status"] = "degraded"
        except Exception as e:
            health_status["components"]["backups"] = {"status": "unhealthy", "message": str(e)}
            health_status["status"] = "unhealthy"
        
        return health_status


# Global monitoring instance
monitoring = MonitoringService()
