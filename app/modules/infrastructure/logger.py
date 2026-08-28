"""
Centralized logging utilities.
Usage:
    from app.modules.infrastructure.logger import setup_logging, get_logger
    setup_logging(level="INFO")
    logger = get_logger(__name__)
    logger.info("hello")
"""
import logging
import os
from typing import Optional

DEFAULT_LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"

# Third-party libraries whose internal logs are noisy and rarely useful for app debugging.
_NOISY_LOGGERS = ["httpx", "httpcore", "groq", "groq._base_client"]


def setup_logging(level: Optional[str] = None, fmt: Optional[str] = None) -> None:
    """
    Configure root logger. Call this once during app startup.
    level: "DEBUG", "INFO", "WARNING", ...
    fmt: optional format string
    """
    if level is None:
        level = os.getenv("LOG_LEVEL", "INFO")
    if fmt is None:
        fmt = os.getenv("LOG_FORMAT", DEFAULT_LOG_FORMAT)

    numeric_level = getattr(logging, level.upper(), logging.INFO)

    root = logging.getLogger()
    root.setLevel(numeric_level)

    for h in list(root.handlers):
        root.removeHandler(h)

    handler = logging.StreamHandler()
    formatter = logging.Formatter(fmt)
    handler.setFormatter(formatter)
    root.addHandler(handler)

    # Keep noisy third-party libraries at WARNING regardless of app log level,
    # so switching the app to DEBUG for troubleshooting doesn't flood the console
    # with raw HTTP request/response bodies from Groq/httpx.
    for noisy_name in _NOISY_LOGGERS:
        logging.getLogger(noisy_name).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Return a logger for the given name. Ensure logging is configured with defaults
    if setup_logging() wasn't called.
    """
    root = logging.getLogger()
    if not root.handlers:
        setup_logging()
    return logging.getLogger(name)
