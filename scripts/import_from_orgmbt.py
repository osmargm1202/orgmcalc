#!/usr/bin/env python3
"""Import script to migrate data from orgmbt to orgmcalc.

This script connects to the orgmbt database and imports:
- Projects (proyectos)
- Companies (empresas)
- Engineers (ingenieros)

Usage:
    python scripts/import_from_orgmbt.py

Environment variables:
    DATABASE_URL: Connection string for orgmcalc database (target)
    ORGMBT_DATABASE_URL: Connection string for orgmbt database (source)
    DRY_RUN: Set to "true" to preview changes without writing

"""

from __future__ import annotations

import asyncio
import os
import sys
from typing import Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import psycopg
from psycopg.rows import dict_row


# Target database (orgmcalc) - uses DATABASE_URL env var
ORGMCALC_DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://user:password@localhost:5432/orgmcalc"
)

# Source database (orgmbt)
ORGMBT_DATABASE_URL = os.environ.get(
    "ORGMBT_DATABASE_URL", "postgresql://user:password@localhost:5432/orgmbt"
)

DRY_RUN = os.environ.get("DRY_RUN", "false").lower() == "true"


class Importer:
    """Handles importing data from orgmbt to orgmcalc."""

    def __init__(self) -> None:
        self.source_conn: psycopg.AsyncConnection | None = None
        self.target_conn: psycopg.AsyncConnection | None = None
        self.stats: dict[str, int] = {
            "proyectos_imported": 0,
            "proyectos_skipped": 0,
            "empresas_imported": 0,
            "empresas_skipped": 0,
            "ingenieros_imported": 0,
            "ingenieros_skipped": 0,
        }

    async def connect(self) -> None:
        """Connect to both databases."""
        print(f"Connecting to source database (orgmbt)...")
        self.source_conn = await psycopg.AsyncConnection.connect(
            ORGMBT_DATABASE_URL,
            row_factory=dict_row,
        )

        print(f"Connecting to target database (orgmcalc)...")
        self.target_conn = await psycopg.AsyncConnection.connect(
            ORGMCALC_DATABASE_URL,
            row_factory=dict_row,
        )
        print("Connected successfully.\n")

    async def close(self) -> None:
        """Close database connections."""
        if self.source_conn:
            await self.source_conn.close()
        if self.target_conn:
            await self.target_conn.close()

    async def import_empresas(self) -> None:
        """Import companies from orgmbt."""
        print("=== Importing Empresas ===")

        async with self.target_conn.cursor() as cur:  # type: ignore[union-attr]
            await cur.execute("SELECT id FROM empresas")
            existing_ids = {row["id"] for row in await cur.fetchall()}

        async with self.source_conn.cursor() as cur:  # type: ignore[union-attr]
            await cur.execute("""
                SELECT id, nombre, lema, created_at, updated_at
                FROM empresas
                ORDER BY id
            """)
            empresas = await cur.fetchall()

        print(f"Found {len(empresas)} empresas in source")

        for empresa in empresas:
            empresa_id = empresa["id"]

            if empresa_id in existing_ids:
                print(f"  Skipping empresa {empresa_id} (already exists)")
                self.stats["empresas_skipped"] += 1
                continue

            if DRY_RUN:
                print(f"  [DRY RUN] Would import empresa {empresa_id}: {empresa['nombre']}")
                self.stats["empresas_imported"] += 1
                continue

            async with self.target_conn.cursor() as cur:  # type: ignore[union-attr]
                await cur.execute(
                    """
                    INSERT INTO empresas (id, nombre, logo_url, contacto, telefono, correo,
                                         direccion, ciudad, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                """,
                    (
                        empresa_id,
                        empresa["nombre"],
                        None,  # logo_url - will be populated via file upload later
                        empresa["lema"]
                        if empresa.get("lema")
                        else None,  # Use lema as contacto if available
                        None,  # telefono
                        None,  # correo
                        None,  # direccion
                        None,  # ciudad
                        empresa["created_at"],
                        empresa["updated_at"],
                    ),
                )

            await self.target_conn.commit()  # type: ignore[union-attr]
            print(f"  Imported empresa {empresa_id}: {empresa['nombre']}")
            self.stats["empresas_imported"] += 1

        print()

    async def import_ingenieros(self) -> None:
        """Import engineers from orgmbt."""
        print("=== Importing Ingenieros ===")

        async with self.target_conn.cursor() as cur:  # type: ignore[union-attr]
            await cur.execute("SELECT id FROM ingenieros")
            existing_ids = {row["id"] for row in await cur.fetchall()}

        async with self.source_conn.cursor() as cur:  # type: ignore[union-attr]
            await cur.execute("""
                SELECT id, codia, nombres, apellidos, id_empresas,
                       telefono_celular, correo, created_at, updated_at
                FROM ingenieros
                ORDER BY id
            """)
            ingenieros = await cur.fetchall()

        print(f"Found {len(ingenieros)} ingenieros in source")

        for ingeniero in ingenieros:
            ingeniero_id = ingeniero["id"]

            if ingeniero_id in existing_ids:
                print(f"  Skipping ingeniero {ingeniero_id} (already exists)")
                self.stats["ingenieros_skipped"] += 1
                continue

            # Concatenate nombres and apellidos for full name
            nombre_completo = f"{ingeniero['nombres'] or ''} {ingeniero['apellidos'] or ''}".strip()
            if not nombre_completo:
                nombre_completo = f"Ingeniero {ingeniero_id}"

            # Use codia as profesion if available
            profesion = f"CODIA: {ingeniero['codia']}" if ingeniero.get("codia") else None

            if DRY_RUN:
                print(f"  [DRY RUN] Would import ingeniero {ingeniero_id}: {nombre_completo}")
                self.stats["ingenieros_imported"] += 1
                continue

            async with self.target_conn.cursor() as cur:  # type: ignore[union-attr]
                await cur.execute(
                    """
                    INSERT INTO ingenieros (id, nombre, email, telefono, profesion, id_empresas,
                                           foto_perfil_url, foto_carnet_url, foto_certificacion_url,
                                           created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                """,
                    (
                        ingeniero_id,
                        nombre_completo,
                        ingeniero["correo"] if ingeniero.get("correo") else None,
                        ingeniero["telefono_celular"]
                        if ingeniero.get("telefono_celular")
                        else None,
                        profesion,
                        ingeniero.get("id_empresas", ""),  # Import company restrictions
                        None,  # foto_perfil_url
                        None,  # foto_carnet_url
                        None,  # foto_certificacion_url
                        ingeniero["created_at"],
                        ingeniero["updated_at"],
                    ),
                )

            await self.target_conn.commit()  # type: ignore[union-attr]
            print(f"  Imported ingeniero {ingeniero_id}: {nombre_completo}")
            self.stats["ingenieros_imported"] += 1

        print()

    async def import_proyectos(self) -> None:
        """Import projects from orgmbt.

        Note: Projects don't have empresa/ingeniero directly in orgmcalc.
        Those are assigned per calculation (calculo).
        """
        print("=== Importing Proyectos ===")

        # Get existing proyectos from target to check for duplicates
        async with self.target_conn.cursor() as cur:  # type: ignore[union-attr]
            await cur.execute("SELECT id FROM projects")
            existing_ids = {row["id"] for row in await cur.fetchall()}

        # Fetch proyectos from source
        async with self.source_conn.cursor() as cur:  # type: ignore[union-attr]
            await cur.execute("""
                SELECT id, proyecto, subproyecto, metadata, created_at, updated_at
                FROM proyectos
                ORDER BY id
            """)
            proyectos = await cur.fetchall()

        print(f"Found {len(proyectos)} proyectos in source")

        for proyecto in proyectos:
            proyecto_id = proyecto["id"]

            if proyecto_id in existing_ids:
                print(f"  Skipping proyecto {proyecto_id} (already exists)")
                self.stats["proyectos_skipped"] += 1
                continue

            nombre = proyecto["proyecto"] or f"Proyecto {proyecto_id}"
            ubicacion = proyecto["subproyecto"] if proyecto.get("subproyecto") else None

            if DRY_RUN:
                print(f"  [DRY RUN] Would import proyecto {proyecto_id}: {nombre}")
                self.stats["proyectos_imported"] += 1
                continue

            # Insert into target (without empresa/ingeniero)
            async with self.target_conn.cursor() as cur:  # type: ignore[union-attr]
                await cur.execute(
                    """
                    INSERT INTO projects (id, nombre, ubicacion, fecha, estado, created_at, updated_at)
                    VALUES (%s, %s, %s, NOW()::date, 'activo', %s, %s)
                    ON CONFLICT (id) DO NOTHING
                """,
                    (
                        proyecto_id,
                        nombre,
                        ubicacion,
                        proyecto["created_at"],
                        proyecto["updated_at"],
                    ),
                )

            await self.target_conn.commit()  # type: ignore[union-attr]
            print(f"  Imported proyecto {proyecto_id}: {nombre}")
            self.stats["proyectos_imported"] += 1

        print()

    async def print_summary(self) -> None:
        """Print import summary."""
        print("=== Import Summary ===")
        print(f"Empresas imported: {self.stats['empresas_imported']}")
        print(f"Empresas skipped: {self.stats['empresas_skipped']}")
        print(f"Ingenieros imported: {self.stats['ingenieros_imported']}")
        print(f"Ingenieros skipped: {self.stats['ingenieros_skipped']}")
        print(f"Proyectos imported: {self.stats['proyectos_imported']}")
        print(f"Proyectos skipped: {self.stats['proyectos_skipped']}")
        print()

        total_imported = (
            self.stats["proyectos_imported"]
            + self.stats["empresas_imported"]
            + self.stats["ingenieros_imported"]
        )

        if DRY_RUN:
            print(f"[DRY RUN] Would import {total_imported} records")
        else:
            print(f"Successfully imported {total_imported} records")


async def main() -> int:
    """Main entry point."""
    print("orgmcalc Data Import Tool")
    print("Importing from orgmbt to orgmcalc")
    print("=" * 50)
    print()

    if DRY_RUN:
        print("*** DRY RUN MODE - No changes will be made ***")
        print()

    print(f"Source: orgmbt")
    print(f"Target: orgmcalc (from DATABASE_URL env var)")
    print()

    importer = Importer()

    try:
        await importer.connect()
        # Import in order: empresas first (referenced by ingenieros and proyectos), then ingenieros, then proyectos
        await importer.import_empresas()
        await importer.import_ingenieros()
        await importer.import_proyectos()
        await importer.print_summary()
        return 0
    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        return 1
    finally:
        await importer.close()


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
