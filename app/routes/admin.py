from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.draws import Database, claim, draw, evaluate, lock, reset
from app.i18n import language
from app.matching import MAX_PARTICIPANTS, MatchResult
from app.models import Event, ExclusionRule, Participant, Subgroup, SubgroupMember
from app.routes import CURRENCIES, Form, event_fields, field_id, page, text
from app.security import reveal_token, token_digest

router = APIRouter(prefix='/admin/{admin_token}')


def get_event(admin_token: str, session: Database) -> Event:
    event = session.scalar(select(Event).where(Event.admin_digest == token_digest(admin_token)))
    if event is None:
        raise HTTPException(404, 'Link not found.')
    return event


Managed = Annotated[Event, Depends(get_event)]


def dashboard(request: Request, session: Session, event: Event, result: MatchResult | None = None):
    people = session.scalars(select(Participant).where(Participant.event_id == event.id).order_by(Participant.id)).all()
    groups = session.scalars(select(Subgroup).where(Subgroup.event_id == event.id).order_by(Subgroup.id)).all()
    members: dict[int, set[int]] = {group.id: set() for group in groups}
    for group_id, person_id in session.execute(select(SubgroupMember.subgroup_id, SubgroupMember.participant_id)
                                               .where(SubgroupMember.event_id == event.id)):
        if group_id in members:
            members[group_id].add(person_id)
    exclusions = session.scalars(select(ExclusionRule).where(ExclusionRule.event_id == event.id)).all()
    settings = request.app.state.settings
    links = {}
    if event.state == 'locked' and event.draw_nonce:
        links = {person.id: f'{settings.public_url}/reveal/{reveal_token(settings.secret, event.id, person.id, event.draw_nonce)}'
                 for person in people}
    return page(request, 'admin.html', event=event, people=people, groups=groups, members=members,
                names={person.id: person.name for person in people}, exclusions=exclusions, links=links,
                currencies=CURRENCIES, admin=request.url.path.split('/')[1:3], validation=result)


def scoped(session: Session, model, event: Event, identifier: int):
    item = session.scalar(select(model).where(model.event_id == event.id, model.id == identifier))
    if item is None:
        raise HTTPException(404, 'Item not found.')
    return item


def finish(session: Session, request: Request):
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, 'That name, membership, or exclusion already exists.') from None
    return RedirectResponse('/' + '/'.join(request.url.path.split('/')[1:3]), 303)


@router.get('')
def view(request: Request, session: Database, event: Managed):
    return dashboard(request, session, event)


@router.post('/validate')
def validate(request: Request, session: Database, event: Managed, form: Form):
    if event.state != 'draft':
        raise HTTPException(409, 'Reset the existing draw first.')
    result = evaluate(session, event, locale=language(request))
    revision = session.scalar(select(Event.revision).where(Event.id == event.id))
    if revision != event.revision:
        raise HTTPException(409, 'The event changed during validation. Reload and check again.')
    result = MatchResult(result.status, result.messages)
    if request.headers.get('HX-Request') == 'true':
        return page(request, 'partials/validation.html', validation=result)
    return dashboard(request, session, event, result)


@router.post('/draw')
def run_draw(request: Request, session: Database, event: Managed, form: Form):
    result = draw(session, event, locale=language(request))
    return dashboard(request, session, event, result) if result.assignments is None else finish(session, request)


@router.post('/lock')
def lock_draw(request: Request, session: Database, event: Managed, form: Form):
    lock(session, event, request.app.state.settings.secret)
    return finish(session, request)


@router.post('/reset')
def reset_draw(request: Request, session: Database, event: Managed, form: Form):
    if form.get('confirmed') != 'on':
        raise HTTPException(422, 'Confirm that the existing draw and all links should be discarded.')
    reset(session, event)
    return finish(session, request)


@router.post('/settings')
def update_settings(request: Request, session: Database, event: Managed, form: Form):
    claim(session, event, 'draft')
    for key, value in event_fields(form).items():
        setattr(event, key, value)
    return finish(session, request)


@router.post('/participants')
def add_participant(request: Request, session: Database, event: Managed, form: Form):
    claim(session, event, 'draft')
    count = session.scalar(select(func.count()).select_from(Participant).where(Participant.event_id == event.id))
    if count is not None and count >= MAX_PARTICIPANTS:
        raise HTTPException(422, {'message': 'An event can have at most {limit} participants.', 'limit': MAX_PARTICIPANTS})
    session.add(Participant(event_id=event.id, name=text(form, 'name', 100, required=True),
                            wishlist=text(form, 'wishlist', 2000)))
    return finish(session, request)


@router.post('/participants/{identifier}/edit', name='edit_participant')
@router.post('/participants/{identifier}/remove', name='remove_participant')
@router.post('/participants/{identifier}/wishlist', name='wishlist_participant')
def change_participant(request: Request, session: Database, event: Managed, form: Form, identifier: int):
    person = scoped(session, Participant, event, identifier)
    action = request.scope['route'].name
    if action == 'wishlist_participant':
        claim(session, event, 'draft', 'drawn', 'locked', bump=False)
        person.wishlist = text(form, 'wishlist', 2000)
    else:
        claim(session, event, 'draft')
        if action == 'remove_participant':
            session.delete(person)
        else:
            person.name = text(form, 'name', 100, required=True)
            person.wishlist = text(form, 'wishlist', 2000)
    return finish(session, request)


@router.post('/subgroups')
def add_subgroup(request: Request, session: Database, event: Managed, form: Form):
    claim(session, event, 'draft')
    session.add(Subgroup(event_id=event.id, name=text(form, 'name', 100, required=True),
                         no_intra_exchange=form.get('no_intra_exchange') == 'on'))
    return finish(session, request)


@router.post('/subgroups/{identifier}/edit', name='edit_subgroup')
@router.post('/subgroups/{identifier}/remove', name='remove_subgroup')
def change_subgroup(request: Request, session: Database, event: Managed, form: Form, identifier: int):
    group = scoped(session, Subgroup, event, identifier)
    claim(session, event, 'draft')
    if request.scope['route'].name == 'remove_subgroup':
        session.delete(group)
    else:
        group.name = text(form, 'name', 100, required=True)
        group.no_intra_exchange = form.get('no_intra_exchange') == 'on'
    return finish(session, request)


@router.post('/subgroups/{identifier}/members')
def add_member(request: Request, session: Database, event: Managed, form: Form, identifier: int):
    group = scoped(session, Subgroup, event, identifier)
    person = scoped(session, Participant, event, field_id(form, 'participant_id'))
    claim(session, event, 'draft')
    session.add(SubgroupMember(event_id=event.id, subgroup_id=group.id, participant_id=person.id))
    return finish(session, request)


@router.post('/subgroups/{identifier}/members/{participant_id}/remove')
def remove_member(request: Request, session: Database, event: Managed, form: Form, identifier: int, participant_id: int):
    membership = session.get(SubgroupMember, (event.id, identifier, participant_id))
    if membership is None:
        raise HTTPException(404, 'Membership not found.')
    claim(session, event, 'draft')
    session.delete(membership)
    return finish(session, request)


@router.post('/exclusions')
def add_exclusion(request: Request, session: Database, event: Managed, form: Form):
    giver = scoped(session, Participant, event, field_id(form, 'giver_id'))
    receiver = scoped(session, Participant, event, field_id(form, 'receiver_id'))
    if giver.id == receiver.id:
        raise HTTPException(422, 'Self-draws are already excluded.')
    claim(session, event, 'draft')
    session.add(ExclusionRule(event_id=event.id, giver_id=giver.id, receiver_id=receiver.id))
    return finish(session, request)


@router.post('/exclusions/{identifier}/remove')
def remove_exclusion(request: Request, session: Database, event: Managed, form: Form, identifier: int):
    rule = scoped(session, ExclusionRule, event, identifier)
    claim(session, event, 'draft')
    session.delete(rule)
    return finish(session, request)