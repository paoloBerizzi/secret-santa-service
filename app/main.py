from pathlib import Path
from urllib.parse import urlsplit

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.staticfiles import StaticFiles

from app.config import Settings
from app.db import make_engine
from app.i18n import language, translate
from app.routes import admin, events, page, reveal


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    app.state.settings = settings
    app.state.engine = make_engine(settings.database_url)
    host = urlsplit(settings.public_url).hostname
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=[host, 'healthcheck.railway.app'])

    @app.middleware('http')
    async def privacy_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers['Referrer-Policy'] = 'no-referrer'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Content-Security-Policy'] = (
            "default-src 'none'; script-src 'self'; style-src 'self' https://cdn.jsdelivr.net; "
            "img-src 'self'; connect-src 'self'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'"
        )
        if not request.url.path.startswith('/static/'):
            response.headers['Cache-Control'] = 'no-store'
            response.headers['X-Robots-Tag'] = 'noindex, nofollow'
        return response

    @app.exception_handler(HTTPException)
    def http_error(request: Request, exc: HTTPException):
        locale = language(request)
        if isinstance(exc.detail, dict):
            values = {key: translate(locale, value) if key == 'field' else value
                      for key, value in exc.detail.items() if key != 'message'}
            message = translate(locale, exc.detail['message'], **values)
        else:
            message = translate(locale, str(exc.detail))
        return page(request, 'error.html', status_code=exc.status_code, message=message)

    @app.exception_handler(RequestValidationError)
    def invalid_request(request: Request, exc: RequestValidationError):
        return page(request, 'error.html', status_code=422, message=translate(language(request), 'The request was not valid.'))

    @app.get('/healthz')
    def health():
        return {'status': 'ok'}

    app.include_router(events.router)
    app.include_router(admin.router)
    app.include_router(reveal.router)
    app.mount('/static', StaticFiles(directory=Path(__file__).parent / 'static', check_dir=False), name='static')
    return app