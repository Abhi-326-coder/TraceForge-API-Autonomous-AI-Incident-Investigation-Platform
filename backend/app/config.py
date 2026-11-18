from pathlib import Path

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class Settings(BaseSettings):
    app_name: str = "TraceForge API"
    app_version: str = "0.1.0"
    debug: bool = False

    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    redis_url: str = "redis://localhost:6379/0"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.8-flash"

    github_token: str = Field(default="", validation_alias="GITHUB_PERSONAL_ACCESS_TOKEN")
    github_mcp_url: str = (
        "https://api.githubcopilot.com/mcp/readonly"
    )

    demo_mode: bool = False

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    cors_origins: list[str] = Field(default_factory=list)

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("postgres_user", "postgres_password", "postgres_db")
    @classmethod
    def validate_postgres_value(cls, value: str, info):
        if not value.strip():
            raise ValueError(f"{info.field_name.upper()} must be set and non-empty")
        return value

    @model_validator(mode="after")
    def validate_security_settings(self):
        if not self.debug:
            if len(self.jwt_secret_key) < 32:
                raise ValueError(
                    "JWT_SECRET_KEY must contain at least 32 characters"
                )

            if self.demo_mode:
                raise ValueError(
                    "DEMO_MODE must be disabled outside development"
                )

        if self.access_token_expire_minutes <= 0:
            raise ValueError(
                "Token expiration must be greater than zero"
            )

        if not self.demo_mode and not self.gemini_api_key.strip():
            raise ValueError("GEMINI_API_KEY is required when demo mode is disabled")

        if not self.demo_mode and not self.github_token.strip():
            raise ValueError("GITHUB_PERSONAL_ACCESS_TOKEN is required when demo mode is disabled")

        return self


    @property
    def database_url(self) -> str:
        """Build the database URL from the shared PostgreSQL settings."""
        return URL.create(
            drivername="postgresql+psycopg",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            database=self.postgres_db,
        ).render_as_string(hide_password=False)


settings = Settings()
