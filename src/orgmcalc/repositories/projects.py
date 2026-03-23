"""Projects repository - CRUD operations."""

from __future__ import annotations

from typing import Any

from orgmcalc.db.connection import get_async_connection


class ProjectsRepository:
    """Repository for projects table operations."""

    @staticmethod
    async def list_all(offset: int = 0, limit: int = 100) -> list[dict[str, Any]]:
        """List all projects with pagination."""
        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT id, nombre, ubicacion, fecha, estado,
                           created_at::text, updated_at::text
                    FROM projects
                    ORDER BY created_at DESC
                    OFFSET %s LIMIT %s
                    """,
                    (offset, limit),
                )
                rows = await cur.fetchall()
                cols = [desc[0] for desc in cur.description]
                return [dict(zip(cols, row)) for row in rows]

    @staticmethod
    async def count_all() -> int:
        """Count total projects."""
        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT COUNT(*) FROM projects")
                result = await cur.fetchone()
                return result[0] if result else 0

    @staticmethod
    async def get_by_id(project_id: str) -> dict[str, Any] | None:
        """Get project by ID."""
        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT id, nombre, ubicacion, fecha, estado,
                           created_at::text, updated_at::text
                    FROM projects WHERE id = %s
                    """,
                    (project_id,),
                )
                row = await cur.fetchone()
                if not row:
                    return None
                cols = [desc[0] for desc in cur.description]
                return dict(zip(cols, row))

    @staticmethod
    async def create(data: dict[str, Any]) -> dict[str, Any]:
        """Create a new project."""
        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO projects (nombre, ubicacion, fecha, estado)
                    VALUES (%(nombre)s, %(ubicacion)s, %(fecha)s, %(estado)s)
                    RETURNING id, nombre, ubicacion, fecha, estado,
                              created_at::text, updated_at::text
                    """,
                    data,
                )
                row = await cur.fetchone()
                cols = [desc[0] for desc in cur.description]
                return dict(zip(cols, row))

    @staticmethod
    async def update(project_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        """Update project fields."""
        fields = []
        params = {"id": project_id}
        for key, value in data.items():
            if value is not None:
                fields.append(f"{key} = %({key})s")
                params[key] = value
        if not fields:
            return await ProjectsRepository.get_by_id(project_id)

        params["updated_at"] = "now()"
        fields.append("updated_at = now()")

        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    f"""
                    UPDATE projects
                    SET {", ".join(fields)}
                    WHERE id = %(id)s
                    RETURNING id, nombre, ubicacion, fecha, estado,
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
    async def delete(project_id: str) -> bool:
        """Delete project by ID. Returns True if deleted."""
        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "DELETE FROM projects WHERE id = %s RETURNING id",
                    (project_id,),
                )
                result = await cur.fetchone()
                return result is not None

    @staticmethod
    async def exists(project_id: str) -> bool:
        """Check if project exists."""
        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT 1 FROM projects WHERE id = %s",
                    (project_id,),
                )
                return await cur.fetchone() is not None
