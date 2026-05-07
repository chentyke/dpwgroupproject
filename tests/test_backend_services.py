from __future__ import annotations

import csv
import json
import warnings
from math import isfinite
from pathlib import Path

import pytest

from app.services import fairness
from app.services.advanced import build_cluster_response, build_prediction_response
from app.services.data_repository import POSITION_COLUMNS, PlayerRepository
from app.services.dataset import build_cleaning_report, build_dataset_summary
from app.services.fairness import build_fairness_by_league
from app.services.injury import build_future_risk_response
from app.services.vfm import build_vfm_response


BASE_COLUMNS = [
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
    "goalkeeping_diving",
    "goalkeeping_handling",
    "goalkeeping_kicking",
    "goalkeeping_positioning",
    "goalkeeping_reflexes",
    "goalkeeping_speed",
]


def _write_fixture(raw_dir: Path) -> None:
    raw_dir.mkdir()
    columns = BASE_COLUMNS + POSITION_COLUMNS
    rows = [
        {
            "sofifa_id": "1",
            "short_name": "Alpha",
            "club_name": "Club A",
            "league_name": "League A",
            "nationality_name": "Nation A",
            "player_positions": "CAM, CM",
            "overall": "86",
            "potential": "90",
            "value_eur": "50000000.0",
            "wage_eur": "250000.0",
            "age": "24",
            "pace": "80",
            "shooting": "78",
            "passing": "84",
            "dribbling": "86",
            "defending": "52",
            "physic": "70",
        },
        {
            "sofifa_id": "2",
            "short_name": "Beta",
            "club_name": "Club B",
            "league_name": "League A",
            "nationality_name": "Nation B",
            "player_positions": "CAM",
            "overall": "84",
            "potential": "88",
            "value_eur": "35000000.0",
            "wage_eur": "210000.0",
            "age": "23",
            "pace": "77",
            "shooting": "75",
            "passing": "82",
            "dribbling": "83",
            "defending": "50",
            "physic": "68",
        },
        {
            "sofifa_id": "3",
            "short_name": "Gamma",
            "club_name": "Club C",
            "league_name": "League B",
            "nationality_name": "Nation A",
            "player_positions": "CB",
            "overall": "83",
            "potential": "86",
            "value_eur": "25000000.0",
            "wage_eur": "45000.0",
            "age": "26",
            "pace": "62",
            "shooting": "45",
            "passing": "65",
            "dribbling": "60",
            "defending": "85",
            "physic": "84",
        },
        {
            "sofifa_id": "4",
            "short_name": "Delta",
            "club_name": "Club D",
            "league_name": "League B",
            "nationality_name": "Nation B",
            "player_positions": "ST",
            "overall": "82",
            "potential": "85",
            "value_eur": "22000000.0",
            "wage_eur": "40000.0",
            "age": "25",
            "pace": "83",
            "shooting": "82",
            "passing": "70",
            "dribbling": "78",
            "defending": "40",
            "physic": "76",
        },
    ]
    for row in rows:
        for field in [
            "goalkeeping_diving",
            "goalkeeping_handling",
            "goalkeeping_kicking",
            "goalkeeping_positioning",
            "goalkeeping_reflexes",
            "goalkeeping_speed",
        ]:
            row[field] = "20"
        for position in POSITION_COLUMNS:
            row[position] = "80+2"

    with (raw_dir / "players_22.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def _repository(tmp_path: Path) -> PlayerRepository:
    sample_path = tmp_path / "sample.json"
    sample_path.write_text(json.dumps([]), encoding="utf-8")
    raw_dir = tmp_path / "raw"
    _write_fixture(raw_dir)
    return PlayerRepository(
        raw_dir,
        sample_path,
        tmp_path / "processed" / "players_tidy.parquet",
    )


def _write_injury_fixture(raw_dir: Path) -> None:
    raw_dir.mkdir()
    columns = [
        "sofifa_id",
        "short_name",
        "long_name",
        "player_traits",
        "age",
        "overall",
        "potential",
        "pace",
        "defending",
        "physic",
        "power_stamina",
        "mentality_composure",
    ]
    players = [
        ("1", "Alpha", "Injury Prone"),
        ("2", "Beta", "Solid Player"),
        ("3", "Gamma", ""),
        ("4", "Delta", "Injury Prone"),
        ("5", "Echo", "Solid Player"),
        ("6", "Foxtrot", ""),
        ("7", "Golf", "Injury Prone"),
        ("8", "Hotel", "Solid Player"),
        ("9", "India", ""),
        ("10", "Juliet", "Injury Prone"),
        ("11", "Kilo", "Solid Player"),
        ("12", "Lima", ""),
    ]

    by_season: dict[str, list[dict[str, str]]] = {"15": [], "16": []}
    for index, (sofifa_id, short_name, future_trait) in enumerate(players, start=1):
        base = 55 + index
        by_season["15"].append(
            {
                "sofifa_id": sofifa_id,
                "short_name": short_name,
                "long_name": f"{short_name} Player",
                "player_traits": "",
                "age": str(20 + index % 8),
                "overall": str(base),
                "potential": str(base + 6),
                "pace": str(base + 3),
                "defending": str(base - 2),
                "physic": str(base + 1),
                "power_stamina": str(base + 4),
                "mentality_composure": str(base + 5),
            }
        )
        by_season["16"].append(
            {
                "sofifa_id": sofifa_id,
                "short_name": short_name,
                "long_name": f"{short_name} Player",
                "player_traits": future_trait,
                "age": str(21 + index % 8),
                "overall": str(base + 1),
                "potential": str(base + 6),
                "pace": str(base + 3),
                "defending": str(base - 1),
                "physic": str(base + 2),
                "power_stamina": str(base + 5),
                "mentality_composure": str(base + 4),
            }
        )

    for season, rows in by_season.items():
        with (raw_dir / f"players_{season}.csv").open(
            "w",
            encoding="utf-8",
            newline="",
        ) as handle:
            writer = csv.DictWriter(handle, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)


def _injury_repository(tmp_path: Path) -> PlayerRepository:
    sample_path = tmp_path / "sample.json"
    sample_path.write_text(json.dumps([]), encoding="utf-8")
    raw_dir = tmp_path / "raw_injury"
    _write_injury_fixture(raw_dir)
    return PlayerRepository(
        raw_dir,
        sample_path,
        tmp_path / "processed_injury" / "players_tidy.parquet",
    )


def test_dataset_summary_and_cleaning_report_use_real_csv(tmp_path: Path) -> None:
    repository = _repository(tmp_path)

    summary = build_dataset_summary(repository)
    report = build_cleaning_report(repository)
    first_player = repository.load_players()[0]

    assert summary.source == "csv-archive"
    assert summary.total_rows == 4
    assert summary.total_columns == len(BASE_COLUMNS) + len(POSITION_COLUMNS)
    assert first_player["cam_base_rating"] == 80
    assert first_player["cam_modifier"] == 2
    assert first_player["cam_effective"] == 82
    assert any(
        step.title == "Split position rating strings" and step.status == "ready"
        for step in report.steps
    )


def test_backend_analysis_services_return_real_results_without_scipy(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repository = _repository(tmp_path)
    monkeypatch.setattr(fairness, "_load_scipy_stats", lambda: None)

    vfm = build_vfm_response(repository, position="CAM", max_value=60_000_000)
    wages = build_fairness_by_league(repository, overall_min=80, overall_max=90)
    clusters = build_cluster_response(repository, k=2)
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="R\\^2 score is not well-defined with less than two samples.",
        )
        prediction = build_prediction_response(
            repository,
            overall=85,
            potential=89,
            age=24,
            wage_eur=100_000,
            pace=79,
            shooting=76,
            dribbling=84,
            passing=83,
            defending=51,
            physic=69,
        )

    assert len(vfm.candidates) == 2
    assert wages.test.statistic is not None
    assert wages.test.p_value is not None
    assert "engine=pure-python" in wages.test.note
    assert clusters.k == 2
    assert len(clusters.points) == 4
    assert prediction.estimated_value_eur > 0
    assert prediction.r2_score is None or isfinite(prediction.r2_score)


def test_prediction_does_not_return_heuristic_when_training_data_is_missing(
    tmp_path: Path,
) -> None:
    sample_path = tmp_path / "empty_sample.json"
    sample_path.write_text("[]", encoding="utf-8")
    repository = PlayerRepository(
        tmp_path / "missing_raw",
        sample_path,
        tmp_path / "processed" / "players_tidy.parquet",
    )

    with pytest.raises(ValueError, match="Insufficient valid training rows"):
        build_prediction_response(
            repository,
            overall=85,
            potential=89,
            age=24,
            wage_eur=100_000,
            pace=79,
            shooting=76,
            dribbling=84,
            passing=83,
            defending=51,
            physic=69,
        )


def test_future_injury_models_use_grouped_future_labels(tmp_path: Path) -> None:
    repository = _injury_repository(tmp_path)

    response = build_future_risk_response(repository)

    assert response.total_records == 24
    assert response.modeling_records == 12
    assert response.feature_count >= 6
    assert response.injury_model.positive_records == 4
    assert response.solid_model.positive_records == 4
    assert response.injury_model.training_rows > 0
    assert response.injury_model.test_rows > 0
    assert response.solid_model.training_rows > 0
    assert response.solid_model.test_rows > 0
    assert response.injury_model.train_players + response.injury_model.test_players == 12
    assert response.injury_model.top_features
    assert response.solid_model.top_features
