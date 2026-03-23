"""Empresas repository - CRUD operations."""

from __future__ import annotations

from typing import Any

from orgmcalc.db.connection import get_async_connection


class EmpresasRepository:
    """Repository for empresas table operations."""

    @staticmethod
    async def list_all(offset: int = 0, limit: int = 100) -> list[dict[str, Any]]:
        """List all companies."""
        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT id, nombre, contacto, telefono, correo, direccion, ciudad,
                           created_at::text, updated_at::text
                    FROM empresas
                    ORDER BY nombre
                    OFFSET %s LIMIT %s
                    """,
                    (offset, limit),
                )
                rows = await cur.fetchall()
                cols = [desc[0] for desc in cur.description]
                return [dict(zip(cols, row)) for row in rows]

    @staticmethod
    async def count_all() -> int:
        """Count total companies."""
        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT COUNT(*) FROM empresas")
                result = await cur.fetchone()
                return result[0] if result else 0

    @staticmethod
    async def get_by_id(empresa_id: int) -> dict[str, Any] | None:
        """Get company by ID."""
        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT id, nombre, contacto, telefono, correo, direccion, ciudad,
                           created_at::text, updated_at::text
                    FROM empresas WHERE id = %s
                    """,
                    (empresa_id,),
                )
                row = await cur.fetchone()
                if not row:
                    return None
                cols = [desc[0] for desc in cur.description]
                return dict(zip(cols, row))

    @staticmethod
    async def create(data: dict[str, Any]) -> dict[str, Any]:
        """Create a new company."""
        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO empresas (nombre, contacto, telefono, correo, direccion, ciudad)
                    VALUES (%(nombre)s, %(contacto)s, %(telefono)s,
                            %(correo)s, %(direccion)s, %(ciudad)s)
                    RETURNING id, nombre, contacto, telefono, correo, direccion, ciudad,
                              created_at::text, updated_at::text
                    """,
                    data,
                )
                row = await cur.fetchone()
                cols = [desc[0] for desc in cur.description]
                return dict(zip(cols, row))

    @staticmethod
    async def update(empresa_id: int, data: dict[str, Any]) -> dict[str, Any] | None:
        """Update company fields."""
        fields = []
        params = {"id": empresa_id}
        for key, value in data.items():
            if value is not None:
                fields.append(f"{key} = %({key})s")
                params[key] = value
        if not fields:
            return await EmpresasRepository.get_by_id(empresa_id)

        fields.append("updated_at = now()")

        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    f"""
                    UPDATE empresas
                    SET {", ".join(fields)}
                    WHERE id = %(id)s
                    RETURNING id, nombre, contacto, telefono, correo, direccion, ciudad,
                              created_at::text, updated_at::text
                    """,
                    params,
                )
                row = await cur.fetchone()
                if not row:
                    return None
                cols = [desc[0] for desc in cur.description]
                return dict(zip(cols, row))

    @staticmethod
    async def delete(empresa_id: int) -> bool:
        """Delete company by ID. Returns True if deleted."""
        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "DELETE FROM empresas WHERE id = %s RETURNING id",
                    (empresa_id,),
                )
                result = await cur.fetchone()
                return result is not None

    @staticmethod
    async def exists(empresa_id: int) -> bool:
        """Check if company exists."""
        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT 1 FROM empresas WHERE id = %s",
                    (empresa_id,),
                )
                return await cur.fetchone() is not None
