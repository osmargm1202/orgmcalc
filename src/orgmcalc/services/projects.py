"""Projects service - business logic."""

from __future__ import annotations

from typing import Any

from orgmcalc.repositories.clientes import ClientesRepository
from orgmcalc.repositories.files import FilesRepository
from orgmcalc.repositories.projects import ProjectsRepository


class ProjectsService:
    """Service for project business logic."""

    @staticmethod
    async def list_projects(offset: int = 0, limit: int = 100) -> list[dict[str, Any]]:
        """List projects with file availability."""
        projects = await ProjectsRepository.list_all(offset, limit)
        # Enrich with logo availability
        for proj in projects:
            proj["logo_available"] = False
            proj["cliente_logo_available"] = False
            file_meta = await FilesRepository.get_active("project", proj["id"], "logo")
            if file_meta:
                proj["logo_available"] = True
            cliente_file_meta = await FilesRepository.get_active(
                "project", proj["id"], "cliente_logo"
            )
            if cliente_file_meta:
                proj["cliente_logo_available"] = True
        return projects

    @staticmethod
    async def get_project(project_id: str) -> dict[str, Any] | None:
        """Get project with file availability."""
        proj = await ProjectsRepository.get_by_id(project_id)
        if proj:
            proj["logo_available"] = False
            proj["cliente_logo_available"] = False
            file_meta = await FilesRepository.get_active("project", project_id, "logo")
            if file_meta:
                proj["logo_available"] = True
            cliente_file_meta = await FilesRepository.get_active(
                "project", project_id, "cliente_logo"
            )
            if cliente_file_meta:
                proj["cliente_logo_available"] = True
        return proj

    @staticmethod
    async def create_project(data: dict[str, Any]) -> dict[str, Any]:
        """Create project."""
        cliente_id = data.get("cliente_id")
        if cliente_id and not await ClientesRepository.exists(cliente_id):
            raise ValueError(f"Cliente con ID '{cliente_id}' no existe")
        return await ProjectsRepository.create(data)

    @staticmethod
    async def update_project(project_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        """Update project."""
        cliente_id = data.get("cliente_id")
        if cliente_id and not await ClientesRepository.exists(cliente_id):
            raise ValueError(f"Cliente con ID '{cliente_id}' no existe")
        return await ProjectsRepository.update(project_id, data)

    @staticmethod
    async def delete_project(project_id: str) -> bool:
        """Delete project."""
        return await ProjectsRepository.delete(project_id)

    @staticmethod
    async def project_exists(project_id: str) -> bool:
        """Check if project exists."""
        return await ProjectsRepository.exists(project_id)
