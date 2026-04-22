# FIFA Player Data Analysis System

Week 1 scaffold for the `Software Development Workshop II` group project. This repository is aligned with the SDS and the April 22 meeting notes: a FastAPI backend, a Next.js frontend, data folders, API contracts, and placeholder analytics paths for the four required usage scenarios.

## What is included

- `app/` FastAPI backend scaffold with the routes defined in the SDS
- `web/` Next.js App Router frontend with pages for Explore, Value for Money, Fairness, and Advanced Analysis
- `data/` raw, processed, and committed sample data folders
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

### 2. Frontend

```bash
cd web
npm install
npm run dev
```

The web app will be available at `http://127.0.0.1:3000`.

### 3. Generate frontend API types

After the backend is running:

```bash
cd web
npm run generate:types
```

## Data layout

- The raw FIFA CSV/XLSX files live in `data/raw/` and are versioned in this repository.
- On this machine they were copied from `/Users/yang/Downloads/archive`.
- `data/sample/player_snapshots.json` is a committed seed dataset so the scaffold can run before the full ETL is implemented.
- `data/processed/` is reserved for generated cache files such as `players_tidy.parquet`.

## Current scope

This scaffold is intentionally week-1 sized:

- The route structure, schema shape, and page structure are stable.
- The backend serves sample-backed responses with clear TODO notes where real statistics and ML should replace placeholders.
- The frontend is already wired to the API contract and falls back to local seed data when the backend is offline.

## Next implementation steps

1. Replace the sample repository with real CSV ingestion and Parquet caching.
2. Implement statistical tests with `scipy.stats` and `statsmodels`.
3. Add the actual clustering and regression models with `scikit-learn`.
4. Generate the typed OpenAPI client and replace local fallback interfaces.
5. Add tests for the backend services and frontend page-level rendering.
