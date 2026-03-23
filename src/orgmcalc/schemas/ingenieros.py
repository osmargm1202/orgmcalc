"""Ingeniero (engineer) schemas with OpenAPI documentation."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class IngenieroCreate(BaseModel):
    """Request body for POST /ingenieros.

    Creates a new engineer with professional information.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nombre": "Ing. María González",
                "email": "maria.gonzalez@email.com",
                "telefono": "+502 5555-9876",
                "profesion": "Ingeniera Civil Estructural",
            }
        }
    )

    nombre: str = Field(
        ..., min_length=1, max_length=255, description="Nombre completo del ingeniero (requerido)"
    )
    email: str | None = Field(
        default=None, max_length=255, description="Correo electrónico profesional"
    )
    telefono: str | None = Field(
        default=None, max_length=50, description="Número de teléfono de contacto"
    )
    profesion: str | None = Field(
        default=None, max_length=255, description="Especialidad o profesión"
    )


class IngenieroUpdate(BaseModel):
    """Request body for PATCH /ingenieros/{id}.

    Updates an existing engineer. Only provided fields are updated.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"telefono": "+502 5555-1111", "profesion": "Ingeniera Civil Senior"}
        }
    )

    nombre: str | None = Field(
        default=None, min_length=1, max_length=255, description="Nombre completo"
    )
    email: str | None = Field(default=None, max_length=255, description="Correo electrónico")
    telefono: str | None = Field(default=None, max_length=50, description="Teléfono de contacto")
    profesion: str | None = Field(
        default=None, max_length=255, description="Especialidad o profesión"
    )


class IngenieroResponse(BaseModel):
    """Response for GET /ingenieros/{id}.

    Includes engineer details and file availability status.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "nombre": "Ing. María González",
                "email": "maria.gonzalez@email.com",
                "telefono": "+502 5555-9876",
                "profesion": "Ingeniera Civil Estructural",
                "created_at": "2024-01-05T08:00:00",
                "updated_at": "2024-03-10T15:20:00",
                "perfil_available": True,
                "carnet_available": True,
                "certificacion_available": False,
            }
        }
    )

    id: int = Field(..., description="Identificador único del ingeniero")
    nombre: str = Field(..., description="Nombre completo")
    email: str | None = Field(None, description="Correo electrónico")
    telefono: str | None = Field(None, description="Teléfono de contacto")
    profesion: str | None = Field(None, description="Especialidad o profesión")
    created_at: str = Field(..., description="Fecha de creación")
    updated_at: str = Field(..., description="Última actualización")
    perfil_available: bool = Field(
        default=False, description="Indica si tiene foto de perfil disponible"
    )
    carnet_available: bool = Field(
        default=False, description="Indica si tiene carnet/ID disponible"
    )
    certificacion_available: bool = Field(
        default=False, description="Indica si tiene certificación disponible"
    )


class IngenieroListItem(BaseModel):
    """Item in list of engineers.

    Lightweight representation for list views.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "nombre": "Ing. María González",
                "email": "maria.gonzalez@email.com",
                "profesion": "Ingeniera Civil",
                "perfil_available": True,
                "carnet_available": False,
                "certificacion_available": False,
            }
        }
    )

    id: int = Field(..., description="Identificador único")
    nombre: str = Field(..., description="Nombre completo")
    email: str | None = Field(None, description="Correo electrónico")
    profesion: str | None = Field(None, description="Especialidad")
    perfil_available: bool = Field(default=False, description="Foto de perfil disponible")
    carnet_available: bool = Field(default=False, description="Carnet disponible")
    certificacion_available: bool = Field(default=False, description="Certificación disponible")


class IngenieroFilter(BaseModel):
    """Filter parameters for listing engineers."""

    model_config = ConfigDict(json_schema_extra={"example": {"empresa_id": 1}})

    empresa_id: int | None = Field(default=None, description="Filtrar por ID de empresa asociada")
