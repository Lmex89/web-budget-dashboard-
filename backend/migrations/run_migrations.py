"""
Migration runner for raw SQL migrations.

Uses the MariaDB/MySQL CLI directly (not SQLAlchemy) for reliable DDL execution.
Expects DATABASE_URL env var (set via .env.docker in Docker Compose) with format:
mysql+aiomysql://user:password@host:port/database
"""
import os
import re
import subprocess
import sys
from pathlib import Path

from loguru import logger

from app.core.logging import setup_logging

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

setup_logging()


def _parse_db_url(url: str) -> dict[str, str]:
    match = re.match(
        r"mysql\+aiomysql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)",
        url,
    )
    if not match:
        logger.error("Cannot parse DATABASE_URL: {}", url)
        sys.exit(1)
    return {
        "user": match.group(1),
        "password": match.group(2),
        "host": match.group(3),
        "port": match.group(4),
        "database": match.group(5),
    }


def get_migration_files() -> list[Path]:
    migrations_dir = Path(__file__).parent / "sql"
    if not migrations_dir.exists():
        logger.error("Migrations directory not found: {}", migrations_dir)
        return []
    files = sorted(migrations_dir.glob("*.sql"))
    logger.info("Found {} migration file(s) in {}", len(files), migrations_dir)
    return files


def run_migrations():
    logger.info("=" * 60)
    logger.info("STARTING DATABASE MIGRATIONS")
    logger.info("=" * 60)

    db_url = os.environ.get("DATABASE_URL", "")
    if not db_url:
        logger.error("DATABASE_URL environment variable is not set")
        sys.exit(1)

    db = _parse_db_url(db_url)

    migration_files = get_migration_files()
    if not migration_files:
        logger.warning("No migration files found. Nothing to apply.")
        return

    for migration_file in migration_files:
        logger.info("Applying migration: {}", migration_file.name)

        with open(migration_file, "r") as f:
            sql_content = f.read()

        result = subprocess.run(
            [
                "mariadb",
                "--skip-ssl",
                "-u", db["user"],
                f"-p{db['password']}",
                "-h", db["host"],
                "-P", db["port"],
                db["database"],
            ],
            input=sql_content,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            logger.error("Migration {} failed:\n{}", migration_file.name, result.stderr)
            sys.exit(1)

        if result.stderr:
            logger.warning("Migration {} stderr: {}", migration_file.name, result.stderr.strip())

        logger.info("  ✓ {} applied", migration_file.name)

    logger.info("=" * 60)
    logger.info("MIGRATIONS COMPLETE")
    logger.info("=" * 60)


if __name__ == "__main__":
    run_migrations()
