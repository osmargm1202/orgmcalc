"""Documentos API routes - Spanish naming for compatibility."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Response

from orgmcalc.api.dependencies import AuthRequiredDep
from orgmcalc.schemas.documentos import DocumentoCreate, DocumentoListItem, DocumentoResponse
from orgmcalc.services.documentos import DocumentosService
from orgmcalc.services.projects import ProjectsService

router = APIRouter(tags=["documentos"])


@router.get("/proyectos/{project_id}/documentos", response_model=list[DocumentoListItem])
async def listar_documentos_proyecto(
    project_id: str,
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(100, ge=1, le=500, description="Limit for pagination (max 500)"),
) -> list[DocumentoListItem]:
    """Listar documentos de un proyecto."""
    if not await ProjectsService.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"Proyecto {project_id} no encontrado")
    documentos = await DocumentosService.list_documentos(project_id, offset, limit)
    return [DocumentoListItem(**d) for d in documentos]


@router.get("/proyectos/{project_id}/documentos/{document_id}", response_model=DocumentoResponse)
async def obtener_documento_proyecto(project_id: str, document_id: str) -> DocumentoResponse:
    """Obtener documento de un proyecto."""
    if not await ProjectsService.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"Proyecto {project_id} no encontrado")
    documento = await DocumentosService.get_documento(document_id)
    if not documento or documento.get("project_id") != project_id:
        raise HTTPException(status_code=404, detail=f"Documento {document_id} no encontrado")
    return DocumentoResponse(**documento)


@router.post(
    "/proyectos/{project_id}/documentos", status_code=201, response_model=DocumentoResponse
)
async def crear_documento_proyecto(
    project_id: str,
    req: DocumentoCreate,
    user: AuthRequiredDep,
) -> DocumentoResponse:
    """Crear documento en un proyecto. Requiere autenticación."""
    if not await ProjectsService.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"Proyecto {project_id} no encontrado")
    data = req.model_dump()
    data["project_id"] = project_id
    documento = await DocumentosService.create_documento(data)
    return DocumentoResponse(**documento)


@router.delete("/proyectos/{project_id}/documentos/{document_id}", status_code=204)
async def eliminar_documento_proyecto(
    project_id: str,
    document_id: str,
    user: AuthRequiredDep,
) -> Response:
    """Eliminar documento de un proyecto. Requiere autenticación."""
    if not await ProjectsService.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"Proyecto {project_id} no encontrado")
    documento = await DocumentosService.get_documento(document_id)
    if not documento or documento.get("project_id") != project_id:
        raise HTTPException(status_code=404, detail=f"Documento {document_id} no encontrado")
    await DocumentosService.delete_documento(document_id)
    return Response(status_code=204)
