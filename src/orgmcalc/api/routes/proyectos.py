"""Projects API routes - Spanish naming for compatibility."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Response

from fastapi import Depends

from orgmcalc.api.dependencies import AuthRequiredDep, require_auth
from orgmcalc.schemas.projects import ProjectCreate, ProjectResponse, ProjectUpdate
from orgmcalc.services.projects import ProjectsService

router = APIRouter(prefix="/proyectos", tags=["proyectos"])


@router.get("", response_model=list[ProjectResponse])
async def listar_proyectos(
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(100, ge=1, le=500, description="Limit for pagination (max 500)"),
) -> list[ProjectResponse]:
    """Listar todos los proyectos.

    Returns:
        Lista de proyectos

    """
    projects = await ProjectsService.list_projects(offset, limit)
    return [ProjectResponse(**p) for p in projects]


@router.get("/{project_id}", response_model=ProjectResponse)
async def obtener_proyecto(project_id: int) -> ProjectResponse:
    """Obtener proyecto por ID.

    Args:
        project_id: ID del proyecto

    Returns:
        Detalles del proyecto

    Raises:
        HTTPException: 404 si no existe

    """
    project = await ProjectsService.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"Proyecto {project_id} no encontrado")
    return ProjectResponse(**project)


@router.post(
    "",
    status_code=201,
    response_model=ProjectResponse,
)
async def crear_proyecto(
    req: ProjectCreate,
    user: AuthRequiredDep,
) -> ProjectResponse:
    """Crear nuevo proyecto.

    Requiere autenticación.

    Args:
        req: Datos del proyecto a crear
        user: Usuario autenticado

    Returns:
        Proyecto creado

    """
    data = req.model_dump()
    project = await ProjectsService.create_project(data)
    return ProjectResponse(**project)


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
)
async def actualizar_proyecto(
    project_id: int,
    req: ProjectUpdate,
    user: AuthRequiredDep,
) -> ProjectResponse:
    """Actualizar proyecto existente.

    Requiere autenticación.

    Args:
        project_id: ID del proyecto
        req: Campos a actualizar
        user: Usuario autenticado

    Returns:
        Proyecto actualizado

    Raises:
        HTTPException: 404 si no existe, 400 si no hay datos

    """
    data = {k: v for k, v in req.model_dump().items() if v is not None}
    if not data:
        raise HTTPException(status_code=400, detail="Nada que actualizar")
    project = await ProjectsService.update_project(project_id, data)
    if not project:
        raise HTTPException(status_code=404, detail=f"Proyecto {project_id} no encontrado")
    return ProjectResponse(**project)


@router.delete(
    "/{project_id}",
    status_code=204,
)
async def eliminar_proyecto(
    project_id: int,
    user: AuthRequiredDep,
) -> Response:
    """Eliminar proyecto.

    Requiere autenticación.

    Args:
        project_id: ID del proyecto
        user: Usuario autenticado

    Returns:
        204 No Content

    Raises:
        HTTPException: 404 si no existe

    """
    if not await ProjectsService.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"Proyecto {project_id} no encontrado")
    await ProjectsService.delete_project(project_id)
    return Response(status_code=204)
