"""Logging helpers for VisuLite."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def configure_logging(debug: bool = False) -> None:
    """Configure logging for GUI + services."""
    level = logging.DEBUG if debug else logging.INFO
    log_dir = Path.home() / ".visulite"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "visulite.log"

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s -> %(message)s"
    )

    file_handler = RotatingFileHandler(
        log_file, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    root_logger = logging.getLogger("visulite")
    root_logger.setLevel(level)
    root_logger.handlers.clear()
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


__all__ = ["configure_logging"]
