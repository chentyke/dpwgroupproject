# Current Progress

Last updated: 2026-05-12

## Team and Current Division

The team information below is taken from the Notion SDS and group meeting notes.

| Member | Current responsibility |
|---|---|
| Chen Zhengyang | Leader; project coordination, runnable full-stack baseline, frontend framework/components, README and submission checks |
| Feng Daolang | Data loading, cleaning, missing-value review, tidy Parquet cache, dataset summary and cleaning report |
| Wang Yishi | Value-for-money ranking, VfM formula/materials, radar and scatter chart analysis |
| Sun Zhangdichi | Salary fairness analysis, league wage spread, nationality wage heatmap, statistical test interpretation |
| Zhang Yiyang | Visualization assets, report/PPT chart material collection, dashboard screenshot preparation |
| He Menghao | Advanced models, K-Means/PCA clustering, value prediction, advanced analysis explanation |

## Completed

- Built a FastAPI backend with routes for dataset exploration, value-for-money analysis, salary fairness, nationality wage heatmaps, injury/solid projection, clustering, and value prediction.
- Added FIFA 15-22 raw data files under `data/raw/`.
- Implemented CSV loading, season/gender tagging, numeric coercion, duplicate handling, position-rating parsing, and tidy Parquet generation.
- Generated processed artifacts under `data/processed/`, including `players_tidy.parquet`, `summary.json`, and `cleaning_report.json`.
- Added backend tests for the data repository, cleaning report, value-for-money analysis, fairness module, clustering, prediction, and injury projection.
- Built a Next.js frontend prototype with pages for Explore, Value for Money, Fairness, Injury, and Advanced Analysis.
- Added reusable frontend chart and table components under `web/components/`.
- Exported PNG figures under `outputs/charts_png/` for data cleaning, market scatter, radar comparison, wage spread, nationality heatmap, clustering, prediction feature weights, and injury/solid projection.
- Exported CSV outputs under `outputs/` for rankings, chart data, regression summaries, and data quality review.
- Drafted a project report in `docs/project_report.md`.

## Implemented Analysis Areas

- Data exploration and cleaning:
  - dataset shape and schema summary
  - missing-value/null hotspot review
  - duplicate player-season handling
  - numeric field normalization
  - position field expansion

- Exploratory analysis and visualization:
  - overall market/value relationships
  - value-for-money candidate rankings
  - league wage distribution summaries
  - nationality and league wage heatmap
  - playing-style clusters

- Advanced draft tasks:
  - K-Means clustering of outfield playing styles
  - Ridge regression market-value prediction
  - Random Forest future Injury Prone and Solid Player projection

## Not Yet Complete

- Final UI polish and full responsive QA.
- More configurable frontend filters for season, gender, league, position, age range, and wage/value thresholds.
- Direct generated OpenAPI client usage across all frontend pages.
- More complete final report interpretation and citations.
- Final presentation slides.
- Export buttons for dashboard charts and tables.
- Additional model diagnostics such as calibration curves, silhouette analysis, and cross-season validation.

## Immediate Next Steps

1. Run the backend and frontend locally before upload.
2. Review `docs/project_report.md` and align wording with the final SDS.
3. Add final screenshots if the instructor expects visual evidence outside the dashboard.
4. Complete final report and presentation materials after the first draft deadline.
