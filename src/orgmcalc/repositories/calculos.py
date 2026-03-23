"""Calculos repository - CRUD and association operations."""

from __future__ import annotations

from typing import Any

from orgmcalc.db.connection import get_async_connection


class CalculosRepository:
    """Repository for calculos table operations."""

    @staticmethod
    async def list_by_project(
        project_id: int, offset: int = 0, limit: int = 100
    ) -> list[dict[str, Any]]:
        """List calculations for a project."""
        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT id, project_id, codigo, nombre, descripcion, estado,
                           fecha_creacion, created_at::text, updated_at::text
                    FROM calculos
                    WHERE project_id = %s
                    ORDER BY fecha_creacion DESC, id DESC
                    OFFSET %s LIMIT %s
                    """,
                    (project_id, offset, limit),
                )
                rows = await cur.fetchall()
                cols = [desc[0] for desc in cur.description]
                return [dict(zip(cols, row)) for row in rows]

    @staticmethod
    async def count_by_project(project_id: int) -> int:
        """Count calculations for a project."""
        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT COUNT(*) FROM calculos WHERE project_id = %s",
                    (project_id,),
                )
                result = await cur.fetchone()
                return result[0] if result else 0

    @staticmethod
    async def get_by_id(calculo_id: int) -> dict[str, Any] | None:
        """Get calculation by ID."""
        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT id, project_id, codigo, nombre, descripcion, estado,
                           fecha_creacion, created_at::text, updated_at::text
                    FROM calculos WHERE id = %s
                    """,
                    (calculo_id,),
                )
                row = await cur.fetchone()
                if not row:
                    return None
                cols = [desc[0] for desc in cur.description]
                return dict(zip(cols, row))

    @staticmethod
    async def create(data: dict[str, Any]) -> dict[str, Any]:
        """Create a new calculation."""
        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO calculos (project_id, codigo, nombre, descripcion, estado)
                    VALUES (%(project_id)s, %(codigo)s, %(nombre)s, %(descripcion)s, %(estado)s)
                    RETURNING id, project_id, codigo, nombre, descripcion, estado,
                              fecha_creacion, created_at::text, updated_at::text
                    """,
                    data,
                )
                row = await cur.fetchone()
                cols = [desc[0] for desc in cur.description]
                return dict(zip(cols, row))

    @staticmethod
    async def update(calculo_id: int, data: dict[str, Any]) -> dict[str, Any] | None:
        """Update calculation fields."""
        fields = []
        params: dict[str, Any] = {"id": calculo_id}
        for key in ["codigo", "nombre", "descripcion", "estado"]:
            if key in data and data[key] is not None:
                fields.append(f"{key} = %({key})s")
                params[key] = data[key]
        if not fields:
            return await CalculosRepository.get_by_id(calculo_id)

        fields.append("updated_at = now()")

        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    f"""
                    UPDATE calculos
                    SET {", ".join(fields)}
                    WHERE id = %(id)s
                    RETURNING id, project_id, codigo, nombre, descripcion, estado,
                              fecha_creacion, created_at::text, updated_at::text
                    """,
                    params,
                )
                row = await cur.fetchone()
                if not row:
                    return None
                cols = [desc[0] for desc in cur.description]
                return dict(zip(cols, row))

    @staticmethod
    async def delete(calculo_id: int) -> bool:
        """Delete calculation by ID. Returns True if deleted."""
        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "DELETE FROM calculos WHERE id = %s RETURNING id",
                    (calculo_id,),
                )
                result = await cur.fetchone()
                return result is not None

    @staticmethod
    async def exists(calculo_id: int) -> bool:
        """Check if calculation exists."""
        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT 1 FROM calculos WHERE id = %s",
                    (calculo_id,),
                )
                return await cur.fetchone() is not None
