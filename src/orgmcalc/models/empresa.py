"""Empresa model."""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Index, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base


class Empresa(Base):
    """Empresa/Company entity - global registry of companies."""

    __tablename__ = "empresas"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    nombre: Mapped[str] = mapped_column(Text, nullable=False)
    logo_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # noqa: UP045
    url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # noqa: UP045
    contacto: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # noqa: UP045
    telefono: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # noqa: UP045
    correo: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # noqa: UP045
    direccion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # noqa: UP045
    ciudad: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # noqa: UP045
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
        "Calculo", back_populates="empresa", lazy="selectin"
    )

    __table_args__ = (Index("idx_empresas_nombre", "nombre"),)
