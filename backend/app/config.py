from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str

    app_name: str = "TraceForge API"
    app_version: str = "0.1.0"
    debug: bool = True

    gemini_api_key: str
    gemini_model: str = "gemini-3.8-flash"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()