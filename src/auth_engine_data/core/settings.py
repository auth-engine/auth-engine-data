"""Seed-only settings — not part of the auth-engine runtime."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SeedSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env.local", env_prefix="", case_sensitive=True, extra="ignore"
    )

    POSTGRES_URL: str = Field(..., description="PostgreSQL connection URL")
    POSTGRES_POOL_SIZE: int = Field(default=5, ge=1)
    POSTGRES_MAX_OVERFLOW: int = Field(default=5, ge=0)
    POSTGRES_SSL: bool = Field(
        default=False,
        description="Enable SSL for PostgreSQL (set true for hosted databases)",
    )
    SECRET_KEY: str = Field(
        ...,
        min_length=32,
        description="Encryption key — must match auth-engine SECRET_KEY for platform config seed",
    )

    SUPERADMIN_EMAIL: str = Field(..., description="Super admin email for seeding")
    SUPERADMIN_PASSWORD: str = Field(..., min_length=8, description="Super admin password for seeding")

    EMAIL_PROVIDER: str = Field(default="ses", description="Platform tenant email provider")
    EMAIL_PROVIDER_API_KEY: str = Field(default="", description="Platform tenant email API key")
    EMAIL_SENDER: str = Field(default="noreply@authengine.org", description="Platform tenant from address")

    SMS_PROVIDER: str = Field(default="android_gateway", description="Platform tenant SMS provider")
    SMS_GATEWAY_URL: str = Field(default="", description="Android SMS gateway base URL")
    SMS_GATEWAY_USERNAME: str = Field(default="", description="Android SMS gateway username")
    SMS_GATEWAY_PASSWORD: str = Field(default="", description="Android SMS gateway password")
    SMS_SENDER: str = Field(default="gateway", description="Platform tenant SMS sender id")

    GOOGLE_CLIENT_ID: str = Field(default="", description="Google OAuth client id")
    GOOGLE_CLIENT_SECRET: str = Field(default="", description="Google OAuth client secret")
    GOOGLE_REDIRECT_URI: str = Field(default="", description="Google OAuth redirect URI")

    AUTHENGINE_BASE_URL: str = Field(default="", description="AuthEngine OIDC issuer / discovery base URL")
    AUTHENGINE_CLIENT_ID: str = Field(default="", description="AuthEngine OIDC client id")
    AUTHENGINE_CLIENT_SECRET: str = Field(default="", description="AuthEngine OIDC client secret")
    AUTHENGINE_REDIRECT_URI: str = Field(default="", description="AuthEngine OIDC redirect URI")

    PASSWORD_MIN_LENGTH: int = Field(default=8, ge=1)
    PASSWORD_REQUIRE_UPPERCASE: bool = Field(default=True)
    PASSWORD_REQUIRE_LOWERCASE: bool = Field(default=True)
    PASSWORD_REQUIRE_DIGIT: bool = Field(default=True)
    PASSWORD_REQUIRE_SPECIAL: bool = Field(default=True)


settings = SeedSettings()  # type: ignore[call-arg]
