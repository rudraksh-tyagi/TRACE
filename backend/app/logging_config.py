"""
TRACE logging configuration.
"""

import logging
import sys

from app.config.settings import settings


def configure_logging() -> None:
    """
    Configure application-wide logging.
    """

    level = getattr(
        logging,
        settings.log_level.upper(),
        logging.INFO,
    )

    formatter = logging.Formatter(
        fmt=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler(
        sys.stdout
    )

    console_handler.setFormatter(
        formatter
    )

    root_logger = logging.getLogger()

    root_logger.setLevel(level)

    # Prevent duplicate handlers when reload is enabled.
    if not root_logger.handlers:

        root_logger.addHandler(
            console_handler
        )

    else:

        for handler in root_logger.handlers:
            handler.setFormatter(formatter)

    logging.getLogger(
        "trace"
    ).info(
        "Logging initialized | level=%s",
        settings.log_level.upper(),
    )