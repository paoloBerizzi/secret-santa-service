from html import unescape

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import draws
from app.models import Assignment, Event, Participant, SubgroupMember


def test_csrf_and_event_scope(browser):
    first = browser.event().headers['location']
    second = browser.event('Other exchange').headers['location']
    assert browser.post(first + '/participants', data={'name': 'Alice'}).status_code == 403
    assert browser.submit(first + '/participants', name='Alice', headers={'Origin': 'https://other.test'}).status_code == 403
    assert browser.submit(first + '/participants', name='Alice').status_code == 303
    assert browser.submit(second + '/participants/1/remove').status_code == 404
    assert browser.get('/admin/' + 'a' * 43).status_code == 404
    assert 'Alice' in browser.get(first).text


def test_live_validation_and_group_toggle(browser):
    admin = browser.event().headers['location']
    for name in ('Alice', 'Bob', 'Cora'):
        assert browser.submit(admin + '/participants', name=name).status_code == 303
    assert browser.submit(admin + '/subgroups', name='Household', no_intra_exchange='on').status_code == 303
    for person in ('1', '2'):
        assert browser.submit(admin + '/subgroups/1/members', participant_id=person).status_code == 303
    result = browser.submit(admin + '/validate', headers={'HX-Request': 'true', 'Origin': 'null', 'Sec-Fetch-Site': 'same-origin'})
    assert result.status_code == 200 and 'outnumber' in result.text
    assert '<html' not in result.text
    assert 'outnumber' in browser.submit(admin + '/draw').text
    with Session(browser.app.state.engine) as session:
        assert not session.scalars(select(Assignment)).all()
    assert browser.submit(admin + '/subgroups/1/edit', name='Household').status_code == 303
    assert 'valid draw is possible' in browser.submit(admin + '/validate').text
    assert browser.submit(admin + '/exclusions', giver_id='1', receiver_id='2').status_code == 303
    assert browser.submit(admin + '/exclusions/1/remove').status_code == 303


def test_stale_draw_rolls_back(browser, monkeypatch):
    admin = browser.event().headers['location']
    for name in ('Alice', 'Bob'):
        assert browser.submit(admin + '/participants', name=name).status_code == 303
    evaluate = draws.evaluate

    def stale(session, event, *, randomized=False, locale='en'):
        result = evaluate(session, event, randomized=randomized, locale=locale)
        with Session(browser.app.state.engine) as writer:
            current = writer.get(Event, event.id)
            current.revision += 1
            writer.commit()
        return result

    monkeypatch.setattr(draws, 'evaluate', stale)
    assert browser.submit(admin + '/draw').status_code == 409
    with Session(browser.app.state.engine) as session:
        assert not session.scalars(select(Assignment)).all()
        assert session.get(Event, 1).state == 'draft'


def test_database_rejects_cross_event_membership(browser):
    first = browser.event().headers['location']
    second = browser.event('Other exchange').headers['location']
    assert browser.submit(first + '/subgroups', name='Household').status_code == 303
    assert browser.submit(second + '/participants', name='Alice').status_code == 303
    with Session(browser.app.state.engine) as session:
        person = session.scalar(select(Participant))
        session.add(SubgroupMember(event_id=1, subgroup_id=1, participant_id=person.id))
        with pytest.raises(IntegrityError):
            session.commit()


def test_italian_default_switching_and_localized_validation(browser):
    browser.cookies.delete('santa_language')
    setup = browser.get('/')
    assert '<html lang="it">' in setup.text
    assert 'Nuovo scambio' in setup.text and "Titolo dell'evento" in unescape(setup.text)
    assert '<option selected>EUR</option>' in setup.text
    created = browser.submit('/events', title='Famiglia', budget='25,50', currency='EUR', exchange_date='2026-12-24')
    admin = created.headers['location']
    dashboard = browser.get(admin)
    assert '<span class="brand">Secret Santa - Famiglia</span>' in dashboard.text
    assert 'Partecipanti' in dashboard.text and '25,50' in dashboard.text
    assert 'da 2 a 32 partecipanti' in browser.submit(admin + '/validate', headers={'HX-Request': 'true'}).text
    for name in ('Anna', 'Bruno', 'Carla'):
        assert browser.submit(admin + '/participants', name=name).status_code == 303
    assert browser.submit(admin + '/subgroups', name='Casa', no_intra_exchange='on').status_code == 303
    for participant in ('1', '2'):
        assert browser.submit(admin + '/subgroups/1/members', participant_id=participant).status_code == 303
    result = browser.submit(admin + '/validate', headers={'HX-Request': 'true'})
    assert 'Casa:' in result.text and 'destinatari disponibili fuori dal sottogruppo' in result.text
    assert browser.get('/admin/' + 'a' * 43).status_code == 404
    assert 'Link non trovato.' in browser.get('/admin/' + 'a' * 43).text

    changed = browser.submit('/language', language='en', return_to=admin)
    assert changed.status_code == 303 and changed.headers['location'] == admin
    assert 'Participants' in browser.get(admin).text
    assert 'outnumber' in browser.submit(admin + '/validate', headers={'HX-Request': 'true'}).text
    assert browser.submit('/language', language='xx', return_to=admin).status_code == 422
    assert browser.post('/language', data={'language': 'it', 'return_to': admin}).status_code == 403
    assert browser.submit('/language', language='it', return_to='//evil.example').headers['location'] == '/'
    assert 'Nuovo scambio' in browser.get('/').text


def test_italian_field_errors_and_invalid_language_cookie(browser):
    browser.cookies.set('santa_language', 'invalid')
    assert 'Nuovo scambio' in browser.get('/').text
    response = browser.submit('/events', title='', budget='25', currency='EUR', exchange_date='2026-12-24')
    assert response.status_code == 422
    assert 'Controlla il campo titolo' in response.text


def test_event_icon_is_validated_and_persisted(browser):
    fields = dict(title='Family', budget='25', currency='EUR', exchange_date='2026-12-24')
    assert browser.submit('/events', **fields, icon='invalid').status_code == 422
    admin = browser.submit('/events', **fields, icon='snowman').headers['location']
    with Session(browser.app.state.engine) as session:
        assert session.get(Event, 1).icon == 'snowman'
    dashboard = browser.get(admin).text
    assert '<span class="mark" aria-hidden="true">⛄</span>' in dashboard
    assert '<span class="woodland-fox fox-one">⛄</span>' in dashboard
    assert 'class="masthead-fox"' not in dashboard
    assert '🌲' in dashboard and '🎁' in dashboard
    assert 'value="snowman" aria-label="Snowman" checked' in dashboard
    assert browser.submit(admin + '/settings', **fields, icon='star').status_code == 303
    with Session(browser.app.state.engine) as session:
        assert session.get(Event, 1).icon == 'star'
    assert '<span class="mark" aria-hidden="true">⭐</span>' in browser.get(admin).text
    assert browser.submit(admin + '/settings', **fields, icon='invalid').status_code == 422
    with Session(browser.app.state.engine) as session:
        assert session.get(Event, 1).icon == 'star'