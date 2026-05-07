"""Tests for auth dependency response mapping."""

from __future__ import annotations

from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
import pytest

from orgmcalc.api import dependencies
from orgmcalc.services.jwks_verifier import AuthTokenError


class _VerifierSuccess:
    async def verify_access_token(self, token: str) -> dict[str, object]:
        return {"sub": token, "type": "access"}


class _VerifierFailure:
    async def verify_access_token(self, token: str) -> dict[str, object]:
        raise AuthTokenError("invalid token")


@pytest.mark.asyncio
async def test_require_auth_returns_missing_bearer_token_contract() -> None:
    with pytest.raises(HTTPException) as exc_info:
        await dependencies.require_auth(None)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Missing bearer token"
    assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}


@pytest.mark.asyncio
async def test_require_auth_returns_verified_claims(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(dependencies, "get_jwks_verifier", lambda: _VerifierSuccess())

    claims = await dependencies.require_auth(
        HTTPAuthorizationCredentials(scheme="Bearer", credentials="token-123")
    )

    assert claims == {"sub": "token-123", "type": "access"}


@pytest.mark.asyncio
async def test_require_auth_maps_all_invalid_tokens_to_invalid_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(dependencies, "get_jwks_verifier", lambda: _VerifierFailure())

    with pytest.raises(HTTPException) as exc_info:
        await dependencies.require_auth(
            HTTPAuthorizationCredentials(scheme="Bearer", credentials="bad-token")
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid token"
    assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}
