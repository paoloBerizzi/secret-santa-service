import os
import secrets
from dataclasses import dataclass
from urllib.parse import urlsplit


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