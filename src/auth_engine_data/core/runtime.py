"""Populate os.environ so auth_engine library modules can import during seeding."""

from __future__ import annotations

import json
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from auth_engine_data.core.settings import SeedSettings

# Satisfy auth_engine.core.config.Settings validation — not used by the seed CLI.
_LIBRARY_STUBS: dict[str, str] = {
    "APP_NAME": "auth-engine-data",
    "APP_VERSION": "0.0.0",
    "APP_DESCRIPTION": "AuthEngine data seeding CLI",
    "DEBUG": "false",
    "APP_URL": "http://localhost:8000",
    "API_V1_PREFIX": "/api/v1",
    "ALGORITHM": "HS256",
    "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
    "REFRESH_TOKEN_EXPIRE_DAYS": "7",
    "MONGODB_URL": "mongodb://localhost:27017",
    "MONGODB_DB_NAME": "authengine",
    "REDIS_URL": "redis://localhost:6379",
    "REDIS_DB": "0",
    "REDIS_MAX_CONNECTIONS": "10",
    "JWT_ALGORITHM": "HS256",
    "JWT_ISSUER": "authengine",
    "JWT_AUDIENCE": "authengine-api",
    "OIDC_PRIVATE_KEY_PATH": "/dev/null",
    "RATE_LIMIT_PER_MINUTE": "1000",
    "RATE_LIMIT_ENABLED": "false",
    "MAX_CONCURRENT_SESSIONS": "5",
    "SESSION_TIMEOUT_MINUTES": "60",
    "AWS_REGION": "us-east-1",
    "WEBAUTHN_RP_ID": "localhost",
    "CORS_ORIGINS": json.dumps(["http://localhost:3000"]),
}


def configure_library_runtime(seed: SeedSettings) -> None:
    """Apply seed settings and library stubs before importing auth_engine."""
    values = {
        **_LIBRARY_STUBS,
        "POSTGRES_URL": seed.POSTGRES_URL,
        "POSTGRES_POOL_SIZE": str(seed.POSTGRES_POOL_SIZE),
        "POSTGRES_MAX_OVERFLOW": str(seed.POSTGRES_MAX_OVERFLOW),
        "SECRET_KEY": seed.SECRET_KEY,
        "JWT_SECRET_KEY": seed.SECRET_KEY,
    }
    for key, value in values.items():
        os.environ.setdefault(key, value)
