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
    Each calculation is assigned to ONE empresa and ONE ingeniero.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "codigo": "CALC-2024-001",
                "nombre": "Cálculo Baja Tensión Edificio A",
                "descripcion": "Cálculo de instalación eléctrica para edificio de oficinas",
                "estado": "borrador",
                "tipo_calculo_id": "tipo-bt-uuid",
                "empresa_id": "empresa-uuid",
                "ingeniero_id": "ingeniero-uuid",
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
        description="Estado del cálculo: borrador, en_progreso, completado, etc.",
    )
    tipo_calculo_id: str = Field(
        ...,
        description="ID del tipo de cálculo predefinido (requerido - usar /tipo-calculos para ver opciones)",
    )
    empresa_id: str = Field(
        ...,
        description="ID de la empresa que realiza el cálculo (requerido)",
    )
    ingeniero_id: str = Field(
        ...,
        description="ID del ingeniero responsable del cálculo (requerido)",
    )


class CalculoUpdate(BaseModel):
    """Request body for PATCH /proyectos/{id}/calculos/{calculo_id}.

    Updates an existing calculation. Only provided fields are updated.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "estado": "en_progreso",
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
    empresa_id: str | None = Field(
        default=None, description="ID de la empresa (para reasignar el cálculo)"
    )
    ingeniero_id: str | None = Field(
        default=None, description="ID del ingeniero (para reasignar el cálculo)"
    )


class EmpresaInfo(BaseModel):
    """Minimal empresa info for nested display."""

    id: str = Field(..., description="ID de la empresa")
    nombre: str = Field(..., description="Nombre de la empresa")


class IngenieroInfo(BaseModel):
    """Minimal ingeniero info for nested display."""

    id: str = Field(..., description="ID del ingeniero")
    nombre: str = Field(..., description="Nombre del ingeniero")
    profesion: str | None = Field(None, description="Profesión o CODIA")


class CalculoResponse(BaseModel):
    """Response for GET /proyectos/{id}/calculos/{calculo_id}.

    Full calculation details with empresa and ingeniero info.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "calc-uuid",
                "project_id": "proj-uuid",
                "tipo_calculo_id": "tipo-bt-uuid",
                "codigo": "CALC-2024-001",
                "nombre": "Cálculo Baja Tensión Edificio A",
                "descripcion": "Cálculo de instalación eléctrica",
                "estado": "borrador",
                "empresa": {"id": "emp-uuid", "nombre": "ORGM"},
                "ingeniero": {
                    "id": "ing-uuid",
                    "nombre": "Osmar Garcia",
                    "profesion": "CODIA: 36467",
                },
                "fecha_creacion": "2024-03-15",
                "created_at": "2024-03-15T09:00:00",
                "updated_at": "2024-03-20T16:45:00",
            }
        }
    )

    id: str = Field(..., description="Identificador único del cálculo")
    project_id: str = Field(..., description="ID del proyecto al que pertenece")
    tipo_calculo_id: str = Field(..., description="ID del tipo de cálculo")
    codigo: str = Field(..., description="Código de identificación")
    nombre: str = Field(..., description="Nombre del cálculo")
    descripcion: str | None = Field(None, description="Descripción detallada")
    estado: str = Field(..., description="Estado actual del cálculo")
    empresa: EmpresaInfo = Field(..., description="Empresa asignada al cálculo")
    ingeniero: IngenieroInfo = Field(..., description="Ingeniero responsable del cálculo")
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
                "nombre": "Cálculo Baja Tensión Edificio A",
                "estado": "borrador",
                "empresa_nombre": "ORGM",
                "ingeniero_nombre": "Osmar Garcia",
                "fecha_creacion": "2024-03-15",
            }
        }
    )

    id: str = Field(..., description="Identificador único")
    codigo: str = Field(..., description="Código del cálculo")
    nombre: str = Field(..., description="Nombre del cálculo")
    estado: str = Field(..., description="Estado actual")
    empresa_nombre: str = Field(..., description="Nombre de la empresa")
    ingeniero_nombre: str = Field(..., description="Nombre del ingeniero")
    fecha_creacion: date = Field(..., description="Fecha de creación")
