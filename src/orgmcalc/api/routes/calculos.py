"""Calculos API routes - Spanish naming for compatibility.

Updated model: Each calculation has exactly ONE empresa and ONE ingeniero directly assigned.
The old association endpoints are deprecated and will be removed in future versions.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Response

from orgmcalc.api.dependencies import AuthRequiredDep
from orgmcalc.schemas.calculos import (
    CalculoCreate,
    CalculoListItem,
    CalculoResponse,
    CalculoUpdate,
)
from orgmcalc.services.calculos import CalculosService
from orgmcalc.services.projects import ProjectsService

router = APIRouter(tags=["calculos"])


# --- Calculo CRUD ---


@router.get("/proyectos/{project_id}/calculos", response_model=list[CalculoListItem])
async def listar_calculos_proyecto(
    project_id: str,
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(100, ge=1, le=500, description="Limit for pagination (max 500)"),
) -> list[CalculoListItem]:
    """Listar cálculos de un proyecto con info de empresa e ingeniero.

    Cada cálculo muestra la empresa asignada y el ingeniero responsable.
    """
    if not await ProjectsService.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"Proyecto {project_id} no encontrado")
    calculos = await CalculosService.list_calculos(project_id, offset, limit)
    return [CalculoListItem(**c) for c in calculos]


@router.get("/proyectos/{project_id}/calculos/{calculo_id}", response_model=CalculoResponse)
async def obtener_calculo_proyecto(project_id: str, calculo_id: str) -> CalculoResponse:
    """Obtener cálculo de un proyecto con detalles de empresa e ingeniero."""
    if not await ProjectsService.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"Proyecto {project_id} no encontrado")
    calculo = await CalculosService.get_calculo(calculo_id)
    if not calculo or calculo.get("project_id") != project_id:
        raise HTTPException(status_code=404, detail=f"Calculo {calculo_id} no encontrado")

    # Build response with nested empresa and ingeniero objects
    from orgmcalc.db.connection import get_sync_connection

    conn = get_sync_connection()
    try:
        with conn.cursor() as cur:
            # Get empresa details
            empresa_id = calculo.get("empresa_id")
            empresa = None
            if empresa_id:
                cur.execute("SELECT id, nombre FROM empresas WHERE id = %s", (empresa_id,))
                row = cur.fetchone()
                if row:
                    empresa = {"id": row[0], "nombre": row[1]}

            # Get ingeniero details
            ingeniero_id = calculo.get("ingeniero_id")
            ingeniero = None
            if ingeniero_id:
                cur.execute(
                    "SELECT id, nombre, profesion FROM ingenieros WHERE id = %s", (ingeniero_id,)
                )
                row = cur.fetchone()
                if row:
                    ingeniero = {"id": row[0], "nombre": row[1], "profesion": row[2]}

            # Build full response
            response_data = {
                **calculo,
                "empresa": empresa or {"id": "", "nombre": "Sin asignar"},
                "ingeniero": ingeniero or {"id": "", "nombre": "Sin asignar", "profesion": None},
            }
            return CalculoResponse(**response_data)
    finally:
        conn.close()


@router.post("/proyectos/{project_id}/calculos", status_code=201, response_model=CalculoResponse)
async def crear_calculo_proyecto(
    project_id: str,
    req: CalculoCreate,
    user: AuthRequiredDep,
) -> CalculoResponse:
    """Crear cálculo en un proyecto con empresa e ingeniero asignados.

    - El ingeniero debe existir y estar autorizado a trabajar para la empresa seleccionada
    - Algunos ingenieros trabajan para todas las empresas (id_empresas vacío)
    - Otros solo trabajan para empresas específicas (lista en id_empresas)
    """
    if not await ProjectsService.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"Proyecto {project_id} no encontrado")

    data = req.model_dump()
    data["project_id"] = project_id

    calculo = await CalculosService.create_calculo(data)

    # Return full response with empresa and ingeniero info
    return await obtener_calculo_proyecto(project_id, calculo["id"])


@router.patch("/proyectos/{project_id}/calculos/{calculo_id}", response_model=CalculoResponse)
async def actualizar_calculo_proyecto(
    project_id: str,
    calculo_id: str,
    req: CalculoUpdate,
    user: AuthRequiredDep,
) -> CalculoResponse:
    """Actualizar cálculo de un proyecto.

    Puede actualizar campos básicos o reasignar empresa/ingeniero.
    La validación de permisos del ingeniero se aplica automáticamente.
    """
    if not await ProjectsService.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"Proyecto {project_id} no encontrado")
    calculo = await CalculosService.get_calculo(calculo_id)
    if not calculo or calculo.get("project_id") != project_id:
        raise HTTPException(status_code=404, detail=f"Calculo {calculo_id} no encontrado")

    data = {k: v for k, v in req.model_dump().items() if v is not None}
    if not data:
        raise HTTPException(status_code=400, detail="Nada que actualizar")

    await CalculosService.update_calculo(calculo_id, data)

    return await obtener_calculo_proyecto(project_id, calculo_id)


@router.delete("/proyectos/{project_id}/calculos/{calculo_id}", status_code=204)
async def eliminar_calculo_proyecto(
    project_id: str,
    calculo_id: str,
    user: AuthRequiredDep,
) -> Response:
    """Eliminar cálculo de un proyecto. Requiere autenticación."""
    if not await ProjectsService.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"Proyecto {project_id} no encontrado")
    calculo = await CalculosService.get_calculo(calculo_id)
    if not calculo or calculo.get("project_id") != project_id:
        raise HTTPException(status_code=404, detail=f"Calculo {calculo_id} no encontrado")
    await CalculosService.delete_calculo(calculo_id)
    return Response(status_code=204)


# --- DEPRECATED: Association endpoints ---
# These endpoints are no longer needed as each calculation has empresa_id and ingeniero_id directly.
# They are kept for backward compatibility but return empty lists or error messages.


@router.get(
    "/proyectos/{project_id}/calculos/{calculo_id}/empresas",
    summary="DEPRECATED: Use empresa field in calculo response",
    description="Este endpoint está obsoleto. La empresa está disponible directamente en el cálculo.",
)
async def listar_empresas_calculo_deprecated(project_id: str, calculo_id: str) -> None:
    """DEPRECATED: Empresas are now directly assigned to calculo via empresa_id."""
    raise HTTPException(
        status_code=410,
        detail="Este endpoint está obsoleto. La empresa está disponible directamente en el objeto cálculo (campo empresa).",
    )


@router.get(
    "/proyectos/{project_id}/calculos/{calculo_id}/ingenieros",
    summary="DEPRECATED: Use ingeniero field in calculo response",
    description="Este endpoint está obsoleto. El ingeniero está disponible directamente en el cálculo.",
)
async def listar_ingenieros_calculo_deprecated(project_id: str, calculo_id: str) -> None:
    """DEPRECATED: Ingenieros are now directly assigned to calculo via ingeniero_id."""
    raise HTTPException(
        status_code=410,
        detail="Este endpoint está obsoleto. El ingeniero está disponible directamente en el objeto cálculo (campo ingeniero).",
    )
