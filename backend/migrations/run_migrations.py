"""
Migration runner for raw SQL migrations.

Uses the MariaDB/MySQL CLI directly (not SQLAlchemy) for reliable DDL execution.
"""
import subprocess
import sys
from pathlib import Path

from loguru import logger

from app.core.logging import setup_logging

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

setup_logging()


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
                "-u", "budget_user",
                "-pbudget_pass",
                "-h", "db",
                "-P", "3306",
                "family_budget",
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
