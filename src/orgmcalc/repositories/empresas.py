"""Empresas repository - CRUD operations."""

from __future__ import annotations

from typing import Any

from sqlalchemy import func, select

from orgmcalc.db.session import get_session
from orgmcalc.models import Empresa


def _empresa_to_dict(empresa: Empresa) -> dict[str, Any]:
    """Convert Empresa model to dict with formatted timestamps."""
    return {
        c.name: (
            getattr(empresa, c.name).isoformat()
            if hasattr(getattr(empresa, c.name), "isoformat")
            else getattr(empresa, c.name)
        )
        for c in empresa.__table__.columns
    }


class EmpresasRepository:
    """Repository for empresas table operations."""

    @staticmethod
    async def list_all(offset: int = 0, limit: int = 100) -> list[dict[str, Any]]:
        """List all companies."""
        async with get_session() as session:
            result = await session.execute(
                select(Empresa).order_by(Empresa.nombre).offset(offset).limit(limit)
            )
            empresas = result.scalars().all()
            return [_empresa_to_dict(e) for e in empresas]

    @staticmethod
    async def count_all() -> int:
        """Count total companies."""
        async with get_session() as session:
            result = await session.execute(select(func.count()).select_from(Empresa))
            return result.scalar_one()

    @staticmethod
    async def get_by_id(empresa_id: str) -> dict[str, Any] | None:
        """Get company by ID."""
        async with get_session() as session:
            result = await session.execute(select(Empresa).where(Empresa.id == empresa_id))
            empresa = result.scalar_one_or_none()
            if empresa is None:
                return None
            return _empresa_to_dict(empresa)

    @staticmethod
    async def create(data: dict[str, Any]) -> dict[str, Any]:
        """Create a new company."""
        empresa = Empresa(
            nombre=data["nombre"],
            contacto=data.get("contacto"),
            telefono=data.get("telefono"),
            correo=data.get("correo"),
            direccion=data.get("direccion"),
            ciudad=data.get("ciudad"),
        )
        async with get_session() as session:
            session.add(empresa)
            await session.flush()
            await session.refresh(empresa)
            return _empresa_to_dict(empresa)

    @staticmethod
    async def update(empresa_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        """Update company fields."""
        async with get_session() as session:
            result = await session.execute(select(Empresa).where(Empresa.id == empresa_id))
            empresa = result.scalar_one_or_none()
            if empresa is None:
                return None

            for key, value in data.items():
                if value is not None and hasattr(empresa, key):
                    setattr(empresa, key, value)

            empresa.updated_at = func.now()
            await session.flush()
            await session.refresh(empresa)
            return _empresa_to_dict(empresa)

    @staticmethod
    async def delete(empresa_id: str) -> bool:
        """Delete company by ID. Returns True if deleted."""
        async with get_session() as session:
            result = await session.execute(select(Empresa).where(Empresa.id == empresa_id))
            empresa = result.scalar_one_or_none()
            if empresa is None:
                return False
            await session.delete(empresa)
            return True

    @staticmethod
    async def exists(empresa_id: str) -> bool:
        """Check if company exists."""
        async with get_session() as session:
            result = await session.execute(
                select(Empresa.id).where(Empresa.id == empresa_id).limit(1)
            )
            return result.scalar_one_or_none() is not None
