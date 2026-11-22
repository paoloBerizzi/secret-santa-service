# Secret Santa Service

A small, self-hosted web app for organizing a family gift exchange. No accounts or Node build required.

## Local setup

Requirements: Python 3.12 or newer and [uv](https://docs.astral.sh/uv/getting-started/installation/). From the repository directory, install the locked dependencies:

```sh
uv sync --locked
```

Generate a secret once, store it securely, and reuse the same value every time the service starts:

```sh
uv run python -c 'import secrets; print(secrets.token_urlsafe(32))'
```

Set these variables in the shell that will run the service, replacing the placeholder with your saved secret:

```sh
export APP_SECRET='your-saved-random-secret-at-least-32-characters'
export DATABASE_URL='sqlite:///secret-santa.db'
export PUBLIC_BASE_URL='http://127.0.0.1:8000'
```

`PUBLIC_BASE_URL` must be the exact origin used in the browser, including the port, with no trailing path. Use HTTPS for non-local hosts. Environment variables must be set in the shell or hosting platform: `.env.example` is a reference and is not loaded automatically. Never commit your secret. Without a configured `APP_SECRET`, localhost generates a temporary one on startup; participant links generated after a restart may not match the stored links, so reset and reissue them if necessary.

Create the database and start the app:

```sh
uv run alembic upgrade head
uv run uvicorn app.main:create_app --factory --reload --no-access-log
```

Open `http://127.0.0.1:8000`. The default SQLite database is `secret-santa.db` in the working directory. A localhost address only works on this computer; deploy the service at an HTTPS address before sending links to people on other devices.

## Organizer guide

1. On the first page, enter the event title, choose an icon, and enter the budget, currency, exchange date, and optional notes. Select **Escludi gli scambi reciproci** if two people must not draw each other. Click **Crea evento**. You can change the icon in event details while the event is a draft.
2. The app immediately opens the private organizer dashboard at `/admin/<admin_token>`. Use **Copia il link organizzatore** and store the link somewhere safe. Anyone with it can manage the event; there is no login or recovery if the link is lost. Each event has its own dashboard link.
3. Under **Partecipanti**, add each person's name and optionally their gift ideas. Open a participant's name to edit or remove them. Events support 2 to 32 participants.
4. Optionally add **Sottogruppi** for households or couples, add members, and enable **Escludi scambi nel gruppo**. Members of an enabled subgroup cannot draw one another; people may be in more than one subgroup. Under **Esclusioni individuali**, add one-way exclusions for particular givers and recipients.
5. Use **Verifica le regole** to check feasibility. Fix any reported restrictions, then choose **Avvia l'estrazione**. The app assigns everyone one recipient and everyone receives one gift; it does not display all pairings on the dashboard.
6. Choose **Blocca e attiva i link**. For each person, copy their **Link privato** and send it only to that person. The service does not send emails or messages automatically.
7. Once locked, event settings, participants, and rules cannot be changed, but wishlists remain editable. To change the draw, confirm and choose **Annulla l'estrazione**; this deletes the assignments and invalidates the old participant links. Draw and lock again and send the new links. Reset cannot make someone forget a recipient they already saw.

## Participant guide

1. Open the private link sent by the organizer. It shows your assigned recipient, the gift budget and date, and your recipient's gift ideas. Keep the link private: anyone with it can see this information and edit your wishlist.
2. Under **La tua lista dei desideri**, enter your own suggestions in the text field, then click **Salva lista dei desideri**. Return to the same link to update them later. The person assigned to you sees your latest saved ideas; you cannot see who drew you.
3. If the link no longer works, ask the organizer whether the draw was reset and request your new link.

Participants can edit their own suggestions **after the draw is locked and their links are shared**. There is currently no participant link for entering suggestions before the draw; the organizer can enter or update them from the dashboard instead.

The interface defaults to Italian. Each person can choose Italian or English in the header; the preference is saved in that browser. Titles, names, notes, and wishlists remain in the language they were entered. Supported currencies: USD, EUR, GBP, CAD, AUD, CHF, NZD.

## Deploy

- **Render:** Connect the repository as a Docker Blueprint. Use a paid instance eligible for the persistent disk in the blueprint. Set `PUBLIC_BASE_URL` to the exact public HTTPS origin (without a path); it must match the browser's host. Use one instance for SQLite. The container applies migrations before listening on `PORT`.
- **Railway:** Deploy from the repository using the Dockerfile. Configure an HTTPS domain, `/healthz`, one instance, and a persistent volume at `/var/data`. Set `DATABASE_URL=sqlite:////var/data/secret-santa.db`, `PUBLIC_BASE_URL`, and a persistent random `APP_SECRET` (at least 32 characters). Confirm the runtime can write the mounted directory.
- **PostgreSQL:** Provision a database and use its connection string for `DATABASE_URL` instead of the SQLite volume. Changing the URL does not transfer existing data. Back up the database regardless of backend; use a SQLite-consistent backup when applicable.

Before sharing links, verify that proxy and platform logging and analytics do not retain private URL paths or redirect headers. The supplied startup commands disable Uvicorn access logs. Restrict or rate-limit public event creation and validation at the hosting boundary when exposing the service publicly. Rotating `APP_SECRET` requires resetting and reissuing participant links.

## Tests

```sh
uv run pytest
```

See [SERVICE_PLAN.md](SERVICE_PLAN.md) for what has been verified.