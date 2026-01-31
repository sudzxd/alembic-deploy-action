"""Centralized logger setup."""

from __future__ import annotations

# =============================================================================
# IMPORTS
# =============================================================================
# Standard Library
import logging
import sys

# Project/Local
from src.constants import LOG_DATE_FORMAT, LOG_FORMAT


# =============================================================================
# PUBLIC API
# =============================================================================
def setup_logger(name: str = __name__, level: int = logging.INFO) -> logging.Logger:
    """Setup and return a configured logger.

    Args:
        name: Name of the logger.
        level: Logging level.

    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(level)
    return logger
