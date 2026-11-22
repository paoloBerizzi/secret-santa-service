# Secret Santa Service Tracker

Approved scope: [implementation plan](plan-secretSantaService.prompt.md).

| Phase | Status |
| --- | --- |
| Matching and feasibility | Implemented and tested |
| Database and migrations | Verified on SQLite and PostgreSQL 17 |
| Organizer, draw lifecycle, and reveal | Implemented; HTTP integration tests pass |
| Deployment scaffold | Docker image builds; Render Blueprint and Railway steps documented |
| Browser and hosted acceptance | Pending |

## Verification

- Italian is the default interface language; English is available per browser. The language switch, Italian draw feedback, budget formatting, and private reveal flow are covered by tests.

- `uv run pytest -q`: nine tests pass, including solver comparisons against brute force, event isolation, stale draws, reveal privacy, wishlist ownership, and reset/reissue.
- Alembic upgrade and schema-drift checks pass against fresh SQLite and PostgreSQL. The PostgreSQL smoke test also exercised draw, lock, and reset.
- The Docker image builds with locked production dependencies.
- The Playwright desktop/mobile check was skipped. Render and Railway have not been deployed or verified. Before sending real links, verify persistent storage across restarts and confirm platform logs do not retain private token URLs.