from __future__ import annotations

import math

from app.schemas.vfm import RadarMetric, ScatterPoint, VfmCandidate, VfmResponse
from app.services.data_repository import PlayerRepository


def _vfm_index(overall: int, value_eur: int) -> float:
    safe_value = max(value_eur, 1)
    return round(overall / math.log(safe_value + 1), 3)


def _build_metrics(player: dict[str, object]) -> list[RadarMetric]:
    return [
        RadarMetric(label="Pace", value=float(player["pace"])),
        RadarMetric(label="Shooting", value=float(player["shooting"])),
        RadarMetric(label="Passing", value=float(player["passing"])),
        RadarMetric(label="Dribbling", value=float(player["dribbling"])),
        RadarMetric(label="Defending", value=float(player["defending"])),
        RadarMetric(label="Physic", value=float(player["physic"])),
    ]


def build_vfm_response(
    repository: PlayerRepository, position: str = "CAM", max_value: int = 120_000_000
) -> VfmResponse:
    players = repository.load_players()
    filtered = [
        player
        for player in players
        if player.get("value_eur") is not None
        if position.upper() in str(player["player_positions"]).upper()
        and int(player["value_eur"]) <= max_value
    ]

    ranked = sorted(
        filtered,
        key=lambda player: _vfm_index(int(player["overall"]), int(player["value_eur"])),
        reverse=True,
    )

    benchmark = max(
        filtered
        or [
            player
            for player in players
            if player.get("overall") is not None and player.get("potential") is not None
        ],
        key=lambda player: (int(player["overall"]), int(player["potential"])),
    )

    candidates = [
        VfmCandidate(
            short_name=str(player["short_name"]),
            club_name=str(player["club_name"]),
            league_name=str(player["league_name"]),
            nationality_name=str(player["nationality_name"]),
            value_eur=int(player["value_eur"]),
            wage_eur=int(player["wage_eur"]),
            overall=int(player["overall"]),
            potential=int(player["potential"]),
            player_positions=str(player["player_positions"]),
            vfm_index=_vfm_index(int(player["overall"]), int(player["value_eur"])),
            metrics=_build_metrics(player),
        )
        for player in ranked[:5]
    ]

    scatter_points = [
        ScatterPoint(
            short_name=str(player["short_name"]),
            overall=int(player["overall"]),
            value_eur=int(player["value_eur"]),
            vfm_index=_vfm_index(int(player["overall"]), int(player["value_eur"])),
            highlight=str(player["short_name"]) in {candidate.short_name for candidate in candidates[:3]},
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
