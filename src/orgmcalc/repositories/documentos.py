"""Documentos repository - CRUD for project documents."""

from __future__ import annotations

from typing import Any

from sqlalchemy import func, select

from orgmcalc.db.session import get_session
from orgmcalc.models import Documento


def _documento_to_dict(documento: Documento) -> dict[str, Any]:
    """Convert Documento model to dict with formatted timestamps."""
    return {
        c.name: (
            getattr(documento, c.name).isoformat()
            if hasattr(getattr(documento, c.name), "isoformat")
            else getattr(documento, c.name)
        )
        for c in documento.__table__.columns
    }


class DocumentosRepository:
    """Repository for project documents."""

    @staticmethod
    async def list_by_project(
        project_id: str, offset: int = 0, limit: int = 100
    ) -> list[dict[str, Any]]:
        """List documents for a project."""
        async with get_session() as session:
            result = await session.execute(
                select(Documento)
                .where(Documento.project_id == project_id)
                .order_by(Documento.created_at.desc())
                .offset(offset)
                .limit(limit)
            )
            documentos = result.scalars().all()
            return [_documento_to_dict(d) for d in documentos]

    @staticmethod
    async def count_by_project(project_id: str) -> int:
        """Count documents for a project."""
        async with get_session() as session:
            result = await session.execute(
                select(func.count())
                .select_from(Documento)
                .where(Documento.project_id == project_id)
            )
            return result.scalar_one()

    @staticmethod
    async def get_by_id(document_id: str) -> dict[str, Any] | None:
        """Get document by ID."""
        async with get_session() as session:
            result = await session.execute(select(Documento).where(Documento.id == document_id))
            documento = result.scalar_one_or_none()
            if documento is None:
                return None
            return _documento_to_dict(documento)

    @staticmethod
    async def create(data: dict[str, Any]) -> dict[str, Any]:
        """Create a new document."""
        documento = Documento(
            project_id=data["project_id"],
            nombre_documento=data["nombre_documento"],
            descripcion=data.get("descripcion"),
        )
        async with get_session() as session:
            session.add(documento)
            await session.flush()
            await session.refresh(documento)
            return _documento_to_dict(documento)

    @staticmethod
    async def update(document_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        """Update document fields."""
        async with get_session() as session:
            result = await session.execute(select(Documento).where(Documento.id == document_id))
            documento = result.scalar_one_or_none()
            if documento is None:
                return None

            for key in ["nombre_documento", "descripcion"]:
                if key in data and data[key] is not None:
                    setattr(documento, key, data[key])

            documento.updated_at = func.now()
            await session.flush()
            await session.refresh(documento)
            return _documento_to_dict(documento)

    @staticmethod
    async def delete(document_id: str) -> bool:
        """Delete document by ID. Returns True if deleted."""
        async with get_session() as session:
            result = await session.execute(select(Documento).where(Documento.id == document_id))
            documento = result.scalar_one_or_none()
            if documento is None:
                return False
            await session.delete(documento)
            return True

    @staticmethod
    async def exists(document_id: str) -> bool:
        """Check if document exists."""
        async with get_session() as session:
            result = await session.execute(
                select(Documento.id).where(Documento.id == document_id).limit(1)
            )
            return result.scalar_one_or_none() is not None
