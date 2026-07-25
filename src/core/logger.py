"""Logging setup for Merchant of the Realm."""

import logging
import sys

from .config import LOG_FORMAT, LOG_DATE_FORMAT

_logger_initialized = False


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance."""
    global _logger_initialized

    if not _logger_initialized:
        logging.basicConfig(
            level=logging.INFO,
            format=LOG_FORMAT,
            datefmt=LOG_DATE_FORMAT,
            handlers=[logging.StreamHandler(sys.stderr)],
        )
        _logger_initialized = True

    return logging.getLogger(name)
