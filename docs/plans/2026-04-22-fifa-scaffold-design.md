# 2026-04-22 FIFA Scaffold Design

## Sources

- SDS: `Software Design Specification · FIFA Player Data Analysis System (v1.0)`
- Meeting: `第二次小组会议 · 议程与讨论事项`
- Supporting notes: `database_schema`, `SDS 填写指南 · FIFA 球员数据分析项目`

## Scope chosen for this scaffold

The repository started as an empty remote. Based on the SDS and the April 22 meeting note, the correct week-1 target is not full analytics; it is a runnable engineering baseline with stable interface boundaries.

This scaffold therefore includes:

- `app/` FastAPI routes for `/api/dataset/*`, `/api/vfm`, `/api/fairness/*`, `/api/cluster`, and `/api/predict`
- `web/` Next.js pages for `/explore`, `/value-for-money`, `/fairness`, and `/advanced`
- shared sample data so every page and endpoint can render before the full CSV ingestion exists
- the data folder policy from the meeting note: `data/raw/` ignored, `data/processed/` reserved for generated Parquet, committed fixtures kept in `data/sample/`
- a typed-client generation entry point for the later OpenAPI workflow

## Design decisions

### Backend

- Use a thin router-service-schema split so each member can work in one module without touching the whole API.
- Serve sample-backed responses now, but preserve the final endpoint shapes described in the SDS.
- Wrap success responses in `{ code, message, data }` to make the contract explicit during early front-end integration.

### Frontend

- Use the Next.js App Router because it is already called out in the SDS and meeting note.
- Build route-level pages with shared visualization components named after the SDS concepts: `RadarChart`, `ScatterPlot`, `Heatmap`, `BoxPlot`, `DataTable`.
- Support local fallbacks when the backend is offline so front-end work does not block on API startup.

### Data

- Commit only a tiny seed dataset.
- Keep the real FIFA CSVs out of Git.
- Leave room for the later `players_tidy.parquet` cache and ETL pipeline.

## Deferred work

- real CSV ingestion and cleaning report generation
- statistical testing with `scipy.stats` and `statsmodels`
- clustering and regression via `scikit-learn`
- generated OpenAPI types replacing local interfaces
- automated tests and CI hardening

