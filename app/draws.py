import random
from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, HTTPException, Request
from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from app.matching import MatchResult, solve
from app.models import Assignment, Event, ExclusionRule, Participant, Subgroup, SubgroupMember
from app.security import digest, new_token, reveal_token


def get_session(request: Request) -> Iterator[Session]:
    with Session(request.app.state.engine) as session:
        yield session


Database = Annotated[Session, Depends(get_session)]


def claim(session: Session, event: Event, *states: str, bump: bool = True) -> None:
    result = session.execute(
        update(Event).where(Event.id == event.id, Event.revision == event.revision, Event.state.in_(states))
        .values(revision=Event.revision + int(bump)).execution_options(synchronize_session=False),
    )
    if result.rowcount != 1:
        raise HTTPException(409, 'The event changed or is not editable. Reload or reset the draw first.')


def evaluate(session: Session, event: Event, *, randomized: bool = False, locale: str = 'en') -> MatchResult:
    roster = {person_id: name for person_id, name in session.execute(select(Participant.id, Participant.name).where(
        Participant.event_id == event.id,
    ))}
    groups: dict[str, set[int]] = {}
    for name, participant_id in session.execute(
        select(Subgroup.name, SubgroupMember.participant_id).join(
            SubgroupMember, Subgroup.id == SubgroupMember.subgroup_id,
        ).where(Subgroup.event_id == event.id, Subgroup.no_intra_exchange.is_(True)),
    ):
        groups.setdefault(name, set()).add(participant_id)
    exclusions = {(giver, receiver) for giver, receiver in session.execute(
        select(ExclusionRule.giver_id, ExclusionRule.receiver_id).where(
        ExclusionRule.event_id == event.id,
        ),
    )}
    return solve(roster, groups, exclusions, no_reciprocal=event.no_reciprocal,
                 rng=random.SystemRandom() if randomized else None, locale=locale)


def draw(session: Session, event: Event, *, locale: str = 'en') -> MatchResult:
    if event.state != 'draft':
        raise HTTPException(409, 'Reset the existing draw first.')
    result = evaluate(session, event, randomized=True, locale=locale)
    if result.assignments is not None:
        claim(session, event, 'draft')
        session.add_all(Assignment(event_id=event.id, giver_id=giver, receiver_id=receiver)
                        for giver, receiver in result.assignments.items())
        event.state = 'drawn'
    return result


def lock(session: Session, event: Event, secret: str) -> None:
    claim(session, event, 'drawn')
    nonce = new_token()
    event.draw_nonce = nonce
    for person in session.scalars(select(Participant).where(Participant.event_id == event.id)):
        person.reveal_digest = digest(reveal_token(secret, event.id, person.id, nonce))
    event.state = 'locked'


def reset(session: Session, event: Event) -> None:
    claim(session, event, 'drawn', 'locked')
    session.execute(delete(Assignment).where(Assignment.event_id == event.id))
    session.execute(update(Participant).where(Participant.event_id == event.id).values(reveal_digest=None))
    event.draw_nonce = None
    event.state = 'draft'