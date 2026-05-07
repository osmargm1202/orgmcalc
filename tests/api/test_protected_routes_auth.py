"""Representative auth coverage for app wiring and protected routes."""

from __future__ import annotations

from fastapi.testclient import TestClient

from orgmcalc.api import dependencies
from orgmcalc.api.app import create_app
from orgmcalc.services import projects as projects_service


class _VerifierSuccess:
    async def verify_access_token(self, token: str) -> dict[str, object]:
        return {"sub": "user-123", "type": "access", "token": token}


class _VerifierFailure:
    async def verify_access_token(self, token: str) -> dict[str, object]:
        raise dependencies.AuthTokenError("invalid token")


def _build_client(monkeypatch) -> TestClient:
    monkeypatch.setattr("orgmcalc.api.app.run_migrations", lambda: [])
    monkeypatch.setattr("orgmcalc.api.app.init_pool", lambda: None)

    async def _close_pool() -> None:
        return None

    monkeypatch.setattr("orgmcalc.api.app.close_pool", _close_pool)
    return TestClient(create_app())


def test_public_gets_ignore_bad_authorization_headers(monkeypatch) -> None:
    client = _build_client(monkeypatch)

    response = client.get("/health", headers={"Authorization": "Bearer not-real"})

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_protected_write_requires_valid_bearer_token(monkeypatch) -> None:
    monkeypatch.setattr(dependencies, "get_jwks_verifier", lambda: _VerifierFailure())
    client = _build_client(monkeypatch)

    response = client.post("/proyectos", json={"nombre": "Demo"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Missing bearer token"}

    response = client.post(
        "/proyectos",
        headers={"Authorization": "Bearer invalid"},
        json={"nombre": "Demo"},
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token"}


def test_protected_write_accepts_valid_bearer_access_token(monkeypatch) -> None:
    async def fake_create_project(data: dict[str, object]) -> dict[str, object]:
        return {
            "id": "project-1",
            "nombre": data["nombre"],
            "cliente": None,
            "ubicacion": None,
            "estado": "activo",
            "fecha": None,
            "created_at": "2026-03-28T00:00:00Z",
            "updated_at": "2026-03-28T00:00:00Z",
            "logo_available": False,
            "cliente_logo_available": False,
        }

    monkeypatch.setattr(dependencies, "get_jwks_verifier", lambda: _VerifierSuccess())
    monkeypatch.setattr(projects_service.ProjectsService, "create_project", fake_create_project)
    client = _build_client(monkeypatch)

    response = client.post(
        "/proyectos",
        headers={"Authorization": "Bearer valid-token"},
        json={"nombre": "Proyecto demo", "ubicacion": "GT"},
    )

    assert response.status_code == 201
    assert response.json()["nombre"] == "Proyecto demo"


def test_legacy_auth_routes_are_not_mounted(monkeypatch) -> None:
    client = _build_client(monkeypatch)

    assert client.get("/auth/google").status_code == 404
    assert client.get("/auth/google/callback").status_code == 404
    assert client.get("/auth/me").status_code == 404
    assert client.post("/auth/logout").status_code == 404
