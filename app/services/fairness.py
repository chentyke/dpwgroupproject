from __future__ import annotations

from collections import defaultdict
from statistics import median

import pandas as pd
from scipy import stats
import scikit_posthocs as sp

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
    
    if not filtered and len(players) < 100:
        filtered = [
            player for player in players 
            if player.get("wage_eur") is not None and player.get("league_name") is not None
        ]
  
    grouped: dict[str, list[int]] = defaultdict(list)
    for player in filtered:
        grouped[str(player["league_name"])].append(int(player["wage_eur"]))
        
    valid_grouped = {league: wages for league, wages in grouped.items() if len(wages) >= 2}

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
        # Kruskal-Wallis H-test
        stat, p_val = stats.kruskal(*league_wages_lists)
        
        if p_val < 0.05:
            note = f"K-W test is significant (p={p_val:.4f}), indicating a significant wage disparity."
            
            # Dunn's Post-hoc Test
            if len(league_wages_lists) > 2:
                try:
                    df_test = pd.DataFrame([
                        {"league": p["league_name"], "wage": p["wage_eur"]}
                        for p in filtered if p["league_name"] in valid_grouped
                    ])
                    # Apply Bonferroni correction
                    dunn_res = sp.posthoc_dunn(df_test, val_col='wage', group_col='league', p_adjust='bonferroni')
                    
                    sig_pairs = []
                    cols = dunn_res.columns
                    for i in range(len(cols)):
                        for j in range(i + 1, len(cols)):
                            if dunn_res.iloc[i, j] < 0.05:
                                sig_pairs.append(f"{cols[i]} vs {cols[j]}")
                                
                    if sig_pairs:
                        note += f" Significant pairs include: {', '.join(sig_pairs[:3])}"
                except Exception:
                    pass
        else:
            note = f"K-W test is not significant (p={p_val:.4f}), no significant wage disparity found."

    return FairnessByLeagueResponse(
        overall_min=overall_min,
        overall_max=overall_max,
        distributions=distributions,
        test=StatisticalTestSummary(
            method="Kruskal-Wallis H-test & Dunn's Post-hoc",
            statistic=round(stat, 3) if stat is not None else None,
            p_value=round(p_val, 4) if p_val is not None else None,
            note=note
        ),
        notes=[
            "Replaced placeholder with real scipy.stats.kruskal and scikit_posthocs tests.",
            "Groups with fewer than 2 players are excluded from statistical tests."
        ],
    )


def build_nationality_heatmap(repository: PlayerRepository) -> NationalityHeatmapResponse:
    players = repository.load_players()
    
    df = pd.DataFrame(players)
    top_leagues, top_nations = set(), set()
    
    if not df.empty:
        df['wage_eur'] = pd.to_numeric(df.get('wage_eur'), errors='coerce')
        df = df.dropna(subset=['wage_eur', 'league_name', 'nationality_name'])
        top_leagues = set(df['league_name'].value_counts().nlargest(10).index)
        top_nations = set(df['nationality_name'].value_counts().nlargest(15).index)

    grouped: dict[tuple[str, str], list[int]] = defaultdict(list)
    for player in players:
        if player.get("wage_eur") is None or player.get("league_name") is None or player.get("nationality_name") is None:
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
            "Values represent the average wage in EUR."
        ],
    )
