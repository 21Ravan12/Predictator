"""Structured logging configuration"""

import logging
import sys
from datetime import datetime
from typing import Optional
import json


class JSONFormatter(logging.Formatter):
    """Format logs as JSON for better parsing"""
    
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        
        if hasattr(record, "extra"):
            log_entry["extra"] = record.extra
        
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry)


class ColoredFormatter(logging.Formatter):
    """Colorful console formatter for development"""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'
    }
    
    def format(self, record):
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        record.levelname = f"{color}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


def setup_logger(
    name: str = "predictator",
    level: str = "INFO",
    json_format: bool = False,
    log_file: Optional[str] = None
) -> logging.Logger:
    """Setup logger with console and file handlers"""
    
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    if json_format:
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(ColoredFormatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(JSONFormatter())
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = None) -> logging.Logger:
    """Get logger instance"""
    if name:
        return logging.getLogger(f"predictator.{name}")
    return logging.getLogger("predictator")


class LoggerContext:
    """Context manager for logging with extra context"""
    
    def __init__(self, logger: logging.Logger, **kwargs):
        self.logger = logger
        self.kwargs = kwargs
    
    def __enter__(self):
        self.old_extra = getattr(self.logger, 'extra', {})
        self.logger.extra = {**self.old_extra, **self.kwargs}
        return self
    
    def __exit__(self, *args):
        self.logger.extra = self.old_extra


def log_function_call(logger: logging.Logger = None):
    """Decorator to log function calls"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            log = logger or get_logger(func.__name__)
            log.debug(f"Calling {func.__name__}")
            try:
                result = func(*args, **kwargs)
                log.debug(f"{func.__name__} completed")
                return result
            except Exception as e:
                log.error(f"{func.__name__} failed: {e}")
                raise
        return wrapper
    return decorator


# Default logger instance
default_logger = setup_logger()