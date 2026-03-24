"""TipoCalculo model."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Index, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base


class TipoCalculo(Base):
    """TipoCalculo/CalculationType entity - predefined calculation types."""

    __tablename__ = "tipo_calculos"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    codigo: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(Text, nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # noqa: UP045
    categoria: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # noqa: UP045
    icono: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # noqa: UP045
    color: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # noqa: UP045
    orden: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
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
        "Calculo", back_populates="tipo_calculo", lazy="selectin"
    )

    __table_args__ = (
        Index("idx_tipo_calculos_activo", "activo"),
        Index("idx_tipo_calculos_orden", "orden"),
        Index("idx_tipo_calculos_categoria", "categoria"),
    )
