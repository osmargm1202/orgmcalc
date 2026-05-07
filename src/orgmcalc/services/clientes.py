"""Clientes service - business logic."""

from __future__ import annotations

from typing import Any

from orgmcalc.repositories.empresas import EmpresasRepository
from orgmcalc.repositories.clientes import ClientesRepository


class ClientesService:
    """Service for cliente business logic."""

    @staticmethod
    async def list_clientes(offset: int = 0, limit: int = 100) -> list[dict[str, Any]]:
        """List clientes."""
        return await ClientesRepository.list_all(offset, limit)

    @staticmethod
    async def get_cliente(cliente_id: str) -> dict[str, Any] | None:
        """Get cliente by ID."""
        return await ClientesRepository.get_by_id(cliente_id)

    @staticmethod
    async def create_cliente(data: dict[str, Any]) -> dict[str, Any]:
        """Create cliente."""
        empresa_id = data.get("empresa_id")
        if empresa_id and not await EmpresasRepository.exists(empresa_id):
            raise ValueError(f"Empresa con ID '{empresa_id}' no existe")
        return await ClientesRepository.create(data)

    @staticmethod
    async def update_cliente(cliente_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        """Update cliente."""
        empresa_id = data.get("empresa_id")
        if empresa_id and not await EmpresasRepository.exists(empresa_id):
            raise ValueError(f"Empresa con ID '{empresa_id}' no existe")
        return await ClientesRepository.update(cliente_id, data)

    @staticmethod
    async def delete_cliente(cliente_id: str) -> bool:
        """Delete cliente."""
        return await ClientesRepository.delete(cliente_id)

    @staticmethod
    async def cliente_exists(cliente_id: str) -> bool:
        """Check if cliente exists."""
        return await ClientesRepository.exists(cliente_id)
