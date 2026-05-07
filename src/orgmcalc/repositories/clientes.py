"""Clientes repository - CRUD operations."""

from __future__ import annotations

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from orgmcalc.db.session import get_session
from orgmcalc.models import Cliente


def _cliente_to_dict(cliente: Cliente) -> dict[str, Any]:
    """Convert Cliente model to dict with embedded empresa data."""
    data = {
        c.name: (
            getattr(cliente, c.name).isoformat()
            if hasattr(getattr(cliente, c.name), "isoformat")
            else getattr(cliente, c.name)
        )
        for c in cliente.__table__.columns
    }
    data["empresa"] = None
    if cliente.empresa:
        data["empresa"] = {
            "id": cliente.empresa.id,
            "nombre": cliente.empresa.nombre,
        }
    return data


class ClientesRepository:
    """Repository for clientes table operations."""

    @staticmethod
    async def list_all(offset: int = 0, limit: int = 100) -> list[dict[str, Any]]:
        """List all clientes with linked empresa info."""
        async with get_session() as session:
            result = await session.execute(
                select(Cliente)
                .options(selectinload(Cliente.empresa))
                .order_by(Cliente.created_at.desc())
                .offset(offset)
                .limit(limit)
            )
            clientes = result.scalars().all()
            return [_cliente_to_dict(c) for c in clientes]

    @staticmethod
    async def count_all() -> int:
        """Count total clientes."""
        async with get_session() as session:
            result = await session.execute(select(func.count()).select_from(Cliente))
            return result.scalar_one()

    @staticmethod
    async def get_by_id(cliente_id: str) -> dict[str, Any] | None:
        """Get cliente by ID."""
        async with get_session() as session:
            result = await session.execute(
                select(Cliente)
                .options(selectinload(Cliente.empresa))
                .where(Cliente.id == cliente_id)
            )
            cliente = result.scalar_one_or_none()
            if cliente is None:
                return None
            return _cliente_to_dict(cliente)

    @staticmethod
    async def create(data: dict[str, Any]) -> dict[str, Any]:
        """Create a new cliente."""
        cliente = Cliente(
            empresa_id=data.get("empresa_id"),
            nombre=data.get("nombre"),
            ubicacion=data.get("ubicacion"),
            telefono=data.get("telefono"),
        )
        async with get_session() as session:
            session.add(cliente)
            await session.flush()
            await session.refresh(cliente)
            result = await session.execute(
                select(Cliente)
                .options(selectinload(Cliente.empresa))
                .where(Cliente.id == cliente.id)
            )
            hydrated = result.scalar_one()
            return _cliente_to_dict(hydrated)

    @staticmethod
    async def update(cliente_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        """Update cliente fields."""
        async with get_session() as session:
            result = await session.execute(
                select(Cliente)
                .options(selectinload(Cliente.empresa))
                .where(Cliente.id == cliente_id)
            )
            cliente = result.scalar_one_or_none()
            if cliente is None:
                return None

            for key in ["empresa_id", "nombre", "ubicacion", "telefono"]:
                if key in data and data[key] is not None:
                    setattr(cliente, key, data[key])

            cliente.updated_at = func.now()
            await session.flush()
            await session.refresh(cliente)
            result = await session.execute(
                select(Cliente)
                .options(selectinload(Cliente.empresa))
                .where(Cliente.id == cliente.id)
            )
            hydrated = result.scalar_one()
            return _cliente_to_dict(hydrated)

    @staticmethod
    async def delete(cliente_id: str) -> bool:
        """Delete cliente by ID. Returns True if deleted."""
        async with get_session() as session:
            result = await session.execute(select(Cliente).where(Cliente.id == cliente_id))
            cliente = result.scalar_one_or_none()
            if cliente is None:
                return False
            await session.delete(cliente)
            return True

    @staticmethod
    async def exists(cliente_id: str) -> bool:
        """Check if cliente exists."""
        async with get_session() as session:
            result = await session.execute(
                select(Cliente.id).where(Cliente.id == cliente_id).limit(1)
            )
            return result.scalar_one_or_none() is not None
