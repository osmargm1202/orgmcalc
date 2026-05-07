"""Application configuration via pydantic-settings."""

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    database_url: str = Field(
        default="postgresql://user:password@localhost:5432/orgmcalc",
        description="PostgreSQL connection string",
    )

    # Auth
    auth_api_url: str = Field(
        default="https://auth.or-gm.com",
        description="OrgAuth base URL used for JWKS discovery",
    )

    # Object Storage (Phase 7)
    r2_endpoint_url: str = Field(
        default="",
        description="R2/S3-compatible endpoint URL",
        validation_alias=AliasChoices("R2_ENDPOINT_URL", "CLOUDFLARE_R2_ENDPOINT_URL"),
    )
    r2_access_key_id: str = Field(
        default="",
        description="R2 access key ID",
        validation_alias=AliasChoices("R2_ACCESS_KEY_ID", "CLOUDFLARE_R2_ACCESS_KEY_ID"),
    )
    r2_secret_access_key: str = Field(
        default="",
        description="R2 secret access key",
        validation_alias=AliasChoices("R2_SECRET_ACCESS_KEY", "CLOUDFLARE_R2_SECRET_ACCESS_KEY"),
    )
    r2_bucket_name: str = Field(
        default="orgmcalc-uploads",
        description="R2 bucket name for file storage",
        validation_alias=AliasChoices("R2_BUCKET_NAME", "CLOUDFLARE_R2_BUCKET"),
    )

    @property
    def database_dsn(self) -> str:
        """Return database URL as string."""
        return self.database_url


def get_settings() -> Settings:
    """Factory for settings singleton."""
    return Settings()
