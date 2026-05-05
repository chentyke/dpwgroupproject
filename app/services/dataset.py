from __future__ import annotations

from collections import Counter

from app.schemas.dataset import (
    CleaningReport,
    CleaningStep,
    ColumnProfile,
    DatasetSummary,
    NullHotspot,
)
from app.services.data_repository import POSITION_COLUMNS, PlayerRepository


def build_dataset_summary(repository: PlayerRepository) -> DatasetSummary:
    snapshot = repository.summary_snapshot()
    column_names = list(snapshot["fieldnames"])
    preview = snapshot["preview"]

    profiles: list[ColumnProfile] = []
    for name in column_names:
        null_count = int(snapshot["null_counts"].get(name, 0))
        if name in {
            "sofifa_id",
            "overall",
            "potential",
            "age",
            "pace",
            "shooting",
            "passing",
            "dribbling",
            "defending",
            "physic",
        }:
            dtype = "int"
        elif name in {"value_eur", "wage_eur", "release_clause_eur"}:
            dtype = "int"
        else:
            dtype = "str"
        profiles.append(
            ColumnProfile(
                name=name,
                dtype=dtype,
                null_count=null_count,
            )
        )

    return DatasetSummary(
        source=repository.source_name(),
        total_rows=int(snapshot["total_rows"]),
        total_columns=len(column_names),
        seasons=list(snapshot["seasons"]),
        genders=list(snapshot["genders"]),
        columns=profiles,
        preview=preview,
    )


def build_cleaning_report(repository: PlayerRepository) -> CleaningReport:
    snapshot = repository.cleaning_report_snapshot()
    total_rows = max(int(snapshot.get("rows_after", 0)), 1)
    null_counter = Counter(snapshot.get("missing_after", {}))

    hotspots = [
        NullHotspot(
            column=column,
            null_rate=round(count / total_rows, 3),
            note="Post-cleaning null rate from the generated tidy dataset.",
        )
        for column, count in null_counter.most_common(5)
        if count > 0
    ]

    if not hotspots:
        hotspots = [
            NullHotspot(
                column="club_team_id",
                null_rate=0.0,
                note="No post-cleaning null hotspots were detected in the current dataset.",
            )
        ]

    parsed_positions = snapshot.get("position_columns_parsed", [])
    parquet_written = bool(snapshot.get("cache", {}).get("written"))
    cache_note = str(snapshot.get("cache", {}).get("note", ""))
    duplicate_count = int(snapshot.get("duplicates_removed", 0))
    numeric_failures = {
        field: count
        for field, count in snapshot.get("numeric_coercion_failures", {}).items()
        if count
    }

    return CleaningReport(
        source=repository.source_name(),
        tidy_cache_path=str(repository.tidy_cache_path),
        position_columns=POSITION_COLUMNS,
        steps=[
            CleaningStep(
                title="Load yearly CSV snapshots",
                detail=(
                    f"Loaded {snapshot.get('rows_before', 0)} rows from the yearly FIFA CSV "
                    f"snapshots into one unified table."
                ),
                status="ready",
            ),
            CleaningStep(
                title="Normalize numeric market fields",
                detail=(
                    "Converted ratings, IDs, value_eur, wage_eur, release_clause_eur, "
                    "and ability columns into nullable numeric types."
                ),
                status="ready",
            ),
            CleaningStep(
                title="Split position rating strings",
                detail=(
                    f"Parsed {len(parsed_positions)} position columns into base, modifier, "
                    "and effective rating fields."
                ),
                status="ready" if len(parsed_positions) == len(POSITION_COLUMNS) else "partial",
            ),
            CleaningStep(
                title="Write tidy parquet cache",
                detail=(
                    cache_note
                    or "Persist players_tidy.parquet for downstream APIs and dashboards."
                ),
                status="ready" if parquet_written else "blocked",
            ),
        ],
        null_hotspots=hotspots,
        notes=[
            (
                f"Final cleaned shape is {snapshot.get('final_shape', [0, 0])[0]} rows "
                f"by {snapshot.get('final_shape', [0, 0])[1]} columns."
            ),
            f"Duplicate player-season rows removed: {duplicate_count}.",
            (
                "Numeric coercion failures: "
                + (
                    ", ".join(
                        f"{field}={count}" for field, count in numeric_failures.items()
                    )
                    or "none"
                )
                + "."
            ),
        ],
    )
