"""Logging configuration and utilities."""
import logging
import logging.handlers
import os
from pathlib import Path
from src.core.config import settings

# Create logs directory if it doesn't exist
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)


def get_logger(name: str) -> logging.Logger:
    """
    Get or create a logger with consistent configuration.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger  # Already configured

    # Set log level
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(log_level)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)

    # File handler (rotating file handler)
    log_file = log_dir / f"chatbot.log"
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10,
    )
    file_handler.setLevel(log_level)

    # Error file handler
    error_log_file = log_dir / f"chatbot_error.log"
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10,
    )
    error_handler.setLevel(logging.ERROR)

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    error_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)

    return logger


# Configure root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

# Root console handler
root_console_handler = logging.StreamHandler()
root_console_handler.setLevel(logging.INFO)
root_formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
root_console_handler.setFormatter(root_formatter)
root_logger.addHandler(root_console_handler)
