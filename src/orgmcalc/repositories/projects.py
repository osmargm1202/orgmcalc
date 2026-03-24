"""Projects repository - CRUD operations."""

from __future__ import annotations

from typing import Any

from sqlalchemy import func, select

from orgmcalc.db.session import get_session
from orgmcalc.models import Project


def _project_to_dict(project: Project) -> dict[str, Any]:
    """Convert Project model to dict with formatted timestamps."""
    return {
        c.name: (
            getattr(project, c.name).isoformat()
            if hasattr(getattr(project, c.name), "isoformat")
            else getattr(project, c.name)
        )
        for c in project.__table__.columns
    }


class ProjectsRepository:
    """Repository for projects table operations."""

    @staticmethod
    async def list_all(offset: int = 0, limit: int = 100) -> list[dict[str, Any]]:
        """List all projects with pagination."""
        async with get_session() as session:
            result = await session.execute(
                select(Project).order_by(Project.created_at.desc()).offset(offset).limit(limit)
            )
            projects = result.scalars().all()
            return [_project_to_dict(p) for p in projects]

    @staticmethod
    async def count_all() -> int:
        """Count total projects."""
        async with get_session() as session:
            result = await session.execute(select(func.count()).select_from(Project))
            return result.scalar_one()

    @staticmethod
    async def get_by_id(project_id: str) -> dict[str, Any] | None:
        """Get project by ID."""
        async with get_session() as session:
            result = await session.execute(select(Project).where(Project.id == project_id))
            project = result.scalar_one_or_none()
            if project is None:
                return None
            return _project_to_dict(project)

    @staticmethod
    async def create(data: dict[str, Any]) -> dict[str, Any]:
        """Create a new project."""
        project = Project(
            nombre=data["nombre"],
            ubicacion=data.get("ubicacion"),
            fecha=data.get("fecha"),
            estado=data.get("estado", "activo"),
            cliente=data.get("cliente"),
        )
        async with get_session() as session:
            session.add(project)
            await session.flush()
            await session.refresh(project)
            return _project_to_dict(project)

    @staticmethod
    async def update(project_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        """Update project fields."""
        async with get_session() as session:
            result = await session.execute(select(Project).where(Project.id == project_id))
            project = result.scalar_one_or_none()
            if project is None:
                return None

            for key, value in data.items():
                if value is not None and hasattr(project, key):
                    setattr(project, key, value)

            project.updated_at = func.now()
            await session.flush()
            await session.refresh(project)
            return _project_to_dict(project)

    @staticmethod
    async def delete(project_id: str) -> bool:
        """Delete project by ID. Returns True if deleted."""
        async with get_session() as session:
            result = await session.execute(select(Project).where(Project.id == project_id))
            project = result.scalar_one_or_none()
            if project is None:
                return False
            await session.delete(project)
            return True

    @staticmethod
    async def exists(project_id: str) -> bool:
        """Check if project exists."""
        async with get_session() as session:
            result = await session.execute(
                select(Project.id).where(Project.id == project_id).limit(1)
            )
            return result.scalar_one_or_none() is not None
