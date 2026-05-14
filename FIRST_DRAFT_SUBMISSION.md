# First Draft Implementation Submission

Project: FIFA Player Data Analysis System
Course: Software Development Workshop II Group Project
Submission target: First Draft Implementation, 2026-05-13

## Team Members and Division of Work

This section follows the project SDS and the second/third group meeting notes in Notion.

| Member | Role / implementation responsibility |
|---|---|
| Chen Zhengyang | Leader; overall project coordination, FastAPI + Next.js runnable baseline, frontend framework, common UI/chart components, README and demo checks |
| Feng Daolang | Data loading and cleaning; raw CSV ingestion, type conversion, missing-value review, duplicate handling, position parsing, `players_tidy.parquet`, dataset summary and cleaning-report endpoints |
| Wang Yishi | Value-for-money analysis; VfM index design, candidate ranking, radar-chart data, market scatter data, `/api/vfm`, `/value-for-money` analysis materials |
| Sun Zhangdichi | Salary fairness analysis; league wage distributions, nationality wage heatmap, Kruskal-Wallis test, post-hoc comparison interpretation, `/api/fairness/*` materials |
| Zhang Yiyang | Data visualization and report/PPT materials; chart style, exported PNG/SVG assets, dashboard screenshots, report visualization sections |
| He Menghao | Advanced analysis; K-Means/PCA clustering, Ridge value-regression model, future model explanation materials, `/api/cluster`, `/api/predict`, advanced-page materials |

## Submission Contents

This package contains a runnable first draft implementation of the FIFA player analytics project. It is implemented as a full-stack application rather than a notebook:

- `app/`: FastAPI backend routes, schemas, and analysis services.
- `web/`: Next.js dashboard frontend with pages for dataset exploration, value-for-money analysis, salary fairness, injury/solid projection, and advanced modeling.
- `data/raw/`: FIFA 15-22 raw CSV dataset files used by the backend.
- `data/processed/`: generated tidy Parquet cache and cleaning summaries.
- `outputs/`: CSV analysis exports and PNG visualization figures.
- `docs/project_report.md`: current report draft with methods, figures, results, limitations, and future work.
- `README.md`: setup and run instructions.
- `progress.md`: current implementation status and next steps.

## Requirement Mapping

| First draft requirement | Current implementation evidence |
|---|---|
| Runnable code | `app/main.py`, FastAPI routers/services, `web/app/*` Next.js pages, `Makefile` commands |
| Data reading | `app/services/data_repository.py` loads yearly FIFA CSV files from `data/raw/` |
| Data cleaning | numeric coercion, duplicate handling, position-rating expansion, Parquet cache, `data/processed/cleaning_report.json` |
| Data exploration | `/api/dataset/summary`, `/api/dataset/cleaning-report`, `web/app/explore/page.tsx` |
| EDA and analysis | value-for-money ranking, wage fairness summaries, nationality heatmap, clustering, value prediction, injury/solid projection |
| Visualization | PNG charts in `outputs/charts_png/` and interactive dashboard chart components in `web/components/` |
| Project system prototype | FastAPI API plus Next.js dashboard pages and reusable UI/chart components |
| README/run guide | `README.md`, `web/README.md`, and `Makefile` |
| Current progress | `progress.md` |
| Advanced task draft | K-Means clustering, Ridge market-value prediction, Random Forest future trait projection |

## How to Run

Backend:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open the API docs at:

```text
http://127.0.0.1:8000/docs
```

Frontend:

```bash
cd web
npm install
npm run dev
```

Open the dashboard at:

```text
http://127.0.0.1:3000
```

## Verification Commands

```bash
python -m compileall app tests
python -m pytest -q tests/test_backend_services.py
```

The frontend can also be checked with:

```bash
cd web
npm run lint
```

## Notes for Marking

This is not the final report or final product. The goal of this submission is to show that implementation has started and that the project is already runnable, data-backed, and analyzable. The current version includes the core data pipeline, analysis services, generated charts, a working dashboard structure, and initial advanced modeling tasks.

To satisfy the 100MB submission limit, the zip package omits the duplicate source XLSX archives from `data/raw/`. The backend reads the included yearly CSV files, so the runnable implementation and ETL pipeline are not affected.
