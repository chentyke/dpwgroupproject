from __future__ import annotations

from collections import Counter

from app.core.config import get_settings
from app.schemas.dataset import (
    CleaningReport,
    CleaningStep,
    ColumnProfile,
    DatasetSummary,
    NullHotspot,
)
from app.services.data_repository import PlayerRepository

POSITION_COLUMNS = [
    "ls",
    "st",
    "rs",
    "lw",
    "lf",
    "cf",
    "rf",
    "rw",
    "lam",
    "cam",
    "ram",
    "lm",
    "lcm",
    "cm",
    "rcm",
    "rm",
    "lwb",
    "ldm",
    "cdm",
    "rdm",
    "rwb",
    "lb",
    "lcb",
    "cb",
    "rcb",
    "rb",
    "gk",
]


def build_dataset_summary(repository: PlayerRepository) -> DatasetSummary:
    snapshot = repository.summary_snapshot()
    column_names = list(snapshot["fieldnames"])
    preview = snapshot["preview"]

    profiles: list[ColumnProfile] = []
    for name in column_names:
        null_count = int(snapshot["null_counts"].get(name, 0))
        if name in {"sofifa_id", "overall", "potential", "age", "pace", "shooting", "passing", "dribbling", "defending", "physic"}:
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
    snapshot = repository.summary_snapshot()
    settings = get_settings()
    total_rows = int(snapshot["total_rows"])
    null_counter = Counter(snapshot["null_counts"])

    hotspots = [
        NullHotspot(
            column=column,
            null_rate=round(count / total_rows, 3),
            note="Replace the seed fixture with the real CSV completeness profile.",
        )
        for column, count in null_counter.most_common(5)
    ]

    if not hotspots:
        hotspots = [
            NullHotspot(
                column="club_team_id",
                null_rate=0.0,
                note="Sample data is intentionally dense; real FIFA CSVs are sparser.",
            )
        ]

    return CleaningReport(
        source=repository.source_name(),
        tidy_cache_path=str(settings.tidy_cache_path),
        position_columns=POSITION_COLUMNS,
        steps=[
            CleaningStep(
                title="Load yearly CSV snapshots",
                detail="The scaffold reserves data/raw/ for the 15 FIFA CSV files.",
                status="next",
            ),
            CleaningStep(
                title="Normalize numeric market fields",
                detail="Convert value_eur and wage_eur into numeric columns.",
                status="ready",
            ),
            CleaningStep(
                title="Split position rating strings",
                detail="Expand values such as '89+3' into base and modifier fields.",
                status="todo",
            ),
            CleaningStep(
                title="Write tidy parquet cache",
                detail="Persist players_tidy.parquet for downstream APIs and dashboards.",
                status="todo",
            ),
        ],
        null_hotspots=hotspots,
        notes=[
            "This report is scaffold-backed and should be replaced by live profiling once raw CSVs are added.",
            "The meeting note explicitly reserves Week 1 for scaffolding plus the first cleaning pass.",
        ],
    )
