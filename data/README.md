# Data Folders

- `raw/` is intentionally omitted from the Git repository and submission archive. Download the original FIFA CSV files separately and place them in `data/raw/`, or set `FIFA_DATA_DIR` to an external raw-data folder.
- `processed/` contains optional generated cleaned artifacts such as `players_tidy.parquet`, `summary.json`, and `cleaning_report.json`.
- `sample/` contains a small fallback fixture used when the raw archive is unavailable.

The data cleaning code is included in `app/services/data_repository.py`.
