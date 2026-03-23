"""Project schemas with OpenAPI documentation."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    """Request body for POST /proyectos.

    Creates a new project with basic information.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nombre": "Edificio Centro Comercial",
                "ubicacion": "Ciudad de Guatemala, Zona 10",
                "fecha": "2024-03-15",
                "estado": "activo",
                "id_empresa": 1,
                "id_ingeniero": 2,
            }
        }
    )

    nombre: str = Field(
        ..., min_length=1, max_length=255, description="Nombre del proyecto (requerido)"
    )
    ubicacion: str | None = Field(
        default=None, max_length=500, description="Ubicación física del proyecto"
    )
    fecha: date | None = Field(default=None, description="Fecha del proyecto (formato: YYYY-MM-DD)")
    estado: str = Field(
        default="activo",
        max_length=50,
        description="Estado del proyecto: activo, completado, suspendido, etc.",
    )
    id_empresa: int | None = Field(
        default=None, description="Compatibilidad: ID de la empresa asociada al proyecto"
    )
    id_ingeniero: int | None = Field(
        default=None, description="Compatibilidad: ID del ingeniero asociado al proyecto"
    )


class ProjectUpdate(BaseModel):
    """Request body for PATCH /proyectos/{id}.

    Updates an existing project. Only provided fields are updated.
    """

    model_config = ConfigDict(
        json_schema_extra={"example": {"estado": "completado", "ubicacion": "Antigua Guatemala"}}
    )

    nombre: str | None = Field(
        default=None, min_length=1, max_length=255, description="Nombre del proyecto"
    )
    ubicacion: str | None = Field(
        default=None, max_length=500, description="Ubicación física del proyecto"
    )
    fecha: date | None = Field(default=None, description="Fecha del proyecto (formato: YYYY-MM-DD)")
    estado: str | None = Field(default=None, max_length=50, description="Estado del proyecto")
    id_empresa: int | None = Field(
        default=None, description="ID de la empresa asociada (null para desasociar)"
    )
    id_ingeniero: int | None = Field(
        default=None, description="ID del ingeniero asociado (null para desasociar)"
    )


class ProjectResponse(BaseModel):
    """Response for GET /proyectos/{id}.

    Includes project details and logo availability status.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "nombre": "Edificio Centro Comercial",
                "ubicacion": "Ciudad de Guatemala, Zona 10",
                "fecha": "2024-03-15",
                "estado": "activo",
                "id_empresa": 1,
                "id_ingeniero": 2,
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-03-20T14:45:00",
                "logo_available": True,
            }
        }
    )

    id: int = Field(..., description="Identificador único del proyecto")
    nombre: str = Field(..., description="Nombre del proyecto")
    ubicacion: str | None = Field(None, description="Ubicación física")
    fecha: date | None = Field(None, description="Fecha del proyecto")
    estado: str = Field(..., description="Estado actual del proyecto")
    id_empresa: int | None = Field(None, description="ID de empresa asociada")
    id_ingeniero: int | None = Field(None, description="ID de ingeniero asociado")
    created_at: str = Field(..., description="Fecha de creación (ISO 8601)")
    updated_at: str = Field(..., description="Última fecha de actualización")
    logo_available: bool = Field(
        default=False, description="Indica si el proyecto tiene un logo disponible"
    )


class ProjectListItem(BaseModel):
    """Item in list of projects.

    Lightweight representation for list views.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "nombre": "Edificio Centro Comercial",
                "ubicacion": "Ciudad de Guatemala",
                "estado": "activo",
                "created_at": "2024-01-15T10:30:00",
                "logo_available": False,
            }
        }
    )

    id: int = Field(..., description="Identificador único")
    nombre: str = Field(..., description="Nombre del proyecto")
    ubicacion: str | None = Field(None, description="Ubicación física")
    estado: str = Field(..., description="Estado del proyecto")
    created_at: str = Field(..., description="Fecha de creación")
    logo_available: bool = Field(default=False, description="Indica si tiene logo disponible")
