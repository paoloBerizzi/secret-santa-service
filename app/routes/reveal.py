from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import aliased

from app.draws import Database, claim
from app.models import Assignment, Event, Participant
from app.routes import Form, page, text
from app.security import token_digest

router = APIRouter(prefix='/reveal/{participant_token}')


@router.get('')
def reveal(request: Request, participant_token: str, session: Database):
    recipient = aliased(Participant)
    row = session.execute(
         select(Event.title, Event.icon, Event.budget, Event.currency, Event.exchange_date, Event.notes,
             Participant.name.label('own_name'), Participant.wishlist.label('own_wishlist'), recipient.name.label('recipient_name'),
               recipient.wishlist.label('recipient_wishlist'))
        .join(Participant, Participant.event_id == Event.id)
        .join(Assignment, (Assignment.event_id == Event.id) & (Assignment.giver_id == Participant.id))
        .join(recipient, (recipient.event_id == Event.id) & (recipient.id == Assignment.receiver_id))
        .where(Event.state == 'locked', Participant.reveal_digest == token_digest(participant_token)),
    ).mappings().one_or_none()
    if row is None:
        raise HTTPException(404, 'Link not found.')
    return page(request, 'reveal.html', reveal=row)


@router.post('/wishlist')
def save_wishlist(request: Request, participant_token: str, form: Form, session: Database):
    hashed = token_digest(participant_token)
    row = session.execute(select(Event, Participant).join(Participant, Participant.event_id == Event.id)
                          .where(Event.state == 'locked', Participant.reveal_digest == hashed)).one_or_none()
    if row is None:
        raise HTTPException(404, 'Link not found.')
    event, participant = row
    try:
        claim(session, event, 'locked', bump=False)
    except HTTPException:
        raise HTTPException(404, 'Link not found.') from None
    participant.wishlist = text(form, 'wishlist', 2000)
    session.commit()
    return RedirectResponse(request.url.path.removesuffix('/wishlist'), 303)