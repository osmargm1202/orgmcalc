"""Project schemas with OpenAPI documentation."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    """Request body for POST /proyectos.

    Creates a new project with basic information.
    Note: Projects don't have empresa/ingeniero directly.
    Each calculation within the project has its own empresa and ingeniero.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nombre": "Edificio Centro Comercial",
                "ubicacion": "Ciudad de Guatemala, Zona 10",
                "fecha": "2024-03-15",
                "estado": "activo",
            }
        }
    )

    nombre: str = Field(
        ..., min_length=1, max_length=255, description="Nombre del proyecto (requerido)"
    )
    cliente: str | None = Field(
        default=None,
        max_length=255,
        description="Nombre del cliente asociado al proyecto",
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
    cliente: str | None = Field(
        default=None,
        max_length=255,
        description="Nombre del cliente asociado al proyecto",
    )
    ubicacion: str | None = Field(
        default=None, max_length=500, description="Ubicación física del proyecto"
    )
    fecha: date | None = Field(default=None, description="Fecha del proyecto (formato: YYYY-MM-DD)")
    estado: str | None = Field(default=None, max_length=50, description="Estado del proyecto")


class ProjectResponse(BaseModel):
    """Response for GET /proyectos/{id}.

    Includes project details and logo availability status.
    Note: empresa/ingeniero are assigned per calculation, not per project.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "proj-uuid",
                "nombre": "Edificio Centro Comercial",
                "ubicacion": "Ciudad de Guatemala, Zona 10",
                "fecha": "2024-03-15",
                "estado": "activo",
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-03-20T14:45:00",
                "logo_available": True,
            }
        }
    )

    id: str = Field(..., description="Identificador único del proyecto")
    nombre: str = Field(..., description="Nombre del proyecto")
    cliente: str | None = Field(default=None, description="Nombre del cliente asociado al proyecto")
    ubicacion: str | None = Field(default=None, description="Ubicación física")
    fecha: date | None = Field(default=None, description="Fecha del proyecto")
    estado: str = Field(..., description="Estado actual del proyecto")
    created_at: str = Field(..., description="Fecha de creación (ISO 8601)")
    updated_at: str = Field(..., description="Última fecha de actualización")
    logo_available: bool = Field(
        default=False, description="Indica si el proyecto tiene un logo disponible"
    )
    cliente_logo_available: bool = Field(
        default=False,
        description="Indica si el proyecto tiene un logo del cliente disponible",
    )
