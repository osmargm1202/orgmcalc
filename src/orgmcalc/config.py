"""Application configuration via pydantic-settings."""

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    base_url: str = Field(
        default="http://localhost:8000",
        description="Base URL for the application (used for OAuth callbacks)",
    )

    # Database
    database_url: PostgresDsn = Field(
        default="postgresql://user:password@localhost:5432/orgmcalc",
        description="PostgreSQL connection string",
    )

    # OAuth (Phase 2)
    google_client_id: str = Field(
        default="",
        description="Google OAuth client ID",
    )
    google_client_secret: str = Field(
        default="",
        description="Google OAuth client secret",
    )

    # Object Storage (Phase 7)
    r2_endpoint_url: str = Field(
        default="",
        description="R2/S3-compatible endpoint URL",
    )
    r2_access_key_id: str = Field(
        default="",
        description="R2 access key ID",
    )
    r2_secret_access_key: str = Field(
        default="",
        description="R2 secret access key",
    )
    r2_bucket_name: str = Field(
        default="orgmcalc-uploads",
        description="R2 bucket name for file storage",
    )

    @property
    def database_dsn(self) -> str:
        """Return database URL as string."""
        return str(self.database_url)


def get_settings() -> Settings:
    """Factory for settings singleton."""
    return Settings()
