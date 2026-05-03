from __future__ import annotations

from collections import Counter

from app.schemas.advanced import (
    ClusterPoint,
    ClusterResponse,
    ClusterSummary,
    FeatureContribution,
    PredictionResponse,
)
from app.services.data_repository import PlayerRepository

CLUSTER_FEATURES = ("pace", "passing", "defending", "shooting", "dribbling")


def _has_cluster_features(player: dict[str, object]) -> bool:
    return all(player.get(feature) is not None for feature in CLUSTER_FEATURES)


def _cluster_label(player: dict[str, object]) -> str:
    pace = int(player["pace"])
    passing = int(player["passing"])
    defending = int(player["defending"])
    shooting = int(player["shooting"])

    if defending >= 80:
        return "Control Anchor"
    if pace >= 88 and shooting >= 86:
        return "Direct Threat"
    if passing >= 84 and int(player["dribbling"]) >= 85:
        return "Creative Link"
    return "Balanced Engine"


def build_cluster_response(repository: PlayerRepository, k: int = 4) -> ClusterResponse:
    players = [
        player
        for player in repository.load_players()
        if _has_cluster_features(player)
    ]
    points: list[ClusterPoint] = []
    labels = []

    for player in players:
        label = _cluster_label(player)
        labels.append(label)
        points.append(
            ClusterPoint(
                short_name=str(player["short_name"]),
                label=label,
                x=round((int(player["pace"]) - int(player["defending"])) / 12, 2),
                y=round((int(player["passing"]) + int(player["dribbling"])) / 20, 2),
                season=int(player["season"]),
            )
        )

    counts = Counter(labels)
    summaries = [
        ClusterSummary(
            label=label,
            count=count,
            description=(
                "Heuristic placeholder cluster. Replace with PCA + K-Means as described in the SDS."
            ),
        )
        for label, count in counts.most_common(k)
    ]

    return ClusterResponse(
        k=k,
        points=points,
        summaries=summaries,
        notes=[
            "This endpoint currently preserves the intended payload shape, not the final ML behaviour.",
            "Rows without outfield aggregate ratings are excluded from the scaffold heuristic.",
            "The meeting note assigns the real clustering implementation to the advanced-task owner.",
        ],
    )


def build_prediction_response(
    overall: int,
    potential: int,
    age: int,
    wage_eur: int,
    pace: int,
    dribbling: int,
    passing: int,
) -> PredictionResponse:
    weighted_score = (
        overall * 0.35
        + potential * 0.25
        + pace * 0.1
        + dribbling * 0.15
        + passing * 0.15
    )
    age_penalty = max(age - 24, 0) * 0.8
    estimated_value = int(
        max((weighted_score - age_penalty) * 1_100_000 + wage_eur * 18, 500_000)
    )

    return PredictionResponse(
        estimated_value_eur=estimated_value,
        band="scaffold-estimate",
        contributions=[
            FeatureContribution(feature="overall", weight=0.35),
            FeatureContribution(feature="potential", weight=0.25),
            FeatureContribution(feature="dribbling", weight=0.15),
            FeatureContribution(feature="passing", weight=0.15),
            FeatureContribution(feature="pace", weight=0.1),
        ],
        notes=[
            "This prediction is a deterministic scaffold heuristic.",
            "Replace with a trained regression model plus held-out metrics in Week 3.",
        ],
    )
