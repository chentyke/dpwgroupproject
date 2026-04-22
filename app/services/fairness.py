from __future__ import annotations

from collections import defaultdict
from statistics import median

from app.schemas.fairness import (
    FairnessByLeagueResponse,
    HeatmapCell,
    LeagueDistribution,
    NationalityHeatmapResponse,
    StatisticalTestSummary,
)
from app.services.data_repository import PlayerRepository


def build_fairness_by_league(
    repository: PlayerRepository, overall_min: int = 80, overall_max: int = 90
) -> FairnessByLeagueResponse:
    players = repository.load_players()
    filtered = [
        player
        for player in players
        if overall_min <= int(player["overall"]) <= overall_max
        and player.get("wage_eur") is not None
        and player.get("league_name") is not None
    ]

    grouped: dict[str, list[int]] = defaultdict(list)
    for player in filtered:
        grouped[str(player["league_name"])].append(int(player["wage_eur"]))

    distributions = [
        LeagueDistribution(
            league_name=league_name,
            sample_size=len(wages),
            min_wage=min(wages),
            median_wage=int(median(wages)),
            average_wage=int(sum(wages) / len(wages)),
            max_wage=max(wages),
        )
        for league_name, wages in sorted(grouped.items())
    ]

    spread = 0.0
    if distributions:
        averages = [item.average_wage for item in distributions]
        spread = round((max(averages) - min(averages)) / max(max(averages), 1), 3)

    return FairnessByLeagueResponse(
        overall_min=overall_min,
        overall_max=overall_max,
        distributions=distributions,
        test=StatisticalTestSummary(
            method="placeholder-kruskal",
            statistic=round(spread * 10, 3) if distributions else None,
            p_value=None,
            note=(
                "This is a scaffold placeholder. Replace it with scipy.stats.kruskal "
                "and Dunn post-hoc testing once the full dataset is wired in."
            ),
        ),
        notes=[
            "Week 1 goal: lock the endpoint contract and page wiring.",
            "Week 2 goal from the meeting note: return real VfM and fairness analysis on real data.",
        ],
    )


def build_nationality_heatmap(repository: PlayerRepository) -> NationalityHeatmapResponse:
    players = repository.load_players()
    grouped: dict[tuple[str, str], list[int]] = defaultdict(list)
    for player in players:
        if player.get("wage_eur") is None or player.get("league_name") is None:
            continue
        key = (str(player["nationality_name"]), str(player["league_name"]))
        grouped[key].append(int(player["wage_eur"]))

    cells = [
        HeatmapCell(
            nationality_name=nationality,
            league_name=league,
            average_wage=int(sum(wages) / len(wages)),
            sample_size=len(wages),
        )
        for (nationality, league), wages in sorted(grouped.items())
    ]

    return NationalityHeatmapResponse(
        cells=cells,
        notes=[
            "The current heatmap uses average wage only.",
            "Real implementation should add top-n league and nationality filtering to avoid sparse matrices.",
        ],
    )
