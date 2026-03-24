"""Empresa (company) schemas with OpenAPI documentation."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class EmpresaCreate(BaseModel):
    """Request body for POST /empresas.

    Creates a new company with contact information.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nombre": "Constructora ABC S.A.",
                "url": "https://www.abc.com",
                "contacto": "Juan Pérez",
                "telefono": "+502 5555-1234",
                "correo": "contacto@abc.com",
                "direccion": "12 Calle 5-45, Zona 10",
                "ciudad": "Ciudad de Guatemala",
            }
        }
    )

    nombre: str = Field(
        ..., min_length=1, max_length=255, description="Nombre de la empresa (requerido)"
    )
    url: str | None = Field(
        default=None, max_length=500, description="URL del sitio web de la empresa"
    )
    contacto: str | None = Field(
        default=None, max_length=255, description="Nombre de la persona de contacto"
    )
    telefono: str | None = Field(
        default=None, max_length=50, description="Número de teléfono de contacto"
    )
    correo: str | None = Field(
        default=None, max_length=255, description="Correo electrónico de contacto"
    )
    direccion: str | None = Field(
        default=None, max_length=500, description="Dirección física de la empresa"
    )
    ciudad: str | None = Field(
        default=None, max_length=100, description="Ciudad donde se ubica la empresa"
    )


class EmpresaUpdate(BaseModel):
    """Request body for PATCH /empresas/{id}.

    Updates an existing company. Only provided fields are updated.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"url": "https://nuevo-sitio.com", "telefono": "+502 5555-5678"}
        }
    )

    nombre: str | None = Field(
        default=None, min_length=1, max_length=255, description="Nombre de la empresa"
    )
    url: str | None = Field(default=None, max_length=500, description="URL del sitio web")
    contacto: str | None = Field(
        default=None, max_length=255, description="Nombre de la persona de contacto"
    )
    telefono: str | None = Field(default=None, max_length=50, description="Número de teléfono")
    correo: str | None = Field(default=None, max_length=255, description="Correo electrónico")
    direccion: str | None = Field(default=None, max_length=500, description="Dirección física")
    ciudad: str | None = Field(default=None, max_length=100, description="Ciudad")


class EmpresaResponse(BaseModel):
    """Response for GET /empresas/{id}.

    Includes company details and logo availability status.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "emp-uuid",
                "nombre": "Constructora ABC S.A.",
                "url": "https://www.abc.com",
                "contacto": "Juan Pérez",
                "telefono": "+502 5555-1234",
                "correo": "contacto@abc.com",
                "direccion": "12 Calle 5-45, Zona 10",
                "ciudad": "Ciudad de Guatemala",
                "created_at": "2024-01-10T09:00:00",
                "updated_at": "2024-03-15T16:30:00",
                "logo_available": True,
            }
        }
    )

    id: str = Field(..., description="Identificador único de la empresa")
    nombre: str = Field(..., description="Nombre de la empresa")
    url: str | None = Field(None, description="URL del sitio web")
    contacto: str | None = Field(None, description="Persona de contacto")
    telefono: str | None = Field(None, description="Teléfono de contacto")
    correo: str | None = Field(None, description="Correo electrónico")
    direccion: str | None = Field(None, description="Dirección física")
    ciudad: str | None = Field(None, description="Ciudad")
    created_at: str = Field(..., description="Fecha de creación")
    updated_at: str = Field(..., description="Última actualización")
    logo_available: bool = Field(
        default=False, description="Indica si la empresa tiene logo disponible"
    )
