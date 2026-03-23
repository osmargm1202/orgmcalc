"""Authentication routes - Google OAuth flow."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse

from orgmcalc.api.dependencies import AuthRequiredDep, security
from orgmcalc.schemas.auth import LogoutResponse, TokenResponse, UserInfo
from orgmcalc.services.auth import AuthService

router = APIRouter(tags=["auth"])


@router.get("/auth/google")
async def start_oauth_flow(
    request: Request,
    redirect_uri: str | None = None,
) -> RedirectResponse:
    """Start Google OAuth flow.

    Redirects the user to Google for authentication.
    After successful auth, Google redirects to /auth/google/callback.

    Args:
        request: FastAPI request object
        redirect_uri: Optional custom redirect URI for the callback

    Returns:
        Redirect to Google's OAuth consent screen

    """
    # Generate authorization URL
    auth_url = AuthService.get_google_authorization_url(redirect_uri)
    return RedirectResponse(url=auth_url, status_code=302)


@router.get("/auth/google/callback")
async def oauth_callback(
    code: str = Query(..., description="Authorization code from Google"),
    state: str | None = Query(None, description="CSRF state parameter"),
) -> TokenResponse:
    """Handle Google OAuth callback.

    Exchanges the authorization code for an access token,
    creates or updates the user, and returns a session token.

    Args:
        code: Authorization code from Google
        state: Optional state parameter for CSRF validation

    Returns:
        Token response with bearer token and user info

    Raises:
        HTTPException: 400 if OAuth flow fails

    """
    try:
        result = await AuthService.handle_oauth_callback(code)
        return TokenResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth callback failed: {str(e)}",
        )


@router.post("/auth/logout", response_model=LogoutResponse)
async def logout(
    credentials: Annotated[object, Depends(security)],
) -> LogoutResponse:
    """Revoke current session.

    Invalidates the bearer token, requiring re-authentication.

    Args:
        credentials: Bearer token from Authorization header

    Returns:
        Logout confirmation message

    Raises:
        HTTPException: 401 if no valid token provided

    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    await AuthService.logout(token)

    return LogoutResponse(message="Sesión cerrada correctamente")


@router.get("/auth/me", response_model=UserInfo)
async def get_current_user_info(
    user: AuthRequiredDep,
) -> UserInfo:
    """Get current user information.

    Returns the profile information of the authenticated user.

    Args:
        user: Authenticated user from dependency

    Returns:
        User profile information

    Raises:
        HTTPException: 401 if not authenticated

    """
    return UserInfo(**user)
