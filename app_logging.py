from __future__ import annotations

import logging
import sys

from app.core.config import get_settings

_CONFIGURED = False


def setup_logging() -> logging.Logger:
    global _CONFIGURED
    settings = get_settings()
    logger = logging.getLogger("david_ai")

    if not _CONFIGURED:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG if settings.debug else logging.INFO)
        logger.propagate = False
        _CONFIGURED = True

    return logger


logger = setup_logging()


def log_startup() -> None:
    settings = get_settings()
    logger.info(f"Starting {settings.app_name} in {settings.app_env} mode")


def log_shutdown() -> None:
    logger.info("Shutting down David AI backend")


def log_request(method: str, path: str) -> None:
    logger.info(f"Request: {method} {path}")


def log_error(context: str, error: Exception) -> None:
    logger.error(f"Error in {context}: {error}")


def log_provider_selection(provider: str) -> None:
    logger.info(f"Provider selected: {provider}")


def log_upload(filename: str, size_bytes: int) -> None:
    logger.info(f"File uploaded: {filename} ({size_bytes} bytes)")
