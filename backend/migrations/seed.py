"""
Seed script: creates the default admin user and demo family.

Run AFTER migrations are complete:
    python -m migrations.seed
"""
import os
import subprocess
import sys
from pathlib import Path

from loguru import logger

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.logging import setup_logging  # noqa: E402
from app.core.security import get_password_hash  # noqa: E402
from migrations.run_migrations import _parse_db_url  # noqa: E402

setup_logging()

DEFAULT_EMAIL = "admin@family.com"
DEFAULT_PASSWORD = "admin123"

SQL = """INSERT IGNORE INTO families (id, name) VALUES ('00000000-0000-0000-0000-000000000001', 'Demo Family');
INSERT IGNORE INTO users (id, email, hashed_password, full_name, is_active, is_admin, family_id)
VALUES ('00000000-0000-0000-0000-000000000002', '{email}', '{password}', 'Admin User', TRUE, TRUE, '00000000-0000-0000-0000-000000000001');
""".format(email=DEFAULT_EMAIL, password=get_password_hash(DEFAULT_PASSWORD))


def seed():
    logger.info("Seeding default user: {} / {}", DEFAULT_EMAIL, DEFAULT_PASSWORD)

    db_url = os.environ.get("DATABASE_URL", "")
    if not db_url:
        logger.error("DATABASE_URL environment variable is not set")
        sys.exit(1)

    db = _parse_db_url(db_url)

    result = subprocess.run(
        ["mariadb", "--skip-ssl", "-u", db["user"], f"-p{db['password']}", "-h", db["host"], "-P", db["port"], db["database"]],
        input=SQL,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        logger.error("Seed failed:\n{}", result.stderr)
        sys.exit(1)

    logger.info("Seed complete. Login with {} / {}", DEFAULT_EMAIL, DEFAULT_PASSWORD)


if __name__ == "__main__":
    seed()
