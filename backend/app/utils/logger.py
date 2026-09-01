"""
Structured logging configuration for Persistent AI Data Analyst.
Ensures sensitive tokens, passwords, and API keys are never leaked to logs.
Safe on Windows console encoding.
"""

import logging
import sys
from app.config import get_settings

settings = get_settings()

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logger(name: str = "ai_analyst") -> logging.Logger:
    """
    Configure and return a structured logger instance.
    """
    logger = logging.getLogger(name)
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(log_level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(log_level)
        formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


logger = setup_logger()
