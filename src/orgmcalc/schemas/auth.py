"""Authentication schemas for OAuth and session management."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class OAuthStartRequest(BaseModel):
    """Request to initiate OAuth flow.

    Contains optional state parameter for CSRF protection.
    """

    model_config = ConfigDict(
        json_schema_extra={"example": {"redirect_uri": "http://localhost:3000/auth/callback"}}
    )

    redirect_uri: str | None = Field(
        default=None, description="URI de redirección opcional (si no se usa la default)"
    )


class OAuthCallbackRequest(BaseModel):
    """Request for OAuth callback.

    Contains the authorization code from Google.
    """

    model_config = ConfigDict(
        json_schema_extra={"example": {"code": "4/0AX4XfWg...", "state": "random-state-string"}}
    )

    code: str = Field(..., description="Código de autorización proporcionado por Google")
    state: str | None = Field(default=None, description="Estado CSRF para validación")


class TokenResponse(BaseModel):
    """Response containing authentication token.

    Returned after successful OAuth completion.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIs...",
                "token_type": "bearer",
                "expires_in": 86400,
                "user": {
                    "id": "auth-user-uuid",
                    "email": "user@example.com",
                    "name": "Usuario Ejemplo",
                    "picture": "https://lh3.googleusercontent.com/...",
                },
            }
        }
    )

    access_token: str = Field(
        ..., description="Token de acceso para autenticación (opaque bearer token)"
    )
    token_type: str = Field(default="bearer", description="Tipo de token (siempre 'bearer')")
    expires_in: int = Field(..., description="Segundos hasta que expire el token")
    user: UserInfo = Field(..., description="Información del usuario autenticado")


class UserInfo(BaseModel):
    """User information from Google OAuth.

    Basic profile information of the authenticated user.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "auth-user-uuid",
                "email": "user@example.com",
                "name": "Usuario Ejemplo",
                "picture": "https://lh3.googleusercontent.com/a-/...",
                "given_name": "Usuario",
                "family_name": "Ejemplo",
            }
        }
    )

    id: str = Field(..., description="Identificador único del usuario en el sistema")
    email: str = Field(..., description="Correo electrónico del usuario")
    name: str | None = Field(default=None, description="Nombre completo del usuario")
    picture: str | None = Field(default=None, description="URL de la foto de perfil")
    given_name: str | None = Field(default=None, description="Nombre de pila")
    family_name: str | None = Field(default=None, description="Apellido(s)")


class LogoutResponse(BaseModel):
    """Response after successful logout."""

    model_config = ConfigDict(
        json_schema_extra={"example": {"message": "Sesión cerrada correctamente"}}
    )

    message: str = Field(
        default="Sesión cerrada correctamente", description="Mensaje de confirmación"
    )


class AuthErrorResponse(BaseModel):
    """Error response for authentication failures."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"detail": "Token inválido o expirado", "error_code": "invalid_token"}
        }
    )

    detail: str = Field(..., description="Descripción del error")
    error_code: str | None = Field(default=None, description="Código de error para debugging")
