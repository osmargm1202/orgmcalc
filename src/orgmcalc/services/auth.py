"""Authentication service - Google OAuth and session management."""

from __future__ import annotations

import secrets
from typing import Any

import httpx

from orgmcalc.config import get_settings
from orgmcalc.repositories.auth import AuthRepository


class AuthService:
    """Service for Google OAuth and session management."""

    @staticmethod
    def get_google_authorization_url(redirect_uri: str | None = None) -> str:
        """Generate Google OAuth authorization URL.

        Args:
            redirect_uri: Optional custom redirect URI

        Returns:
            Full URL to redirect user to for Google consent

        """
        settings = get_settings()
        client_id = settings.google_client_id

        # Use provided redirect URI or build default
        if not redirect_uri:
            redirect_uri = f"{settings.base_url or 'http://localhost:8000'}/auth/google/callback"

        # Google OAuth authorization endpoint
        auth_url = (
            "https://accounts.google.com/o/oauth2/v2/auth"
            f"?client_id={client_id}"
            f"&redirect_uri={redirect_uri}"
            "&response_type=code"
            "&scope=openid%20email%20profile"
            "&access_type=offline"
            "&prompt=consent"
        )
        return auth_url

    @staticmethod
    async def exchange_code_for_token(
        code: str,
        redirect_uri: str | None = None,
    ) -> dict[str, Any]:
        """Exchange OAuth authorization code for access token.

        Args:
            code: Authorization code from Google callback
            redirect_uri: Must match the one used in authorization request

        Returns:
            Token response from Google

        Raises:
            HTTPException: If token exchange fails

        """
        settings = get_settings()

        if not redirect_uri:
            redirect_uri = f"{settings.base_url or 'http://localhost:8000'}/auth/google/callback"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
            response.raise_for_status()
            return response.json()

    @staticmethod
    async def get_google_user_info(access_token: str) -> dict[str, Any]:
        """Get user info from Google using access token.

        Args:
            access_token: OAuth access token

        Returns:
            User profile information from Google

        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            return response.json()

    @staticmethod
    def generate_session_token() -> str:
        """Generate a cryptographically secure session token.

        Returns:
            Secure random token string

        """
        return secrets.token_urlsafe(48)

    @staticmethod
    async def handle_oauth_callback(
        code: str,
        redirect_uri: str | None = None,
    ) -> dict[str, Any]:
        """Complete OAuth flow - exchange code and create session.

        Args:
            code: Authorization code from Google
            redirect_uri: Redirect URI used in authorization

        Returns:
            Token response with user info and session token

        """
        # Exchange code for access token
        token_data = await AuthService.exchange_code_for_token(code, redirect_uri)
        access_token = token_data.get("access_token")

        # Get user info from Google
        google_user = await AuthService.get_google_user_info(access_token)

        # Create or update user in database
        user = await AuthRepository.create_or_update_user(
            google_id=google_user["id"],
            email=google_user["email"],
            name=google_user.get("name"),
            given_name=google_user.get("given_name"),
            family_name=google_user.get("family_name"),
            picture=google_user.get("picture"),
        )

        # Generate session token
        session_token = AuthService.generate_session_token()

        # Create session (24 hour expiry)
        await AuthRepository.create_session(
            user_id=user["id"],
            token=session_token,
            expires_in_seconds=86400,
        )

        return {
            "access_token": session_token,
            "token_type": "bearer",
            "expires_in": 86400,
            "user": {
                "id": user["id"],
                "email": user["email"],
                "name": user["name"],
                "picture": user["picture"],
                "given_name": user["given_name"],
                "family_name": user["family_name"],
            },
        }

    @staticmethod
    async def validate_session(token: str) -> dict[str, Any] | None:
        """Validate a session token and return user info.

        Args:
            token: The bearer token from Authorization header

        Returns:
            Session with user info or None if invalid

        """
        if not token:
            return None

        session = await AuthRepository.get_session_by_token(token)
        if session:
            # Update last used timestamp (fire and forget)
            await AuthRepository.update_last_used(token)
        return session

    @staticmethod
    async def get_current_user(token: str) -> dict[str, Any] | None:
        """Get current user from token.

        Args:
            token: The bearer token

        Returns:
            User dict or None

        """
        session = await AuthService.validate_session(token)
        if session:
            return session.get("user")
        return None

    @staticmethod
    async def logout(token: str) -> bool:
        """Revoke a session.

        Args:
            token: The bearer token to revoke

        Returns:
            True if session was revoked, False if not found

        """
        return await AuthRepository.revoke_session(token)
