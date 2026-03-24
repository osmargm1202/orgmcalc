"""Files service - file upload/replacement/status logic."""

from __future__ import annotations

from typing import Any

from orgmcalc.repositories.files import FilesRepository
from orgmcalc.storage.keys import StorageKeys
from orgmcalc.storage.object_store import (
    ALLOWED_CONTENT_TYPES,
    extension_from_content_type,
    get_object_store,
)


class FilesService:
    """Service for file business logic."""

    @staticmethod
    def is_valid_content_type(content_type: str) -> bool:
        """Check if content type is allowed."""
        ct = (content_type or "").split(";")[0].strip().lower()
        return ct in ALLOWED_CONTENT_TYPES

    @staticmethod
    async def upload_project_logo(
        project_id: str, content: bytes, content_type: str, original_name: str | None
    ) -> dict[str, Any] | None:
        """Upload project logo with single-active semantics."""
        store = get_object_store()
        if not store.available:
            return None

        ext = extension_from_content_type(content_type)
        key = StorageKeys.project_logo(project_id, ext)

        # Upload to object storage
        url = store.upload_bytes(key, content, content_type)
        if not url:
            return None

        # Update metadata
        result = await FilesRepository.create_or_replace(
            owner_type="project",
            owner_id=project_id,
            asset_type="logo",
            filename=f"logo.{ext}",
            storage_key=key,
            storage_bucket=store._bucket,
            original_name=original_name,
            content_type=content_type,
            size_bytes=len(content),
        )
        result["url"] = url
        return result

    @staticmethod
    async def upload_project_cliente_logo(
        project_id: str, content: bytes, content_type: str, original_name: str | None
    ) -> dict[str, Any] | None:
        """Upload project client logo with single-active semantics."""
        store = get_object_store()
        if not store.available:
            return None

        ext = extension_from_content_type(content_type)
        key = StorageKeys.project_cliente_logo(project_id, ext)

        url = store.upload_bytes(key, content, content_type)
        if not url:
            return None

        result = await FilesRepository.create_or_replace(
            owner_type="project",
            owner_id=project_id,
            asset_type="cliente_logo",
            filename=f"cliente_logo.{ext}",
            storage_key=key,
            storage_bucket=store._bucket,
            original_name=original_name,
            content_type=content_type,
            size_bytes=len(content),
        )
        result["url"] = url
        return result

    @staticmethod
    async def get_project_cliente_logo_url(project_id: str) -> str | None:
        """Get presigned URL for the active project client logo."""
        return await FilesService.get_download_url("project", project_id, "cliente_logo")

    @staticmethod
    async def get_project_cliente_logo_status(project_id: str) -> dict[str, Any]:
        """Get status for the active project client logo."""
        return await FilesService.get_file_status("project", project_id, "cliente_logo")

    @staticmethod
    async def upload_empresa_logo(
        empresa_id: str, content: bytes, content_type: str, original_name: str | None
    ) -> dict[str, Any] | None:
        """Upload company logo."""
        store = get_object_store()
        if not store.available:
            return None

        ext = extension_from_content_type(content_type)
        key = StorageKeys.empresa_logo(empresa_id, ext)

        url = store.upload_bytes(key, content, content_type)
        if not url:
            return None

        result = await FilesRepository.create_or_replace(
            owner_type="empresa",
            owner_id=empresa_id,
            asset_type="logo",
            filename=f"logo.{ext}",
            storage_key=key,
            storage_bucket=store._bucket,
            original_name=original_name,
            content_type=content_type,
            size_bytes=len(content),
        )
        result["url"] = url
        return result

    @staticmethod
    async def upload_ingeniero_perfil(
        ingeniero_id: str, content: bytes, content_type: str, original_name: str | None
    ) -> dict[str, Any] | None:
        """Upload engineer profile photo."""
        store = get_object_store()
        if not store.available:
            return None

        ext = extension_from_content_type(content_type)
        key = StorageKeys.ingeniero_perfil(ingeniero_id, ext)

        url = store.upload_bytes(key, content, content_type)
        if not url:
            return None

        result = await FilesRepository.create_or_replace(
            owner_type="ingeniero",
            owner_id=ingeniero_id,
            asset_type="perfil",
            filename=f"perfil.{ext}",
            storage_key=key,
            storage_bucket=store._bucket,
            original_name=original_name,
            content_type=content_type,
            size_bytes=len(content),
        )
        result["url"] = url
        return result

    @staticmethod
    async def upload_ingeniero_carnet(
        ingeniero_id: str, content: bytes, content_type: str, original_name: str | None
    ) -> dict[str, Any] | None:
        """Upload engineer carnet."""
        store = get_object_store()
        if not store.available:
            return None

        ext = extension_from_content_type(content_type)
        key = StorageKeys.ingeniero_carnet(ingeniero_id, ext)

        url = store.upload_bytes(key, content, content_type)
        if not url:
            return None

        result = await FilesRepository.create_or_replace(
            owner_type="ingeniero",
            owner_id=ingeniero_id,
            asset_type="carnet",
            filename=f"carnet.{ext}",
            storage_key=key,
            storage_bucket=store._bucket,
            original_name=original_name,
            content_type=content_type,
            size_bytes=len(content),
        )
        result["url"] = url
        return result

    @staticmethod
    async def upload_ingeniero_certificacion(
        ingeniero_id: str, content: bytes, content_type: str, original_name: str | None
    ) -> dict[str, Any] | None:
        """Upload engineer certification."""
        store = get_object_store()
        if not store.available:
            return None

        ext = extension_from_content_type(content_type)
        key = StorageKeys.ingeniero_certificacion(ingeniero_id, ext)

        url = store.upload_bytes(key, content, content_type)
        if not url:
            return None

        result = await FilesRepository.create_or_replace(
            owner_type="ingeniero",
            owner_id=ingeniero_id,
            asset_type="certificacion",
            filename=f"certificacion.{ext}",
            storage_key=key,
            storage_bucket=store._bucket,
            original_name=original_name,
            content_type=content_type,
            size_bytes=len(content),
        )
        result["url"] = url
        return result

    @staticmethod
    async def upload_documento_file(
        project_id: str,
        documento_id: str,
        content: bytes,
        content_type: str,
        filename: str,
    ) -> dict[str, Any] | None:
        """Upload document file."""
        store = get_object_store()
        if not store.available:
            return None

        key = StorageKeys.project_document(project_id, documento_id, filename)

        url = store.upload_bytes(key, content, content_type)
        if not url:
            return None

        result = await FilesRepository.create_or_replace(
            owner_type="documento",
            owner_id=documento_id,
            asset_type="documento",
            filename=filename,
            storage_key=key,
            storage_bucket=store._bucket,
            original_name=filename,
            content_type=content_type,
            size_bytes=len(content),
        )
        result["url"] = url
        return result

    @staticmethod
    async def get_download_url(owner_type: str, owner_id: str, asset_type: str) -> str | None:
        """Get presigned download URL for active file."""
        store = get_object_store()
        if not store.available:
            return None

        meta = await FilesRepository.get_active(owner_type, owner_id, asset_type)
        if not meta:
            return None

        return store.get_presigned_url(meta["storage_key"])

    @staticmethod
    async def get_file_status(owner_type: str, owner_id: str, asset_type: str) -> dict[str, Any]:
        """Get file availability status."""
        store = get_object_store()
        if not store.available:
            return {"available": False, "storage_key": None}

        meta = await FilesRepository.get_active(owner_type, owner_id, asset_type)
        if not meta:
            return {"available": False, "storage_key": None}

        return {
            "available": True,
            "storage_key": meta["storage_key"],
            "filename": meta["filename"],
            "size_bytes": meta["size_bytes"],
            "content_type": meta["content_type"],
        }

    @staticmethod
    async def get_batch_status(storage_keys: list[str]) -> dict[str, dict[str, Any]]:
        """Get status for multiple files."""
        return await FilesRepository.get_batch_status(storage_keys)
