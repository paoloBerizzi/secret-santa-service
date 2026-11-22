import re

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

from app.draws import Database
from app.i18n import LANGUAGE_COOKIE, LANGUAGES
from app.models import Event
from app.routes import CURRENCIES, Form, event_fields, page
from app.security import digest, new_token

router = APIRouter()


@router.post('/language')
def change_language(request: Request, form: Form):
    selected = form.get('language')
    if selected not in LANGUAGES:
        raise HTTPException(422, 'The request was not valid.')
    target = form.get('return_to', '/')
    if not isinstance(target, str) or not re.fullmatch(r'/(?:|(?:admin|reveal)/[A-Za-z0-9_-]{43})', target):
        target = '/'
    response = RedirectResponse(target, 303)
    response.set_cookie(LANGUAGE_COOKIE, selected, max_age=31536000, httponly=True,
                        samesite='strict', secure=request.app.state.settings.public_url.startswith('https:'))
    return response


@router.get('/')
def new_event(request: Request):
    return page(request, 'new_event.html', currencies=CURRENCIES)


@router.post('/events')
def create_event(form: Form, session: Database):
    token = new_token()
    session.add(Event(admin_digest=digest(token), **event_fields(form)))
    session.commit()
    return RedirectResponse(f'/admin/{token}', 303)