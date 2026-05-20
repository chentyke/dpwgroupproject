# FIFA Player Data Analysis System

This repository contains the code set for the Software Development Workshop II FIFA group project. It includes the FastAPI backend, Next.js frontend, data cleaning and modeling code, tests, generated analysis outputs, and a small sample dataset for fallback mode.

The original FIFA raw dataset is not stored in this repository. This keeps the repository size manageable and follows the submission requirement that the original dataset should not be included. The data loading and cleaning code needed to reproduce the cleaned dataset is included.

## Project Structure

```text
.
├── app/                    # FastAPI backend, routers, schemas, and services
├── web/                    # Next.js dashboard frontend
├── scripts/                # Utility scripts for OpenAPI and chart export
├── tests/                  # Backend service tests
├── data/
│   ├── sample/             # Small fallback fixture
│   └── processed/          # Optional generated cleaned artifacts
├── outputs/                # Generated CSV, JSON, and PNG analysis outputs
├── presentation_assets/    # Architecture and reporting assets
├── requirements.txt        # Python backend dependencies
├── requirements-analytics.txt
├── web/package.json        # Frontend dependencies and scripts
└── Makefile                # Common local commands
```

## Dataset

The raw FIFA CSV/XLSX files are intentionally omitted. To reproduce the full data processing pipeline, download the FIFA Career Mode Player Dataset from Kaggle:

- [FIFA 22 complete player dataset](https://www.kaggle.com/datasets/stefanoleone992/fifa-22-complete-player-dataset)

Place the yearly CSV files in `data/raw/`, for example:

```text
data/raw/players_15.csv
data/raw/players_16.csv
...
data/raw/players_22.csv
data/raw/female_players_16.csv
...
data/raw/female_players_22.csv
```

Alternatively, set `FIFA_DATA_DIR` to an external folder that contains those CSV files:

```bash
export FIFA_DATA_DIR=/absolute/path/to/fifa/raw/csv/files
```

If the raw files are not present, the backend runs in sample-fixture mode using `data/sample/player_snapshots.json`.

## Backend Setup

Create and activate a Python virtual environment from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the backend:

```bash
uvicorn app.main:app --reload
```

Open the API documentation:

```text
http://127.0.0.1:8000/docs
```

## Data Cleaning and ETL

After placing the raw CSV files in `data/raw/` or setting `FIFA_DATA_DIR`, run:

```bash
python -c "from app.services.data_repository import get_player_repository; print(get_player_repository().run_etl())"
```

This generates:

```text
data/processed/players_tidy.parquet
data/processed/cleaning_report.json
data/processed/summary.json
```

The cleaning logic is implemented in `app/services/data_repository.py`.

## Frontend Setup

Install frontend dependencies:

```bash
cd web
npm install
```

Start the frontend development server:

```bash
npm run dev
```

Open:

```text
http://127.0.0.1:3000
```

The frontend expects the backend at `http://127.0.0.1:8000`. This can be changed with `NEXT_PUBLIC_API_BASE_URL`.

## Generate Frontend API Types

From the `web/` folder:

```bash
npm run generate:types
```

This exports the FastAPI OpenAPI schema and refreshes `web/lib/generated/api-types.ts`.

## Tests

Run backend verification from the repository root:

```bash
python -m compileall app tests
python -m pytest -q tests/test_backend_services.py
```

Frontend checks:

```bash
cd web
npm run lint
npm run typecheck
```

## Models and Reproducibility

No pre-trained model or external fine-tuned model file is included. The project trains classical machine learning models from the available FIFA data at runtime:

- Future Injury Prone and Solid Player projection: `app/services/injury.py`
- K-Means clustering and Ridge market-value prediction: `app/services/advanced.py`
- Current cleaned-data prediction notebook: `outputs/predict_notebook_current_data/predict_current_cleaned_data.ipynb`

No separate model download is required.

## External Package References

Exact versions are recorded in `requirements.txt`, `requirements-analytics.txt`, and `web/package.json`.

Python packages:

- [FastAPI](https://fastapi.tiangolo.com/)
- [Uvicorn](https://www.uvicorn.org/)
- [pandas](https://pandas.pydata.org/)
- [NumPy](https://numpy.org/)
- [PyArrow](https://arrow.apache.org/docs/python/)
- [SciPy](https://scipy.org/)
- [statsmodels](https://www.statsmodels.org/)
- [scikit-learn](https://scikit-learn.org/stable/)
- [Matplotlib](https://matplotlib.org/)
- [HTTPX](https://www.python-httpx.org/)
- [pytest](https://docs.pytest.org/)

Frontend packages:

- [Next.js](https://nextjs.org/)
- [React](https://react.dev/)
- [React DOM](https://react.dev/reference/react-dom)
- [Recharts](https://recharts.org/)
- [HeroUI](https://www.heroui.com/)
- [Radix UI](https://www.radix-ui.com/)
- [lucide-react](https://lucide.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [class-variance-authority](https://cva.style/)
- [clsx](https://github.com/lukeed/clsx)
- [tailwind-merge](https://github.com/dcastil/tailwind-merge)
- [tw-animate-css](https://github.com/Wombosvideo/tw-animate-css)
- [openapi-typescript](https://openapi-ts.dev/)
- [shadcn](https://ui.shadcn.com/)
- [TypeScript](https://www.typescriptlang.org/)
- [ESLint](https://eslint.org/)
- [DefinitelyTyped](https://github.com/DefinitelyTyped/DefinitelyTyped)
