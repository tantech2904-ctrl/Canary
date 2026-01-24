# RegimeShift Sentinel Frontend

React 18 (JS) + Vite UI for inspecting time-series runs, Bayesian change-point posteriors, mitigations, and audit events.

## Quickstart

### 1) Configure API base URL

By default the UI talks to `http://localhost:8000/api/v1`.

- Option A (recommended): set `VITE_API_BASE_URL` in `frontend/.env`:

```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

- Option B: keep the default and just run the backend on `:8000`.

### 2) Install + run

```bash
npm ci
npm run dev
```

Open: http://localhost:5173

## Demo credentials

The backend seeds these users on first DB init:

- `admin` / `admin123`
- `analyst` / `analyst123`
- `viewer` / `viewer123`

## Upload a dataset

Use the UI route `/upload` to upload a metrics JSON file.

You can also:

- Click “Load sample into form” to generate a sample run instantly.
- Click “Download sample JSON” for a ready-to-upload file.

There is a repo sample at `datasets/synthetic/run_mean_shift.json`.

## E2E tests (Playwright)

```bash
npm run test:e2e
```

Notes:

- The E2E flow expects the backend to be reachable at `http://localhost:8000`.
- CI starts `vite preview` and the backend automatically.

## Lint / build

```bash
npm run lint
npm run build
```
