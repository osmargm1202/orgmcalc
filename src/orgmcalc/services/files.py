"""Files service - file upload/replacement/status logic."""

from __future__ import annotations

import re
from typing import Any

from orgmcalc.repositories.clientes import ClientesRepository
from orgmcalc.repositories.empresas import EmpresasRepository
from orgmcalc.repositories.files import FilesRepository
from orgmcalc.repositories.ingenieros import IngenierosRepository
from orgmcalc.repositories.projects import ProjectsRepository
from orgmcalc.storage.keys import StorageKeys
from orgmcalc.storage.object_store import (
    ALLOWED_CONTENT_TYPES,
    extension_from_content_type,
    get_object_store,
)


class FilesService:
    """Service for file business logic."""

    @staticmethod
    def _slug_part(value: str | None, fallback: str = "archivo") -> str:
        raw = (value or "").strip().lower()
        if not raw:
            return fallback
        normalized = re.sub(r"[^a-z0-9]+", "-", raw)
        normalized = normalized.strip("-")
        return normalized or fallback

    @staticmethod
    async def _replace_single_active(
        *,
        owner_type: str,
        owner_id: str,
        asset_type: str,
        storage_key: str,
        filename: str,
        original_name: str | None,
        content: bytes,
        content_type: str,
    ) -> dict[str, Any] | None:
        """Upload new file and replace previous active metadata/object.

        This keeps only one active asset in DB and deletes previous physical
        object when key changes (e.g., extension changed from jpg -> pdf).
        """
        store = get_object_store()
        if not store.available:
            return None

        previous = await FilesRepository.get_active(owner_type, owner_id, asset_type)

        url = store.upload_bytes(storage_key, content, content_type)
        if not url:
            return None

        result = await FilesRepository.create_or_replace(
            owner_type=owner_type,
            owner_id=owner_id,
            asset_type=asset_type,
            filename=filename,
            storage_key=storage_key,
            storage_bucket=store._bucket,
            original_name=original_name,
            content_type=content_type,
            size_bytes=len(content),
        )

        previous_key = (previous or {}).get("storage_key") if previous else None
        if previous_key and previous_key != storage_key:
            store.delete_object(previous_key)

        result["url"] = url
        return result

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
        ext = extension_from_content_type(content_type)
        key = StorageKeys.project_logo(project_id, ext)
        return await FilesService._replace_single_active(
            owner_type="project",
            owner_id=project_id,
            asset_type="logo",
            storage_key=key,
            filename=f"logo.{ext}",
            original_name=original_name,
            content=content,
            content_type=content_type,
        )

    @staticmethod
    async def upload_project_cliente_logo(
        project_id: str, content: bytes, content_type: str, original_name: str | None
    ) -> dict[str, Any] | None:
        """Upload project client logo with single-active semantics."""
        ext = extension_from_content_type(content_type)
        project = await ProjectsRepository.get_by_id(project_id)
        cliente = (project or {}).get("cliente") if project else None
        cliente_name = (cliente or {}).get("nombre") if cliente else None
        if not cliente_name:
            empresa = (cliente or {}).get("empresa") if cliente else None
            cliente_name = (empresa or {}).get("nombre") if empresa else None
        if not cliente_name:
            cliente_name = f"cliente-{project_id[:8]}"
        label = FilesService._slug_part(cliente_name)
        key = StorageKeys.project_cliente_logo(project_id, ext)
        return await FilesService._replace_single_active(
            owner_type="project",
            owner_id=project_id,
            asset_type="cliente_logo",
            storage_key=key,
            filename=f"{label}_logo.{ext}",
            original_name=original_name,
            content=content,
            content_type=content_type,
        )

    @staticmethod
    async def get_project_cliente_logo_url(project_id: str) -> str | None:
        """Get presigned URL for the active project client logo."""
        return await FilesService.get_download_url("project", project_id, "cliente_logo")

    @staticmethod
    async def get_project_cliente_logo_status(project_id: str) -> dict[str, Any]:
        """Get status for the active project client logo."""
        return await FilesService.get_file_status("project", project_id, "cliente_logo")

    @staticmethod
    async def get_cliente_logo_url(cliente_id: str) -> str | None:
        """Get presigned URL for active cliente logo."""
        return await FilesService.get_download_url("cliente", cliente_id, "logo")

    @staticmethod
    async def get_cliente_logo_status(cliente_id: str) -> dict[str, Any]:
        """Get status for active cliente logo."""
        return await FilesService.get_file_status("cliente", cliente_id, "logo")

    @staticmethod
    async def upload_empresa_logo(
        empresa_id: str, content: bytes, content_type: str, original_name: str | None
    ) -> dict[str, Any] | None:
        """Upload company logo."""
        empresa = await EmpresasRepository.get_by_id(empresa_id)
        ext = extension_from_content_type(content_type)
        empresa_name = (empresa or {}).get("nombre") or f"empresa-{empresa_id[:8]}"
        label = FilesService._slug_part(empresa_name)
        key = StorageKeys.empresa_logo(f"{label}-{empresa_id[:8]}", ext)
        return await FilesService._replace_single_active(
            owner_type="empresa",
            owner_id=empresa_id,
            asset_type="logo",
            storage_key=key,
            filename=f"{label}_logo.{ext}",
            original_name=original_name,
            content=content,
            content_type=content_type,
        )

    @staticmethod
    async def upload_cliente_logo(
        cliente_id: str, content: bytes, content_type: str, original_name: str | None
    ) -> dict[str, Any] | None:
        """Upload cliente logo with owner_type=cliente metadata."""
        cliente = await ClientesRepository.get_by_id(cliente_id)
        ext = extension_from_content_type(content_type)
        cliente_name = (cliente or {}).get("nombre")
        if not cliente_name:
            empresa = (cliente or {}).get("empresa") if cliente else None
            cliente_name = (empresa or {}).get("nombre") if empresa else None
        if not cliente_name:
            cliente_name = f"cliente-{cliente_id[:8]}"

        label = FilesService._slug_part(cliente_name)
        key = StorageKeys.cliente_logo(f"{label}-{cliente_id[:8]}", ext)
        return await FilesService._replace_single_active(
            owner_type="cliente",
            owner_id=cliente_id,
            asset_type="logo",
            storage_key=key,
            filename=f"{label}_logo.{ext}",
            original_name=original_name,
            content=content,
            content_type=content_type,
        )

    @staticmethod
    async def upload_ingeniero_perfil(
        ingeniero_id: str, content: bytes, content_type: str, original_name: str | None
    ) -> dict[str, Any] | None:
        """Upload engineer profile photo."""
        ingeniero = await IngenierosRepository.get_by_id(ingeniero_id)
        nombre = (ingeniero or {}).get("nombre") or f"ingeniero-{ingeniero_id[:8]}"
        label = FilesService._slug_part(nombre)
        ext = extension_from_content_type(content_type)
        key = StorageKeys.ingeniero_perfil(f"{label}-{ingeniero_id[:8]}", ext)
        return await FilesService._replace_single_active(
            owner_type="ingeniero",
            owner_id=ingeniero_id,
            asset_type="perfil",
            storage_key=key,
            filename=f"{label}_perfil.{ext}",
            original_name=original_name,
            content=content,
            content_type=content_type,
        )

    @staticmethod
    async def upload_ingeniero_carnet(
        ingeniero_id: str, content: bytes, content_type: str, original_name: str | None
    ) -> dict[str, Any] | None:
        """Upload engineer carnet."""
        ingeniero = await IngenierosRepository.get_by_id(ingeniero_id)
        nombre = (ingeniero or {}).get("nombre") or f"ingeniero-{ingeniero_id[:8]}"
        codia = (ingeniero or {}).get("codia")
        label = FilesService._slug_part(nombre)
        codia_slug = FilesService._slug_part(codia, fallback="sin-codia")
        ext = extension_from_content_type(content_type)
        key = StorageKeys.ingeniero_carnet(f"{label}-{ingeniero_id[:8]}", ext)
        return await FilesService._replace_single_active(
            owner_type="ingeniero",
            owner_id=ingeniero_id,
            asset_type="carnet",
            storage_key=key,
            filename=f"{label}_{codia_slug}.{ext}",
            original_name=original_name,
            content=content,
            content_type=content_type,
        )

    @staticmethod
    async def upload_ingeniero_certificacion(
        ingeniero_id: str, content: bytes, content_type: str, original_name: str | None
    ) -> dict[str, Any] | None:
        """Upload engineer certification."""
        ingeniero = await IngenierosRepository.get_by_id(ingeniero_id)
        nombre = (ingeniero or {}).get("nombre") or f"ingeniero-{ingeniero_id[:8]}"
        label = FilesService._slug_part(nombre)
        ext = extension_from_content_type(content_type)
        key = StorageKeys.ingeniero_certificacion(f"{label}-{ingeniero_id[:8]}", ext)
        return await FilesService._replace_single_active(
            owner_type="ingeniero",
            owner_id=ingeniero_id,
            asset_type="certificacion",
            storage_key=key,
            filename=f"{label}_certificacion.{ext}",
            original_name=original_name,
            content=content,
            content_type=content_type,
        )

    @staticmethod
    async def upload_documento_file(
        project_id: str,
        documento_id: str,
        content: bytes,
        content_type: str,
        filename: str,
    ) -> dict[str, Any] | None:
        """Upload document file."""
        key = StorageKeys.project_document(project_id, documento_id, filename)
        return await FilesService._replace_single_active(
            owner_type="documento",
            owner_id=documento_id,
            asset_type="documento",
            storage_key=key,
            filename=filename,
            original_name=filename,
            content=content,
            content_type=content_type,
        )

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
