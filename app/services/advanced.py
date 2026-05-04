from __future__ import annotations

from collections import Counter
from typing import Any

from app.schemas.advanced import (
    ClusterPoint,
    ClusterResponse,
    ClusterSummary,
    FeatureContribution,
    PredictionResponse,
)
from app.services.data_repository import PlayerRepository

LATEST_CLUSTER_SEASON = 22
CLUSTER_FEATURES = ("pace", "shooting", "passing", "dribbling", "defending", "physic")


def _has_cluster_features(player: dict[str, object]) -> bool:
    return all(player.get(feature) is not None for feature in CLUSTER_FEATURES)


def _is_outfield_latest_season(player: dict[str, object]) -> bool:
    return (
        int(player.get("season", 0)) == LATEST_CLUSTER_SEASON
        and str(player.get("main_position") or "").upper() != "GK"
        and _has_cluster_features(player)
    )


def _cluster_label(profile: dict[str, float]) -> str:
    pace = profile["pace"]
    shooting = profile["shooting"]
    passing = profile["passing"]
    dribbling = profile["dribbling"]
    defending = profile["defending"]
    physic = profile["physic"]

    if defending >= 60 and passing < 50:
        return "Traditional Defenders"
    if min(pace, shooting, passing, dribbling, defending, physic) >= 58:
        return "All-Rounders"
    if defending >= 60 and passing >= 55:
        return "Ball-Playing Defenders"
    if pace >= 74 and shooting >= 62:
        return "Pacey Attackers"
    if defending < 45 and dribbling >= 58:
        return "Lightweight Attackers"
    if dribbling >= 70 and physic < 65:
        return "Lightweight Attackers"
    return "Role Players"


def _unique_labels(profiles: list[dict[str, float]]) -> dict[int, str]:
    counts: Counter[str] = Counter()
    labels: dict[int, str] = {}

    for profile in profiles:
        cluster_id = int(profile["cluster_id"])
        base_label = _cluster_label(profile)
        counts[base_label] += 1
        labels[cluster_id] = (
            base_label if counts[base_label] == 1 else f"{base_label} {counts[base_label]}"
        )

    return labels


def _run_kmeans_pca(rows: list[dict[str, object]], k: int) -> dict[str, Any]:
    try:
        return _run_sklearn_kmeans_pca(rows, k)
    except ImportError:
        return _run_numpy_kmeans_pca(rows, k)


def _run_sklearn_kmeans_pca(rows: list[dict[str, object]], k: int) -> dict[str, Any]:
    import numpy as np
    from sklearn.cluster import KMeans
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler

    x_raw = np.array(
        [[float(row[feature]) for feature in CLUSTER_FEATURES] for row in rows],
        dtype=float,
    )
    scaler = StandardScaler()
    x_scaled = scaler.fit_transform(x_raw)

    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = kmeans.fit_predict(x_scaled)

    pca = PCA(n_components=2, random_state=42)
    coordinates = pca.fit_transform(x_scaled)
    centers = scaler.inverse_transform(kmeans.cluster_centers_)

    return {
        "labels": labels,
        "coordinates": coordinates,
        "centers": centers,
        "engine": "sklearn",
    }


def _run_numpy_kmeans_pca(rows: list[dict[str, object]], k: int) -> dict[str, Any]:
    import numpy as np

    x_raw = np.array(
        [[float(row[feature]) for feature in CLUSTER_FEATURES] for row in rows],
        dtype=float,
    )
    means = x_raw.mean(axis=0)
    scales = x_raw.std(axis=0)
    scales[scales == 0] = 1.0
    x_scaled = (x_raw - means) / scales

    rng = np.random.default_rng(42)
    best_labels = None
    best_centers = None
    best_inertia = float("inf")

    for _ in range(10):
        initial_indices = rng.choice(len(x_scaled), size=k, replace=False)
        centers = x_scaled[initial_indices].copy()
        labels = np.zeros(len(x_scaled), dtype=int)

        for _ in range(100):
            distances = ((x_scaled[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2)
            next_labels = distances.argmin(axis=1)

            next_centers = centers.copy()
            for cluster_id in range(k):
                members = x_scaled[next_labels == cluster_id]
                if len(members):
                    next_centers[cluster_id] = members.mean(axis=0)

            if np.array_equal(labels, next_labels):
                centers = next_centers
                break

            labels = next_labels
            centers = next_centers

        inertia = float(((x_scaled - centers[labels]) ** 2).sum())
        if inertia < best_inertia:
            best_inertia = inertia
            best_labels = labels.copy()
            best_centers = centers.copy()

    centered = x_scaled - x_scaled.mean(axis=0)
    _, _, vt = np.linalg.svd(centered, full_matrices=False)
    coordinates = centered @ vt[:2].T
    centers = best_centers * scales + means

    return {
        "labels": best_labels,
        "coordinates": coordinates,
        "centers": centers,
        "engine": "numpy",
    }


def _profile_from_center(cluster_id: int, center: object) -> dict[str, float]:
    return {
        "cluster_id": float(cluster_id),
        **{
            feature: round(float(center[index]), 1)
            for index, feature in enumerate(CLUSTER_FEATURES)
        },
    }


def build_cluster_response(repository: PlayerRepository, k: int = 5) -> ClusterResponse:
    players = [
        player
        for player in repository.load_players()
        if _is_outfield_latest_season(player)
    ]
    if not players:
        return ClusterResponse(
            k=k,
            points=[],
            summaries=[],
            notes=[
                "No latest-season outfield players have the six aggregate features required for K-Means.",
            ],
        )

    effective_k = min(k, len(players))
    result = _run_kmeans_pca(players, effective_k)
    profiles = [
        _profile_from_center(cluster_id, center)
        for cluster_id, center in enumerate(result["centers"])
    ]
    cluster_labels = _unique_labels(profiles)

    points = [
        ClusterPoint(
            short_name=str(player["short_name"]),
            label=cluster_labels[int(result["labels"][index])],
            x=round(float(result["coordinates"][index][0]), 3),
            y=round(float(result["coordinates"][index][1]), 3),
            season=int(player["season"]),
        )
        for index, player in enumerate(players)
    ]

    counts = Counter(point.label for point in points)
    summaries = []
    for profile in profiles:
        cluster_id = int(profile["cluster_id"])
        label = cluster_labels[cluster_id]
        feature_summary = ", ".join(
            f"{feature}: {profile[feature]:.1f}" for feature in CLUSTER_FEATURES
        )
        summaries.append(
            ClusterSummary(
                label=label,
                count=counts[label],
                description=feature_summary,
            )
        )

    return ClusterResponse(
        k=effective_k,
        points=points,
        summaries=summaries,
        notes=[
            "K-Means uses FIFA 22 outfield players only, matching the notebook logic.",
            "Features are pace, shooting, passing, dribbling, defending, and physic.",
            f"Model engine: {result['engine']}; rows clustered: {len(players)}.",
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
