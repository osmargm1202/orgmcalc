"""Ingenieros repository - CRUD operations."""

from __future__ import annotations

from typing import Any

from orgmcalc.db.connection import get_async_connection


class IngenierosRepository:
    """Repository for ingenieros table operations."""

    @staticmethod
    async def list_all(
        offset: int = 0, limit: int = 100, empresa_id: int | None = None
    ) -> list[dict[str, Any]]:
        """List all engineers, optionally filtered by empresa."""
        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                if empresa_id:
                    # Join with calculo_ingenieros -> calculos -> projects to filter
                    await cur.execute(
                        """
                        SELECT DISTINCT i.id, i.nombre, i.email, i.telefono, i.profesion,
                               i.created_at::text, i.updated_at::text
                        FROM ingenieros i
                        LEFT JOIN calculo_ingenieros ci ON i.id = ci.ingeniero_id
                        LEFT JOIN calculos c ON ci.calculo_id = c.id
                        LEFT JOIN projects p ON c.project_id = p.id
                        WHERE p.id IS NULL OR p.id = %s
                        ORDER BY i.nombre
                        OFFSET %s LIMIT %s
                        """,
                        (empresa_id, offset, limit),
                    )
                else:
                    await cur.execute(
                        """
                        SELECT id, nombre, email, telefono, profesion,
                               created_at::text, updated_at::text
                        FROM ingenieros
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
        """Count total engineers."""
        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT COUNT(*) FROM ingenieros")
                result = await cur.fetchone()
                return result[0] if result else 0

    @staticmethod
    async def get_by_id(ingeniero_id: int) -> dict[str, Any] | None:
        """Get engineer by ID."""
        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT id, nombre, email, telefono, profesion,
                           created_at::text, updated_at::text
                    FROM ingenieros WHERE id = %s
                    """,
                    (ingeniero_id,),
                )
                row = await cur.fetchone()
                if not row:
                    return None
                cols = [desc[0] for desc in cur.description]
                return dict(zip(cols, row))

    @staticmethod
    async def create(data: dict[str, Any]) -> dict[str, Any]:
        """Create a new engineer."""
        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO ingenieros (nombre, email, telefono, profesion)
                    VALUES (%(nombre)s, %(email)s, %(telefono)s, %(profesion)s)
                    RETURNING id, nombre, email, telefono, profesion,
                              created_at::text, updated_at::text
                    """,
                    data,
                )
                row = await cur.fetchone()
                cols = [desc[0] for desc in cur.description]
                return dict(zip(cols, row))

    @staticmethod
    async def update(ingeniero_id: int, data: dict[str, Any]) -> dict[str, Any] | None:
        """Update engineer fields."""
        fields = []
        params = {"id": ingeniero_id}
        for key, value in data.items():
            if value is not None:
                fields.append(f"{key} = %({key})s")
                params[key] = value
        if not fields:
            return await IngenierosRepository.get_by_id(ingeniero_id)

        fields.append("updated_at = now()")

        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    f"""
                    UPDATE ingenieros
                    SET {", ".join(fields)}
                    WHERE id = %(id)s
                    RETURNING id, nombre, email, telefono, profesion,
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
    async def delete(ingeniero_id: int) -> bool:
        """Delete engineer by ID. Returns True if deleted."""
        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "DELETE FROM ingenieros WHERE id = %s RETURNING id",
                    (ingeniero_id,),
                )
                result = await cur.fetchone()
                return result is not None

    @staticmethod
    async def exists(ingeniero_id: int) -> bool:
        """Check if engineer exists."""
        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT 1 FROM ingenieros WHERE id = %s",
                    (ingeniero_id,),
                )
                return await cur.fetchone() is not None
