"""Clientes API routes - Spanish naming for compatibility."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Response

from orgmcalc.api.dependencies import AuthRequiredDep
from orgmcalc.schemas.clientes import ClienteCreate, ClienteResponse, ClienteUpdate
from orgmcalc.services.clientes import ClientesService

router = APIRouter(prefix="/clientes", tags=["clientes"])


@router.get("", response_model=list[ClienteResponse])
async def listar_clientes(
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(100, ge=1, le=500, description="Limit for pagination (max 500)"),
) -> list[ClienteResponse]:
    """Listar todos los clientes."""
    clientes = await ClientesService.list_clientes(offset, limit)
    return [ClienteResponse(**c) for c in clientes]


@router.get("/{cliente_id}", response_model=ClienteResponse)
async def obtener_cliente(cliente_id: str) -> ClienteResponse:
    """Obtener cliente por ID."""
    cliente = await ClientesService.get_cliente(cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail=f"Cliente {cliente_id} no encontrado")
    return ClienteResponse(**cliente)


@router.post("", status_code=201, response_model=ClienteResponse)
async def crear_cliente(
    req: ClienteCreate,
    _claims: AuthRequiredDep,
) -> ClienteResponse:
    """Crear nuevo cliente. Requiere autenticación."""
    data = req.model_dump()
    try:
        cliente = await ClientesService.create_cliente(data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ClienteResponse(**cliente)


@router.patch("/{cliente_id}", response_model=ClienteResponse)
async def actualizar_cliente(
    cliente_id: str,
    req: ClienteUpdate,
    _claims: AuthRequiredDep,
) -> ClienteResponse:
    """Actualizar cliente existente. Requiere autenticación."""
    data = {k: v for k, v in req.model_dump().items() if v is not None}
    if not data:
        raise HTTPException(status_code=400, detail="Nada que actualizar")
    try:
        cliente = await ClientesService.update_cliente(cliente_id, data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not cliente:
        raise HTTPException(status_code=404, detail=f"Cliente {cliente_id} no encontrado")
    return ClienteResponse(**cliente)


@router.delete("/{cliente_id}", status_code=204)
async def eliminar_cliente(
    cliente_id: str,
    _claims: AuthRequiredDep,
) -> Response:
    """Eliminar cliente. Requiere autenticación."""
    if not await ClientesService.cliente_exists(cliente_id):
        raise HTTPException(status_code=404, detail=f"Cliente {cliente_id} no encontrado")
    await ClientesService.delete_cliente(cliente_id)
    return Response(status_code=204)
