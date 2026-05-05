from __future__ import annotations

from collections import Counter
from math import isfinite
from typing import Any

from app.schemas.advanced import (
    ClusterPoint,
    ClusterResponse,
    ClusterSummary,
    FeatureContribution,
    PredictionResponse,
    ResidualPoint,
)
from app.services.data_repository import PlayerRepository

LATEST_CLUSTER_SEASON = 22
CLUSTER_FEATURES = ("pace", "shooting", "passing", "dribbling", "defending", "physic")
LATEST_VALUE_SEASON = 22
PREDICTION_FEATURES = (
    "overall",
    "potential",
    "age",
    "pace",
    "shooting",
    "passing",
    "dribbling",
    "defending",
    "physic",
)
RIDGE_ALPHA = 10.0
PREDICTION_RANDOM_STATE = 42
MIN_PREDICTION_TRAINING_ROWS = 2
CLUSTER_COLUMNS = (
    "short_name",
    "season",
    "main_position",
    *CLUSTER_FEATURES,
)
PREDICTION_COLUMNS = (
    "season",
    "main_position",
    "value_eur",
    *PREDICTION_FEATURES,
)


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
    except Exception:
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
        for player in repository.load_player_columns(CLUSTER_COLUMNS)
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
    repository: PlayerRepository,
    overall: int,
    potential: int,
    age: int,
    wage_eur: int,
    pace: int,
    dribbling: int,
    passing: int,
    shooting: int | None = None,
    defending: int | None = None,
    physic: int | None = None,
) -> PredictionResponse:
    rows = [
        player
        for player in repository.load_player_columns(PREDICTION_COLUMNS)
        if _is_prediction_training_row(player)
    ]
    if len(rows) < MIN_PREDICTION_TRAINING_ROWS:
        raise ValueError(
            "Insufficient valid training rows for value prediction. "
            "Load the FIFA 22 outfield data before calling /api/predict."
        )

    model = _run_value_prediction_model(rows)
    request_values = {
        "overall": overall,
        "potential": potential,
        "age": age,
        "pace": pace,
        "shooting": shooting,
        "passing": passing,
        "dribbling": dribbling,
        "defending": defending,
        "physic": physic,
    }
    predicted_log_value = _predict_log_value(model, request_values)

    import numpy as np

    estimated_value = int(round(max(float(np.expm1(predicted_log_value)), 0.0)))
    missing_features = [
        feature for feature, value in request_values.items() if value is None
    ]
    notes = [
        "Ridge regression is trained on FIFA 22 outfield players and log1p(value_eur), matching the Predict value notebook.",
        f"Features are {', '.join(PREDICTION_FEATURES)}.",
        f"Model engine: {model['engine']}; rows used: {len(rows)}.",
    ]
    if missing_features:
        notes.append(
            "Missing request fields were filled with training feature means: "
            + ", ".join(missing_features)
            + "."
        )
    notes.append(
        "wage_eur is accepted for backward compatibility but is not used by this notebook model."
    )

    return PredictionResponse(
        estimated_value_eur=estimated_value,
        band="ridge-log-value",
        contributions=model["feature_importance"],
        r2_score=model["r2_score"],
        mae_eur=model["mae_eur"],
        residuals=model["residuals"],
        training_rows=model["training_rows"],
        test_rows=model["test_rows"],
        notes=notes,
    )


def _is_prediction_training_row(player: dict[str, object]) -> bool:
    try:
        return (
            int(player.get("season", 0)) == LATEST_VALUE_SEASON
            and str(player.get("main_position") or "").upper() != "GK"
            and int(player.get("value_eur") or 0) > 0
            and all(player.get(feature) is not None for feature in PREDICTION_FEATURES)
        )
    except (TypeError, ValueError):
        return False


def _run_value_prediction_model(rows: list[dict[str, object]]) -> dict[str, Any]:
    try:
        return _run_sklearn_value_model(rows)
    except Exception:
        return _run_numpy_value_model(rows)


def _prediction_arrays(rows: list[dict[str, object]]) -> tuple[Any, Any]:
    import numpy as np

    x_raw = np.array(
        [[float(row[feature]) for feature in PREDICTION_FEATURES] for row in rows],
        dtype=float,
    )
    y = np.log1p(
        np.array([float(row["value_eur"]) for row in rows], dtype=float)
    )
    return x_raw, y


def _run_sklearn_value_model(rows: list[dict[str, object]]) -> dict[str, Any]:
    from sklearn.linear_model import Ridge
    from sklearn.metrics import mean_absolute_error, r2_score
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler

    x_raw, y = _prediction_arrays(rows)
    x_train, x_test, y_train, y_test = train_test_split(
        x_raw,
        y,
        test_size=0.2,
        random_state=PREDICTION_RANDOM_STATE,
    )

    scaler = StandardScaler()
    x_train_scaled = scaler.fit_transform(x_train)
    x_test_scaled = scaler.transform(x_test)

    ridge_model = Ridge(alpha=RIDGE_ALPHA, random_state=PREDICTION_RANDOM_STATE)
    ridge_model.fit(x_train_scaled, y_train)

    y_pred = ridge_model.predict(x_test_scaled)
    return _package_value_model_result(
        engine="sklearn",
        feature_means=scaler.mean_,
        feature_scales=scaler.scale_,
        coefficients=ridge_model.coef_,
        intercept=float(ridge_model.intercept_),
        y_test=y_test,
        y_pred=y_pred,
        r2_score_value=float(r2_score(y_test, y_pred)),
        mae_eur_value=float(
            mean_absolute_error(_expm1_values(y_test), _expm1_values(y_pred))
        ),
        training_rows=len(x_train),
        test_rows=len(x_test),
    )


def _run_numpy_value_model(rows: list[dict[str, object]]) -> dict[str, Any]:
    import numpy as np

    x_raw, y = _prediction_arrays(rows)
    rng = np.random.default_rng(PREDICTION_RANDOM_STATE)
    indices = rng.permutation(len(x_raw))
    test_size = max(1, int(round(len(x_raw) * 0.2)))
    if test_size >= len(x_raw):
        test_size = 1
    test_indices = indices[:test_size]
    train_indices = indices[test_size:]

    x_train = x_raw[train_indices]
    x_test = x_raw[test_indices]
    y_train = y[train_indices]
    y_test = y[test_indices]

    feature_means = x_train.mean(axis=0)
    feature_scales = x_train.std(axis=0)
    feature_scales[feature_scales == 0] = 1.0
    x_train_scaled = (x_train - feature_means) / feature_scales
    x_test_scaled = (x_test - feature_means) / feature_scales

    x_train_augmented = np.column_stack(
        [np.ones(len(x_train_scaled)), x_train_scaled]
    )
    regularization = np.eye(x_train_augmented.shape[1]) * RIDGE_ALPHA
    regularization[0, 0] = 0.0
    left = x_train_augmented.T @ x_train_augmented + regularization
    right = x_train_augmented.T @ y_train

    try:
        fitted = np.linalg.solve(left, right)
    except np.linalg.LinAlgError:
        fitted = np.linalg.pinv(left) @ right

    intercept = float(fitted[0])
    coefficients = fitted[1:]
    y_pred = np.column_stack([np.ones(len(x_test_scaled)), x_test_scaled]) @ fitted
    r2_value, mae_value = _regression_metrics(y_test, y_pred)

    return _package_value_model_result(
        engine="numpy",
        feature_means=feature_means,
        feature_scales=feature_scales,
        coefficients=coefficients,
        intercept=intercept,
        y_test=y_test,
        y_pred=y_pred,
        r2_score_value=r2_value,
        mae_eur_value=mae_value,
        training_rows=len(x_train),
        test_rows=len(x_test),
    )


def _package_value_model_result(
    *,
    engine: str,
    feature_means: Any,
    feature_scales: Any,
    coefficients: Any,
    intercept: float,
    y_test: Any,
    y_pred: Any,
    r2_score_value: float,
    mae_eur_value: float,
    training_rows: int,
    test_rows: int,
) -> dict[str, Any]:
    import numpy as np

    sorted_importance = sorted(
        zip(PREDICTION_FEATURES, np.abs(coefficients), strict=True),
        key=lambda item: float(item[1]),
        reverse=True,
    )
    residuals = y_test - y_pred

    return {
        "engine": engine,
        "feature_means": feature_means,
        "feature_scales": feature_scales,
        "coefficients": coefficients,
        "intercept": intercept,
        "r2_score": _round_finite(r2_score_value, 3),
        "mae_eur": _round_finite(mae_eur_value, 2),
        "feature_importance": [
            FeatureContribution(feature=feature, weight=round(float(weight), 3))
            for feature, weight in sorted_importance
        ],
        "residuals": [
            ResidualPoint(
                predicted_log_value=round(float(predicted), 3),
                residual=round(float(residual), 3),
            )
            for predicted, residual in list(zip(y_pred, residuals, strict=True))[:1000]
        ],
        "training_rows": training_rows,
        "test_rows": test_rows,
    }


def _round_finite(value: float, digits: int) -> float | None:
    return round(float(value), digits) if isfinite(float(value)) else None


def _predict_log_value(model: dict[str, Any], values: dict[str, int | None]) -> float:
    import numpy as np

    sample = np.array(
        [
            float(values[feature])
            if values[feature] is not None
            else float(model["feature_means"][index])
            for index, feature in enumerate(PREDICTION_FEATURES)
        ],
        dtype=float,
    )
    sample_scaled = (sample - model["feature_means"]) / model["feature_scales"]
    return float(model["intercept"] + sample_scaled @ model["coefficients"])


def _regression_metrics(y_test: Any, y_pred: Any) -> tuple[float, float]:
    import numpy as np

    residual_sum = float(((y_test - y_pred) ** 2).sum())
    total_sum = float(((y_test - y_test.mean()) ** 2).sum())
    r2_value = 0.0 if total_sum == 0 else 1.0 - residual_sum / total_sum
    mae_value = float(np.mean(np.abs(_expm1_values(y_test) - _expm1_values(y_pred))))
    return r2_value, mae_value


def _expm1_values(values: Any) -> Any:
    import numpy as np

    return np.expm1(values)
