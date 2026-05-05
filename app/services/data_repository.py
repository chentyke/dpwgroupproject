from __future__ import annotations

import csv
import json
import re
from functools import cached_property, lru_cache
from pathlib import Path
from typing import Any, Iterable

from app.core.config import get_settings

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
POSITION_RATING_PATTERN = re.compile(r"^\s*(?P<base>\d+)(?P<modifier>[+-]\d+)?\s*$")
INT_FIELDS = {
    "sofifa_id",
    "overall",
    "potential",
    "age",
    "height_cm",
    "weight_kg",
    "club_team_id",
    "league_level",
    "club_jersey_number",
    "club_contract_valid_until",
    "nationality_id",
    "nation_team_id",
    "nation_jersey_number",
    "weak_foot",
    "skill_moves",
    "international_reputation",
    "pace",
    "shooting",
    "passing",
    "dribbling",
    "defending",
    "physic",
    "goalkeeping_diving",
    "goalkeeping_handling",
    "goalkeeping_kicking",
    "goalkeeping_positioning",
    "goalkeeping_reflexes",
    "goalkeeping_speed",
    "attacking_crossing",
    "attacking_finishing",
    "attacking_heading_accuracy",
    "attacking_short_passing",
    "attacking_volleys",
    "skill_dribbling",
    "skill_curve",
    "skill_fk_accuracy",
    "skill_long_passing",
    "skill_ball_control",
    "movement_acceleration",
    "movement_sprint_speed",
    "movement_agility",
    "movement_reactions",
    "movement_balance",
    "power_shot_power",
    "power_jumping",
    "power_stamina",
    "power_strength",
    "power_long_shots",
    "mentality_aggression",
    "mentality_interceptions",
    "mentality_positioning",
    "mentality_vision",
    "mentality_penalties",
    "mentality_composure",
    "defending_marking_awareness",
    "defending_standing_tackle",
    "defending_sliding_tackle",
}
FLOAT_TO_INT_FIELDS = {
    "value_eur",
    "wage_eur",
    "release_clause_eur",
}
DATE_FIELDS = {"dob", "club_joined"}
PREVIEW_FIELDS = [
    "sofifa_id",
    "short_name",
    "player_positions",
    "overall",
    "potential",
    "value_eur",
    "wage_eur",
    "league_name",
    "nationality_name",
]


class PlayerRepository:
    def __init__(
        self,
        raw_data_dir: Path,
        sample_path: Path,
        tidy_cache_path: Path | None = None,
    ) -> None:
        self.raw_data_dir = raw_data_dir
        self.sample_path = sample_path
        self.tidy_cache_path = tidy_cache_path or get_settings().tidy_cache_path

    @cached_property
    def csv_files(self) -> list[Path]:
        return sorted(self.raw_data_dir.glob("*.csv"))

    @cached_property
    def _players(self) -> list[dict[str, Any]]:
        if self.csv_files:
            dataframe, _ = self._cleaned_dataset
            return self._frame_to_records(dataframe)
        return self._load_sample_players()

    def load_players(self) -> list[dict[str, Any]]:
        return self._players

    def load_player_columns(self, columns: Iterable[str]) -> list[dict[str, Any]]:
        column_key = tuple(dict.fromkeys(columns))
        return self._load_player_columns_cached(column_key)

    @lru_cache(maxsize=16)
    def _load_player_columns_cached(
        self,
        columns: tuple[str, ...],
    ) -> list[dict[str, Any]]:
        if not columns:
            return []

        if self.csv_files:
            frame = self._read_column_frame(columns)
            return self._frame_to_records(frame)

        return [
            {column: player.get(column) for column in columns}
            for player in self._load_sample_players()
        ]

    def _read_column_frame(self, columns: tuple[str, ...]) -> Any:
        if self.tidy_cache_path.exists() and self._cache_is_fresh(self.tidy_cache_path):
            try:
                import pandas as pd
                import pyarrow.parquet as pq

                parquet_file = pq.ParquetFile(self.tidy_cache_path)
                available_columns = set(parquet_file.schema_arrow.names)
                selected_columns = [
                    column for column in columns if column in available_columns
                ]
                frame = pd.read_parquet(
                    self.tidy_cache_path,
                    columns=selected_columns,
                )
                for column in columns:
                    if column not in frame.columns:
                        frame[column] = None
                return frame.loc[:, list(columns)]
            except Exception:
                pass

        dataframe, _ = self._cleaned_dataset
        frame = dataframe.copy()
        for column in columns:
            if column not in frame.columns:
                frame[column] = None
        return frame.loc[:, list(columns)]

    def _load_sample_players(self) -> list[dict[str, Any]]:
        with self.sample_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    @cached_property
    def _cleaned_dataset(self) -> tuple[Any, dict[str, Any]]:
        import pandas as pd

        cached_frame = self._read_tidy_cache()
        if cached_frame is not None:
            report = self._read_cleaning_report()
            if report is None:
                report = self._build_report_from_frame(
                    cached_frame,
                    parquet_written=True,
                    cache_status="read existing tidy cache",
                )
            return cached_frame, report

        raw_frame = self._read_raw_csv_frame(pd)
        cleaned_frame, report = self._clean_frame(raw_frame)
        parquet_written, parquet_note = self._write_tidy_cache(cleaned_frame)
        report["cache"] = {
            "path": str(self.tidy_cache_path),
            "written": parquet_written,
            "note": parquet_note,
        }
        self._write_processing_artifacts(cleaned_frame, report)
        return cleaned_frame, report

    def _read_raw_csv_frame(self, pd: Any) -> Any:
        frames = []
        for path in self.csv_files:
            frame = pd.read_csv(path, encoding="utf-8-sig", low_memory=False)
            frame["season"] = int(path.stem.split("_")[-1])
            frame["gender"] = "female" if path.name.startswith("female_") else "male"
            frame["source_file"] = path.name
            frames.append(frame)
        return pd.concat(frames, ignore_index=True)

    def _clean_frame(self, raw_frame: Any) -> tuple[Any, dict[str, Any]]:
        import pandas as pd

        frame = raw_frame.copy()
        missing_before = self._missing_counts(frame)
        rows_before = int(frame.shape[0])
        columns_before = int(frame.shape[1])

        if "player_positions" in frame.columns:
            frame["main_position"] = (
                frame["player_positions"].astype("string").str.split(",").str[0].str.strip()
            )

        coercion_counts: dict[str, int] = {}
        numeric_fields = (INT_FIELDS | FLOAT_TO_INT_FIELDS) & set(frame.columns)
        for field in sorted(numeric_fields):
            before_invalid = frame[field].notna() & pd.to_numeric(
                frame[field], errors="coerce"
            ).isna()
            coerced = pd.to_numeric(frame[field], errors="coerce")
            if field in INT_FIELDS or field in FLOAT_TO_INT_FIELDS:
                coerced = coerced.round().astype("Int64")
            frame[field] = coerced
            coercion_counts[field] = int(before_invalid.sum())

        for field in sorted(DATE_FIELDS & set(frame.columns)):
            frame[field] = pd.to_datetime(frame[field], errors="coerce").dt.date

        parsed_position_columns = []
        for position in POSITION_COLUMNS:
            if position not in frame.columns:
                continue
            extracted = frame[position].astype("string").str.extract(POSITION_RATING_PATTERN)
            base = pd.to_numeric(extracted["base"], errors="coerce").astype("Int64")
            modifier = pd.to_numeric(
                extracted["modifier"].fillna("0"), errors="coerce"
            ).astype("Int64")
            modifier = modifier.where(base.notna())
            frame[f"{position}_base_rating"] = base
            frame[f"{position}_modifier"] = modifier
            frame[f"{position}_effective"] = (base + modifier).astype("Int64")
            parsed_position_columns.append(position)

        duplicate_subset = [
            field
            for field in ("season", "gender", "sofifa_id")
            if field in frame.columns
        ]
        duplicates_removed = 0
        if len(duplicate_subset) == 3:
            duplicates_removed = int(frame.duplicated(subset=duplicate_subset).sum())
            if duplicates_removed:
                frame = frame.drop_duplicates(subset=duplicate_subset, keep="first")

        missing_after = self._missing_counts(frame)
        report = {
            "source": self.source_name(),
            "rows_before": rows_before,
            "rows_after": int(frame.shape[0]),
            "columns_before": columns_before,
            "columns_after": int(frame.shape[1]),
            "duplicates_removed": duplicates_removed,
            "missing_before": missing_before,
            "missing_after": missing_after,
            "numeric_coercion_failures": coercion_counts,
            "position_columns_parsed": parsed_position_columns,
            "final_shape": [int(frame.shape[0]), int(frame.shape[1])],
        }
        return frame, report

    def _read_tidy_cache(self) -> Any | None:
        cache_path = self.tidy_cache_path
        if not cache_path.exists() or not self._cache_is_fresh(cache_path):
            return None
        try:
            import pandas as pd

            frame = pd.read_parquet(cache_path)
        except Exception:
            return None
        required_columns = {"season", "gender", "sofifa_id", "main_position", "source_file"}
        required_columns.update({f"{position}_base_rating" for position in POSITION_COLUMNS})
        if not required_columns.issubset(set(frame.columns)):
            return None
        cached_sources = {str(item) for item in frame["source_file"].dropna().unique()}
        expected_sources = {path.name for path in self.csv_files}
        if cached_sources != expected_sources:
            return None
        report = self._read_cleaning_report()
        if report is not None:
            if int(report.get("rows_after", -1)) != int(frame.shape[0]):
                return None
            if int(report.get("rows_before", -1)) != self._raw_row_count():
                return None
        return frame

    def _raw_row_count(self) -> int:
        total = 0
        for path in self.csv_files:
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                total += max(sum(1 for _ in handle) - 1, 0)
        return total

    def _cache_is_fresh(self, cache_path: Path) -> bool:
        cache_mtime = cache_path.stat().st_mtime
        return all(path.stat().st_mtime <= cache_mtime for path in self.csv_files)

    def _write_tidy_cache(self, frame: Any) -> tuple[bool, str]:
        output_path = self.tidy_cache_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            frame.to_parquet(output_path, index=False)
        except Exception as exc:
            if output_path.exists():
                output_path.unlink()
            return (
                False,
                f"Parquet cache was not written because the parquet engine failed: {exc}",
            )
        return True, "Parquet cache written successfully."

    def _write_processing_artifacts(self, frame: Any, report: dict[str, Any]) -> None:
        self.tidy_cache_path.parent.mkdir(parents=True, exist_ok=True)
        report_path = self.tidy_cache_path.with_name("cleaning_report.json")
        summary_path = self.tidy_cache_path.with_name("summary.json")
        with report_path.open("w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=4, default=str)
        summary = {
            "total_rows": int(frame.shape[0]),
            "total_columns": int(frame.shape[1]),
            "seasons": sorted(int(item) for item in frame["season"].dropna().unique()),
            "genders": sorted(str(item) for item in frame["gender"].dropna().unique()),
        }
        with summary_path.open("w", encoding="utf-8") as handle:
            json.dump(summary, handle, indent=2)

    def _read_cleaning_report(self) -> dict[str, Any] | None:
        report_path = self.tidy_cache_path.with_name("cleaning_report.json")
        if not report_path.exists():
            return None
        try:
            with report_path.open("r", encoding="utf-8") as handle:
                return json.load(handle)
        except (json.JSONDecodeError, OSError):
            return None

    def _build_report_from_frame(
        self,
        frame: Any,
        *,
        parquet_written: bool,
        cache_status: str,
    ) -> dict[str, Any]:
        return {
            "source": self.source_name(),
            "rows_before": int(frame.shape[0]),
            "rows_after": int(frame.shape[0]),
            "columns_before": int(frame.shape[1]),
            "columns_after": int(frame.shape[1]),
            "duplicates_removed": 0,
            "missing_before": self._missing_counts(frame),
            "missing_after": self._missing_counts(frame),
            "numeric_coercion_failures": {},
            "position_columns_parsed": [
                position
                for position in POSITION_COLUMNS
                if f"{position}_base_rating" in frame.columns
            ],
            "final_shape": [int(frame.shape[0]), int(frame.shape[1])],
            "cache": {
                "path": str(self.tidy_cache_path),
                "written": parquet_written,
                "note": cache_status,
            },
        }

    def _missing_counts(self, frame: Any) -> dict[str, int]:
        return {
            str(column): int(count)
            for column, count in frame.isna().sum().items()
        }

    def _frame_to_records(self, frame: Any) -> list[dict[str, Any]]:
        object_frame = frame.astype(object).where(frame.notna(), None)
        return object_frame.to_dict(orient="records")

    def _normalize_value(self, key: str, value: str | None) -> Any:
        if value is None:
            return None

        cleaned = value.strip()
        if cleaned == "":
            return None

        if key in INT_FIELDS:
            try:
                return int(float(cleaned))
            except ValueError:
                return None
        if key in FLOAT_TO_INT_FIELDS:
            try:
                return int(float(cleaned))
            except ValueError:
                return None
        return cleaned

    def source_name(self) -> str:
        return "csv-archive" if self.csv_files else "sample-fixture"

    @cached_property
    def _summary_snapshot(self) -> dict[str, Any]:
        if self.csv_files:
            return self._build_csv_summary_snapshot()
        players = self._load_sample_players()
        fieldnames = list(players[0].keys())
        preview = [
            {key: player.get(key) for key in PREVIEW_FIELDS if key in player}
            for player in players[:5]
        ]
        null_counts = {
            key: sum(player.get(key) in (None, "") for player in players)
            for key in fieldnames
        }
        return {
            "fieldnames": fieldnames,
            "preview": preview,
            "null_counts": null_counts,
            "total_rows": len(players),
            "seasons": sorted({int(player["season"]) for player in players}),
            "genders": sorted({str(player["gender"]) for player in players}),
        }

    def _build_csv_summary_snapshot(self) -> dict[str, Any]:
        fieldnames: list[str] | None = None
        preview: list[dict[str, Any]] = []
        null_counts: dict[str, int] = {}
        total_rows = 0
        seasons: set[int] = set()
        genders: set[str] = set()

        for path in self.csv_files:
            gender = "female" if path.name.startswith("female_") else "male"
            season = int(path.stem.split("_")[-1])
            genders.add(gender)
            seasons.add(season)
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle)
                if fieldnames is None:
                    fieldnames = list(reader.fieldnames or [])
                    null_counts = {key: 0 for key in fieldnames}
                for row in reader:
                    total_rows += 1
                    if len(preview) < 5:
                        preview_row = {
                            key: self._normalize_value(key, row.get(key))
                            for key in PREVIEW_FIELDS
                        }
                        preview_row["season"] = season
                        preview_row["gender"] = gender
                        preview.append(preview_row)
                    for key in fieldnames or []:
                        if self._normalize_value(key, row.get(key)) is None:
                            null_counts[key] += 1

        return {
            "fieldnames": fieldnames or [],
            "preview": preview,
            "null_counts": null_counts,
            "total_rows": total_rows,
            "seasons": sorted(seasons),
            "genders": sorted(genders),
        }

    def summary_snapshot(self) -> dict[str, Any]:
        return self._summary_snapshot

    def run_etl(self) -> dict[str, Any]:
        dataframe, report = self._cleaned_dataset

        return {
            "rows": int(dataframe.shape[0]),
            "cols": int(dataframe.shape[1]),
            "output": str(self.tidy_cache_path),
            "report": str(self.tidy_cache_path.with_name("cleaning_report.json")),
            "parquet_written": bool(report.get("cache", {}).get("written")),
        }

    def cleaning_report_snapshot(self) -> dict[str, Any]:
        if self.csv_files:
            _, report = self._cleaned_dataset
            return report
        players = self._load_sample_players()
        return {
            "source": self.source_name(),
            "rows_before": len(players),
            "rows_after": len(players),
            "columns_before": len(players[0]) if players else 0,
            "columns_after": len(players[0]) if players else 0,
            "duplicates_removed": 0,
            "missing_before": {},
            "missing_after": {},
            "numeric_coercion_failures": {},
            "position_columns_parsed": [],
            "final_shape": [len(players), len(players[0]) if players else 0],
            "cache": {
                "path": str(self.tidy_cache_path),
                "written": False,
                "note": "Sample fixture mode does not write a tidy cache.",
            },
        }


@lru_cache
def get_player_repository() -> PlayerRepository:
    settings = get_settings()
    return PlayerRepository(settings.raw_data_dir, settings.sample_data_path)
