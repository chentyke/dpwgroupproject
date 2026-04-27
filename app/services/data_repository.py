from __future__ import annotations

import csv
import json
from functools import cached_property, lru_cache
from pathlib import Path
from typing import Any

from app.core.config import get_settings

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
}
FLOAT_TO_INT_FIELDS = {
    "value_eur",
    "wage_eur",
    "release_clause_eur",
}
PROJECT_FIELDS = {
    "sofifa_id",
    "short_name",
    "club_name",
    "league_name",
    "nationality_name",
    "player_positions",
    "overall",
    "potential",
    "value_eur",
    "wage_eur",
    "age",
    "pace",
    "shooting",
    "passing",
    "dribbling",
    "defending",
    "physic",
}
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
    def __init__(self, raw_data_dir: Path, sample_path: Path) -> None:
        self.raw_data_dir = raw_data_dir
        self.sample_path = sample_path

    @cached_property
    def csv_files(self) -> list[Path]:
        return sorted(self.raw_data_dir.glob("*.csv"))

    @cached_property
    def _players(self) -> list[dict[str, Any]]:
        if self.csv_files:
            return self._load_csv_players()
        return self._load_sample_players()

    def load_players(self) -> list[dict[str, Any]]:
        return self._players

    def _load_sample_players(self) -> list[dict[str, Any]]:
        with self.sample_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _load_csv_players(self) -> list[dict[str, Any]]:
        players: list[dict[str, Any]] = []
        for path in self.csv_files:
            gender = "female" if path.name.startswith("female_") else "male"
            season = int(path.stem.split("_")[-1])
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle)
                for row in reader:
                    normalized = {
                        key: self._normalize_value(key, row.get(key))
                        for key in PROJECT_FIELDS
                    }
                    if normalized.get("player_positions"):
                        normalized["main_position"] = normalized["player_positions"].split(",")[0]
                    if normalized.get("age") is None:
                        normalized["age"] = 0
                    normalized["season"] = season
                    normalized["gender"] = gender
                    players.append(normalized)
        return players

    def _normalize_value(self, key: str, value: str | None) -> Any:
        if value is None:
            return None

        cleaned = value.strip()
        if cleaned == "":
            return None

        if key in INT_FIELDS:
            return int(float(cleaned))
        if key in FLOAT_TO_INT_FIELDS:
            return int(float(cleaned))
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
        import pandas as pd
        import json
        from pathlib import Path

        output_path = Path("data/processed/players_tidy.parquet")
        report_path = Path("data/processed/cleaning_report.json")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        players = self.load_players()
        df = pd.DataFrame(players)


        report = {
             "missing_before": df.isnull().sum().to_dict()
        }


        df = df.dropna()

        report["missing_after"] = df.isnull().sum().to_dict()
        report["final_shape"] = df.shape

        df.to_parquet(output_path, index=False)

        with report_path.open("w", encoding="utf-8") as f:
             json.dump(report, f, indent=4)

        return {
              "rows": df.shape[0],
              "cols": df.shape[1],
              "output": str(output_path)
        }


@lru_cache
def get_player_repository() -> PlayerRepository:
    settings = get_settings()
    return PlayerRepository(settings.raw_data_dir, settings.sample_data_path)
