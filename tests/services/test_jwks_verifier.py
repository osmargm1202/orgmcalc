"""Tests for JWKS-backed access-token verification."""

from __future__ import annotations

import base64
from datetime import UTC, datetime, timedelta

import httpx
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat

from orgmcalc.config import Settings
from orgmcalc.services.jwks_verifier import AuthTokenError, JwksVerifier


def _b64url_uint(value: int) -> str:
    raw = value.to_bytes((value.bit_length() + 7) // 8, "big")
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _build_keypair(kid: str = "kid-1") -> tuple[dict[str, str], str]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_numbers = private_key.public_key().public_numbers()
    jwk = {
        "kty": "RSA",
        "use": "sig",
        "alg": "RS256",
        "kid": kid,
        "n": _b64url_uint(public_numbers.n),
        "e": _b64url_uint(public_numbers.e),
    }
    private_pem = private_key.private_bytes(
        encoding=Encoding.PEM,
        format=PrivateFormat.PKCS8,
        encryption_algorithm=NoEncryption(),
    ).decode("utf-8")
    return jwk, private_pem


def _encode_token(private_pem: str, kid: str, **claims: object) -> str:
    from jose import jwt

    payload = {
        "sub": "user-123",
        "email": "user@example.com",
        "app_name": "orgmcalc-tests",
        "type": "access",
        "exp": int((datetime.now(UTC) + timedelta(minutes=5)).timestamp()),
    }
    payload.update(claims)
    return jwt.encode(payload, private_pem, algorithm="RS256", headers={"kid": kid})


@pytest.mark.asyncio
async def test_verify_access_token_fetches_jwks_and_uses_cache_headers() -> None:
    jwk, private_pem = _build_keypair()
    token = _encode_token(private_pem, kid=jwk["kid"])
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        assert str(request.url) == "https://auth.example/.well-known/jwks.json"
        return httpx.Response(
            200, json={"keys": [jwk]}, headers={"Cache-Control": "public, max-age=60"}
        )

    verifier = JwksVerifier(
        Settings(auth_api_url="https://auth.example"),
        transport=httpx.MockTransport(handler),
    )

    claims_one = await verifier.verify_access_token(token)
    claims_two = await verifier.verify_access_token(token)

    assert claims_one["sub"] == "user-123"
    assert claims_two["type"] == "access"
    assert calls == 1


@pytest.mark.asyncio
async def test_verify_access_token_refreshes_once_for_unknown_kid() -> None:
    token_jwk, private_pem = _build_keypair("requested-kid")
    other_jwk, _ = _build_keypair("other-kid")
    token = _encode_token(private_pem, kid=token_jwk["kid"])
    calls = 0

    def handler(_: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(
            200, json={"keys": [other_jwk]}, headers={"Cache-Control": "max-age=60"}
        )

    verifier = JwksVerifier(
        Settings(auth_api_url="https://auth.example"),
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(AuthTokenError):
        await verifier.verify_access_token(token)

    assert calls == 2


@pytest.mark.asyncio
async def test_verify_access_token_rejects_expired_wrong_type_and_bad_signature() -> None:
    jwk, private_pem = _build_keypair("good-kid")
    other_jwk, other_private_pem = _build_keypair("bad-kid")
    transport = httpx.MockTransport(
        lambda _: httpx.Response(200, json={"keys": [jwk]}, headers={"Cache-Control": "max-age=60"})
    )
    verifier = JwksVerifier(Settings(auth_api_url="https://auth.example"), transport=transport)

    expired = _encode_token(
        private_pem,
        kid=jwk["kid"],
        exp=int((datetime.now(UTC) - timedelta(minutes=1)).timestamp()),
    )
    wrong_type = _encode_token(private_pem, kid=jwk["kid"], type="refresh")
    bad_signature = _encode_token(other_private_pem, kid=other_jwk["kid"])

    for token in (expired, wrong_type, bad_signature, "not-a-jwt"):
        with pytest.raises(AuthTokenError):
            await verifier.verify_access_token(token)
