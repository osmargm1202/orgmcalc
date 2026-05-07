"""Cliente schemas with OpenAPI documentation."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ClienteCreate(BaseModel):
    """Request body for POST /clientes."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "summary": "Cliente empresa",
                    "value": {"empresa_id": "emp-uuid"},
                },
                {
                    "summary": "Cliente persona",
                    "value": {
                        "nombre": "Juan Pérez",
                        "ubicacion": "Santo Domingo",
                        "telefono": "+1 809-555-1122",
                    },
                },
                {
                    "summary": "Cliente mixto",
                    "value": {
                        "empresa_id": "emp-uuid",
                        "nombre": "Obra Punta Cana",
                        "ubicacion": "Punta Cana",
                        "telefono": "+1 829-555-0000",
                    },
                },
            ]
        }
    )

    empresa_id: str | None = Field(
        default=None,
        description="ID de empresa asociada (opcional)",
    )
    nombre: str | None = Field(
        default=None,
        max_length=255,
        description="Nombre fallback/manual del cliente (persona o alias comercial)",
    )
    ubicacion: str | None = Field(
        default=None,
        max_length=500,
        description="Ubicación fallback/manual del cliente",
    )
    telefono: str | None = Field(
        default=None,
        max_length=50,
        description="Teléfono fallback/manual del cliente",
    )


class ClienteUpdate(BaseModel):
    """Request body for PATCH /clientes/{id}."""

    empresa_id: str | None = Field(default=None, description="ID de empresa asociada")
    nombre: str | None = Field(default=None, max_length=255, description="Nombre fallback/manual")
    ubicacion: str | None = Field(
        default=None,
        max_length=500,
        description="Ubicación fallback/manual",
    )
    telefono: str | None = Field(
        default=None,
        max_length=50,
        description="Teléfono fallback/manual",
    )


class ClienteEmpresaInfo(BaseModel):
    """Minimal company info embedded inside cliente."""

    id: str = Field(..., description="ID de la empresa")
    nombre: str = Field(..., description="Nombre de la empresa")


class ClienteResponse(BaseModel):
    """Response for GET /clientes/{id}."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "cli-uuid",
                "empresa_id": "emp-uuid",
                "empresa": {"id": "emp-uuid", "nombre": "Constructora ABC"},
                "nombre": "Obra Punta Cana",
                "ubicacion": "Punta Cana",
                "telefono": "+1 829-555-0000",
                "created_at": "2026-03-29T10:00:00",
                "updated_at": "2026-03-29T10:00:00",
            }
        }
    )

    id: str = Field(..., description="Identificador único del cliente")
    empresa_id: str | None = Field(default=None, description="Empresa asociada")
    empresa: ClienteEmpresaInfo | None = Field(
        default=None,
        description="Empresa asociada embebida (si aplica)",
    )
    nombre: str | None = Field(default=None, description="Nombre fallback/manual")
    ubicacion: str | None = Field(default=None, description="Ubicación fallback/manual")
    telefono: str | None = Field(default=None, description="Teléfono fallback/manual")
    created_at: str = Field(..., description="Fecha de creación")
    updated_at: str = Field(..., description="Última actualización")
