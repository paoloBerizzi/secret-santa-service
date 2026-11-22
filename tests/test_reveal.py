import re
from html import unescape
from urllib.parse import urlsplit

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Assignment, Participant


def links(response):
    return [urlsplit(url).path for url in re.findall(r'data-copy="(https://santa.test/reveal/[^\"]+)"', response.text)]


def test_draw_reveal_wishlist_and_reset(browser):
    admin = browser.event().headers['location']
    names = ('Anouk', 'Bastien', 'Camille', 'Daria')
    for name in names:
        assert browser.submit(admin + '/participants', name=name, wishlist=f'Ideas for {name} <script>').status_code == 303
    assert browser.submit(admin + '/draw').status_code == 303
    assert not links(browser.get(admin))
    assert browser.submit(admin + '/participants', name='Extra').status_code == 409
    assert browser.submit(admin + '/lock').status_code == 303
    private_links = links(browser.get(admin))
    assert len(set(private_links)) == len(names)
    with Session(browser.app.state.engine) as session:
        orders = {giver: recipient for giver, recipient in session.execute(select(Assignment.giver_id, Assignment.receiver_id))}
    for giver, recipient in orders.items():
        link = private_links[giver - 1]
        page = browser.get(link)
        assert page.status_code == 200
        assert page.headers['Cache-Control'] == 'no-store'
        assert page.headers['Referrer-Policy'] == 'no-referrer'
        assert '<span class="brand">Secret Santa - Family exchange</span>' in page.text
        assert '<p class="eyebrow">Family exchange</p>' not in page.text
        assert f'<h1>Welcome, {names[giver - 1]}!</h1>' in page.text
        assert f'<h2 class="reveal-recipient">{names[recipient - 1]}</h2>' in page.text
        assert f"<h2>{names[recipient - 1]}'s wishlist</h2>" in unescape(page.text)
        assert 'USD 25.50' in page.text and '2026-12-24' in page.text
        assert ' &lt;script&gt;' in page.text
        assert all(other not in page.text for other in private_links if other != link)
        assert all(name not in page.text for name in set(names) - {names[giver - 1], names[recipient - 1]})
    assert browser.submit(private_links[0] + '/wishlist', wishlist='Updated hints', participant_id='2').status_code == 303
    with Session(browser.app.state.engine) as session:
        assert session.get(Participant, 1).wishlist == 'Updated hints'
        assert 'Bastien' in session.get(Participant, 2).wishlist
    incoming = next(giver for giver, recipient in orders.items() if recipient == 1)
    assert 'Updated hints' in browser.get(private_links[incoming - 1]).text
    assert browser.submit(admin + '/reset').status_code == 422
    assert browser.submit(admin + '/reset', confirmed='on').status_code == 303
    for link in private_links:
        assert browser.get(link).status_code == 404
        assert browser.submit(link + '/wishlist', wishlist='Old link').status_code == 404
    assert browser.submit(admin + '/draw').status_code == 303
    assert browser.submit(admin + '/lock').status_code == 303
    assert set(links(browser.get(admin))).isdisjoint(private_links)


def test_reveal_language_is_per_browser_and_preserves_private_link(browser):
    admin = browser.event().headers['location']
    for name in ('Anna', 'Bruno'):
        assert browser.submit(admin + '/participants', name=name, wishlist='Un libro').status_code == 303
    assert browser.submit(admin + '/draw').status_code == 303
    assert browser.submit(admin + '/lock').status_code == 303
    private_links = links(browser.get(admin))
    changed = browser.submit('/language', language='it', return_to=private_links[0])
    assert changed.headers['location'] == private_links[0]
    reveal = browser.get(private_links[0])
    assert '<html lang="it">' in reveal.text
    assert '<h1>Ciao, Anna!</h1>' in reveal.text
    assert 'Il tuo regalo è per' in reveal.text
    assert '<h2 class="reveal-recipient">Bruno</h2>' in reveal.text
    assert '<h2>Lista dei desideri di Bruno</h2>' in reveal.text
    assert 'La tua lista dei desideri' in reveal.text and 'Un libro' in reveal.text
    assert 'USD 25,50' in reveal.text and '24/12/2026' in reveal.text
    assert private_links[1] not in reveal.text
    assert browser.submit(private_links[0] + '/wishlist', wishlist='Un gioco').status_code == 303
    assert 'Un gioco' in browser.get(private_links[0]).text
    assert browser.submit('/language', language='en', return_to=private_links[0]).status_code == 303
    english = unescape(browser.get(private_links[0]).text)
    assert '<h1>Welcome, Anna!</h1>' in english and "You're giving to" in english


def test_reveal_escapes_participant_names(browser):
    admin = browser.event().headers['location']
    for name in ('<script>alert(1)</script>', 'Bruno'):
        assert browser.submit(admin + '/participants', name=name).status_code == 303
    assert browser.submit(admin + '/draw').status_code == 303
    assert browser.submit(admin + '/lock').status_code == 303
    first, second = links(browser.get(admin))
    assert '<h1>Welcome, &lt;script&gt;alert(1)&lt;/script&gt;!</h1>' in browser.get(first).text
    assert '<h2 class="reveal-recipient">&lt;script&gt;alert(1)&lt;/script&gt;</h2>' in browser.get(second).text
    assert '<h2>&lt;script&gt;alert(1)&lt;/script&gt;&#39;s wishlist</h2>' in browser.get(second).text


def test_wishlist_placeholder_is_not_saved_and_existing_wishes_remain(browser):
    admin = browser.event().headers['location']
    for name in ('Anna', 'Bruno'):
        assert browser.submit(admin + '/participants', name=name).status_code == 303
    assert browser.submit(admin + '/draw').status_code == 303
    assert browser.submit(admin + '/lock').status_code == 303
    link = links(browser.get(admin))[0]
    page = browser.get(link).text
    assert 'aria-label="Your wishlist"' in page
    assert 'placeholder="Enter gift ideas you would like to receive this year."' in page
    assert re.search(r'<textarea name="wishlist"[^>]*></textarea>', page)
    assert browser.submit(link + '/wishlist', wishlist='').status_code == 303
    with Session(browser.app.state.engine) as session:
        assert session.get(Participant, 1).wishlist == ''
    assert browser.submit(link + '/wishlist', wishlist='A book').status_code == 303
    assert '>A book</textarea>' in browser.get(link).text
    assert browser.submit('/language', language='it', return_to=link).status_code == 303
    italian = browser.get(link).text
    assert 'aria-label="La tua lista dei desideri"' in italian
    assert 'Inserisci qui le idee regalo che vorresti ricevere quest’anno.' in italian
    assert '>A book</textarea>' in italian


def test_reveal_uses_event_icon(browser):
    created = browser.submit('/events', title='Family', budget='25', currency='EUR',
                             exchange_date='2026-12-24', icon='reindeer')
    admin = created.headers['location']
    for name in ('Anna', 'Bruno'):
        assert browser.submit(admin + '/participants', name=name).status_code == 303
    assert browser.submit(admin + '/draw').status_code == 303
    assert browser.submit(admin + '/lock').status_code == 303
    reveal = browser.get(links(browser.get(admin))[0]).text
    assert '<span class="mark" aria-hidden="true">🦌</span>' in reveal
    assert '<span class="woodland-fox fox-one">🦌</span>' in reveal
    assert '🌲' in reveal and '🎁' in reveal
    assert 'class="masthead-fox"' not in reveal