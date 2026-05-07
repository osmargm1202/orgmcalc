"""Cliente model."""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Index, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base


class Cliente(Base):
    """Cliente entity for project-level client assignment.

    A cliente can reference a known empresa, fallback manual data,
    or both at the same time.
    """

    __tablename__ = "clientes"

    id: Mapped[str] = mapped_column(Text, primary_key=True, default=lambda: str(uuid4()))
    empresa_id: Mapped[Optional[str]] = mapped_column(  # noqa: UP045
        Text,
        ForeignKey("empresas.id", ondelete="RESTRICT"),
        nullable=True,
    )
    nombre: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # noqa: UP045
    ubicacion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # noqa: UP045
    telefono: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # noqa: UP045
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

    empresa: Mapped[Optional["Empresa"]] = relationship(  # noqa: F821,UP045  # type: ignore[name-defined]
        "Empresa",
        back_populates="clientes",
        lazy="selectin",
    )
    projects: Mapped[list["Project"]] = relationship(  # noqa: F821  # type: ignore[name-defined]
        "Project",
        back_populates="cliente",
        lazy="selectin",
    )

    __table_args__ = (
        Index("idx_clientes_empresa", "empresa_id"),
        Index("idx_clientes_nombre", "nombre"),
    )
