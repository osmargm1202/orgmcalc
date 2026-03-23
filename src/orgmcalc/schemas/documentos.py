"""Documento schemas for project documents with OpenAPI documentation."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class DocumentoCreate(BaseModel):
    """Request body for POST /proyectos/{id}/documentos.

    Creates a document record. The actual file must be uploaded separately
    via POST /proyectos/{id}/documentos/{doc_id}/file.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nombre_documento": "Plano Estructural Rev A.pdf",
                "descripcion": "Plano estructural aprobado por el cliente - Revisión A",
            }
        }
    )

    nombre_documento: str = Field(
        ..., min_length=1, max_length=255, description="Nombre del documento/archivo (requerido)"
    )
    descripcion: str | None = Field(
        default=None, max_length=1000, description="Descripción detallada del documento"
    )


class DocumentoResponse(BaseModel):
    """Response for document operations.

    Includes document metadata and file availability status.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "project_id": 5,
                "nombre_documento": "Plano Estructural Rev A.pdf",
                "descripcion": "Plano estructural aprobado",
                "file_available": True,
                "created_at": "2024-02-01T10:00:00",
                "updated_at": "2024-02-15T14:30:00",
            }
        }
    )

    id: int = Field(..., description="Identificador único del documento")
    project_id: int = Field(..., description="ID del proyecto al que pertenece")
    nombre_documento: str = Field(..., description="Nombre del documento")
    descripcion: str | None = Field(None, description="Descripción del documento")
    file_available: bool = Field(
        default=False, description="Indica si el archivo físico está disponible"
    )
    created_at: str = Field(..., description="Fecha de creación del registro")
    updated_at: str = Field(..., description="Última actualización")


class DocumentoListItem(BaseModel):
    """Item in list of documents.

    Lightweight representation for list views.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "nombre_documento": "Plano Estructural Rev A.pdf",
                "descripcion": "Plano estructural aprobado",
                "file_available": True,
                "created_at": "2024-02-01T10:00:00",
            }
        }
    )

    id: int = Field(..., description="Identificador único")
    nombre_documento: str = Field(..., description="Nombre del documento")
    descripcion: str | None = Field(None, description="Descripción breve")
    file_available: bool = Field(default=False, description="Archivo disponible para descarga")
    created_at: str = Field(..., description="Fecha de creación")
