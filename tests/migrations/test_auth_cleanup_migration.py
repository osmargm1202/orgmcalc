"""Verification for consolidated initial migration."""

from __future__ import annotations

from pathlib import Path


def test_only_one_init_migration_exists() -> None:
    migrations_dir = Path("migrations")
    sql_files = sorted(p.name for p in migrations_dir.glob("*.sql"))

    assert sql_files == ["0001_init.sql"]


def test_0001_contains_clientes_and_no_deprecated_tables() -> None:
    sql = Path("migrations/0001_init.sql").read_text(encoding="utf-8")

    assert "CREATE TABLE IF NOT EXISTS clientes" in sql
    assert "cliente_id TEXT REFERENCES clientes(id) ON DELETE SET NULL" in sql
    assert "CREATE TABLE IF NOT EXISTS calculo_empresas" not in sql
    assert "CREATE TABLE IF NOT EXISTS calculo_ingenieros" not in sql
