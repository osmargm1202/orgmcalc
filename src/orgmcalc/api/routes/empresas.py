"""Empresas API routes - Spanish naming for compatibility."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Response

from orgmcalc.api.dependencies import AuthRequiredDep
from orgmcalc.schemas.empresas import EmpresaCreate, EmpresaResponse, EmpresaUpdate
from orgmcalc.services.empresas import EmpresasService

router = APIRouter(prefix="/empresas", tags=["empresas"])


@router.get("", response_model=list[EmpresaResponse])
async def listar_empresas(
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(100, ge=1, le=500, description="Limit for pagination (max 500)"),
) -> list[EmpresaResponse]:
    """Listar todas las empresas."""
    empresas = await EmpresasService.list_empresas(offset, limit)
    return [EmpresaResponse(**e) for e in empresas]


@router.get("/{empresa_id}", response_model=EmpresaResponse)
async def obtener_empresa(empresa_id: int) -> EmpresaResponse:
    """Obtener empresa por ID."""
    empresa = await EmpresasService.get_empresa(empresa_id)
    if not empresa:
        raise HTTPException(status_code=404, detail=f"Empresa {empresa_id} no encontrada")
    return EmpresaResponse(**empresa)


@router.post("", status_code=201, response_model=EmpresaResponse)
async def crear_empresa(
    req: EmpresaCreate,
    user: AuthRequiredDep,
) -> EmpresaResponse:
    """Crear nueva empresa. Requiere autenticación."""
    data = req.model_dump()
    empresa = await EmpresasService.create_empresa(data)
    return EmpresaResponse(**empresa)


@router.patch("/{empresa_id}", response_model=EmpresaResponse)
async def actualizar_empresa(
    empresa_id: int,
    req: EmpresaUpdate,
    user: AuthRequiredDep,
) -> EmpresaResponse:
    """Actualizar empresa existente. Requiere autenticación."""
    data = {k: v for k, v in req.model_dump().items() if v is not None}
    if not data:
        raise HTTPException(status_code=400, detail="Nada que actualizar")
    empresa = await EmpresasService.update_empresa(empresa_id, data)
    if not empresa:
        raise HTTPException(status_code=404, detail=f"Empresa {empresa_id} no encontrada")
    return EmpresaResponse(**empresa)


@router.delete("/{empresa_id}", status_code=204)
async def eliminar_empresa(
    empresa_id: int,
    user: AuthRequiredDep,
) -> Response:
    """Eliminar empresa. Requiere autenticación."""
    if not await EmpresasService.empresa_exists(empresa_id):
        raise HTTPException(status_code=404, detail=f"Empresa {empresa_id} no encontrada")
    await EmpresasService.delete_empresa(empresa_id)
    return Response(status_code=204)
