"""Ingenieros service - business logic."""
from __future__ import annotations

from typing import Any

from orgmcalc.repositories.files import FilesRepository
from orgmcalc.repositories.ingenieros import IngenierosRepository


class IngenierosService:
    """Service for engineer business logic."""

    @staticmethod
    async def list_ingenieros(
        offset: int = 0, limit: int = 100, empresa_id: int | None = None
    ) -> list[dict[str, Any]]:
        """List engineers with file availability."""
        ingenieros = await IngenierosRepository.list_all(offset, limit, empresa_id)
        for ing in ingenieros:
            ing["perfil_available"] = False
            ing["carnet_available"] = False
            ing["certificacion_available"] = False
            # Check file availability
            if await FilesRepository.get_active("ingeniero", ing["id"], "perfil"):
                ing["perfil_available"] = True
            if await FilesRepository.get_active("ingeniero", ing["id"], "carnet"):
                ing["carnet_available"] = True
            if await FilesRepository.get_active("ingeniero", ing["id"], "certificacion"):
                ing["certificacion_available"] = True
        return ingenieros

    @staticmethod
    async def get_ingeniero(ingeniero_id: int) -> dict[str, Any] | None:
        """Get engineer with file availability."""
        ing = await IngenierosRepository.get_by_id(ingeniero_id)
        if ing:
            ing["perfil_available"] = False
            ing["carnet_available"] = False
            ing["certificacion_available"] = False
            if await FilesRepository.get_active("ingeniero", ingeniero_id, "perfil"):
                ing["perfil_available"] = True
            if await FilesRepository.get_active("ingeniero", ingeniero_id, "carnet"):
                ing["carnet_available"] = True
            if await FilesRepository.get_active("ingeniero", ingeniero_id, "certificacion"):
                ing["certificacion_available"] = True
        return ing

    @staticmethod
    async def create_ingeniero(data: dict[str, Any]) -> dict[str, Any]:
        """Create engineer."""
        return await IngenierosRepository.create(data)

    @staticmethod
    async def update_ingeniero(ingeniero_id: int, data: dict[str, Any]) -> dict[str, Any] | None:
        """Update engineer."""
        return await IngenierosRepository.update(ingeniero_id, data)

    @staticmethod
    async def delete_ingeniero(ingeniero_id: int) -> bool:
        """Delete engineer."""
        return await IngenierosRepository.delete(ingeniero_id)

    @staticmethod
    async def ingeniero_exists(ingeniero_id: int) -> bool:
        """Check if engineer exists."""
        return await IngenierosRepository.exists(ingeniero_id)
