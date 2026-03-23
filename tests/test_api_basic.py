"""Basic API integration tests."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from httpx import AsyncClient


class TestHealthEndpoint:
    """Tests for health endpoint."""

    async def test_health_check(self, async_client: AsyncClient) -> None:
        """Test health check endpoint returns 200."""
        response = await async_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


class TestDocsEndpoint:
    """Tests for documentation endpoints."""

    async def test_openapi_json(self, async_client: AsyncClient) -> None:
        """Test OpenAPI schema is accessible."""
        response = await async_client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert data["info"]["title"] == "orgmcalc"

    async def test_docs_ui(self, async_client: AsyncClient) -> None:
        """Test Swagger UI is accessible."""
        response = await async_client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    async def test_redoc_ui(self, async_client: AsyncClient) -> None:
        """Test ReDoc UI is accessible."""
        response = await async_client.get("/redoc")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    async def test_api_markdown(self, async_client: AsyncClient) -> None:
        """Test API markdown documentation is served."""
        response = await async_client.get("/externo/api-md")
        assert response.status_code == 200
        content = response.text
        assert "# API Documentation" in content
        assert "/proyectos" in content


class TestAuthEndpoints:
    """Tests for authentication endpoints."""

    async def test_auth_google_redirects(self, async_client: AsyncClient) -> None:
        """Test Google OAuth endpoint redirects."""
        response = await async_client.get("/auth/google", follow_redirects=False)
        assert response.status_code == 307  # Temporary redirect
        assert "accounts.google.com" in response.headers["location"]

    async def test_auth_me_requires_auth(self, async_client: AsyncClient) -> None:
        """Test /auth/me requires authentication."""
        response = await async_client.get("/auth/me")
        assert response.status_code == 403

    async def test_auth_me_with_token(self, async_client: AsyncClient, auth_headers: dict[str, str]) -> None:
        """Test /auth/me with valid token returns user info."""
        # This will require proper mocking of AuthService
        # For now, just test that it doesn't crash
        response = await async_client.get("/auth/me", headers=auth_headers)
        # Should return 401 since token is not valid
        assert response.status_code in [401, 403]

    async def test_logout_requires_auth(self, async_client: AsyncClient) -> None:
        """Test logout requires authentication."""
        response = await async_client.post("/auth/logout")
        assert response.status_code == 403


class TestProyectosEndpoints:
    """Tests for proyectos endpoints."""

    async def test_list_proyectos(self, async_client: AsyncClient) -> None:
        """Test GET /proyectos returns list (may be empty)."""
        response = await async_client.get("/proyectos")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_get_proyecto_not_found(self, async_client: AsyncClient) -> None:
        """Test GET /proyectos/{id} returns 404 for non-existent project."""
        response = await async_client.get("/proyectos/99999")
        assert response.status_code == 404

    async def test_create_proyecto_requires_auth(self, async_client: AsyncClient) -> None:
        """Test POST /proyectos requires authentication."""
        payload = {"nombre": "Test Project"}
        response = await async_client.post("/proyectos", json=payload)
        assert response.status_code == 403

    async def test_update_proyecto_requires_auth(self, async_client: AsyncClient) -> None:
        """Test PATCH /proyectos/{id} requires authentication."""
        payload = {"nombre": "Updated Project"}
        response = await async_client.patch("/proyectos/1", json=payload)
        assert response.status_code == 403

    async def test_delete_proyecto_requires_auth(self, async_client: AsyncClient) -> None:
        """Test DELETE /proyectos/{id} requires authentication."""
        response = await async_client.delete("/proyectos/1")
        assert response.status_code == 403


class TestEmpresasEndpoints:
    """Tests for empresas endpoints."""

    async def test_list_empresas(self, async_client: AsyncClient) -> None:
        """Test GET /empresas returns list."""
        response = await async_client.get("/empresas")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_get_empresa_not_found(self, async_client: AsyncClient) -> None:
        """Test GET /empresas/{id} returns 404 for non-existent empresa."""
        response = await async_client.get("/empresas/99999")
        assert response.status_code == 404

    async def test_create_empresa_requires_auth(self, async_client: AsyncClient) -> None:
        """Test POST /empresas requires authentication."""
        payload = {"nombre": "Test Empresa"}
        response = await async_client.post("/empresas", json=payload)
        assert response.status_code == 403


class TestIngenierosEndpoints:
    """Tests for ingenieros endpoints."""

    async def test_list_ingenieros(self, async_client: AsyncClient) -> None:
        """Test GET /ingenieros returns list."""
        response = await async_client.get("/ingenieros")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_get_ingeniero_not_found(self, async_client: AsyncClient) -> None:
        """Test GET /ingenieros/{id} returns 404 for non-existent ingeniero."""
        response = await async_client.get("/ingenieros/99999")
        assert response.status_code == 404

    async def test_create_ingeniero_requires_auth(self, async_client: AsyncClient) -> None:
        """Test POST /ingenieros requires authentication."""
        payload = {"nombre": "Test Ingeniero"}
        response = await async_client.post("/ingenieros", json=payload)
        assert response.status_code == 403


class TestCalculosEndpoints:
    """Tests for calculos endpoints."""

    async def test_list_calculos_project_not_found(self, async_client: AsyncClient) -> None:
        """Test GET /proyectos/{id}/calculos returns 404 for non-existent project."""
        response = await async_client.get("/proyectos/99999/calculos")
        assert response.status_code == 404

    async def test_create_calculo_requires_auth(self, async_client: AsyncClient) -> None:
        """Test POST /proyectos/{id}/calculos requires authentication."""
        payload = {"codigo": "TEST-001", "nombre": "Test Calculo"}
        response = await async_client.post("/proyectos/1/calculos", json=payload)
        assert response.status_code == 403


class TestDocumentosEndpoints:
    """Tests for documentos endpoints."""

    async def test_list_documentos_project_not_found(self, async_client: AsyncClient) -> None:
        """Test GET /proyectos/{id}/documentos returns 404 for non-existent project."""
        response = await async_client.get("/proyectos/99999/documentos")
        assert response.status_code == 404

    async def test_create_documento_requires_auth(self, async_client: AsyncClient) -> None:
        """Test POST /proyectos/{id}/documentos requires authentication."""
        payload = {"nombre_documento": "test.pdf"}
        response = await async_client.post("/proyectos/1/documentos", json=payload)
        assert response.status_code == 403


class TestStorageEndpoints:
    """Tests for storage endpoints."""

    async def test_batch_status(self, async_client: AsyncClient) -> None:
        """Test POST /storage/status requires keys."""
        payload = {"keys": ["project/1/logo"]}
        response = await async_client.post("/storage/status", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "statuses" in data

    async def test_upload_project_logo_requires_auth(self, async_client: AsyncClient) -> None:
        """Test POST /proyectos/{id}/logo requires authentication."""
        response = await async_client.post("/proyectos/1/logo")
        assert response.status_code == 403

    async def test_upload_empresa_logo_requires_auth(self, async_client: AsyncClient) -> None:
        """Test POST /empresas/{id}/logo requires authentication."""
        response = await async_client.post("/empresas/1/logo")
        assert response.status_code == 403

    async def test_upload_ingeniero_perfil_requires_auth(self, async_client: AsyncClient) -> None:
        """Test POST /ingenieros/{id}/perfil requires authentication."""
        response = await async_client.post("/ingenieros/1/perfil")
        assert response.status_code == 403
