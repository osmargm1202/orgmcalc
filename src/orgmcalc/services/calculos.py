"""Calculos service - business logic."""
from __future__ import annotations

from typing import Any

from orgmcalc.repositories.calculo_empresas import CalculoEmpresasRepository
from orgmcalc.repositories.calculo_ingenieros import CalculoIngenierosRepository
from orgmcalc.repositories.calculos import CalculosRepository


class CalculosService:
    """Service for calculation business logic."""

    @staticmethod
    async def list_calculos(
        project_id: int, offset: int = 0, limit: int = 100
    ) -> list[dict[str, Any]]:
        """List calculations for a project."""
        return await CalculosRepository.list_by_project(project_id, offset, limit)

    @staticmethod
    async def get_calculo(calculo_id: int) -> dict[str, Any] | None:
        """Get calculation by ID."""
        return await CalculosRepository.get_by_id(calculo_id)

    @staticmethod
    async def create_calculo(data: dict[str, Any]) -> dict[str, Any]:
        """Create calculation."""
        return await CalculosRepository.create(data)

    @staticmethod
    async def update_calculo(calculo_id: int, data: dict[str, Any]) -> dict[str, Any] | None:
        """Update calculation."""
        return await CalculosRepository.update(calculo_id, data)

    @staticmethod
    async def delete_calculo(calculo_id: int) -> bool:
        """Delete calculation."""
        return await CalculosRepository.delete(calculo_id)

    @staticmethod
    async def calculo_exists(calculo_id: int) -> bool:
        """Check if calculation exists."""
        return await CalculosRepository.exists(calculo_id)


class CalculoEmpresasService:
    """Service for calculation-company association logic."""

    @staticmethod
    async def list_links(calculo_id: int) -> list[dict[str, Any]]:
        """List company links for calculation."""
        return await CalculoEmpresasRepository.list_by_calculo(calculo_id)

    @staticmethod
    async def get_link(link_id: int) -> dict[str, Any] | None:
        """Get link by ID."""
        return await CalculoEmpresasRepository.get_by_id(link_id)

    @staticmethod
    async def create_link(
        calculo_id: int, empresa_id: int, rol: str | None, orden: int
    ) -> dict[str, Any]:
        """Create company link."""
        return await CalculoEmpresasRepository.create(calculo_id, empresa_id, rol, orden)

    @staticmethod
    async def update_link(
        link_id: int, rol: str | None, orden: int | None
    ) -> dict[str, Any] | None:
        """Update company link."""
        return await CalculoEmpresasRepository.update(link_id, rol, orden)

    @staticmethod
    async def delete_link(link_id: int) -> bool:
        """Delete company link."""
        return await CalculoEmpresasRepository.delete(link_id)

    @staticmethod
    async def link_exists(link_id: int) -> bool:
        """Check if link exists."""
        return await CalculoEmpresasRepository.exists(link_id)


class CalculoIngenierosService:
    """Service for calculation-engineer association logic."""

    @staticmethod
    async def list_links(calculo_id: int) -> list[dict[str, Any]]:
        """List engineer links for calculation."""
        return await CalculoIngenierosRepository.list_by_calculo(calculo_id)

    @staticmethod
    async def get_link(link_id: int) -> dict[str, Any] | None:
        """Get link by ID."""
        return await CalculoIngenierosRepository.get_by_id(link_id)

    @staticmethod
    async def create_link(
        calculo_id: int, ingeniero_id: int, rol: str | None, orden: int
    ) -> dict[str, Any]:
        """Create engineer link."""
        return await CalculoIngenierosRepository.create(calculo_id, ingeniero_id, rol, orden)

    @staticmethod
    async def update_link(
        link_id: int, rol: str | None, orden: int | None
    ) -> dict[str, Any] | None:
        """Update engineer link."""
        return await CalculoIngenierosRepository.update(link_id, rol, orden)

    @staticmethod
    async def delete_link(link_id: int) -> bool:
        """Delete engineer link."""
        return await CalculoIngenierosRepository.delete(link_id)

    @staticmethod
    async def link_exists(link_id: int) -> bool:
        """Check if link exists."""
        return await CalculoIngenierosRepository.exists(link_id)
