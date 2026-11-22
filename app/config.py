import os
import secrets
from dataclasses import dataclass
from urllib.parse import urlsplit

from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError


@dataclass(frozen=True)
class Settings:
    database_url: str
    secret: str
    public_url: str

    @classmethod
    def from_env(cls) -> 'Settings':
        database_url = os.getenv('DATABASE_URL', 'sqlite:///secret-santa.db')
        for prefix in ('postgres://', 'postgresql://'):
            if database_url.startswith(prefix):
                database_url = 'postgresql+psycopg://' + database_url.removeprefix(prefix)
                break
        database_error = (
            'DATABASE_URL must be a valid connection URL with all variable references resolved. '
            'On Railway, reference Postgres.DATABASE_URL only from the app service, '
            'and keep the database service connection URL independent of shared.DATABASE_URL.'
        )
        if '${{' in database_url:
            raise RuntimeError(database_error)
        try:
            make_url(database_url)
        except (ArgumentError, ValueError):
            raise RuntimeError(database_error) from None
        public_url = os.getenv('PUBLIC_BASE_URL', 'http://127.0.0.1:8000').rstrip('/')
        parsed = urlsplit(public_url)
        if (parsed.scheme not in {'http', 'https'} or not parsed.hostname or parsed.path
                or parsed.query or parsed.fragment or parsed.username is not None):
            raise RuntimeError('PUBLIC_BASE_URL must be an HTTP(S) origin.')
        secret = os.getenv('APP_SECRET')
        if (parsed.scheme == 'https' and not secret) or (secret and len(secret) < 32):
            raise RuntimeError('Set APP_SECRET to a persistent random secret of at least 32 characters.')
        if parsed.scheme == 'http' and parsed.hostname not in {'127.0.0.1', 'localhost', '::1'}:
            raise RuntimeError('Use HTTPS outside localhost.')
        return cls(database_url, secret or secrets.token_urlsafe(32), public_url)