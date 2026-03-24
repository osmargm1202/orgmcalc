"""File handling schemas with OpenAPI documentation."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


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
