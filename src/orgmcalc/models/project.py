"""Project model."""

from datetime import date, datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import Date, DateTime, ForeignKey, Index, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base


class Project(Base):
    """Project entity - top-level container for calculations."""

    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=lambda: str(uuid4()))
    nombre: Mapped[str] = mapped_column(Text, nullable=False)
    ubicacion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # noqa: UP045
    fecha: Mapped[Optional[date]] = mapped_column(Date, nullable=True)  # noqa: UP045
    estado: Mapped[str] = mapped_column(Text, nullable=False, default="activo")
    cliente_id: Mapped[Optional[str]] = mapped_column(  # noqa: UP045
        Text,
        ForeignKey("clientes.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    calculos: Mapped[list["Calculo"]] = relationship(  # noqa: F821  # type: ignore[name-defined]
        "Calculo", back_populates="project", lazy="selectin"
    )
    documentos: Mapped[list["Documento"]] = relationship(  # noqa: F821  # type: ignore[name-defined]
        "Documento", back_populates="project", lazy="selectin"
    )
    cliente: Mapped[Optional["Cliente"]] = relationship(  # noqa: F821,UP045  # type: ignore[name-defined]
        "Cliente", back_populates="projects", lazy="selectin"
    )

    __table_args__ = (
        Index("idx_projects_nombre", "nombre"),
        Index("idx_projects_cliente_id", "cliente_id"),
    )
