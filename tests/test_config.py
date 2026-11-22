import pytest

from app.config import Settings
from app.db import make_engine


@pytest.mark.parametrize('prefix', ['postgres://', 'postgresql://', 'postgresql+psycopg://'])
def test_postgres_database_url_uses_installed_driver(monkeypatch, prefix):
    monkeypatch.setenv('DATABASE_URL', prefix + 'user:password@postgres.railway.internal:5432/railway')
    monkeypatch.setenv('PUBLIC_BASE_URL', 'https://santa.test')
    monkeypatch.setenv('APP_SECRET', 'test-secret' * 4)
    settings = Settings.from_env()
    engine = make_engine(settings.database_url)
    try:
        assert engine.dialect.name == 'postgresql'
        assert engine.dialect.driver == 'psycopg'
        assert engine.url.host == 'postgres.railway.internal'
        assert engine.url.database == 'railway'
    finally:
        engine.dispose()


@pytest.mark.parametrize('url', [
    '',
    '${{Postgres.DATABASE_URL}}',
    'postgresql://user:password@${{PGHOST}}:5432/railway',
    'postgresql://user:password@postgres.railway.internal:invalid/railway',
])
def test_invalid_database_url_reports_configuration_error(monkeypatch, url):
    monkeypatch.setenv('DATABASE_URL', url)
    with pytest.raises(RuntimeError, match='DATABASE_URL must be a valid connection URL') as error:
        Settings.from_env()
    assert 'password' not in str(error.value)
