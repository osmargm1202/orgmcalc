"""Storage API routes - file upload/download/status."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import RedirectResponse

from orgmcalc.api.dependencies import AuthRequiredDep
from orgmcalc.schemas.files import FileStatus, FileStatusBatchResponse, FileStatusRequest
from orgmcalc.services.empresas import EmpresasService
from orgmcalc.services.files import FilesService
from orgmcalc.services.ingenieros import IngenierosService
from orgmcalc.services.projects import ProjectsService

router = APIRouter(tags=["storage"])


def _check_content_type(content_type: str | None) -> str:
    ct = (content_type or "").split(";")[0].strip().lower()
    if not FilesService.is_valid_content_type(ct):
        raise HTTPException(
            status_code=422,
            detail="Tipo de archivo no permitido. Permitidos: imagen (png, jpeg, webp, gif) o PDF",
        )
    return ct


# --- Project Logo ---


@router.get("/proyectos/{project_id}/logo")
async def descargar_logo_proyecto(project_id: int) -> RedirectResponse:
    """Descargar logo del proyecto."""
    if not await ProjectsService.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"Proyecto {project_id} no encontrado")
    url = await FilesService.get_download_url("project", project_id, "logo")
    if not url:
        raise HTTPException(status_code=404, detail="Logo no encontrado")
    return RedirectResponse(url=url, status_code=302)


@router.get("/proyectos/{project_id}/logo/status", response_model=FileStatus)
async def estado_logo_proyecto(project_id: int) -> FileStatus:
    """Estado del logo del proyecto."""
    if not await ProjectsService.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"Proyecto {project_id} no encontrado")
    status = await FilesService.get_file_status("project", project_id, "logo")
    return FileStatus(**status)


@router.post("/proyectos/{project_id}/logo")
async def subir_logo_proyecto(
    project_id: int,
    user: AuthRequiredDep,
    file: UploadFile = File(...),
) -> dict[str, Any]:
    """Subir/reemplazar logo del proyecto. Requiere autenticación."""
    if not await ProjectsService.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"Proyecto {project_id} no encontrado")
    ct = _check_content_type(file.content_type)
    content = await file.read()
    result = await FilesService.upload_project_logo(project_id, content, ct, file.filename)
    if not result:
        raise HTTPException(status_code=503, detail="Almacenamiento no disponible")
    return {"storage_key": result["storage_key"], "url": result.get("url")}


# --- Proyecto Cliente Logo ---

@router.get("/proyectos/{project_id}/cliente/logo")
async def descargar_logo_cliente_proyecto(project_id: int) -> RedirectResponse:
    """Descargar logo del cliente del proyecto."""
    if not await ProjectsService.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"Proyecto {project_id} no encontrado")
    url = await FilesService.get_project_cliente_logo_url(project_id)
    if not url:
        raise HTTPException(status_code=404, detail="Logo de cliente no encontrado")
    return RedirectResponse(url=url, status_code=302)


@router.get("/proyectos/{project_id}/cliente/logo/status", response_model=FileStatus)
async def estado_logo_cliente_proyecto(project_id: int) -> FileStatus:
    """Estado del logo del cliente del proyecto."""
    if not await ProjectsService.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"Proyecto {project_id} no encontrado")
    status = await FilesService.get_project_cliente_logo_status(project_id)
    return FileStatus(**status)


@router.post("/proyectos/{project_id}/cliente/logo")
async def subir_logo_cliente_proyecto(
    project_id: int,
    user: AuthRequiredDep,
    file: UploadFile = File(...),
) -> dict[str, Any]:
    """Subir/reemplazar logo del cliente del proyecto. Requiere autenticación."""
    if not await ProjectsService.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"Proyecto {project_id} no encontrado")
    ct = _check_content_type(file.content_type)
    content = await file.read()
    result = await FilesService.upload_project_cliente_logo(project_id, content, ct, file.filename)
    if not result:
        raise HTTPException(status_code=503, detail="Almacenamiento no disponible")
    return {"storage_key": result["storage_key"], "url": result.get("url")}


# --- Empresa Logo ---


@router.get("/empresas/{empresa_id}/logo")
async def descargar_logo_empresa(empresa_id: int) -> RedirectResponse:
    """Descargar logo de la empresa."""
    if not await EmpresasService.empresa_exists(empresa_id):
        raise HTTPException(status_code=404, detail=f"Empresa {empresa_id} no encontrada")
    url = await FilesService.get_download_url("empresa", empresa_id, "logo")
    if not url:
        raise HTTPException(status_code=404, detail="Logo no encontrado")
    return RedirectResponse(url=url, status_code=302)


@router.get("/empresas/{empresa_id}/logo/status", response_model=FileStatus)
async def estado_logo_empresa(empresa_id: int) -> FileStatus:
    """Estado del logo de la empresa."""
    if not await EmpresasService.empresa_exists(empresa_id):
        raise HTTPException(status_code=404, detail=f"Empresa {empresa_id} no encontrada")
    status = await FilesService.get_file_status("empresa", empresa_id, "logo")
    return FileStatus(**status)


@router.post("/empresas/{empresa_id}/logo")
async def subir_logo_empresa(
    empresa_id: int,
    user: AuthRequiredDep,
    file: UploadFile = File(...),
) -> dict[str, Any]:
    """Subir/reemplazar logo de la empresa. Requiere autenticación."""
    if not await EmpresasService.empresa_exists(empresa_id):
        raise HTTPException(status_code=404, detail=f"Empresa {empresa_id} no encontrada")
    ct = _check_content_type(file.content_type)
    content = await file.read()
    result = await FilesService.upload_empresa_logo(empresa_id, content, ct, file.filename)
    if not result:
        raise HTTPException(status_code=503, detail="Almacenamiento no disponible")
    return {"storage_key": result["storage_key"], "url": result.get("url")}


# --- Ingeniero Perfil ---


@router.get("/ingenieros/{ingeniero_id}/perfil")
async def descargar_perfil_ingeniero(ingeniero_id: int) -> RedirectResponse:
    """Descargar foto de perfil del ingeniero."""
    if not await IngenierosService.ingeniero_exists(ingeniero_id):
        raise HTTPException(status_code=404, detail=f"Ingeniero {ingeniero_id} no encontrado")
    url = await FilesService.get_download_url("ingeniero", ingeniero_id, "perfil")
    if not url:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")
    return RedirectResponse(url=url, status_code=302)


@router.get("/ingenieros/{ingeniero_id}/perfil/status", response_model=FileStatus)
async def estado_perfil_ingeniero(ingeniero_id: int) -> FileStatus:
    """Estado del perfil del ingeniero."""
    if not await IngenierosService.ingeniero_exists(ingeniero_id):
        raise HTTPException(status_code=404, detail=f"Ingeniero {ingeniero_id} no encontrado")
    status = await FilesService.get_file_status("ingeniero", ingeniero_id, "perfil")
    return FileStatus(**status)


@router.post("/ingenieros/{ingeniero_id}/perfil")
async def subir_perfil_ingeniero(
    ingeniero_id: int,
    user: AuthRequiredDep,
    file: UploadFile = File(...),
) -> dict[str, Any]:
    """Subir/reemplazar foto de perfil del ingeniero. Requiere autenticación."""
    if not await IngenierosService.ingeniero_exists(ingeniero_id):
        raise HTTPException(status_code=404, detail=f"Ingeniero {ingeniero_id} no encontrado")
    ct = _check_content_type(file.content_type)
    content = await file.read()
    result = await FilesService.upload_ingeniero_perfil(ingeniero_id, content, ct, file.filename)
    if not result:
        raise HTTPException(status_code=503, detail="Almacenamiento no disponible")
    return {"storage_key": result["storage_key"], "url": result.get("url")}


# --- Ingeniero Carnet ---


@router.get("/ingenieros/{ingeniero_id}/carnet")
async def descargar_carnet_ingeniero(ingeniero_id: int) -> RedirectResponse:
    """Descargar carnet del ingeniero."""
    if not await IngenierosService.ingeniero_exists(ingeniero_id):
        raise HTTPException(status_code=404, detail=f"Ingeniero {ingeniero_id} no encontrado")
    url = await FilesService.get_download_url("ingeniero", ingeniero_id, "carnet")
    if not url:
        raise HTTPException(status_code=404, detail="Carnet no encontrado")
    return RedirectResponse(url=url, status_code=302)


@router.get("/ingenieros/{ingeniero_id}/carnet/status", response_model=FileStatus)
async def estado_carnet_ingeniero(ingeniero_id: int) -> FileStatus:
    """Estado del carnet del ingeniero."""
    if not await IngenierosService.ingeniero_exists(ingeniero_id):
        raise HTTPException(status_code=404, detail=f"Ingeniero {ingeniero_id} no encontrado")
    status = await FilesService.get_file_status("ingeniero", ingeniero_id, "carnet")
    return FileStatus(**status)


@router.post("/ingenieros/{ingeniero_id}/carnet")
async def subir_carnet_ingeniero(
    ingeniero_id: int,
    user: AuthRequiredDep,
    file: UploadFile = File(...),
) -> dict[str, Any]:
    """Subir/reemplazar carnet del ingeniero. Requiere autenticación."""
    if not await IngenierosService.ingeniero_exists(ingeniero_id):
        raise HTTPException(status_code=404, detail=f"Ingeniero {ingeniero_id} no encontrado")
    ct = _check_content_type(file.content_type)
    content = await file.read()
    result = await FilesService.upload_ingeniero_carnet(ingeniero_id, content, ct, file.filename)
    if not result:
        raise HTTPException(status_code=503, detail="Almacenamiento no disponible")
    return {"storage_key": result["storage_key"], "url": result.get("url")}


# --- Ingeniero Certificacion ---


@router.get("/ingenieros/{ingeniero_id}/certificacion")
async def descargar_certificacion_ingeniero(ingeniero_id: int) -> RedirectResponse:
    """Descargar certificacion del ingeniero."""
    if not await IngenierosService.ingeniero_exists(ingeniero_id):
        raise HTTPException(status_code=404, detail=f"Ingeniero {ingeniero_id} no encontrado")
    url = await FilesService.get_download_url("ingeniero", ingeniero_id, "certificacion")
    if not url:
        raise HTTPException(status_code=404, detail="Certificacion no encontrada")
    return RedirectResponse(url=url, status_code=302)


@router.get("/ingenieros/{ingeniero_id}/certificacion/status", response_model=FileStatus)
async def estado_certificacion_ingeniero(ingeniero_id: int) -> FileStatus:
    """Estado de la certificacion del ingeniero."""
    if not await IngenierosService.ingeniero_exists(ingeniero_id):
        raise HTTPException(status_code=404, detail=f"Ingeniero {ingeniero_id} no encontrado")
    status = await FilesService.get_file_status("ingeniero", ingeniero_id, "certificacion")
    return FileStatus(**status)


@router.post("/ingenieros/{ingeniero_id}/certificacion")
async def subir_certificacion_ingeniero(
    ingeniero_id: int,
    user: AuthRequiredDep,
    file: UploadFile = File(...),
) -> dict[str, Any]:
    """Subir/reemplazar certificacion del ingeniero. Requiere autenticación."""
    if not await IngenierosService.ingeniero_exists(ingeniero_id):
        raise HTTPException(status_code=404, detail=f"Ingeniero {ingeniero_id} no encontrado")
    ct = _check_content_type(file.content_type)
    content = await file.read()
    result = await FilesService.upload_ingeniero_certificacion(
        ingeniero_id, content, ct, file.filename
    )
    if not result:
        raise HTTPException(status_code=503, detail="Almacenamiento no disponible")
    return {"storage_key": result["storage_key"], "url": result.get("url")}


# --- Documento File ---


@router.get("/proyectos/{project_id}/documentos/{document_id}/file")
async def descargar_documento_file(project_id: int, document_id: int) -> RedirectResponse:
    """Descargar archivo de documento."""
    if not await ProjectsService.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"Proyecto {project_id} no encontrado")
    url = await FilesService.get_download_url("documento", document_id, "documento")
    if not url:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    return RedirectResponse(url=url, status_code=302)


@router.post("/proyectos/{project_id}/documentos/{document_id}/file")
async def subir_documento_file(
    project_id: int,
    document_id: int,
    user: AuthRequiredDep,
    file: UploadFile = File(...),
) -> dict[str, Any]:
    """Subir/reemplazar archivo de documento. Requiere autenticación."""
    if not await ProjectsService.project_exists(project_id):
        raise HTTPException(status_code=404, detail=f"Proyecto {project_id} no encontrado")
    ct = _check_content_type(file.content_type)
    content = await file.read()
    result = await FilesService.upload_documento_file(
        project_id, document_id, content, ct, file.filename or "document.pdf"
    )
    if not result:
        raise HTTPException(status_code=503, detail="Almacenamiento no disponible")
    return {"storage_key": result["storage_key"], "url": result.get("url")}


# --- Batch Status ---


@router.post("/storage/status", response_model=FileStatusBatchResponse)
async def batch_file_status(req: FileStatusRequest) -> FileStatusBatchResponse:
    """Verificar estado de multiples archivos."""
    statuses = await FilesService.get_batch_status(req.keys)
    result = {}
    for key, status in statuses.items():
        result[key] = FileStatus(**status)
    # Add missing keys as unavailable
    for key in req.keys:
        if key not in result:
            result[key] = FileStatus(available=False, storage_key=None)
    return FileStatusBatchResponse(statuses=result)
