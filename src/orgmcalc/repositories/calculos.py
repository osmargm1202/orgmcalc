"""Calculos repository - CRUD operations with empresa and ingeniero assignments."""

from __future__ import annotations

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from orgmcalc.db.session import get_session
from orgmcalc.models import Calculo


def _calculo_to_dict(calculo: Calculo, include_relations: bool = True) -> dict[str, Any]:
    """Convert Calculo model to dict with formatted timestamps."""
    result = {}
    for c in calculo.__table__.columns:
        val = getattr(calculo, c.name)
        if hasattr(val, "isoformat"):
            result[c.name] = val.isoformat()
        else:
            result[c.name] = val

    if include_relations:
        if calculo.empresa is not None:
            result["empresa_nombre"] = calculo.empresa.nombre
        if calculo.ingeniero is not None:
            result["ingeniero_nombre"] = calculo.ingeniero.nombre
            result["ingeniero_profesion"] = getattr(calculo.ingeniero, "profesion", None)
    return result


class CalculosRepository:
    """Repository for calculos table operations.

    Each calculation has ONE empresa and ONE ingeniero directly assigned.
    """

    @staticmethod
    async def list_by_project(
        project_id: str, offset: int = 0, limit: int = 100
    ) -> list[dict[str, Any]]:
        """List calculations for a project with empresa and ingeniero info."""
        async with get_session() as session:
            result = await session.execute(
                select(Calculo)
                .options(selectinload(Calculo.empresa), selectinload(Calculo.ingeniero))
                .where(Calculo.project_id == project_id)
                .order_by(Calculo.fecha_creacion.desc(), Calculo.id.desc())
                .offset(offset)
                .limit(limit)
            )
            calculos = result.scalars().all()
            return [_calculo_to_dict(c) for c in calculos]

    @staticmethod
    async def count_by_project(project_id: str) -> int:
        """Count calculations for a project."""
        async with get_session() as session:
            result = await session.execute(
                select(func.count()).select_from(Calculo).where(Calculo.project_id == project_id)
            )
            return result.scalar_one()

    @staticmethod
    async def get_by_id(calculo_id: str) -> dict[str, Any] | None:
        """Get calculation by ID with empresa and ingeniero details."""
        async with get_session() as session:
            result = await session.execute(
                select(Calculo)
                .options(selectinload(Calculo.empresa), selectinload(Calculo.ingeniero))
                .where(Calculo.id == calculo_id)
            )
            calculo = result.scalar_one_or_none()
            if calculo is None:
                return None
            return _calculo_to_dict(calculo)

    @staticmethod
    async def create(data: dict[str, Any]) -> dict[str, Any]:
        """Create a new calculation with empresa and ingeniero."""
        calculo = Calculo(
            project_id=data["project_id"],
            tipo_calculo_id=data.get("tipo_calculo_id"),
            codigo=data["codigo"],
            nombre=data["nombre"],
            descripcion=data.get("descripcion"),
            estado=data.get("estado", "borrador"),
            empresa_id=data["empresa_id"],
            ingeniero_id=data["ingeniero_id"],
            parametros=data.get("parametros", {}),
        )
        async with get_session() as session:
            session.add(calculo)
            await session.flush()
            await session.refresh(calculo)
            result = await session.execute(
                select(Calculo)
                .options(selectinload(Calculo.empresa), selectinload(Calculo.ingeniero))
                .where(Calculo.id == calculo.id)
            )
            calculo = result.scalar_one()
            return _calculo_to_dict(calculo)

    @staticmethod
    async def update(calculo_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        """Update calculation fields including empresa and ingeniero."""
        allowed_fields = [
            "codigo",
            "nombre",
            "descripcion",
            "estado",
            "empresa_id",
            "ingeniero_id",
            "tipo_calculo_id",
        ]
        async with get_session() as session:
            result = await session.execute(
                select(Calculo)
                .options(selectinload(Calculo.empresa), selectinload(Calculo.ingeniero))
                .where(Calculo.id == calculo_id)
            )
            calculo = result.scalar_one_or_none()
            if calculo is None:
                return None

            for key in allowed_fields:
                if key in data and data[key] is not None:
                    setattr(calculo, key, data[key])

            calculo.updated_at = func.now()
            await session.flush()
            await session.refresh(calculo)
            result = await session.execute(
                select(Calculo)
                .options(selectinload(Calculo.empresa), selectinload(Calculo.ingeniero))
                .where(Calculo.id == calculo_id)
            )
            calculo = result.scalar_one()
            return _calculo_to_dict(calculo)

    @staticmethod
    async def delete(calculo_id: str) -> bool:
        """Delete calculation by ID. Returns True if deleted."""
        async with get_session() as session:
            result = await session.execute(select(Calculo).where(Calculo.id == calculo_id))
            calculo = result.scalar_one_or_none()
            if calculo is None:
                return False
            await session.delete(calculo)
            return True

    @staticmethod
    async def exists(calculo_id: str) -> bool:
        """Check if calculation exists."""
        async with get_session() as session:
            result = await session.execute(
                select(Calculo.id).where(Calculo.id == calculo_id).limit(1)
            )
            return result.scalar_one_or_none() is not None

    @staticmethod
    async def get_by_codigo_and_project(project_id: str, codigo: str) -> dict[str, Any] | None:
        """Get calculation by project ID and codigo (for uniqueness check)."""
        async with get_session() as session:
            result = await session.execute(
                select(Calculo.id).where(Calculo.project_id == project_id, Calculo.codigo == codigo)
            )
            calc_id = result.scalar_one_or_none()
            if calc_id is None:
                return None
            return {"id": calc_id}
