"""Calculos API routes - Spanish naming for compatibility."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Response

from orgmcalc.api.dependencies import AuthRequiredDep
from orgmcalc.schemas.calculos import (
    CalculoCreate,
    CalculoEmpresaLink,
    CalculoEmpresaLinkCreate,
    CalculoEmpresaLinkUpdate,
    CalculoIngenieroLink,
    CalculoIngenieroLinkCreate,
    CalculoIngenieroLinkUpdate,
    CalculoListItem,
    CalculoResponse,
    CalculoUpdate,
)
from orgmcalc.services.calculos import (
    CalculoEmpresasService,
    CalculoIngenierosService,
    CalculosService,
)
from orgmcalc.services.empresas import EmpresasService
from orgmcalc.services.ingenieros import IngenierosService
from orgmcalc.services.projects import ProjectsService

router = APIRouter(tags=["calculos"])


# --- Calculo CRUD ---


@router.get("/proyectos/{project_id}/calculos", response_model=list[CalculoListItem])
async def listar_calculos_proyecto(
    project_id: int,
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(100, ge=1, le=500, description="Limit for pagination (max 500)"),
) -> list[CalculoListItem]:
    """Listar calculos de un proyecto."""
    if not await ProjectsService.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"Proyecto {project_id} no encontrado")
    calculos = await CalculosService.list_calculos(project_id, offset, limit)
    return [CalculoListItem(**c) for c in calculos]


@router.get("/proyectos/{project_id}/calculos/{calculo_id}", response_model=CalculoResponse)
async def obtener_calculo_proyecto(project_id: int, calculo_id: int) -> CalculoResponse:
    """Obtener calculo de un proyecto."""
    if not await ProjectsService.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"Proyecto {project_id} no encontrado")
    calculo = await CalculosService.get_calculo(calculo_id)
    if not calculo or calculo.get("project_id") != project_id:
        raise HTTPException(status_code=404, detail=f"Calculo {calculo_id} no encontrado")
    return CalculoResponse(**calculo)


@router.post("/proyectos/{project_id}/calculos", status_code=201, response_model=CalculoResponse)
async def crear_calculo_proyecto(
    project_id: int,
    req: CalculoCreate,
    user: AuthRequiredDep,
) -> CalculoResponse:
    """Crear calculo en un proyecto. Requiere autenticación."""
    if not await ProjectsService.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"Proyecto {project_id} no encontrado")
    data = req.model_dump()
    data["project_id"] = project_id
    calculo = await CalculosService.create_calculo(data)
    return CalculoResponse(**calculo)


@router.patch("/proyectos/{project_id}/calculos/{calculo_id}", response_model=CalculoResponse)
async def actualizar_calculo_proyecto(
    project_id: int,
    calculo_id: int,
    req: CalculoUpdate,
    user: AuthRequiredDep,
) -> CalculoResponse:
    """Actualizar calculo de un proyecto. Requiere autenticación."""
    if not await ProjectsService.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"Proyecto {project_id} no encontrado")
    calculo = await CalculosService.get_calculo(calculo_id)
    if not calculo or calculo.get("project_id") != project_id:
        raise HTTPException(status_code=404, detail=f"Calculo {calculo_id} no encontrado")
    data = {k: v for k, v in req.model_dump().items() if v is not None}
    if not data:
        raise HTTPException(status_code=400, detail="Nada que actualizar")
    updated = await CalculosService.update_calculo(calculo_id, data)
    return CalculoResponse(**updated)


@router.delete("/proyectos/{project_id}/calculos/{calculo_id}", status_code=204)
async def eliminar_calculo_proyecto(
    project_id: int,
    calculo_id: int,
    user: AuthRequiredDep,
) -> Response:
    """Eliminar calculo de un proyecto. Requiere autenticación."""
    if not await ProjectsService.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"Proyecto {project_id} no encontrado")
    calculo = await CalculosService.get_calculo(calculo_id)
    if not calculo or calculo.get("project_id") != project_id:
        raise HTTPException(status_code=404, detail=f"Calculo {calculo_id} no encontrado")
    await CalculosService.delete_calculo(calculo_id)
    return Response(status_code=204)


# --- Calculo-Empresa Associations ---


@router.get(
    "/proyectos/{project_id}/calculos/{calculo_id}/empresas",
    response_model=list[CalculoEmpresaLink],
)
async def listar_empresas_calculo(project_id: int, calculo_id: int) -> list[CalculoEmpresaLink]:
    """Listar empresas vinculadas a un calculo."""
    if not await ProjectsService.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"Proyecto {project_id} no encontrado")
    calculo = await CalculosService.get_calculo(calculo_id)
    if not calculo or calculo.get("project_id") != project_id:
        raise HTTPException(status_code=404, detail=f"Calculo {calculo_id} no encontrado")
    links = await CalculoEmpresasService.list_links(calculo_id)
    return [CalculoEmpresaLink(**link) for link in links]


@router.post(
    "/proyectos/{project_id}/calculos/{calculo_id}/empresas",
    status_code=201,
    response_model=CalculoEmpresaLink,
)
async def vincular_empresa_calculo(
    project_id: int,
    calculo_id: int,
    req: CalculoEmpresaLinkCreate,
    user: AuthRequiredDep,
) -> CalculoEmpresaLink:
    """Vincular empresa a un calculo. Requiere autenticación."""
    if not await ProjectsService.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"Proyecto {project_id} no encontrado")
    calculo = await CalculosService.get_calculo(calculo_id)
    if not calculo or calculo.get("project_id") != project_id:
        raise HTTPException(status_code=404, detail=f"Calculo {calculo_id} no encontrado")
    if not await EmpresasService.empresa_exists(req.empresa_id):
        raise HTTPException(status_code=404, detail=f"Empresa {req.empresa_id} no encontrada")
    link = await CalculoEmpresasService.create_link(calculo_id, req.empresa_id, req.rol, req.orden)
    return CalculoEmpresaLink(**link)


@router.patch(
    "/proyectos/{project_id}/calculos/{calculo_id}/empresas/{link_id}",
    response_model=CalculoEmpresaLink,
)
async def actualizar_vinculo_empresa_calculo(
    project_id: int,
    calculo_id: int,
    link_id: int,
    req: CalculoEmpresaLinkUpdate,
    user: AuthRequiredDep,
) -> CalculoEmpresaLink:
    """Actualizar vinculo empresa-calculo. Requiere autenticación."""
    if not await ProjectsService.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"Proyecto {project_id} no encontrado")
    calculo = await CalculosService.get_calculo(calculo_id)
    if not calculo or calculo.get("project_id") != project_id:
        raise HTTPException(status_code=404, detail=f"Calculo {calculo_id} no encontrado")
    if not await CalculoEmpresasService.link_exists(link_id):
        raise HTTPException(status_code=404, detail=f"Vinculo {link_id} no encontrado")
    data = {k: v for k, v in req.model_dump().items() if v is not None}
    link = await CalculoEmpresasService.update_link(link_id, data.get("rol"), data.get("orden"))
    return CalculoEmpresaLink(**link)


@router.delete("/proyectos/{project_id}/calculos/{calculo_id}/empresas/{link_id}", status_code=204)
async def desvincular_empresa_calculo(
    project_id: int,
    calculo_id: int,
    link_id: int,
    user: AuthRequiredDep,
) -> Response:
    """Desvincular empresa de un calculo. Requiere autenticación."""
    if not await ProjectsService.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"Proyecto {project_id} no encontrado")
    calculo = await CalculosService.get_calculo(calculo_id)
    if not calculo or calculo.get("project_id") != project_id:
        raise HTTPException(status_code=404, detail=f"Calculo {calculo_id} no encontrado")
    if not await CalculoEmpresasService.link_exists(link_id):
        raise HTTPException(status_code=404, detail=f"Vinculo {link_id} no encontrado")
    await CalculoEmpresasService.delete_link(link_id)
    return Response(status_code=204)


# --- Calculo-Ingeniero Associations ---


@router.get(
    "/proyectos/{project_id}/calculos/{calculo_id}/ingenieros",
    response_model=list[CalculoIngenieroLink],
)
async def listar_ingenieros_calculo(project_id: int, calculo_id: int) -> list[CalculoIngenieroLink]:
    """Listar ingenieros vinculados a un calculo."""
    if not await ProjectsService.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"Proyecto {project_id} no encontrado")
    calculo = await CalculosService.get_calculo(calculo_id)
    if not calculo or calculo.get("project_id") != project_id:
        raise HTTPException(status_code=404, detail=f"Calculo {calculo_id} no encontrado")
    links = await CalculoIngenierosService.list_links(calculo_id)
    return [CalculoIngenieroLink(**link) for link in links]


@router.post(
    "/proyectos/{project_id}/calculos/{calculo_id}/ingenieros",
    status_code=201,
    response_model=CalculoIngenieroLink,
)
async def vincular_ingeniero_calculo(
    project_id: int,
    calculo_id: int,
    req: CalculoIngenieroLinkCreate,
    user: AuthRequiredDep,
) -> CalculoIngenieroLink:
    """Vincular ingeniero a un calculo. Requiere autenticación."""
    if not await ProjectsService.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"Proyecto {project_id} no encontrado")
    calculo = await CalculosService.get_calculo(calculo_id)
    if not calculo or calculo.get("project_id") != project_id:
        raise HTTPException(status_code=404, detail=f"Calculo {calculo_id} no encontrado")
    if not await IngenierosService.ingeniero_exists(req.ingeniero_id):
        raise HTTPException(status_code=404, detail=f"Ingeniero {req.ingeniero_id} no encontrado")
    link = await CalculoIngenierosService.create_link(
        calculo_id, req.ingeniero_id, req.rol, req.orden
    )
    return CalculoIngenieroLink(**link)


@router.patch(
    "/proyectos/{project_id}/calculos/{calculo_id}/ingenieros/{link_id}",
    response_model=CalculoIngenieroLink,
)
async def actualizar_vinculo_ingeniero_calculo(
    project_id: int,
    calculo_id: int,
    link_id: int,
    req: CalculoIngenieroLinkUpdate,
    user: AuthRequiredDep,
) -> CalculoIngenieroLink:
    """Actualizar vinculo ingeniero-calculo. Requiere autenticación."""
    if not await ProjectsService.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"Proyecto {project_id} no encontrado")
    calculo = await CalculosService.get_calculo(calculo_id)
    if not calculo or calculo.get("project_id") != project_id:
        raise HTTPException(status_code=404, detail=f"Calculo {calculo_id} no encontrado")
    if not await CalculoIngenierosService.link_exists(link_id):
        raise HTTPException(status_code=404, detail=f"Vinculo {link_id} no encontrado")
    data = {k: v for k, v in req.model_dump().items() if v is not None}
    link = await CalculoIngenierosService.update_link(link_id, data.get("rol"), data.get("orden"))
    return CalculoIngenieroLink(**link)


@router.delete(
    "/proyectos/{project_id}/calculos/{calculo_id}/ingenieros/{link_id}", status_code=204
)
async def desvincular_ingeniero_calculo(
    project_id: int,
    calculo_id: int,
    link_id: int,
    user: AuthRequiredDep,
) -> Response:
    """Desvincular ingeniero de un calculo. Requiere autenticación."""
    if not await ProjectsService.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"Proyecto {project_id} no encontrado")
    calculo = await CalculosService.get_calculo(calculo_id)
    if not calculo or calculo.get("project_id") != project_id:
        raise HTTPException(status_code=404, detail=f"Calculo {calculo_id} no encontrado")
    if not await CalculoIngenierosService.link_exists(link_id):
        raise HTTPException(status_code=404, detail=f"Vinculo {link_id} no encontrado")
    await CalculoIngenierosService.delete_link(link_id)
    return Response(status_code=204)
