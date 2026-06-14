"""
Logging configuration for the Family Budget API.

Uses loguru for structured, human-readable logging with automatic
traceback capture. Configured once at startup; all modules import
``from loguru import logger`` directly.

Log levels used throughout the codebase:
    DEBUG    – Detailed diagnostic information (DB queries, param dumps)
    INFO     – Normal operational messages (CRUD ops, auth)
    WARNING  – Unexpected but handled situations (validation failures)
    ERROR    – Runtime errors that need investigation (DB failures)
    EXCEPTION– Always used inside ``except`` blocks (auto traceback)
"""
import sys

from loguru import logger

from app.core.config import settings


class HealthCheckFilter:
    """Suppresses health-check log lines to reduce noise."""

    def __call__(self, record) -> bool:
        return "/health" not in record["message"] or record["level"].no >= 40


def setup_logging() -> None:
    """Configure loguru sinks and format once at application startup."""
    logger.remove()  # remove default stderr sink

    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level:<8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    log_level = getattr(settings, "LOG_LEVEL", "INFO").upper()

    logger.add(
        sys.stdout,
        format=log_format,
        level=log_level,
        colorize=True,
        filter=HealthCheckFilter(),
    )

    # Optional file rotation for production
    if settings.ENVIRONMENT == "production":
        logger.add(
            "logs/app_{time:YYYY-MM-DD}.log",
            rotation="10 MB",
            retention="30 days",
            level="DEBUG",
            format="{time} | {level:<8} | {name}:{function}:{line} | {message}",
            compression="gz",
        )

    # Quiet third-party loggers via their standard-logging bridge
    import logging
    for lib in ("aiomysql", "asyncio", "urllib3"):
        logging.getLogger(lib).setLevel(logging.WARNING)

    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.DEBUG if settings.DB_ECHO else logging.WARNING
    )

    logger.info("Loguru configured | level={} | environment={}", log_level, settings.ENVIRONMENT)
