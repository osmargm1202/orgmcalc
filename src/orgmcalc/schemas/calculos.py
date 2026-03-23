"""Calculo (calculation) schemas with OpenAPI documentation."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class TipoCalculoResponse(BaseModel):
    """Response for GET /tipo-calculos.

    Predefined calculation types.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "abc-123",
                "codigo": "BT",
                "nombre": "Cálculo de Baja Tensión",
                "descripcion": "Cálculo de instalaciones eléctricas de baja tensión",
                "categoria": "electricidad",
                "icono": "⚡",
                "color": "#FFD700",
                "orden": 1,
                "activo": True,
            }
        }
    )

    id: str = Field(..., description="Identificador único del tipo de cálculo")
    codigo: str = Field(..., description="Código corto del tipo (ej: BT, SPT, AC)")
    nombre: str = Field(..., description="Nombre descriptivo del tipo de cálculo")
    descripcion: str | None = Field(None, description="Descripción detallada")
    categoria: str | None = Field(
        None, description="Categoría (electricidad, mecanica, climatizacion)"
    )
    icono: str | None = Field(None, description="Emoji o icono para UI")
    color: str | None = Field(None, description="Color en formato hex para UI")
    orden: int = Field(..., description="Orden de aparición")
    activo: bool = Field(..., description="Si el tipo está activo")


class CalculoCreate(BaseModel):
    """Request body for POST /proyectos/{id}/calculos.

    Creates a new calculation within a project.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "codigo": "CALC-2024-001",
                "nombre": "Análisis de Cimentación Profunda",
                "descripcion": "Cálculo de pilotes y zapatas para edificio de 10 niveles",
                "estado": "borrador",
                "tipo_calculo_id": "tipo-bt-uuid",
            }
        }
    )

    codigo: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Código único de identificación del cálculo (requerido)",
    )
    nombre: str = Field(
        ..., min_length=1, max_length=255, description="Nombre descriptivo del cálculo (requerido)"
    )
    descripcion: str | None = Field(
        default=None, max_length=2000, description="Descripción detallada del cálculo"
    )
    estado: str = Field(
        default="borrador",
        max_length=50,
        description="Estado del cálculo: borrador, en_revision, aprobado, rechazado, etc.",
    )
    tipo_calculo_id: str = Field(
        ...,
        description="ID del tipo de cálculo predefinido (requerido - usar /tipo-calculos para ver opciones)",
    )


class CalculoUpdate(BaseModel):
    """Request body for PATCH /proyectos/{id}/calculos/{calculo_id}.

    Updates an existing calculation. Only provided fields are updated.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "estado": "en_revision",
                "descripcion": "Cálculo actualizado con nuevos parámetros",
            }
        }
    )

    codigo: str | None = Field(
        default=None, min_length=1, max_length=100, description="Código del cálculo"
    )
    nombre: str | None = Field(
        default=None, min_length=1, max_length=255, description="Nombre del cálculo"
    )
    descripcion: str | None = Field(
        default=None, max_length=2000, description="Descripción del cálculo"
    )
    estado: str | None = Field(default=None, max_length=50, description="Estado del cálculo")


class CalculoResponse(BaseModel):
    """Response for GET /proyectos/{id}/calculos/{calculo_id}.

    Full calculation details with timestamps.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "calc-uuid",
                "project_id": "proj-uuid",
                "tipo_calculo_id": "tipo-bt-uuid",
                "codigo": "CALC-2024-001",
                "nombre": "Análisis de Cimentación Profunda",
                "descripcion": "Cálculo de pilotes y zapatas",
                "estado": "borrador",
                "fecha_creacion": "2024-03-15",
                "created_at": "2024-03-15T09:00:00",
                "updated_at": "2024-03-20T16:45:00",
            }
        }
    )

    id: str = Field(..., description="Identificador único del cálculo")
    project_id: str = Field(..., description="ID del proyecto al que pertenece")
    tipo_calculo_id: str | None = Field(None, description="ID del tipo de cálculo")
    codigo: str = Field(..., description="Código de identificación")
    nombre: str = Field(..., description="Nombre del cálculo")
    descripcion: str | None = Field(None, description="Descripción detallada")
    estado: str = Field(..., description="Estado actual del cálculo")
    fecha_creacion: date = Field(..., description="Fecha de creación del cálculo")
    created_at: str = Field(..., description="Fecha de creación del registro")
    updated_at: str = Field(..., description="Última actualización")


class CalculoListItem(BaseModel):
    """Item in list of calculations.

    Lightweight representation for list views.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "calc-uuid",
                "codigo": "CALC-2024-001",
                "nombre": "Análisis de Cimentación Profunda",
                "estado": "borrador",
                "fecha_creacion": "2024-03-15",
            }
        }
    )

    id: str = Field(..., description="Identificador único")
    codigo: str = Field(..., description="Código del cálculo")
    nombre: str = Field(..., description="Nombre del cálculo")
    estado: str = Field(..., description="Estado actual")
    fecha_creacion: date = Field(..., description="Fecha de creación")


class CalculoEmpresaLink(BaseModel):
    """Link between calculation and company.

    Represents the association of a company with a calculation,
    including role and ordering information.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "link-uuid",
                "calculo_id": "calc-uuid",
                "empresa_id": "emp-uuid",
                "empresa_nombre": "Constructora ABC S.A.",
                "rol": "Constructora Principal",
                "orden": 1,
                "created_at": "2024-03-16T10:00:00",
            }
        }
    )

    id: str = Field(..., description="Identificador único del vínculo")
    calculo_id: str = Field(..., description="ID del cálculo")
    empresa_id: str = Field(..., description="ID de la empresa")
    empresa_nombre: str = Field(..., description="Nombre de la empresa")
    rol: str | None = Field(None, description="Rol de la empresa en el cálculo")
    orden: int = Field(..., description="Orden de aparición (para ordenamiento)")
    created_at: str = Field(..., description="Fecha de creación del vínculo")


class CalculoEmpresaLinkCreate(BaseModel):
    """Request to link company to calculation.

    Establishes an association between a calculation and a company.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"empresa_id": "emp-uuid", "rol": "Constructora Principal", "orden": 1}
        }
    )

    empresa_id: str = Field(..., description="ID de la empresa a vincular (requerido)")
    rol: str | None = Field(
        default=None, max_length=255, description="Rol o función de la empresa en este cálculo"
    )
    orden: int = Field(
        default=0, ge=0, description="Orden de aparición (0 = primero, incrementa según necesidad)"
    )


class CalculoEmpresaLinkUpdate(BaseModel):
    """Request to update link.

    Modifies an existing company-calculation association.
    """

    model_config = ConfigDict(
        json_schema_extra={"example": {"rol": "Constructora Subcontratada", "orden": 2}}
    )

    rol: str | None = Field(default=None, max_length=255, description="Nuevo rol de la empresa")
    orden: int | None = Field(default=None, ge=0, description="Nuevo orden de aparición")


class CalculoIngenieroLink(BaseModel):
    """Link between calculation and engineer.

    Represents the association of an engineer with a calculation,
    including role and ordering information.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "link-uuid",
                "calculo_id": "calc-uuid",
                "ingeniero_id": "ing-uuid",
                "ingeniero_nombre": "Ing. María González",
                "rol": "Ingeniero Calculista",
                "orden": 1,
                "created_at": "2024-03-16T10:00:00",
            }
        }
    )

    id: str = Field(..., description="Identificador único del vínculo")
    calculo_id: str = Field(..., description="ID del cálculo")
    ingeniero_id: str = Field(..., description="ID del ingeniero")
    ingeniero_nombre: str = Field(..., description="Nombre del ingeniero")
    rol: str | None = Field(None, description="Rol del ingeniero en el cálculo")
    orden: int = Field(..., description="Orden de aparición (para ordenamiento)")
    created_at: str = Field(..., description="Fecha de creación del vínculo")


class CalculoIngenieroLinkCreate(BaseModel):
    """Request to link engineer to calculation.

    Establishes an association between a calculation and an engineer.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"ingeniero_id": "ing-uuid", "rol": "Ingeniero Calculista", "orden": 1}
        }
    )

    ingeniero_id: str = Field(..., description="ID del ingeniero a vincular (requerido)")
    rol: str | None = Field(
        default=None, max_length=255, description="Rol o función del ingeniero en este cálculo"
    )
    orden: int = Field(
        default=0, ge=0, description="Orden de aparición (0 = primero, incrementa según necesidad)"
    )


class CalculoIngenieroLinkUpdate(BaseModel):
    """Request to update link.

    Modifies an existing engineer-calculation association.
    """

    model_config = ConfigDict(
        json_schema_extra={"example": {"rol": "Ingeniero Revisor", "orden": 2}}
    )

    rol: str | None = Field(default=None, max_length=255, description="Nuevo rol del ingeniero")
    orden: int | None = Field(default=None, ge=0, description="Nuevo orden de aparición")
