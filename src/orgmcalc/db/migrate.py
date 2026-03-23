"""Numbered SQL migration runner."""

import logging
from pathlib import Path

from orgmcalc.db.connection import get_sync_connection

logger = logging.getLogger(__name__)
MIGRATIONS_DIR = Path(__file__).parent.parent.parent.parent / "migrations"


def init_schema_migrations() -> None:
    """Create the schema_migrations tracking table if it doesn't exist."""
    conn = get_sync_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version INTEGER PRIMARY KEY,
                    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
        conn.commit()
    finally:
        conn.close()


def get_applied_migrations() -> set[int]:
    """Get set of already applied migration versions."""
    conn = get_sync_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT version FROM schema_migrations")
            return {row[0] for row in cur.fetchall()}
    finally:
        conn.close()


def apply_migration(version: int, sql: str) -> None:
    """Apply a single migration and record it."""
    conn = get_sync_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            cur.execute("INSERT INTO schema_migrations (version) VALUES (%s)", (version,))
        conn.commit()
        logger.info(f"Applied migration {version:04d}")
    except Exception as e:
        conn.rollback()
        raise RuntimeError(f"Migration {version:04d} failed: {e}") from e
    finally:
        conn.close()


def run_migrations() -> list[int]:
    """Run all pending migrations and return list of applied versions."""
    init_schema_migrations()
    applied = get_applied_migrations()

    if not MIGRATIONS_DIR.exists():
        logger.warning(f"Migrations directory not found: {MIGRATIONS_DIR}")
        return []

    # Find all .sql files and sort by numeric prefix
    migration_files = sorted(f for f in MIGRATIONS_DIR.glob("*.sql") if f.stem[:4].isdigit())

    newly_applied: list[int] = []

    for migration_file in migration_files:
        version = int(migration_file.stem[:4])

        if version in applied:
            continue

        sql = migration_file.read_text()
        apply_migration(version, sql)
        newly_applied.append(version)

    if newly_applied:
        logger.info(f"Applied {len(newly_applied)} migration(s): {newly_applied}")
    else:
        logger.info("No migrations to apply")

    return newly_applied
