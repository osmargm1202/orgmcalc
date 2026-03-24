"""Ingeniero model."""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Index, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base


class Ingeniero(Base):
    """Ingeniero/Engineer entity - global registry of engineers."""

    __tablename__ = "ingenieros"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    nombre: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # noqa: UP045
    telefono: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # noqa: UP045
    codia: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # noqa: UP045
    id_empresas: Mapped[str] = mapped_column(Text, nullable=False, default="")
    foto_perfil_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # noqa: UP045
    foto_carnet_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # noqa: UP045
    foto_certificacion_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # noqa: UP045
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
        "Calculo", back_populates="ingeniero", lazy="selectin"
    )

    __table_args__ = (
        Index("idx_ingenieros_nombre", "nombre"),
        Index("idx_ingenieros_email", "email"),
        Index("idx_ingenieros_empresas", "id_empresas"),
    )
