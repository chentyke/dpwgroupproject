from __future__ import annotations

from collections import Counter, defaultdict
from math import sqrt
from statistics import median
from typing import Any

from app.schemas.fairness import (
    FairnessByLeagueResponse,
    HeatmapCell,
    LeagueDistribution,
    NationalityHeatmapResponse,
    StatisticalTestSummary,
)
from app.services.data_repository import PlayerRepository

SIGNIFICANCE_LEVEL = 0.05
MAX_SIGNIFICANT_PAIRS = 3


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

    if not filtered and len(players) < 100:
        filtered = [
            player for player in players
            if player.get("wage_eur") is not None and player.get("league_name") is not None
        ]

    grouped: dict[str, list[int]] = defaultdict(list)
    for player in filtered:
        grouped[str(player["league_name"])].append(int(player["wage_eur"]))

    valid_grouped = {
        league: wages for league, wages in grouped.items() if len(wages) >= 2
    }

    distributions = [
        LeagueDistribution(
            league_name=league_name,
            sample_size=len(wages),
            min_wage=min(wages),
            median_wage=int(median(wages)),
            average_wage=int(sum(wages) / len(wages)),
            max_wage=max(wages),
        )
        for league_name, wages in sorted(valid_grouped.items())
    ]

    distributions.sort(key=lambda item: item.average_wage, reverse=True)

    stat, p_val = None, None
    note = "Insufficient sample groups to perform the Kruskal-Wallis test."

    league_wages_lists = list(valid_grouped.values())

    if len(league_wages_lists) >= 2:
        stats_module = _load_scipy_stats()
        if stats_module is None:
            note = (
                "SciPy is not installed in this environment; install requirements.txt "
                "to run the Kruskal-Wallis and Dunn tests."
            )
        else:
            stat, p_val = stats_module.kruskal(*league_wages_lists)

        if p_val is not None and p_val < SIGNIFICANCE_LEVEL:
            note = (
                f"K-W test is significant (p={p_val:.4f}), indicating a "
                "significant wage disparity."
            )

            if len(league_wages_lists) > 2:
                sig_pairs = _dunn_significant_pairs(valid_grouped, stats_module)
                if sig_pairs:
                    note += f" Significant pairs include: {', '.join(sig_pairs)}."
        elif p_val is not None:
            note = (
                f"K-W test is not significant (p={p_val:.4f}), no significant "
                "wage disparity found."
            )

    return FairnessByLeagueResponse(
        overall_min=overall_min,
        overall_max=overall_max,
        distributions=distributions,
        test=StatisticalTestSummary(
            method="Kruskal-Wallis H-test & Dunn's Post-hoc",
            statistic=round(stat, 3) if stat is not None else None,
            p_value=round(p_val, 4) if p_val is not None else None,
            note=note,
        ),
        notes=[
            "Kruskal-Wallis is run with scipy.stats.kruskal.",
            "Dunn post-hoc pairs use Bonferroni correction and groups with "
            "fewer than 2 players are excluded from statistical tests.",
        ],
    )


def build_nationality_heatmap(repository: PlayerRepository) -> NationalityHeatmapResponse:
    players = repository.load_players()

    league_counts: Counter[str] = Counter()
    nation_counts: Counter[str] = Counter()
    for player in players:
        if (
            player.get("wage_eur") is None
            or player.get("league_name") is None
            or player.get("nationality_name") is None
        ):
            continue
        league_counts[str(player["league_name"])] += 1
        nation_counts[str(player["nationality_name"])] += 1

    top_leagues = {league for league, _ in league_counts.most_common(10)}
    top_nations = {nation for nation, _ in nation_counts.most_common(15)}

    grouped: dict[tuple[str, str], list[int]] = defaultdict(list)
    for player in players:
        if (
            player.get("wage_eur") is None
            or player.get("league_name") is None
            or player.get("nationality_name") is None
        ):
            continue

        nat = str(player["nationality_name"])
        lea = str(player["league_name"])

        if nat in top_nations and lea in top_leagues:
            grouped[(nat, lea)].append(int(player["wage_eur"]))

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
            "Dynamically filtered to Top 10 Leagues and Top 15 Nationalities to avoid sparse matrices.",
            "Values represent the average wage in EUR.",
        ],
    )


def _load_scipy_stats() -> Any | None:
    try:
        from scipy import stats
    except ImportError:
        return None
    return stats


def _dunn_significant_pairs(
    grouped: dict[str, list[int]],
    stats_module: Any,
) -> list[str]:
    ranked_values: list[int] = []
    league_by_value: list[str] = []
    for league, wages in grouped.items():
        ranked_values.extend(wages)
        league_by_value.extend([league] * len(wages))

    total_count = len(ranked_values)
    if total_count < 2:
        return []

    ranks = stats_module.rankdata(ranked_values)
    tie_counts = Counter(ranked_values)
    tie_term = sum(count**3 - count for count in tie_counts.values())
    variance_base = total_count * (total_count + 1) / 12
    if total_count > 1:
        variance_base -= tie_term / (12 * (total_count - 1))
    if variance_base <= 0:
        return []

    rank_sums: dict[str, float] = defaultdict(float)
    sample_sizes: dict[str, int] = defaultdict(int)
    for league, rank in zip(league_by_value, ranks, strict=True):
        rank_sums[league] += float(rank)
        sample_sizes[league] += 1

    pair_count = len(grouped) * (len(grouped) - 1) / 2
    if pair_count <= 0:
        return []

    significant_pairs: list[tuple[float, str]] = []
    leagues = sorted(grouped)
    for index, left in enumerate(leagues):
        for right in leagues[index + 1:]:
            left_size = sample_sizes[left]
            right_size = sample_sizes[right]
            denominator = sqrt(variance_base * (1 / left_size + 1 / right_size))
            if denominator == 0:
                continue

            mean_rank_diff = abs(
                rank_sums[left] / left_size - rank_sums[right] / right_size
            )
            z_score = mean_rank_diff / denominator
            raw_p_value = 2 * stats_module.norm.sf(abs(z_score))
            adjusted_p_value = min(raw_p_value * pair_count, 1.0)
            if adjusted_p_value < SIGNIFICANCE_LEVEL:
                significant_pairs.append(
                    (adjusted_p_value, f"{left} vs {right} (p={adjusted_p_value:.4f})")
                )

    significant_pairs.sort(key=lambda item: item[0])
    return [label for _, label in significant_pairs[:MAX_SIGNIFICANT_PAIRS]]
