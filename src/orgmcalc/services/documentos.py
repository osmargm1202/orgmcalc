"""Documentos service - business logic."""
from __future__ import annotations

from typing import Any

from orgmcalc.repositories.documentos import DocumentosRepository
from orgmcalc.repositories.files import FilesRepository


class DocumentosService:
    """Service for document business logic."""

    @staticmethod
    async def list_documentos(
        project_id: int, offset: int = 0, limit: int = 100
    ) -> list[dict[str, Any]]:
        """List documents for a project with file availability."""
        docs = await DocumentosRepository.list_by_project(project_id, offset, limit)
        for doc in docs:
            doc["file_available"] = False
            file_meta = await FilesRepository.get_active("documento", doc["id"], "documento")
            if file_meta:
                doc["file_available"] = True
        return docs

    @staticmethod
    async def get_documento(document_id: int) -> dict[str, Any] | None:
        """Get document with file availability."""
        doc = await DocumentosRepository.get_by_id(document_id)
        if doc:
            doc["file_available"] = False
            file_meta = await FilesRepository.get_active("documento", document_id, "documento")
            if file_meta:
                doc["file_available"] = True
        return doc

    @staticmethod
    async def create_documento(data: dict[str, Any]) -> dict[str, Any]:
        """Create document."""
        return await DocumentosRepository.create(data)

    @staticmethod
    async def update_documento(document_id: int, data: dict[str, Any]) -> dict[str, Any] | None:
        """Update document."""
        return await DocumentosRepository.update(document_id, data)

    @staticmethod
    async def delete_documento(document_id: int) -> bool:
        """Delete document."""
        return await DocumentosRepository.delete(document_id)

    @staticmethod
    async def documento_exists(document_id: int) -> bool:
        """Check if document exists."""
        return await DocumentosRepository.exists(document_id)
