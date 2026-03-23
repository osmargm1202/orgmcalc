"""Empresas service - business logic."""
from __future__ import annotations

from typing import Any

from orgmcalc.repositories.empresas import EmpresasRepository
from orgmcalc.repositories.files import FilesRepository


class EmpresasService:
    """Service for company business logic."""

    @staticmethod
    async def list_empresas(offset: int = 0, limit: int = 100) -> list[dict[str, Any]]:
        """List companies with file availability."""
        empresas = await EmpresasRepository.list_all(offset, limit)
        for emp in empresas:
            emp["logo_available"] = False
            file_meta = await FilesRepository.get_active("empresa", emp["id"], "logo")
            if file_meta:
                emp["logo_available"] = True
        return empresas

    @staticmethod
    async def get_empresa(empresa_id: int) -> dict[str, Any] | None:
        """Get company with file availability."""
        emp = await EmpresasRepository.get_by_id(empresa_id)
        if emp:
            emp["logo_available"] = False
            file_meta = await FilesRepository.get_active("empresa", empresa_id, "logo")
            if file_meta:
                emp["logo_available"] = True
        return emp

    @staticmethod
    async def create_empresa(data: dict[str, Any]) -> dict[str, Any]:
        """Create company."""
        return await EmpresasRepository.create(data)

    @staticmethod
    async def update_empresa(empresa_id: int, data: dict[str, Any]) -> dict[str, Any] | None:
        """Update company."""
        return await EmpresasRepository.update(empresa_id, data)

    @staticmethod
    async def delete_empresa(empresa_id: int) -> bool:
        """Delete company."""
        return await EmpresasRepository.delete(empresa_id)

    @staticmethod
    async def empresa_exists(empresa_id: int) -> bool:
        """Check if company exists."""
        return await EmpresasRepository.exists(empresa_id)
