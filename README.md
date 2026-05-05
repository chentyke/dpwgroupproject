# FIFA Player Data Analysis System

FastAPI + Next.js implementation for the `Software Development Workshop II` FIFA group project. The backend now loads the full FIFA 15-22 archive, builds a tidy Parquet cache, and serves the four SDS analysis scenarios.

## What is included

- `app/` FastAPI backend with the routes defined in the SDS
- `web/` Next.js App Router frontend with pages for Explore, Value for Money, Fairness, and Advanced Analysis
- `data/` raw CSV/XLSX files, generated processed artifacts, and small sample fixtures
- `docs/plans/` implementation notes derived from the Notion SDS and meeting records
- `Makefile`, `.editorconfig`, `.env.example`, and install scripts for a shared team setup

## Repo structure

```text
.
├── app/
│   ├── core/
│   ├── routers/
│   ├── schemas/
│   └── services/
├── data/
│   ├── processed/
│   ├── raw/
│   └── sample/
├── docs/plans/
└── web/
```

## Quick start

### 1. Backend

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API will be available at:

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/openapi.json`

Generate or refresh the tidy dataset cache:

```bash
python - <<'PY'
from app.services.data_repository import get_player_repository
print(get_player_repository().run_etl())
PY
```

### 2. Frontend

```bash
cd web
npm install
npm run dev
```

The web app will be available at `http://127.0.0.1:3000`.

### 3. Generate frontend API types

The type generation step exports the OpenAPI schema directly from the FastAPI app;
the backend server does not need to be running.

```bash
cd web
npm run generate:types
```

## Data layout

- The raw FIFA CSV/XLSX files live in `data/raw/` and are versioned in this repository.
- On this machine they were copied from `/Users/yang/Downloads/archive`.
- `data/sample/player_snapshots.json` is a committed seed dataset for fallback mode.
- `data/processed/players_tidy.parquet` is generated from the 15 CSV files and currently contains 144,323 rows and 195 columns after position-rating expansion.

## Current backend scope

- `/api/dataset/summary` reports the archive shape, schema profile, seasons, genders, and preview rows.
- `/api/dataset/cleaning-report` reports numeric coercion, duplicate handling, null hotspots, position parsing, and Parquet cache status.
- `/api/vfm` ranks value-for-money candidates using the SDS formula `overall / log(value_eur + 1)`.
- `/api/fairness/*` returns league wage distributions, a nationality wage heatmap, Kruskal-Wallis results, and Dunn-style post-hoc pairs.
- `/api/cluster` and `/api/predict` run K-Means/PCA clustering and Ridge log-value prediction.

## Verification

```bash
python -m compileall app tests
python -m pytest -q tests/test_backend_services.py
```

The frontend still has its own remaining work: generated OpenAPI client integration, richer chart interactivity, and final report/PPT export assets.
