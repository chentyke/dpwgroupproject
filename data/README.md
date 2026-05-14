# Data folders

- `raw/` stores the original FIFA CSV files used by the backend plus the supporting XLSX source archives. The duplicate XLSX archives are omitted from the under-100MB submission zip.
- `processed/` stores generated artifacts such as `players_tidy.parquet`, `summary.json`, and `cleaning_report.json`.
- `sample/` stores small committed fixtures used when the raw archive is unavailable.
