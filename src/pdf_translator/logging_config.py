"""Logging configuration for PDF Translator."""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
    console: bool = True,
) -> logging.Logger:
    """Set up logging for the application.
    
    Args:
        level: Logging level (default: INFO)
        log_file: Optional path to log file
        console: Whether to log to console (default: True)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("pdf_translator")
    logger.setLevel(level)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Format
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = "pdf_translator") -> logging.Logger:
    """Get a logger instance.
    
    Args:
        name: Logger name (will be prefixed with 'pdf_translator.')
        
    Returns:
        Logger instance
    """
    if name == "pdf_translator":
        return logging.getLogger(name)
    return logging.getLogger(f"pdf_translator.{name}")


# Default logger setup
_default_logger: Optional[logging.Logger] = None


def get_default_logger() -> logging.Logger:
    """Get the default application logger, initializing if needed."""
    global _default_logger
    if _default_logger is None:
        _default_logger = setup_logging()
    return _default_logger
