"""Storage key conventions for object storage."""
from __future__ import annotations


class StorageKeys:
    """Key naming conventions for object storage."""

    @staticmethod
    def project_logo(project_id: int, extension: str = "png") -> str:
        return f"projects/{project_id}/logo.{extension.lstrip('.').lower() or 'png'}"

    @staticmethod
    def project_cliente_logo(project_id: int, extension: str = "png") -> str:
        return f"projects/{project_id}/cliente/logo.{extension.lstrip('.').lower() or 'png'}"

    @staticmethod
    def empresa_logo(empresa_id: int, extension: str = "png") -> str:
        return f"empresas/{empresa_id}/logo.{extension.lstrip('.').lower() or 'png'}"

    @staticmethod
    def ingeniero_perfil(ingeniero_id: int, extension: str = "png") -> str:
        return f"ingenieros/{ingeniero_id}/perfil.{extension.lstrip('.').lower() or 'png'}"

    @staticmethod
    def ingeniero_carnet(ingeniero_id: int, extension: str = "pdf") -> str:
        return f"ingenieros/{ingeniero_id}/carnet.{extension.lstrip('.').lower() or 'pdf'}"

    @staticmethod
    def ingeniero_certificacion(ingeniero_id: int, extension: str = "pdf") -> str:
        return f"ingenieros/{ingeniero_id}/certificacion.{extension.lstrip('.').lower() or 'pdf'}"

    @staticmethod
    def project_document(project_id: int, document_id: int, filename: str) -> str:
        ext = filename.split('.')[-1] if '.' in filename else 'pdf'
        return f"projects/{project_id}/documents/{document_id}/document.{ext}"
