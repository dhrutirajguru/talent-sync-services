# TalentSync

Academia-Industry Collaboration Portal, built for SIH26044 ("Portal for Academia - Industry
collaboration for Skill Mapping, Internships, and Placement"). See [`sih-story.md`](sih-story.md)
for the full problem statement and [`design-anthropic.md`](design-anthropic.md) for the domain
model, schema, and phased roadmap.

## What it does

TalentSync connects three roles on one platform:

- **Students**: build a skill profile, get ranked opportunity matches, apply, and track
  applications.
- **Industry**: post internships/jobs with required skills, and see ranked candidate matches.
- **Academicians**: view an institution-level skill-gap report (skills demanded by live
  postings vs. skills present in the student body).

This repo (`talent-sync-services`) is the backend. The frontend lives in a separate repo,
`talent-sync-web` (React + Vite), deployed to GitHub Pages.

### Current scope: hackathon demo phase

Per [`design-anthropic.md` Section 6.10](design-anthropic.md), this build is scoped to the
Round 2 demo prototype, not the full Phase 1 roadmap:

- Full DB schema and migrations exist for all domains (skills, opportunities, applications,
  learning, portfolio, collaboration, notifications, recommendations), but only a subset has
  live API/UI behind it.
- Fully live: student login/dashboard/skill edit/recommended opportunities/apply; industry
  login/dashboard/post opportunity/ranked candidates/applicant list; academician
  login/dashboard/institution skill-gap report.
- Matching is a synchronous skill-overlap score, computed in the request, not precomputed.
- Deliberately deferred: Redis, async worker, materialized views, full-text search, audit log
  writes, refresh-token rotation. The tables exist; the logic is not wired up yet.
- Everything else in the UI (assessments, learning programs, portfolio, collaboration,
  notifications feed, curriculum) renders from static fixture data.

Seeded demo accounts and test flows are in [`demo-users.md`](demo-users.md).

## Tech stack

**Backend (this repo)**

- FastAPI, Uvicorn
- SQLAlchemy 2.x, Alembic migrations
- PostgreSQL 16
- Pydantic v2 / pydantic-settings
- psycopg (binary) as the DB driver
- argon2-cffi for password hashing, python-jose for JWT
- uv for dependency management and packaging
- pytest / pytest-asyncio / httpx for tests, ruff for linting

**Frontend (`talent-sync-web`, separate repo)**

- React 18, TypeScript, Vite
- React Router v6, TanStack Query

**Infra**

- Docker + Docker Compose for local and deployed runs
- Caddy as a reverse proxy for automatic HTTPS (Let's Encrypt) in the deployed environment
- AWS EC2 for hosted demo compute; DuckDNS for a free domain name

## Repository layout

```text
app/
  main.py              FastAPI app, CORS, health/root routes
  core/                settings, database session, security (hashing/JWT)
  models/              SQLAlchemy ORM models
  schemas/             Pydantic request/response schemas
  repositories/        DB access layer
  services/            business logic (auth, matching, applications, ...)
  api/v1/              route handlers, mounted under /api/v1
  seed.py              loads demo data (Section 6.8/6.9 of the design doc)
alembic/               migrations
docs/                  design docs, demo data, this README
docker-compose.yml     local dev stack (postgres + api, hot reload)
Dockerfile             production image for the api service
```

## Local development

Requirements: Python 3.11+, [uv](https://docs.astral.sh/uv/), Docker (for Postgres).

```bash
cp .env.example .env              # set JWT_SECRET_KEY for anything beyond quick local testing:
                                   # openssl rand -hex 32
uv sync                           # install backend dependencies
docker compose up -d postgres     # start just the database
uv run alembic upgrade head       # apply migrations
uv run python -m app.seed         # load demo data (see docs/demo-users.md)
uv run uvicorn app.main:app --reload
```

API is then at `http://localhost:8000`, interactive docs at `http://localhost:8000/docs`.

To run the whole stack (Postgres + API) in containers instead:

```bash
docker compose up -d
```

### Frontend (separate repo)

```bash
cd ../talent-sync-web
cp .env.example .env              # set VITE_API_BASE_URL to your local API, e.g.
                                   # http://localhost:8000/api/v1
npm install
npm run dev
```

## API overview

All routes are mounted under `/api/v1` (see `app/api/v1/router.py`): `auth`, `users`, `skills`,
`opportunities`, `applications`, `institutions`, `organizations`. `/health` and `/` are outside
the prefix for load-balancer/liveness checks. Full request/response shapes are in the OpenAPI
docs at `/docs` once the app is running. The demo-phase API surface is enumerated in
[`design-anthropic.md` Section 6.2](design-anthropic.md).

## Environment variables

Set in `.env` (see `.env.example`):

| Variable | Purpose |
|---|---|
| `ENVIRONMENT` | `local` or `production`; informational, no behavior switch yet |
| `DEBUG` | FastAPI debug flag |
| `DATABASE_URL` | SQLAlchemy connection string, e.g. `postgresql+psycopg://user:pass@host:5432/db` |
| `JWT_SECRET_KEY` | signing key for access tokens; generate a real one for any hosted deploy |
| `JWT_ALGORITHM` | defaults to `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | defaults to 1440 (24h; generous for demo purposes) |
| `CORS_ORIGINS` | comma-separated list of allowed frontend origins |

## Deployed demo (AWS)

The hackathon demo backend runs on a single AWS EC2 instance, chosen for minimal cost over
production robustness; see [`design-anthropic.md` Section 7.1](design-anthropic.md) for the
tradeoffs against a managed Postgres provider.

**Live environment**

- API: `https://dau-talentsync.duckdns.org` (TLS via Caddy + Let's Encrypt)
- Frontend: `https://dhrutirajguru.github.io/talentsync/` (GitHub Pages, built from
  `talent-sync-web`)
- Region: `us-east-1`, instance type `t2.micro`, with a 2 GB swap file (1 GiB RAM is tight for
  Postgres + API + Caddy together)

**What is running on the instance**

```text
postgres  (16-alpine, bound to 127.0.0.1:5432 only, not internet-reachable)
api       (this repo, built from Dockerfile)
caddy     (reverse proxy, terminates TLS, forwards to api:8000)
```

Defined in `docker-compose.prod.yml` on the instance (not the same file as the local
`docker-compose.yml`, which runs Postgres + API only, with hot reload, for development).

**How it was provisioned**

1. SSH key pair, security group (22 restricted to the operator's IP, 80/443 open for ACME and
   HTTPS), and the instance itself were created via the AWS CLI using a dedicated named
   profile.
2. An Elastic IP was allocated and associated for a stable public IP; see Cost notes below for
   what this actually costs, since AWS charges for public IPv4 addresses regardless of
   free-tier status.
3. A free DuckDNS subdomain was pointed at the Elastic IP; Let's Encrypt cannot issue a
   certificate for a bare IP, so a domain name is required for HTTPS.
4. User-data on first boot created the swap file and installed Docker Engine + the Compose
   plugin from Docker's official apt repository.
5. The repo was cloned onto the instance, a production `.env` was generated on the instance
   itself (random `JWT_SECRET_KEY` and Postgres password, never transmitted or committed),
   `docker-compose.prod.yml` and a `Caddyfile` were added, and the stack was brought up with
   `docker compose -f docker-compose.prod.yml up -d --build`.
6. Migrations and demo seed data were run inside the running `api` container.

**Redeploying an update**

```bash
ssh -i talentsync-demo.pem ubuntu@<elastic-ip>
cd app
git pull
sudo docker compose -f docker-compose.prod.yml up -d --build
sudo docker compose -f docker-compose.prod.yml exec api alembic upgrade head
```

**Cost notes**

- AWS now charges for every public IPv4 address, Elastic IP or not, attached or not: about
  $0.005/hr, roughly $3.60/month. This applies regardless of free-tier status.
- t2.micro compute and the EBS volume are free-tier eligible (750 hrs/month and 30 GB
  respectively) for eligible accounts; check the Billing Console's Free Tier page for your
  account's exact eligibility window, since AWS changed the free-tier structure for accounts
  created on or after July 15, 2024.
- Once free tier lapses, expect roughly $12 to 13/month total (instance + public IPv4 charge).
- Post-hackathon production architecture (ECS, RDS, ElastiCache, S3, CloudFront) is a separate,
  higher-cost path; see [`design-anthropic.md` Section 7.3](design-anthropic.md).

## Frontend deployment notes

The frontend is built and deployed to a subfolder of a shared GitHub Pages user site
(`dhrutirajguru.github.io/talentsync/`), not its own domain, which has two consequences:

- The Vite build must be run with `--base=/talentsync/` so asset URLs resolve correctly:
  `npm run build -- --base=/talentsync/`.
- `BrowserRouter` uses `basename={import.meta.env.BASE_URL}` so client-side routing matches the
  served subpath.
- GitHub Pages has no SPA fallback by default, so a hard refresh or direct deep link under
  `/talentsync/...` would normally 404. A `404.html` at the GitHub Pages repo root and a
  restoration script in `talent-sync-web/index.html` implement the standard
  [spa-github-pages](https://github.com/rafgraph/spa-github-pages) redirect workaround, scoped
  to keep the first path segment (the project folder) intact since that repo hosts multiple
  projects.
