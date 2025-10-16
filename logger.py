#!/usr/bin/env python3
"""
Scarred Winds - Centralized Logging System
Replaces print statements with proper logging for better code quality.
"""

import logging
import sys
from datetime import datetime
from typing import Optional

class GameLogger:
    """Centralized logging system for Scarred Winds."""
    
    _instance: Optional['GameLogger'] = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialized = True
            self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration."""
        # Create logger
        self.logger = logging.getLogger('scarred_winds')
        self.logger.setLevel(logging.INFO)
        
        # Prevent duplicate handlers
        if self.logger.handlers:
            return
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler (optional)
        try:
            file_handler = logging.FileHandler('scarred_winds.log', mode='a')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        except (OSError, PermissionError):
            # If we can't create log file, just use console
            pass
    
    def info(self, message: str):
        """Log info message."""
        self.logger.info(message)
    
    def debug(self, message: str):
        """Log debug message."""
        self.logger.debug(message)
    
    def warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log error message."""
        self.logger.error(message)
    
    def critical(self, message: str):
        """Log critical message."""
        self.logger.critical(message)

# Global instance
game_logger = GameLogger()

# Convenience functions
def log_info(message: str):
    """Log info message."""
    game_logger.info(message)

def log_debug(message: str):
    """Log debug message."""
    game_logger.debug(message)

def log_warning(message: str):
    """Log warning message."""
    game_logger.warning(message)

def log_error(message: str):
    """Log error message."""
    game_logger.error(message)

def log_critical(message: str):
    """Log critical message."""
    game_logger.critical(message)
