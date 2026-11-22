We are building a lightweight, self-hosted family Secret Santa web application in Python. Before writing any application code, please review the requirements below and output a clear implementation plan (directory structure, database schema, matching algorithm design, routes, and deployment steps) for my approval.

### 1. Tech Stack & Tooling
- **Language & Package Manager:** Python 3.12+ managed with `uv` (`pyproject.toml`).
- **Backend:** FastAPI + Uvicorn.
- **Database:** SQLite (via SQLModel or SQLAlchemy) configured cleanly via an environment variable (`DATABASE_URL`) so it works locally with a file and deploys easily with a persistent volume or Postgres.
- **Frontend:** Server-rendered Jinja2 templates styled with Tailwind CSS (via CDN) and lightweight interactivity via HTMX or Alpine.js (no separate Node/React build step).
- **Testing:** `pytest` for unit testing the matching engine, subgroup constraints, and rule validation.
- **Deployment:** Include minimal deployment config (`Dockerfile` and/or `render.yaml`) ready for one-click Git push deployment on Render or Railway.

### 2. Core Features & User Flows
- **Organizer Setup & Admin Dashboard (`/admin/{admin_token}`):**
  - Create a Secret Santa event with a title, gift budget/spending limit, exchange date, and custom notes.
  - Protect the organizer dashboard via a secret unguessable `admin_token` URL (no full user/password auth system needed).
  - Add, edit, and remove participants (name, optional wishlist/gift hints).

- **Tunable Exclusion Rules:**
  - **Subgroup No-Intra-Exchange Rules (Primary Group Rule):**
    - Given the universe $U$ of all participants in an event, allow the organizer to define named subgroups $A \subseteq U$ (e.g., couples, households, or family branches) and assign participants to one or more subgroups.
    - When a subgroup $A$ has the "no intra-group exchange" rule active, members of $A$ **cannot exchange gifts with one another** (for all $x, y \in A$, $x \nrightarrow y$). Consequently, members of $A$ can only give gifts to participants in $U \setminus A$, while participants in $U \setminus A$ can give gifts to anyone in $U$ (either in $A$ or in $U \setminus A$), subject to any other active rules.
  - **Individual & Global Rule Modifiers:**
    - Support optional directed exclusions (`giver_id` cannot draw `receiver_id`) for one-off exceptions.
    - Support an optional event-wide toggle for **"No mutual/reciprocal pairs"** (if $x$ draws $y$, then $y$ cannot draw $x$).
  - **Pre-Draw Feasibility Validation:**
    - Live validation in the admin UI before running the draw that checks:
      1. Whether any participant has zero valid recipients left.
      2. Subgroup cardinality feasibility (e.g., warning when $|A| > |U \setminus A|$ makes a valid bijection impossible).
      3. Full solver feasibility via a dry-run check so the organizer gets a clear, actionable message if the combined rule set has no valid solution.

- **The Draw & Private Reveal Links (`/reveal/{participant_token}`):**
  - Run a randomized **backtracking solver** on the server to find a valid assignment (a bijection where every participant gives one gift and receives one gift, no self-draws, and all subgroup/directed/mutual constraints are satisfied).
  - Generate a unique, unguessable `participant_token` URL for each person so the organizer can copy and send each link privately.
  - Opening `/reveal/{participant_token}` displays **only** that participant's assigned recipient, the event budget/date, and the recipient's wishlist notes—never exposing other pairings in the HTML or network responses.
  - Allow participants to update their own wishlist/hints from their reveal page without seeing who drew them.
  - Support locking/resetting the draw from the admin page if rules or participants change before links are shared.

### 3. What I Need From You Now
1. Propose the exact file/folder structure.
2. Outline the database models (`Event`, `Participant`, `Subgroup`, `SubgroupMember`, `ExclusionRule`, `Assignment`) and relationships.
3. Explain the graph construction and backtracking matching algorithm, including how subgroup rules ($x, y \in A \implies x \nrightarrow y$), mutual-exclusion toggles, and impossible rule sets are handled.
4. List the FastAPI routes (HTML views + HTMX/form endpoints) and how admin/participant tokens are secured.
5. Wait for my confirmation on the plan before generating any files.