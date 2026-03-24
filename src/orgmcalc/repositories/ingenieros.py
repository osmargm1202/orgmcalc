"""Ingenieros repository - CRUD operations."""

from __future__ import annotations

from typing import Any

from sqlalchemy import func, or_, select

from orgmcalc.db.session import get_session
from orgmcalc.models import Calculo, Ingeniero, Project


def _ingeniero_to_dict(ingeniero: Ingeniero) -> dict[str, Any]:
    """Convert Ingeniero model to dict with formatted timestamps."""
    return {
        c.name: (
            getattr(ingeniero, c.name).isoformat()
            if hasattr(getattr(ingeniero, c.name), "isoformat")
            else getattr(ingeniero, c.name)
        )
        for c in ingeniero.__table__.columns
    }


class IngenierosRepository:
    """Repository for ingenieros table operations."""

    @staticmethod
    async def list_all(
        offset: int = 0, limit: int = 100, empresa_id: str | None = None
    ) -> list[dict[str, Any]]:
        """List all engineers, optionally filtered by empresa."""
        async with get_session() as session:
            if empresa_id:
                result = await session.execute(
                    select(Ingeniero)
                    .join(Calculo, Calculo.ingeniero_id == Ingeniero.id, isouter=True)
                    .join(Project, Calculo.project_id == Project.id, isouter=True)
                    .where(or_(Project.id == empresa_id, Project.id.is_(None)))
                    .order_by(Ingeniero.nombre)
                    .offset(offset)
                    .limit(limit)
                )
            else:
                result = await session.execute(
                    select(Ingeniero).order_by(Ingeniero.nombre).offset(offset).limit(limit)
                )
            ingenieros = result.scalars().all()
            return [_ingeniero_to_dict(i) for i in ingenieros]

    @staticmethod
    async def count_all() -> int:
        """Count total engineers."""
        async with get_session() as session:
            result = await session.execute(select(func.count()).select_from(Ingeniero))
            return result.scalar_one()

    @staticmethod
    async def get_by_id(ingeniero_id: str) -> dict[str, Any] | None:
        """Get engineer by ID."""
        async with get_session() as session:
            result = await session.execute(select(Ingeniero).where(Ingeniero.id == ingeniero_id))
            ingeniero = result.scalar_one_or_none()
            if ingeniero is None:
                return None
            return _ingeniero_to_dict(ingeniero)

    @staticmethod
    async def create(data: dict[str, Any]) -> dict[str, Any]:
        """Create a new engineer."""
        ingeniero = Ingeniero(
            nombre=data["nombre"],
            email=data.get("email"),
            telefono=data.get("telefono"),
            codia=data.get("codia"),
            id_empresas=data.get("id_empresas", ""),
        )
        async with get_session() as session:
            session.add(ingeniero)
            await session.flush()
            await session.refresh(ingeniero)
            return _ingeniero_to_dict(ingeniero)

    @staticmethod
    async def update(ingeniero_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        """Update engineer fields."""
        allowed_fields = {
            "nombre",
            "email",
            "telefono",
            "codia",
            "id_empresas",
            "foto_perfil_url",
            "foto_carnet_url",
            "foto_certificacion_url",
        }
        async with get_session() as session:
            result = await session.execute(select(Ingeniero).where(Ingeniero.id == ingeniero_id))
            ingeniero = result.scalar_one_or_none()
            if ingeniero is None:
                return None

            for key, value in data.items():
                if key in allowed_fields and value is not None and hasattr(ingeniero, key):
                    setattr(ingeniero, key, value)

            ingeniero.updated_at = func.now()
            await session.flush()
            await session.refresh(ingeniero)
            return _ingeniero_to_dict(ingeniero)

    @staticmethod
    async def delete(ingeniero_id: str) -> bool:
        """Delete engineer by ID. Returns True if deleted."""
        async with get_session() as session:
            result = await session.execute(select(Ingeniero).where(Ingeniero.id == ingeniero_id))
            ingeniero = result.scalar_one_or_none()
            if ingeniero is None:
                return False
            await session.delete(ingeniero)
            return True

    @staticmethod
    async def exists(ingeniero_id: str) -> bool:
        """Check if engineer exists."""
        async with get_session() as session:
            result = await session.execute(
                select(Ingeniero.id).where(Ingeniero.id == ingeniero_id).limit(1)
            )
            return result.scalar_one_or_none() is not None
