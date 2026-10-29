from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    database_url: str

    app_name: str = "TraceForge API"
    app_version: str = "0.1.0"
    debug: bool = True

    gemini_api_key: str
    gemini_model: str = "gemini-3.8-flash"
    
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    redis_url: str = "redis://localhost:6379/0"

    github_token: str = Field(
        validation_alias="GITHUB_PERSONAL_ACCESS_TOKEN"
    )
    github_mcp_url: str = (
        "https://api.githubcopilot.com/mcp/readonly"
    )
    
    demo_mode: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
settings = Settings()