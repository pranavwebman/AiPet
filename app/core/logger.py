"""Structured logging module for AIPet."""

import logging
import sys
from logging.handlers import RotatingFileHandler
from app.core.config import get_logs_dir

def setup_logger(name: str = "AIPet") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] (%(filename)s:%(lineno)d) - %(message)s"
    )

    # File Handler
    log_file = get_logs_dir() / "aipet.log"
    file_handler = RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console Handler (if stdout is available)
    if sys.stdout:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger

logger = setup_logger()
