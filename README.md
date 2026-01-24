# RegimeShift Sentinel

Production-minded, AI-native early-warning platform for regime shifts in time-series using Bayesian change-point detection (BCPD) with human-in-the-loop approvals and an immutable audit trail.

## Stack

- Backend: FastAPI + Pydantic v2 + Async SQLAlchemy (Postgres) + Redis + JWT/RBAC
- Frontend: React 18 (JS) + Vite + Tailwind
- CI: GitHub Actions (backend pytest, frontend lint/build, Playwright E2E)

## Run with Docker Compose

```bash
docker compose up --build
```

- Frontend: http://localhost:5173
- Backend health: http://localhost:8000/healthz
- OpenAPI: http://localhost:8000/api/v1/openapi.json

## Run locally (no Docker)

Fast path (starts both backend + frontend in background):

```bash
make dev-up
make dev-check
```

Stop them:

```bash
make dev-down
```

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env for your local Postgres/Redis
PYTHONPATH=. alembic upgrade head
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Migrations workflow and commands: see `backend/README.md`.

### Frontend

```bash
cd frontend
npm ci
npm run dev
```

## Demo credentials

Seeded on first DB init:

- `admin` / `admin123`
- `analyst` / `analyst123`
- `viewer` / `viewer123`

## Try it

1. Login as `analyst`
2. Go to `/upload`
3. Click “Load sample into form”, then “Upload”
4. Inspect the run: metric chart + online/offline posteriors + mitigations + recent audit events

## Repo layout

- `backend/` FastAPI app and Bayesian services
- `frontend/` React UI
- `datasets/` synthetic dataset generator and sample payloads
- `.github/workflows/` CI
