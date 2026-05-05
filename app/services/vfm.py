from __future__ import annotations

import math

from app.schemas.vfm import RadarMetric, ScatterPoint, VfmCandidate, VfmResponse
from app.services.data_repository import PlayerRepository

OUTFIELD_METRIC_FIELDS = [
    ("Pace", "pace"),
    ("Shooting", "shooting"),
    ("Passing", "passing"),
    ("Dribbling", "dribbling"),
    ("Defending", "defending"),
    ("Physic", "physic"),
]

GOALKEEPER_METRIC_FIELDS = [
    ("Diving", "goalkeeping_diving"),
    ("Handling", "goalkeeping_handling"),
    ("Kicking", "goalkeeping_kicking"),
    ("Positioning", "goalkeeping_positioning"),
    ("Reflexes", "goalkeeping_reflexes"),
    ("Speed", "goalkeeping_speed"),
]


def _vfm_index(overall: int, value_eur: int) -> float:
    safe_value = max(value_eur, 1)
    return round(overall / math.log(safe_value + 1), 3)


def _as_float(value: object, default: float = 0.0) -> float:
    if value is None:
        return default
    return float(value)


def _as_int(value: object, default: int = 0) -> int:
    if value is None:
        return default
    return int(value)


def _is_goalkeeper(player: dict[str, object]) -> bool:
    main_position = str(player.get("main_position") or "").upper()
    positions = {
        position.strip().upper()
        for position in str(player.get("player_positions") or "").split(",")
    }
    return main_position == "GK" or "GK" in positions


def _build_metrics(player: dict[str, object]) -> list[RadarMetric]:
    metric_fields = (
        GOALKEEPER_METRIC_FIELDS if _is_goalkeeper(player) else OUTFIELD_METRIC_FIELDS
    )
    return [
        RadarMetric(label=label, value=_as_float(player.get(field)))
        for label, field in metric_fields
    ]


def build_vfm_response(
    repository: PlayerRepository, position: str = "CAM", max_value: int = 120_000_000
) -> VfmResponse:
    players = repository.load_players()
    filtered = [
        player
        for player in players
        if player.get("value_eur") is not None
        and position.upper() in str(player.get("player_positions") or "").upper()
        and _as_int(player.get("value_eur")) <= max_value
    ]

    ranked = sorted(
        filtered,
        key=lambda player: _vfm_index(
            _as_int(player.get("overall")),
            _as_int(player.get("value_eur")),
        ),
        reverse=True,
    )

    benchmark = max(
        filtered
        or [
            player
            for player in players
            if player.get("overall") is not None and player.get("potential") is not None
        ],
        key=lambda player: (
            _as_int(player.get("overall")),
            _as_int(player.get("potential")),
        ),
    )

    candidates = [
        VfmCandidate(
            short_name=str(player["short_name"]),
            club_name=str(player["club_name"]),
            league_name=str(player["league_name"]),
            nationality_name=str(player["nationality_name"]),
            value_eur=_as_int(player.get("value_eur")),
            wage_eur=_as_int(player.get("wage_eur")),
            overall=_as_int(player.get("overall")),
            potential=_as_int(player.get("potential")),
            player_positions=str(player["player_positions"]),
            vfm_index=_vfm_index(
                _as_int(player.get("overall")),
                _as_int(player.get("value_eur")),
            ),
            metrics=_build_metrics(player),
        )
        for player in ranked[:20]
    ]

    scatter_points = [
        ScatterPoint(
            short_name=str(player["short_name"]),
            overall=_as_int(player.get("overall")),
            value_eur=_as_int(player.get("value_eur")),
            vfm_index=_vfm_index(
                _as_int(player.get("overall")),
                _as_int(player.get("value_eur")),
            ),
            highlight=str(player["short_name"])
            in {candidate.short_name for candidate in candidates[:3]},
        )
        for player in (filtered or players)
        if player.get("value_eur") is not None
    ]

    return VfmResponse(
        position=position.upper(),
        max_value=max_value,
        benchmark_name=str(benchmark["short_name"]),
        benchmark_metrics=_build_metrics(benchmark),
        candidates=candidates,
        scatter_points=scatter_points,
        notes=[
            "The scaffold already uses the SDS VfM formula: overall / log(value_eur + 1).",
            "Replace the seed ranking with the full-season merged dataset once the ETL is ready.",
        ],
    )
