"""JWKS-backed bearer access-token verification."""

from __future__ import annotations

import base64
import logging
from datetime import UTC, datetime, timedelta
from email.utils import parsedate_to_datetime
from typing import Any, Literal, TypedDict, cast

import httpx
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from jose import jwt
from jose.exceptions import JWTError

from orgmcalc.config import Settings

logger = logging.getLogger(__name__)
DEFAULT_JWKS_TTL_SECONDS = 300


class VerifiedAccessClaims(TypedDict, total=False):
    """Validated access-token claims used by protected endpoints."""

    sub: str
    email: str
    app_name: str
    type: Literal["access"]
    exp: int


class CachedJwks(TypedDict):
    """Process-local JWKS cache entry."""

    keys: list[dict[str, Any]]
    expires_at: datetime


class AuthTokenError(Exception):
    """Normalized auth verification error."""


class JwksVerifier:
    """Verify OrgAuth-issued bearer access tokens using JWKS."""

    def __init__(
        self,
        settings: Settings,
        *,
        transport: httpx.AsyncBaseTransport | None = None,
        fallback_ttl_seconds: int = DEFAULT_JWKS_TTL_SECONDS,
    ) -> None:
        self._settings = settings
        self._transport = transport
        self._fallback_ttl_seconds = fallback_ttl_seconds
        self._cache: CachedJwks | None = None

    @property
    def jwks_url(self) -> str:
        """Return the configured JWKS endpoint URL."""
        return f"{self._settings.auth_api_url.rstrip('/')}/.well-known/jwks.json"

    async def verify_access_token(self, token: str) -> VerifiedAccessClaims:
        """Verify an inbound bearer access token against JWKS."""
        try:
            header = jwt.get_unverified_header(token)
        except JWTError as exc:
            logger.info("Rejected malformed bearer token")
            raise AuthTokenError("invalid token") from exc

        kid = header.get("kid")
        if header.get("alg") != "RS256" or not isinstance(kid, str) or not kid:
            logger.info("Rejected token with unsupported algorithm or missing kid")
            raise AuthTokenError("invalid token")

        jwks = await self._get_jwks()
        key = self._find_key(jwks["keys"], kid)
        if key is None:
            logger.info("Unknown JWKS kid encountered; forcing one refresh", extra={"kid": kid})
            jwks = await self._get_jwks(force_refresh=True)
            key = self._find_key(jwks["keys"], kid)
            if key is None:
                logger.info(
                    "Rejected token after JWKS refresh still missed kid", extra={"kid": kid}
                )
                raise AuthTokenError("invalid token")

        public_key = self._public_key_from_jwk(key)

        try:
            claims = jwt.decode(
                token, public_key, algorithms=["RS256"], options={"verify_aud": False}
            )
        except JWTError as exc:
            logger.info("Rejected bearer token during JWT validation")
            raise AuthTokenError("invalid token") from exc

        if claims.get("type") != "access":
            logger.info("Rejected non-access token on protected endpoint")
            raise AuthTokenError("invalid token")

        return cast(VerifiedAccessClaims, claims)

    async def _get_jwks(self, *, force_refresh: bool = False) -> CachedJwks:
        now = datetime.now(UTC)
        if not force_refresh and self._cache is not None and self._cache["expires_at"] > now:
            return self._cache

        self._cache = await self._fetch_jwks()
        return self._cache

    async def _fetch_jwks(self) -> CachedJwks:
        logger.info("Fetching JWKS", extra={"jwks_url": self.jwks_url})
        try:
            async with httpx.AsyncClient(transport=self._transport, timeout=10.0) as client:
                response = await client.get(self.jwks_url)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.warning("JWKS fetch failed")
            raise AuthTokenError("invalid token") from exc

        payload = response.json()
        keys = payload.get("keys")
        if not isinstance(keys, list):
            logger.warning("JWKS response missing keys array")
            raise AuthTokenError("invalid token")

        expires_at = self._resolve_expiry(response.headers)
        logger.info(
            "JWKS cache refreshed successfully", extra={"expires_at": expires_at.isoformat()}
        )
        return {"keys": cast(list[dict[str, Any]], keys), "expires_at": expires_at}

    def _resolve_expiry(self, headers: httpx.Headers) -> datetime:
        now = datetime.now(UTC)
        cache_control = headers.get("Cache-Control", "")
        for directive in cache_control.split(","):
            directive = directive.strip().lower()
            if directive.startswith("max-age="):
                try:
                    seconds = max(int(directive.split("=", 1)[1]), 0)
                except ValueError:
                    break
                return now + timedelta(seconds=seconds)

        expires = headers.get("Expires")
        if expires:
            try:
                expires_at = parsedate_to_datetime(expires)
                if expires_at.tzinfo is None:
                    expires_at = expires_at.replace(tzinfo=UTC)
                return expires_at.astimezone(UTC)
            except (TypeError, ValueError, IndexError):
                logger.info("Failed to parse JWKS Expires header; using fallback TTL")

        return now + timedelta(seconds=self._fallback_ttl_seconds)

    @staticmethod
    def _find_key(keys: list[dict[str, Any]], kid: str) -> dict[str, Any] | None:
        for key in keys:
            if key.get("kid") == kid:
                return key
        return None

    @staticmethod
    def _public_key_from_jwk(jwk_data: dict[str, Any]) -> str:
        if jwk_data.get("kty") != "RSA":
            raise AuthTokenError("invalid token")
        try:
            n = JwksVerifier._decode_base64url_int(str(jwk_data["n"]))
            e = JwksVerifier._decode_base64url_int(str(jwk_data["e"]))
        except (KeyError, ValueError, TypeError) as exc:
            raise AuthTokenError("invalid token") from exc

        public_numbers = rsa.RSAPublicNumbers(e, n)
        public_key = public_numbers.public_key()
        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        return pem.decode("utf-8")

    @staticmethod
    def _decode_base64url_int(value: str) -> int:
        padding = "=" * (-len(value) % 4)
        raw = base64.urlsafe_b64decode(f"{value}{padding}")
        return int.from_bytes(raw, "big")
