"""Calculo-Empresa association repository."""

from __future__ import annotations

from typing import Any

from orgmcalc.db.connection import get_async_connection


class CalculoEmpresasRepository:
    """Repository for calculo_empresas association operations."""

    @staticmethod
    async def list_by_calculo(calculo_id: int) -> list[dict[str, Any]]:
        """List company links for a calculation."""
        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT ce.id, ce.calculo_id, ce.empresa_id, e.nombre as empresa_nombre,
                           ce.rol, ce.orden, ce.created_at::text
                    FROM calculo_empresas ce
                    JOIN empresas e ON ce.empresa_id = e.id
                    WHERE ce.calculo_id = %s
                    ORDER BY ce.orden, e.nombre
                    """,
                    (calculo_id,),
                )
                rows = await cur.fetchall()
                cols = [desc[0] for desc in cur.description]
                return [dict(zip(cols, row)) for row in rows]

    @staticmethod
    async def get_by_id(link_id: int) -> dict[str, Any] | None:
        """Get link by ID."""
        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT ce.id, ce.calculo_id, ce.empresa_id, e.nombre as empresa_nombre,
                           ce.rol, ce.orden, ce.created_at::text
                    FROM calculo_empresas ce
                    JOIN empresas e ON ce.empresa_id = e.id
                    WHERE ce.id = %s
                    """,
                    (link_id,),
                )
                row = await cur.fetchone()
                if not row:
                    return None
                cols = [desc[0] for desc in cur.description]
                return dict(zip(cols, row))

    @staticmethod
    async def create(
        calculo_id: int, empresa_id: int, rol: str | None, orden: int
    ) -> dict[str, Any]:
        """Link a company to a calculation."""
        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO calculo_empresas (calculo_id, empresa_id, rol, orden)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (calculo_id, empresa_id, rol) DO UPDATE SET
                        orden = EXCLUDED.orden,
                        updated_at = now()
                    RETURNING id, calculo_id, empresa_id, rol, orden, created_at::text
                    """,
                    (calculo_id, empresa_id, rol, orden),
                )
                row = await cur.fetchone()
                cols = [desc[0] for desc in cur.description]
                result = dict(zip(cols, row))
                # Get empresa_nombre
                await cur.execute(
                    "SELECT nombre FROM empresas WHERE id = %s",
                    (result["empresa_id"],),
                )
                empresa_row = await cur.fetchone()
                if empresa_row:
                    result["empresa_nombre"] = empresa_row[0]
                return result

    @staticmethod
    async def update(link_id: int, rol: str | None, orden: int | None) -> dict[str, Any] | None:
        """Update link fields."""
        fields = []
        params: dict[str, Any] = {"id": link_id}
        if rol is not None:
            fields.append("rol = %(rol)s")
            params["rol"] = rol
        if orden is not None:
            fields.append("orden = %(orden)s")
            params["orden"] = orden
        if not fields:
            return await CalculoEmpresasRepository.get_by_id(link_id)

        fields.append("updated_at = now()")

        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    f"""
                    UPDATE calculo_empresas
                    SET {", ".join(fields)}
                    WHERE id = %(id)s
                    RETURNING id, calculo_id, empresa_id, rol, orden, created_at::text
                    """,
                    params,
                )
                row = await cur.fetchone()
                if not row:
                    return None
                cols = [desc[0] for desc in cur.description]
                result = dict(zip(cols, row))
                # Get empresa_nombre
                await cur.execute(
                    "SELECT nombre FROM empresas WHERE id = %s",
                    (result["empresa_id"],),
                )
                empresa_row = await cur.fetchone()
                if empresa_row:
                    result["empresa_nombre"] = empresa_row[0]
                return result

    @staticmethod
    async def delete(link_id: int) -> bool:
        """Delete link by ID. Returns True if deleted."""
        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "DELETE FROM calculo_empresas WHERE id = %s RETURNING id",
                    (link_id,),
                )
                result = await cur.fetchone()
                return result is not None

    @staticmethod
    async def exists(link_id: int) -> bool:
        """Check if link exists."""
        async with get_async_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT 1 FROM calculo_empresas WHERE id = %s",
                    (link_id,),
                )
                return await cur.fetchone() is not None
