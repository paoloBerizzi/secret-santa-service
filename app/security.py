import base64
import hashlib
import hmac
import re
import secrets

from fastapi import HTTPException, Request
from starlette.datastructures import FormData

COOKIE = 'santa_csrf'
TOKEN_PATTERN = re.compile(r'[A-Za-z0-9_-]{43}')


def new_token() -> str:
    return secrets.token_urlsafe(32)


def digest(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def signature(secret: str, message: str) -> str:
    return hmac.digest(secret.encode(), message.encode(), 'sha256').hex()


def reveal_token(secret: str, event_id: int, participant_id: int, nonce: str) -> str:
    hashed = bytes.fromhex(signature(secret, f'reveal:{event_id}:{participant_id}:{nonce}'))
    return base64.urlsafe_b64encode(hashed).decode().rstrip('=')


def token_digest(token: str) -> str:
    if not TOKEN_PATTERN.fullmatch(token):
        raise HTTPException(404, 'Link not found.')
    return digest(token)


def csrf_value(secret: str, cookie: str) -> str:
    return signature(secret, f'csrf:{cookie}')


async def checked_form(request: Request) -> FormData:
    settings = request.app.state.settings
    origin = request.headers.get('origin')
    cookie = request.cookies.get(COOKIE, '')
    fetch_site = request.headers.get('sec-fetch-site')
    if (origin not in {None, 'null', settings.public_url}
            or fetch_site in {'cross-site', 'same-site'}
            or not TOKEN_PATTERN.fullmatch(cookie)):
        raise HTTPException(403, 'Reload the page and submit the form again.')
    form = await request.form(max_fields=30, max_files=0, max_part_size=8192)
    proof = form.get('csrf')
    if not isinstance(proof, str) or not re.fullmatch(r'[0-9a-f]{64}', proof) or not hmac.compare_digest(
        proof, csrf_value(settings.secret, cookie),
    ):
        raise HTTPException(403, 'Reload the page and submit the form again.')
    return form