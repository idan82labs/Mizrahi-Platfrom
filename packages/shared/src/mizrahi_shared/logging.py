"""
Logging utilities for Mizrahi Compliance Platform.

This module provides structured logging setup with support for:
- Per-check loggers
- File and console output
- JSON formatting for production
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any


class JSONFormatter(logging.Formatter):
    """JSON log formatter for production environments."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add extra fields
        if hasattr(record, "check_id"):
            log_data["check_id"] = record.check_id
        if hasattr(record, "job_id"):
            log_data["job_id"] = record.job_id
        if hasattr(record, "manager_name"):
            log_data["manager_name"] = record.manager_name

        # Add exception info
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, ensure_ascii=False)


class TextFormatter(logging.Formatter):
    """Text log formatter for development environments."""

    def __init__(self):
        super().__init__(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )


def setup_logging(
    level: str = "INFO",
    format_type: str = "text",
    log_dir: Optional[Path] = None,
    job_id: Optional[str] = None,
) -> logging.Logger:
    """
    Set up logging configuration.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR).
        format_type: Format type ("text" or "json").
        log_dir: Directory for log files. If None, only console output.
        job_id: Optional job ID for organizing log files.

    Returns:
        Root logger configured for the application.
    """
    # Get or set log level from environment
    level = os.environ.get("LOG_LEVEL", level).upper()
    log_level = getattr(logging, level, logging.INFO)

    # Create formatter
    if format_type == "json":
        formatter = JSONFormatter()
    else:
        formatter = TextFormatter()

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler (if log_dir provided)
    if log_dir:
        log_dir = Path(log_dir)
        if job_id:
            log_dir = log_dir / job_id
        log_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"app_{timestamp}.log"

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    return root_logger


def get_check_logger(
    check_id: str,
    log_dir: Optional[Path] = None,
    job_id: Optional[str] = None,
) -> logging.Logger:
    """
    Get a logger for a specific check.

    Args:
        check_id: The check identifier.
        log_dir: Directory for log files.
        job_id: Optional job ID.

    Returns:
        Logger configured for the check.
    """
    logger = logging.getLogger(f"check.{check_id}")

    # Add file handler for this check if log_dir provided
    if log_dir:
        log_dir = Path(log_dir)
        if job_id:
            log_dir = log_dir / job_id
        log_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"{check_id}_{timestamp}.log"

        # Only add handler if not already present
        if not any(
            isinstance(h, logging.FileHandler) and h.baseFilename == str(log_file)
            for h in logger.handlers
        ):
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(TextFormatter())
            logger.addHandler(file_handler)

    return logger


class LogContext:
    """
    Context manager for adding extra fields to log records.

    Usage:
        with LogContext(job_id="123", manager_name="מגדל"):
            logger.info("Processing...")  # Will include job_id and manager_name
    """

    def __init__(self, **kwargs: Any):
        self.extra = kwargs
        self._old_factory = None

    def __enter__(self):
        self._old_factory = logging.getLogRecordFactory()

        def record_factory(*args, **record_kwargs):
            record = self._old_factory(*args, **record_kwargs)
            for key, value in self.extra.items():
                setattr(record, key, value)
            return record

        logging.setLogRecordFactory(record_factory)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.setLogRecordFactory(self._old_factory)


def log_check_start(logger: logging.Logger, check_id: str, check_name: str):
    """Log the start of a check."""
    logger.info(f"Starting check: {check_name} ({check_id})")


def log_check_end(
    logger: logging.Logger,
    check_id: str,
    check_name: str,
    status: str,
    findings_count: int,
    duration_ms: int,
):
    """Log the end of a check."""
    logger.info(
        f"Completed check: {check_name} ({check_id}) - "
        f"Status: {status}, Findings: {findings_count}, Duration: {duration_ms}ms"
    )


def log_finding(
    logger: logging.Logger,
    check_id: str,
    severity: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
):
    """Log a finding from a check."""
    level = {
        "error": logging.ERROR,
        "warning": logging.WARNING,
        "info": logging.INFO,
    }.get(severity.lower(), logging.INFO)

    log_message = f"[{check_id}] {message}"
    if details:
        log_message += f" | Details: {json.dumps(details, ensure_ascii=False)}"

    logger.log(level, log_message)
