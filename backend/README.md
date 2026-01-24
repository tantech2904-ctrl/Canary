# RegimeShift Sentinel Backend

FastAPI-based backend providing REST API, Bayesian change-point detection, mitigation suggestions, and auditing.

## Key Features
- Async SQLAlchemy (PostgreSQL)
- Redis caching and rate limiting
- JWT auth + RBAC (admin, analyst, viewer)
- Bayesian CPD (online + offline PyMC)
- Background offline posterior tasks
- Strict Pydantic v2 validation

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env for your local Postgres/Redis
PYTHONPATH=. alembic upgrade head
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open API at `/api/v1/openapi.json`.

## Demo users

On first DB init, the backend seeds:

- `admin` / `admin123`
- `analyst` / `analyst123`
- `viewer` / `viewer123`

## Environment variables

Common settings:

- `POSTGRES_DSN` (async SQLAlchemy DSN)
- `REDIS_URL`
- `SECRET_KEY` (JWT signing)
- `CORS_ALLOW_ORIGINS`

Test-only:

- `ENV=test` or `RSS_SKIP_STARTUP=1` skips startup side-effects (DB/Redis init), useful for unit tests.

## Schema migrations (Alembic)

Alembic is configured to read the DB URL from `app.core.config.settings.POSTGRES_DSN` (so `POSTGRES_DSN` must be set in your environment).

Common commands (run from `backend/`):

```bash
# Apply migrations
PYTHONPATH=. alembic upgrade head

# Create a new migration from model changes
PYTHONPATH=. alembic revision --autogenerate -m "describe change"

# Downgrade one revision (local/dev only)
PYTHONPATH=. alembic downgrade -1
```

Makefile shortcuts:

```bash
make install
make migrate
make revision MSG="describe change"
```

Recommended workflow:

1. Edit SQLAlchemy models under `app/db/models/`.
2. Run `make revision MSG="..."` and review the generated file under `alembic/versions/`.
3. Run `make migrate` and start the app.

Notes:

- Autogenerate is a starting point; always review constraints/indexes and data migrations.
- If you already have a DB created via the old `create_all` behavior, consider recreating it, or (carefully) stamping: `make stamp-current`.
