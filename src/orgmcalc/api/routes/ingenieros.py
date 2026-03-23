"""Ingenieros API routes - Spanish naming for compatibility."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Response

from orgmcalc.api.dependencies import AuthRequiredDep
from orgmcalc.schemas.ingenieros import (
    IngenieroCreate,
    IngenieroListItem,
    IngenieroResponse,
    IngenieroUpdate,
)
from orgmcalc.services.ingenieros import IngenierosService

router = APIRouter(prefix="/ingenieros", tags=["ingenieros"])


@router.get("", response_model=list[IngenieroListItem])
async def listar_ingenieros(
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(100, ge=1, le=500, description="Limit for pagination (max 500)"),
    empresa_id: int | None = Query(None, description="Filtrar por empresa"),
) -> list[IngenieroListItem]:
    """Listar ingenieros, opcionalmente filtrados por empresa."""
    ingenieros = await IngenierosService.list_ingenieros(offset, limit, empresa_id)
    return [IngenieroListItem(**i) for i in ingenieros]


@router.get("/{ingeniero_id}", response_model=IngenieroResponse)
async def obtener_ingeniero(ingeniero_id: int) -> IngenieroResponse:
    """Obtener ingeniero por ID."""
    ingeniero = await IngenierosService.get_ingeniero(ingeniero_id)
    if not ingeniero:
        raise HTTPException(status_code=404, detail=f"Ingeniero {ingeniero_id} no encontrado")
    return IngenieroResponse(**ingeniero)


@router.post("", status_code=201, response_model=IngenieroResponse)
async def crear_ingeniero(
    req: IngenieroCreate,
    user: AuthRequiredDep,
) -> IngenieroResponse:
    """Crear nuevo ingeniero. Requiere autenticación."""
    data = req.model_dump()
    ingeniero = await IngenierosService.create_ingeniero(data)
    return IngenieroResponse(**ingeniero)


@router.patch("/{ingeniero_id}", response_model=IngenieroResponse)
async def actualizar_ingeniero(
    ingeniero_id: int,
    req: IngenieroUpdate,
    user: AuthRequiredDep,
) -> IngenieroResponse:
    """Actualizar ingeniero existente. Requiere autenticación."""
    data = {k: v for k, v in req.model_dump().items() if v is not None}
    if not data:
        raise HTTPException(status_code=400, detail="Nada que actualizar")
    ingeniero = await IngenierosService.update_ingeniero(ingeniero_id, data)
    if not ingeniero:
        raise HTTPException(status_code=404, detail=f"Ingeniero {ingeniero_id} no encontrado")
    return IngenieroResponse(**ingeniero)


@router.delete("/{ingeniero_id}", status_code=204)
async def eliminar_ingeniero(
    ingeniero_id: int,
    user: AuthRequiredDep,
) -> Response:
    """Eliminar ingeniero. Requiere autenticación."""
    if not await IngenierosService.ingeniero_exists(ingeniero_id):
        raise HTTPException(status_code=404, detail=f"Ingeniero {ingeniero_id} no encontrado")
    await IngenierosService.delete_ingeniero(ingeniero_id)
    return Response(status_code=204)
