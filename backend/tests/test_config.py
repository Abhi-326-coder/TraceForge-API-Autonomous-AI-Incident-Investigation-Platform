import pytest
from pydantic import ValidationError
from sqlalchemy.engine import make_url

from app.config import Settings


def _settings_kwargs() -> dict[str, object]:
    return {
        "postgres_user": "trace user@local",
        "postgres_password": "password:/@? #",
        "postgres_db": "trace forge",
        "postgres_host": "postgres",
        "postgres_port": 5432,
        "gemini_api_key": "test-gemini-key",
        "GITHUB_PERSONAL_ACCESS_TOKEN": "test-github-token",
        "jwt_secret_key": "test-jwt-secret-key-with-at-least-32-characters",
    }


def test_settings_builds_database_url_from_postgres_components():
    settings = Settings(_env_file=None, **_settings_kwargs())

    database_url = settings.database_url
    parsed_url = make_url(database_url)

    assert parsed_url.drivername == "postgresql+psycopg"
    assert parsed_url.username == "trace user@local"
    assert parsed_url.password == "password:/@? #"
    assert parsed_url.host == "postgres"
    assert parsed_url.port == 5432
    assert parsed_url.database == "trace forge"


@pytest.mark.parametrize("missing_key", [
    "postgres_user", "postgres_password", "postgres_db",
])
def test_settings_requires_each_postgres_credential(missing_key):
    kwargs = _settings_kwargs()
    kwargs.pop(missing_key)

    with pytest.raises(ValidationError, match=missing_key):
        Settings(_env_file=None, **kwargs)


@pytest.mark.parametrize("empty_key", [
    "postgres_user", "postgres_password", "postgres_db",
])
def test_settings_rejects_empty_postgres_credentials(empty_key):
    kwargs = _settings_kwargs()
    kwargs[empty_key] = "  "

    with pytest.raises(ValidationError, match="must be set and non-empty"):
        Settings(_env_file=None, **kwargs)
