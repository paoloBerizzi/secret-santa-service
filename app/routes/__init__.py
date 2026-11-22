from datetime import date
from decimal import Decimal
from pathlib import Path
import re
from typing import Annotated

from fastapi import Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from jinja2 import pass_context
from starlette.datastructures import FormData

from app.icons import DEFAULT_ICON, EVENT_ICONS
from app.i18n import language, translate
from app.security import COOKIE, TOKEN_PATTERN, checked_form, csrf_value, new_token

templates = Jinja2Templates(directory=Path(__file__).resolve().parents[1] / 'templates')
Form = Annotated[FormData, Depends(checked_form)]
CURRENCIES = ('USD', 'EUR', 'GBP', 'CAD', 'AUD', 'CHF', 'NZD')
@pass_context
def money(context, amount):
    value = f'{Decimal(amount) / 100:.2f}'
    return value.replace('.', ',') if context.get('locale') == 'it' else value


templates.env.filters['money'] = money


def page(request: Request, name: str, *, status_code: int = 200, **context):
    cookie = request.cookies.get(COOKIE, '')
    fresh = not TOKEN_PATTERN.fullmatch(cookie)
    if fresh:
        cookie = new_token()
    settings = request.app.state.settings
    locale = language(request)
    event = context.get('event')
    reveal = context.get('reveal')
    icon = getattr(event, 'icon', None) or (reveal.get('icon') if reveal else None) or DEFAULT_ICON
    response = templates.TemplateResponse(
        request, name, {'csrf': csrf_value(settings.secret, cookie), 'locale': locale,
                        '_': lambda message, **values: translate(locale, message, **values),
                        'event_icons': EVENT_ICONS, 'event_icon': EVENT_ICONS.get(icon, EVENT_ICONS[DEFAULT_ICON])[0],
                        **context}, status_code=status_code,
    )
    if fresh:
        response.set_cookie(COOKIE, cookie, httponly=True, samesite='strict', secure=settings.public_url.startswith('https:'))
    return response


def text(form: FormData, key: str, limit: int, *, required: bool = False) -> str:
    value = form.get(key, '')
    if not isinstance(value, str) or len(value) > limit or required and not value.strip():
        raise HTTPException(422, {'message': 'Check the {field} field (limit: {limit} characters).',
                      'field': key, 'limit': limit})
    return value.strip()


def field_id(form: FormData, key: str) -> int:
    value = text(form, key, 18)
    if not re.fullmatch(r'[1-9][0-9]*', value):
        raise HTTPException(422, 'Select a participant.')
    return int(value)


def event_fields(form: FormData) -> dict:
    budget = text(form, 'budget', 10)
    currency = text(form, 'currency', 3)
    icon = text(form, 'icon', 20) if 'icon' in form else DEFAULT_ICON
    if icon not in EVENT_ICONS:
        raise HTTPException(422, 'Select a valid event icon.')
    if not re.fullmatch(r'[0-9]{1,7}(?:[.,][0-9]{1,2})?', budget) or currency not in CURRENCIES:
        raise HTTPException(422, 'Enter a nonnegative budget with up to two decimals and select a currency.')
    try:
        exchange_date = date.fromisoformat(text(form, 'exchange_date', 10, required=True))
    except ValueError:
        raise HTTPException(422, 'Enter a valid exchange date.') from None
    return dict(title=text(form, 'title', 100, required=True), icon=icon, budget=int(Decimal(budget.replace(',', '.')) * 100),
                currency=currency, exchange_date=exchange_date, notes=text(form, 'notes', 2000),
                no_reciprocal=form.get('no_reciprocal') == 'on')