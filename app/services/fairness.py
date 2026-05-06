from __future__ import annotations

from collections import Counter, defaultdict
from math import erfc, exp, isfinite, lgamma, log, sqrt
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
FAIRNESS_COLUMNS = (
    "overall",
    "wage_eur",
    "league_name",
    "nationality_name",
)


def build_fairness_by_league(
    repository: PlayerRepository, overall_min: int = 80, overall_max: int = 90
) -> FairnessByLeagueResponse:
    players = repository.load_player_columns(FAIRNESS_COLUMNS)
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
    engine = "unavailable"

    league_wages_lists = list(valid_grouped.values())

    if len(league_wages_lists) >= 2:
        stats_module = _load_scipy_stats()
        if stats_module is None:
            stat, p_val = _kruskal_wallis(league_wages_lists)
            engine = "pure-python"
        else:
            stat, p_val = stats_module.kruskal(*league_wages_lists)
            stat = float(stat)
            p_val = float(p_val)
            engine = "scipy"

        if p_val is not None and p_val < SIGNIFICANCE_LEVEL:
            note = (
                f"K-W test is significant (p={_format_p_value(p_val)}, engine={engine}), "
                "indicating a significant wage disparity."
            )

            if len(league_wages_lists) > 2:
                sig_pairs = _dunn_significant_pairs(valid_grouped, stats_module)
                if sig_pairs:
                    note += f" Significant pairs include: {', '.join(sig_pairs)}."
        elif p_val is not None:
            note = (
                f"K-W test is not significant (p={_format_p_value(p_val)}, engine={engine}), "
                "no significant wage disparity found."
            )

    return FairnessByLeagueResponse(
        overall_min=overall_min,
        overall_max=overall_max,
        distributions=distributions,
        test=StatisticalTestSummary(
            method="Kruskal-Wallis H-test & Dunn's Post-hoc",
            statistic=round(stat, 3) if stat is not None else None,
            p_value=float(p_val) if p_val is not None else None,
            note=note,
        ),
        notes=[
            "Kruskal-Wallis uses scipy.stats.kruskal when available and a "
            "pure-Python chi-square approximation otherwise.",
            "Dunn post-hoc pairs use Bonferroni correction and groups with "
            "fewer than 2 players are excluded from statistical tests.",
        ],
    )


def build_nationality_heatmap(repository: PlayerRepository) -> NationalityHeatmapResponse:
    players = repository.load_player_columns(FAIRNESS_COLUMNS)

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
            "Dynamically filtered to Top 10 Leagues and Top 15 Nationalities "
            "to avoid sparse matrices.",
            "Values represent the average wage in EUR.",
        ],
    )


def _load_scipy_stats() -> Any | None:
    try:
        from scipy import stats
    except Exception:
        return None
    return stats


def _format_p_value(value: float) -> str:
    return f"{value:.2e}"


def _kruskal_wallis(groups: list[list[int]]) -> tuple[float | None, float | None]:
    valid_groups = [group for group in groups if len(group) > 0]
    if len(valid_groups) < 2:
        return None, None

    values: list[float] = []
    group_labels: list[int] = []
    for group_id, group in enumerate(valid_groups):
        values.extend(float(value) for value in group)
        group_labels.extend([group_id] * len(group))

    total_count = len(values)
    if total_count <= len(valid_groups):
        return None, None

    ranks = _rankdata(values)
    rank_sums: dict[int, float] = defaultdict(float)
    group_sizes: dict[int, int] = defaultdict(int)
    for group_id, rank in zip(group_labels, ranks, strict=True):
        rank_sums[group_id] += rank
        group_sizes[group_id] += 1

    statistic = (
        12.0
        / (total_count * (total_count + 1))
        * sum((rank_sums[group_id] ** 2) / group_sizes[group_id] for group_id in rank_sums)
        - 3 * (total_count + 1)
    )

    tie_counts = Counter(values)
    tie_correction = 1.0 - (
        sum(count**3 - count for count in tie_counts.values())
        / (total_count**3 - total_count)
    )
    if tie_correction > 0:
        statistic /= tie_correction

    p_value = _chi_square_sf(statistic, len(valid_groups) - 1)
    return statistic, p_value


def _rankdata(values: list[float] | list[int]) -> list[float]:
    sorted_pairs = sorted(enumerate(values), key=lambda item: item[1])
    ranks = [0.0] * len(values)
    index = 0
    while index < len(sorted_pairs):
        end = index + 1
        while end < len(sorted_pairs) and sorted_pairs[end][1] == sorted_pairs[index][1]:
            end += 1
        average_rank = (index + 1 + end) / 2
        for original_index, _ in sorted_pairs[index:end]:
            ranks[original_index] = average_rank
        index = end
    return ranks


def _chi_square_sf(value: float, degrees_of_freedom: int) -> float | None:
    if value < 0 or degrees_of_freedom < 1 or not isfinite(value):
        return None
    return _regularized_gamma_q(degrees_of_freedom / 2.0, value / 2.0)


def _regularized_gamma_q(shape: float, x_value: float) -> float:
    if x_value < 0 or shape <= 0:
        return float("nan")
    if x_value == 0:
        return 1.0
    if x_value < shape + 1.0:
        return max(0.0, min(1.0, 1.0 - _regularized_gamma_p_series(shape, x_value)))
    return max(0.0, min(1.0, _regularized_gamma_q_fraction(shape, x_value)))


def _regularized_gamma_p_series(shape: float, x_value: float) -> float:
    epsilon = 1e-12
    term = 1.0 / shape
    total = term
    ap_value = shape
    for _ in range(10_000):
        ap_value += 1.0
        term *= x_value / ap_value
        total += term
        if abs(term) < abs(total) * epsilon:
            break
    return total * exp(-x_value + shape * log(x_value) - lgamma(shape))


def _regularized_gamma_q_fraction(shape: float, x_value: float) -> float:
    epsilon = 1e-12
    tiny = 1e-300
    b_value = x_value + 1.0 - shape
    c_value = 1.0 / tiny
    d_value = 1.0 / max(b_value, tiny)
    h_value = d_value

    for index in range(1, 10_000):
        an_value = -index * (index - shape)
        b_value += 2.0
        d_value = an_value * d_value + b_value
        if abs(d_value) < tiny:
            d_value = tiny
        c_value = b_value + an_value / c_value
        if abs(c_value) < tiny:
            c_value = tiny
        d_value = 1.0 / d_value
        delta = d_value * c_value
        h_value *= delta
        if abs(delta - 1.0) < epsilon:
            break

    return exp(-x_value + shape * log(x_value) - lgamma(shape)) * h_value


def _normal_sf(value: float) -> float:
    return 0.5 * erfc(value / sqrt(2.0))


def _dunn_significant_pairs(
    grouped: dict[str, list[int]],
    stats_module: Any | None,
) -> list[str]:
    ranked_values: list[int] = []
    league_by_value: list[str] = []
    for league, wages in grouped.items():
        ranked_values.extend(wages)
        league_by_value.extend([league] * len(wages))

    total_count = len(ranked_values)
    if total_count < 2:
        return []

    ranks = (
        stats_module.rankdata(ranked_values)
        if stats_module is not None
        else _rankdata(ranked_values)
    )
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
            raw_p_value = (
                2 * stats_module.norm.sf(abs(z_score))
                if stats_module is not None
                else 2 * _normal_sf(abs(z_score))
            )
            adjusted_p_value = min(raw_p_value * pair_count, 1.0)
            if adjusted_p_value < SIGNIFICANCE_LEVEL:
                significant_pairs.append(
                    (
                        adjusted_p_value,
                        f"{left} vs {right} (p={_format_p_value(adjusted_p_value)})",
                    )
                )

    significant_pairs.sort(key=lambda item: item[0])
    return [label for _, label in significant_pairs[:MAX_SIGNIFICANT_PAIRS]]
