"""
Logging Configuration Module
Centralized logging setup for the diagnostic platform
"""

import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime


def setup_logging(
    log_dir: str = "data/logs",
    log_name: str = "diagnostic_platform",
    level: int = logging.INFO
) -> logging.Logger:
    """
    Configure logging with both file and console handlers
    
    Args:
        log_dir: Directory to store log files
        log_name: Name of the log file
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    # Create log directory if it doesn't exist
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(__name__)
    logger.setLevel(level)
    
    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Log file path
    log_file = Path(log_dir) / f"{log_name}_{datetime.now().strftime('%Y%m%d')}.log"
    
    # ==========================================
    # FILE HANDLER (Rotating)
    # ==========================================
    file_handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,  # Keep 5 backup files
        encoding='utf-8',
        mode='a'
    )
    file_handler.setLevel(level)
    
    file_formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)-8s | %(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    
    # ==========================================
    # CONSOLE HANDLER
    # ==========================================
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    console_formatter = logging.Formatter(
        '%(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logger.info(f"Logging initialized. Log file: {log_file}")
    return logger


# ==========================================
# MODULE-SPECIFIC LOGGERS
# ==========================================
def get_logger(module_name: str) -> logging.Logger:
    """
    Get a logger for a specific module
    
    Args:
        module_name: Name of the module (__name__)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(module_name)


# ==========================================
# PERFORMANCE LOGGER
# ==========================================
class PerformanceLogger:
    """Track execution times and performance metrics"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.metrics = {}
    
    def log_execution_time(self, operation_name: str, duration_ms: float):
        """Log operation execution time"""
        self.logger.info(f"⏱️ {operation_name} took {duration_ms:.2f}ms")
        
        if operation_name not in self.metrics:
            self.metrics[operation_name] = []
        self.metrics[operation_name].append(duration_ms)
    
    def get_statistics(self, operation_name: str) -> dict:
        """Get performance statistics for an operation"""
        if operation_name not in self.metrics:
            return {}
        
        times = self.metrics[operation_name]
        return {
            'count': len(times),
            'min_ms': min(times),
            'max_ms': max(times),
            'avg_ms': sum(times) / len(times),
        }


# Initialize global performance logger
perf_logger = PerformanceLogger()
