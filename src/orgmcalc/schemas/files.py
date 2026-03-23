"""File handling schemas with OpenAPI documentation."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class FileUploadResponse(BaseModel):
    """Response after file upload.

    Contains the storage key and optional direct URL.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "storage_key": "project/1/logo",
                "url": "https://cdn.example.com/project/1/logo",
                "message": "Archivo subido correctamente",
            }
        }
    )

    storage_key: str = Field(..., description="Clave única del archivo en el almacenamiento")
    url: str | None = Field(
        default=None, description="URL directa del archivo (si está disponible)"
    )
    message: str = Field(
        default="Archivo subido correctamente", description="Mensaje de confirmación"
    )


class FileStatus(BaseModel):
    """File availability status.

    Indicates whether a file exists and provides its metadata.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "available": True,
                "storage_key": "project/1/logo",
                "filename": "logo.png",
                "size_bytes": 20480,
                "content_type": "image/png",
            }
        }
    )

    available: bool = Field(..., description="Indica si el archivo está disponible")
    storage_key: str | None = Field(
        default=None, description="Clave de almacenamiento (null si no disponible)"
    )
    filename: str | None = Field(default=None, description="Nombre original del archivo")
    size_bytes: int | None = Field(default=None, description="Tamaño del archivo en bytes")
    content_type: str | None = Field(
        default=None, description="Tipo MIME del archivo (ej: image/png, application/pdf)"
    )


class FileStatusRequest(BaseModel):
    """Request for batch status check.

    Check the availability of multiple files at once.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"keys": ["project/1/logo", "empresa/2/logo", "ingeniero/3/perfil"]}
        }
    )

    keys: list[str] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Lista de claves de almacenamiento a verificar (máx 100)",
    )


class FileStatusBatchResponse(BaseModel):
    """Batch file status response.

    Map of storage keys to their respective status.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "statuses": {
                    "project/1/logo": {
                        "available": True,
                        "storage_key": "project/1/logo",
                        "filename": "logo.png",
                        "size_bytes": 20480,
                        "content_type": "image/png",
                    },
                    "empresa/2/logo": {"available": False, "storage_key": None},
                }
            }
        }
    )

    statuses: dict[str, FileStatus] = Field(..., description="Mapa de claves a estados de archivo")


class FileDownloadUrl(BaseModel):
    """Download URL response.

    Contains a presigned URL for temporary access.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "url": "https://storage.example.com/project/1/logo?signature=abc123",
                "expires_in_seconds": 3600,
            }
        }
    )

    url: str = Field(..., description="URL firmada para descarga temporal")
    expires_in_seconds: int = Field(default=3600, description="Segundos hasta que expire la URL")


class FileMetadataResponse(BaseModel):
    """File metadata response.

    Detailed information about a stored file.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "owner_type": "project",
                "owner_id": 5,
                "asset_type": "logo",
                "filename": "logo.png",
                "original_name": "mi-logo.png",
                "content_type": "image/png",
                "size_bytes": 20480,
                "is_active": True,
                "created_at": "2024-01-15T10:30:00",
            }
        }
    )

    id: int = Field(..., description="ID interno del registro de archivo")
    owner_type: str = Field(
        ..., description="Tipo de propietario: project, empresa, ingeniero, documento"
    )
    owner_id: int = Field(..., description="ID del propietario")
    asset_type: str = Field(
        ..., description="Tipo de asset: logo, perfil, carnet, certificacion, documento"
    )
    filename: str = Field(..., description="Nombre del archivo almacenado")
    original_name: str | None = Field(None, description="Nombre original del archivo")
    content_type: str | None = Field(None, description="Tipo MIME")
    size_bytes: int | None = Field(None, description="Tamaño en bytes")
    is_active: bool = Field(..., description="Indica si el registro está activo")
    created_at: str = Field(..., description="Fecha de creación del registro")
