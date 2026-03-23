"""Router for tipo_calculos endpoints.

Provides read-only access to predefined calculation types.
These are seeded in migrations and cannot be created/modified via API.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from orgmcalc.db.connection import get_sync_connection
from orgmcalc.schemas.calculos import TipoCalculoResponse

router = APIRouter(prefix="/tipo-calculos", tags=["Tipo de Cálculos"])


def _get_db_connection():
    """Get database connection."""
    conn = get_sync_connection()
    try:
        yield conn
    finally:
        conn.close()


@router.get(
    "",
    response_model=list[TipoCalculoResponse],
    summary="Listar tipos de cálculos predefinidos",
    description="""
    Obtiene la lista de tipos de cálculos predefinidos disponibles.
    
    Estos tipos son fijos y se definen en la base de datos:
    - BT: Cálculo de Baja Tensión
    - SPT: Sistema de Puesta a Tierra
    - AC: Capacidad de Aire Acondicionado
    - ILUM: Cálculo de Iluminación
    - CARGAS: Cálculo de Cargas Eléctricas
    - Y más...
    
    Los cálculos deben ser creados usando uno de estos tipos.
    """,
    responses={
        200: {
            "description": "Lista de tipos de cálculos",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "uuid",
                            "codigo": "BT",
                            "nombre": "Cálculo de Baja Tensión",
                            "descripcion": "Cálculo de instalaciones eléctricas...",
                            "categoria": "electricidad",
                            "icono": "⚡",
                            "color": "#FFD700",
                            "orden": 1,
                            "activo": True,
                        }
                    ]
                }
            },
        }
    },
)
async def list_tipo_calculos(
    categoria: Annotated[
        str | None,
        Query(description="Filtrar por categoría (electricidad, mecanica, climatizacion)"),
    ] = None,
    solo_activos: Annotated[bool, Query(description="Solo mostrar tipos activos")] = True,
) -> list[TipoCalculoResponse]:
    """List all predefined calculation types."""
    conn = get_sync_connection()
    try:
        with conn.cursor() as cur:
            query = """
                SELECT id, codigo, nombre, descripcion, categoria, 
                       icono, color, orden, activo, created_at, updated_at
                FROM tipo_calculos
                WHERE 1=1
            """
            params = []

            if solo_activos:
                query += " AND activo = TRUE"

            if categoria:
                query += " AND categoria = %s"
                params.append(categoria)

            query += " ORDER BY orden, nombre"

            cur.execute(query, params)
            rows = cur.fetchall()

            # Convert to dict format
            columns = [desc[0] for desc in cur.description]
            result = [dict(zip(columns, row)) for row in rows]

            return [TipoCalculoResponse(**row) for row in result]
    finally:
        conn.close()


@router.get(
    "/{tipo_id}",
    response_model=TipoCalculoResponse,
    summary="Obtener tipo de cálculo por ID",
    description="Obtiene los detalles de un tipo de cálculo específico.",
    responses={
        200: {"description": "Tipo de cálculo encontrado"},
        404: {"description": "Tipo de cálculo no encontrado"},
    },
)
async def get_tipo_calculo(
    tipo_id: str,
) -> TipoCalculoResponse:
    """Get a specific calculation type by ID."""
    conn = get_sync_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, codigo, nombre, descripcion, categoria,
                       icono, color, orden, activo, created_at, updated_at
                FROM tipo_calculos
                WHERE id = %s
                """,
                (tipo_id,),
            )
            row = cur.fetchone()

            if not row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Tipo de cálculo con ID {tipo_id} no encontrado",
                )

            columns = [desc[0] for desc in cur.description]
            result = dict(zip(columns, row))

            return TipoCalculoResponse(**result)
    finally:
        conn.close()


@router.get(
    "/by-codigo/{codigo}",
    response_model=TipoCalculoResponse,
    summary="Obtener tipo de cálculo por código",
    description="Obtiene un tipo de cálculo usando su código corto (ej: BT, SPT, AC).",
    responses={
        200: {"description": "Tipo de cálculo encontrado"},
        404: {"description": "Tipo de cálculo no encontrado"},
    },
)
async def get_tipo_calculo_by_codigo(
    codigo: str,
) -> TipoCalculoResponse:
    """Get a calculation type by its short code."""
    conn = get_sync_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, codigo, nombre, descripcion, categoria,
                       icono, color, orden, activo, created_at, updated_at
                FROM tipo_calculos
                WHERE codigo = %s
                """,
                (codigo.upper(),),
            )
            row = cur.fetchone()

            if not row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Tipo de cálculo con código '{codigo}' no encontrado",
                )

            columns = [desc[0] for desc in cur.description]
            result = dict(zip(columns, row))

            return TipoCalculoResponse(**result)
    finally:
        conn.close()
