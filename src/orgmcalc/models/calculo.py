"""Calculo model."""

from datetime import date, datetime
from typing import Any, Optional

from sqlalchemy import (
    JSON,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base import Base


class Calculo(Base):
    """Calculo/Calculation entity - individual calculation per project."""

    __tablename__ = "calculos"

    id: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    project_id: Mapped[str] = mapped_column(
        Text,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    tipo_calculo_id: Mapped[Optional[str]] = mapped_column(  # noqa: UP045
        Text,
        ForeignKey("tipo_calculos.id", ondelete="RESTRICT"),
        nullable=True,
    )
    codigo: Mapped[str] = mapped_column(Text, nullable=False)
    nombre: Mapped[str] = mapped_column(Text, nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # noqa: UP045
    estado: Mapped[str] = mapped_column(Text, nullable=False, default="borrador")
    fecha_creacion: Mapped[date] = mapped_column(
        Date, nullable=False, server_default=func.current_date()
    )
    empresa_id: Mapped[str] = mapped_column(
        Text,
        ForeignKey("empresas.id", ondelete="RESTRICT"),
        nullable=False,
    )
    ingeniero_id: Mapped[str] = mapped_column(
        Text,
        ForeignKey("ingenieros.id", ondelete="RESTRICT"),
        nullable=False,
    )
    parametros: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
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

    project: Mapped["Project"] = relationship("Project", back_populates="calculos")  # noqa: F821  # type: ignore[name-defined]
    tipo_calculo: Mapped[Optional["TipoCalculo"]] = relationship(  # noqa: F821,UP045  # type: ignore[name-defined]
        "TipoCalculo", back_populates="calculos"
    )
    empresa: Mapped["Empresa"] = relationship("Empresa", back_populates="calculos")  # noqa: F821  # type: ignore[name-defined]
    ingeniero: Mapped["Ingeniero"] = relationship("Ingeniero", back_populates="calculos")  # noqa: F821  # type: ignore[name-defined]

    __table_args__ = (
        Index("idx_calculos_project", "project_id"),
        Index("idx_calculos_codigo", "codigo"),
        Index("idx_calculos_empresa", "empresa_id"),
        Index("idx_calculos_ingeniero", "ingeniero_id"),
        Index("idx_calculos_tipo", "tipo_calculo_id"),
        UniqueConstraint("project_id", "codigo", name="uq_calculos_project_codigo"),
        CheckConstraint("empresa_id IS NOT NULL", name="chk_calculo_has_empresa"),
        CheckConstraint("ingeniero_id IS NOT NULL", name="chk_calculo_has_ingeniero"),
    )
