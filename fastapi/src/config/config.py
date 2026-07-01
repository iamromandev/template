from functools import lru_cache
from typing import Annotated

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.core.type import Env


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- core ---
    env: Annotated[Env, Field(description="Application environment")]
    debug: Annotated[bool, Field(description="Enable debug mode")]
    log_format: Annotated[str, Field(default="text", description="text | json")]

    # --- db ---
    db_schema: Annotated[str, Field(description="Database schema label")]
    db_host: Annotated[str, Field(description="Database host")]
    db_port: Annotated[int, Field(description="Database port")]
    db_name: Annotated[str, Field(description="Database name")]
    db_user: Annotated[str, Field(description="Database user")]
    db_password: Annotated[SecretStr, Field(description="Database password")]

    # --- cors ---
    cors_origins: str = ""

    # --- auth ---
    jwt_secret: Annotated[SecretStr, Field(description="JWT signing secret")]
    jwt_algorithm: Annotated[str, Field(default="HS256", description="JWT algorithm")]
    jwt_access_token_expire_minutes: Annotated[int, Field(default=30, ge=1)]
    jwt_refresh_token_expire_days: Annotated[int, Field(default=7, ge=1)]

    # --- cache ---
    redis_host: Annotated[str, Field(default="redis")]
    redis_port: Annotated[int, Field(default=6379)]
    redis_db: Annotated[int, Field(default=0)]
    redis_password: Annotated[SecretStr | None, Field(default=None)]
    cache_ttl_default: Annotated[int, Field(default=300, ge=1)]

    # --- observability ---
    metrics_enabled: Annotated[bool, Field(default=True)]

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
