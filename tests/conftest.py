import re

import pytest
from starlette.testclient import TestClient

from app.config import Settings
from app.main import create_app
from app.models import Base


class Browser(TestClient):
    def submit(self, path, *, headers=None, **fields):
        return self.post(path, data={'csrf': self.csrf, **fields}, headers=headers)

    def event(self, title='Family exchange'):
        return self.submit('/events', title=title, budget='25.50', currency='USD', exchange_date='2026-12-24')


@pytest.fixture
def browser(tmp_path):
    origin = 'https://santa.test'
    app = create_app(Settings(f'sqlite:///{tmp_path / "santa.db"}', 'test-secret' * 4, origin))
    Base.metadata.create_all(app.state.engine)
    with Browser(app, base_url=origin, follow_redirects=False) as client:
        client.cookies.set('santa_language', 'en')
        client.csrf = re.search(r'name="csrf" value="([0-9a-f]{64})"', client.get('/').text)[1]
        yield client
    app.state.engine.dispose()