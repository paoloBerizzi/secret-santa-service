## Plan: Family Secret Santa Service

Build a single FastAPI app with server-rendered Jinja2 pages, Tailwind CSS from a pinned CDN stylesheet, and HTMX for live validation. Use Python 3.12+, `uv`, SQLAlchemy 2, and Alembic. SQLite is the default; `DATABASE_URL` can point to PostgreSQL without changing application code.

**Status: awaiting approval.** I saved this draft in session memory and made no repository changes. After approval, the first repository change will be `SERVICE_PLAN.md`, the living tracker for decisions, progress, and verification. The existing [initial-plan.md](initial-plan.md) stays unchanged.

**Directory Structure**

| Location | Files |
|---|---|
| Root | `SERVICE_PLAN.md`, `README.md`, `pyproject.toml`, `uv.lock`, `.python-version`, `.env.example`, `.gitignore`, `.dockerignore`, `Dockerfile`, `render.yaml`, `alembic.ini`; retain `initial-plan.md` and `LICENSE` |
| `app/` | `__init__.py`, `main.py`, `config.py`, `db.py`, `models.py`, `matching.py`, `draws.py`, `security.py` |
| `app/routes/` | `__init__.py`, `events.py`, `admin.py`, `reveal.py` |
| `app/templates/` | `base.html`, `new_event.html`, `admin.html`, `reveal.html`, `error.html`, `partials/validation.html` |
| `app/static/vendor/` | `htmx.min.js`, `htmx.LICENSE` |
| `migrations/` | `env.py`, `script.py.mako`, `versions/0001_initial.py` |
| `tests/` | `conftest.py`, `test_matching.py`, `test_admin.py`, `test_reveal.py` |

**1. Define the Database**

| Model | Fields and relationships |
|---|---|
| `Event` | Title, budget in minor units and currency, exchange date, notes, admin-token digest, no-reciprocal toggle, draw state, revision, and current draw nonce. Owns participants, subgroups, exclusions, and assignments. |
| `Participant` | Event, name, optional wishlist, and nullable reveal-token digest. Names need not be unique. |
| `Subgroup` | Event, name unique within the event, and no-intra-exchange toggle. |
| `SubgroupMember` | Unique subgroup–participant membership. Participants can belong to multiple subgroups. |
| `ExclusionRule` | Unique directed giver–receiver pair within an event. The reverse direction is unaffected. |
| `Assignment` | Current event, giver, and receiver. Unique giver and unique receiver per event; no self-pairs. |

Use event-scoped foreign keys to prevent cross-event relationships and enable foreign-key checks in SQLite. Persist a complete assignment set in one transaction, never a partial draw.

**2. Build the Matching Engine** *(can run in parallel with schema work)*

1. Build separate giver and receiver sets from the same roster. Remove self-edges, edges whose endpoints share **any active subgroup**, and explicitly excluded directions. A subgroup does not restrict a pair unless both people belong to it.
2. Flag rosters under two, givers with no recipients, receivers with no possible givers, and active subgroups where $|A| > |U \setminus A|$. A static bipartite matching check can catch bottlenecks these local checks miss, but it cannot prove feasibility when reciprocal pairs are forbidden.
3. Backtrack by choosing the giver with the fewest viable recipients. Randomize ties and candidate order for real draws. Use each receiver once, reject $x \to y$ if $y \to x$ is already assigned and reciprocity is disabled, and backtrack when a tentative choice leaves someone without a match. Randomized does not mean uniformly sampled.
4. Use the same solver for dry-run and draw. Report **feasible**, **infeasible**, or **not verified within the search limit**. Propose a 32-person MVP cap; never describe a timeout as proof of impossibility. Name specific conflicts when known and suggest which kinds of rules to relax otherwise.

**3. Implement the Lifecycle and Routes** *(after schema and solver)*

Drafts are editable even when infeasible. **Draw** solves against the current revision and saves assignments without enabling links. **Lock** freezes settings, roster, and rules and enables private links. Wishlists remain editable. **Reset** requires confirmation, deletes assignments, and revokes all old links before returning to draft; it cannot undo a reveal someone already saw.

| Route | Behavior |
|---|---|
| `GET /`, `POST /events` | Setup form and event creation; redirect to the organizer dashboard. |
| `GET /admin/{admin_token}` | Manage the event and, once locked, copy participant links without seeing pairings. |
| Admin-prefixed `POST /settings`, `/participants`, `/participants/{id}/edit`, `/participants/{id}/remove`, `/participants/{id}/wishlist` | Update settings, roster, and wishlists. |
| Admin-prefixed `POST /subgroups`, `/subgroups/{id}/edit`, `/subgroups/{id}/remove`, `/subgroups/{id}/members`, `/subgroups/{id}/members/{participant_id}/remove` | Manage subgroup rules and membership. |
| Admin-prefixed `POST /exclusions`, `/exclusions/{id}/remove`, `/validate`, `/draw`, `/lock`, `/reset` | Manage directed exclusions, refresh the read-only HTMX feasibility result, and control the draw. Forms also work without HTMX. |
| `GET /reveal/{participant_token}`, `POST /reveal/{participant_token}/wishlist` | Show only the assigned recipient’s name and wishlist plus the budget and date. Participants can edit their own wishlist without learning who drew them. |
| `GET /healthz` | Deployment health check. |

Treat URLs as bearer credentials: use a 32-byte random organizer token and per-draw participant tokens derived using a server secret and fresh nonce. Store only token digests; the organizer dashboard can regenerate participant links while locked. Require HTTPS, CSRF protection for writes, and event-scoped authorization. Set `no-store` and `no-referrer` on private responses, avoid third-party scripts on token pages, and verify that hosting logs do not capture token URLs. Never include other pairings in HTML, HTMX responses, or an API.

**4. Deploy and Verify**

- **Local:** `uv sync`, `uv run alembic upgrade head`, then `uv run uvicorn app.main:app --reload`.
- **Render:** Connect the repo using the Docker Blueprint, mount a persistent disk on an eligible plan, and set `DATABASE_URL=sqlite:////var/data/secret-santa.db`, the app secret, and the public base URL. Run migrations before Uvicorn starts on `$PORT`. Use one instance with SQLite. **Railway** can use the same Dockerfile with its own volume and variables. PostgreSQL is an alternative; changing the URL does not migrate existing data.
- **Automated:** Run `uv run pytest` for overlapping groups, directed rules, reciprocal pairs, infeasible combinations, and search limits. Test cross-event isolation, stale draws, lock/reset, wishlist ownership, and reveal leakage. Apply migrations against fresh SQLite and smoke-test PostgreSQL.
- **Manual:** On desktop and mobile, create an event, resolve a rule conflict, draw and lock, open separate reveal links, update a wishlist, and verify reset invalidates old links. Restart the deployed service and verify data and links persist.

Accounts, email/SMS delivery, draw history, and multi-instance SQLite are outside the MVP. No application files will be generated before approval.
