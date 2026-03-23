"""Calculos repository - CRUD operations with empresa and ingeniero assignments."""

from __future__ import annotations

from typing import Any

from orgmcalc.db.connection import get_async_connection


class CalculosRepository:
    """Repository for calculos table operations.

    Each calculation has ONE empresa and ONE ingeniero directly assigned.
    """

    @staticmethod
    async def list_by_project(
        project_id: str, offset: int = 0, limit: int = 100
    ) -> list[dict[str, Any]]:
        """List calculations for a project with empresa and ingeniero info."""
        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT 
                        c.id, c.project_id, c.tipo_calculo_id, c.codigo, c.nombre, 
                        c.descripcion, c.estado, c.fecha_creacion,
                        c.empresa_id, e.nombre as empresa_nombre,
                        c.ingeniero_id, i.nombre as ingeniero_nombre,
                        c.created_at::text, c.updated_at::text
                    FROM calculos c
                    LEFT JOIN empresas e ON c.empresa_id = e.id
                    LEFT JOIN ingenieros i ON c.ingeniero_id = i.id
                    WHERE c.project_id = %s
                    ORDER BY c.fecha_creacion DESC, c.id DESC
                    OFFSET %s LIMIT %s
                    """,
                    (project_id, offset, limit),
                )
                rows = await cur.fetchall()
                cols = [desc[0] for desc in cur.description]
                return [dict(zip(cols, row)) for row in rows]

    @staticmethod
    async def count_by_project(project_id: str) -> int:
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
    async def get_by_id(calculo_id: str) -> dict[str, Any] | None:
        """Get calculation by ID with empresa and ingeniero details."""
        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT 
                        c.id, c.project_id, c.tipo_calculo_id, c.codigo, c.nombre, 
                        c.descripcion, c.estado, c.fecha_creacion,
                        c.empresa_id, e.nombre as empresa_nombre,
                        c.ingeniero_id, i.nombre as ingeniero_nombre, i.profesion as ingeniero_profesion,
                        c.parametros, c.version,
                        c.created_at::text, c.updated_at::text
                    FROM calculos c
                    LEFT JOIN empresas e ON c.empresa_id = e.id
                    LEFT JOIN ingenieros i ON c.ingeniero_id = i.id
                    WHERE c.id = %s
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
        """Create a new calculation with empresa and ingeniero."""
        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO calculos (
                        project_id, tipo_calculo_id, codigo, nombre, descripcion, estado,
                        empresa_id, ingeniero_id
                    )
                    VALUES (
                        %(project_id)s, %(tipo_calculo_id)s, %(codigo)s, %(nombre)s, 
                        %(descripcion)s, %(estado)s, %(empresa_id)s, %(ingeniero_id)s
                    )
                    RETURNING id, project_id, tipo_calculo_id, codigo, nombre, descripcion, estado,
                              empresa_id, ingeniero_id, fecha_creacion, 
                              created_at::text, updated_at::text
                    """,
                    data,
                )
                row = await cur.fetchone()
                cols = [desc[0] for desc in cur.description]
                return dict(zip(cols, row))

    @staticmethod
    async def update(calculo_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        """Update calculation fields including empresa and ingeniero."""
        allowed_fields = [
            "codigo",
            "nombre",
            "descripcion",
            "estado",
            "empresa_id",
            "ingeniero_id",
            "tipo_calculo_id",
        ]

        fields = []
        params: dict[str, Any] = {"id": calculo_id}

        for key in allowed_fields:
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
                    RETURNING id, project_id, tipo_calculo_id, codigo, nombre, descripcion, estado,
                              empresa_id, ingeniero_id, fecha_creacion, 
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
    async def delete(calculo_id: str) -> bool:
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
    async def exists(calculo_id: str) -> bool:
        """Check if calculation exists."""
        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT 1 FROM calculos WHERE id = %s",
                    (calculo_id,),
                )
                return await cur.fetchone() is not None

    @staticmethod
    async def get_by_codigo_and_project(project_id: str, codigo: str) -> dict[str, Any] | None:
        """Get calculation by project ID and codigo (for uniqueness check)."""
        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT id FROM calculos 
                    WHERE project_id = %s AND codigo = %s
                    """,
                    (project_id, codigo),
                )
                row = await cur.fetchone()
                if not row:
                    return None
                return {"id": row[0]}
