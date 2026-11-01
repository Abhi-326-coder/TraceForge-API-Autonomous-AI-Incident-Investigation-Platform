from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "TraceForge API"
    app_version: str = "0.1.0"
    debug: bool = False

    database_url: str
    redis_url: str = "redis://localhost:6379/0"

    gemini_api_key: str
    gemini_model: str = "gemini-3.8-flash"

    github_token: str = Field(
        validation_alias="GITHUB_PERSONAL_ACCESS_TOKEN"
    )
    github_mcp_url: str = (
        "https://api.githubcopilot.com/mcp/readonly"
    )

    demo_mode: bool = False

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    cors_origins: list[str] = Field(default_factory=list)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

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

        return self


settings = Settings()