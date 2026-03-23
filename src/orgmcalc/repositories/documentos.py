"""Documentos repository - CRUD for project documents."""
from __future__ import annotations

from typing import Any

from orgmcalc.db.connection import get_async_connection


class DocumentosRepository:
    """Repository for project documents."""

    @staticmethod
    async def list_by_project(
        project_id: int, offset: int = 0, limit: int = 100
    ) -> list[dict[str, Any]]:
        """List documents for a project."""
        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT id, project_id, nombre_documento, descripcion,
                           created_at::text, updated_at::text
                    FROM documentos
                    WHERE project_id = %s
                    ORDER BY created_at DESC
                    OFFSET %s LIMIT %s
                    """,
                    (project_id, offset, limit),
                )
                rows = await cur.fetchall()
                cols = [desc[0] for desc in cur.description]
                return [dict(zip(cols, row)) for row in rows]

    @staticmethod
    async def count_by_project(project_id: int) -> int:
        """Count documents for a project."""
        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT COUNT(*) FROM documentos WHERE project_id = %s",
                    (project_id,),
                )
                result = await cur.fetchone()
                return result[0] if result else 0

    @staticmethod
    async def get_by_id(document_id: int) -> dict[str, Any] | None:
        """Get document by ID."""
        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT id, project_id, nombre_documento, descripcion,
                           created_at::text, updated_at::text
                    FROM documentos WHERE id = %s
                    """,
                    (document_id,),
                )
                row = await cur.fetchone()
                if not row:
                    return None
                cols = [desc[0] for desc in cur.description]
                return dict(zip(cols, row))

    @staticmethod
    async def create(data: dict[str, Any]) -> dict[str, Any]:
        """Create a new document."""
        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO documentos (project_id, nombre_documento, descripcion)
                    VALUES (%(project_id)s, %(nombre_documento)s, %(descripcion)s)
                    RETURNING id, project_id, nombre_documento, descripcion,
                              created_at::text, updated_at::text
                    """,
                    data,
                )
                row = await cur.fetchone()
                cols = [desc[0] for desc in cur.description]
                return dict(zip(cols, row))

    @staticmethod
    async def update(document_id: int, data: dict[str, Any]) -> dict[str, Any] | None:
        """Update document fields."""
        fields = []
        params: dict[str, Any] = {"id": document_id}
        for key in ["nombre_documento", "descripcion"]:
            if key in data and data[key] is not None:
                fields.append(f"{key} = %({key})s")
                params[key] = data[key]
        if not fields:
            return await DocumentosRepository.get_by_id(document_id)
        fields.append("updated_at = now()")
        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    f"""
                    UPDATE documentos
                    SET {', '.join(fields)}
                    WHERE id = %(id)s
                    RETURNING id, project_id, nombre_documento, descripcion,
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
    async def delete(document_id: int) -> bool:
        """Delete document by ID. Returns True if deleted."""
        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "DELETE FROM documentos WHERE id = %s RETURNING id",
                    (document_id,),
                )
                result = await cur.fetchone()
                return result is not None

    @staticmethod
    async def exists(document_id: int) -> bool:
        """Check if document exists."""
        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT 1 FROM documentos WHERE id = %s",
                    (document_id,),
                )
                return await cur.fetchone() is not None
