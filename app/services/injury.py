from __future__ import annotations

from math import isfinite
from typing import Any

from app.schemas.injury import (
    FutureModelSummary,
    FutureRiskExample,
    FutureRiskFeature,
    FutureRiskMetrics,
    FutureRiskResponse,
    FutureTimeline,
    FutureTimelinePoint,
    InjuryStatusCount,
)
from app.services.data_repository import PlayerRepository

PLAYER_KEY = "sofifa_id"
RANDOM_STATE = 42
MALE_SOURCE_FILES = {f"players_{season:02d}.csv" for season in range(15, 23)}
INJURY_FEATURES = (
    "age",
    "height_cm",
    "weight_kg",
    "overall",
    "potential",
    "pace",
    "shooting",
    "passing",
    "dribbling",
    "defending",
    "physic",
    "attacking_crossing",
    "attacking_finishing",
    "attacking_heading_accuracy",
    "attacking_short_passing",
    "attacking_volleys",
    "skill_dribbling",
    "skill_curve",
    "skill_fk_accuracy",
    "skill_long_passing",
    "skill_ball_control",
    "movement_acceleration",
    "movement_sprint_speed",
    "movement_agility",
    "movement_reactions",
    "movement_balance",
    "power_shot_power",
    "power_jumping",
    "power_stamina",
    "power_strength",
    "power_long_shots",
    "mentality_aggression",
    "mentality_interceptions",
    "mentality_positioning",
    "mentality_vision",
    "mentality_penalties",
    "mentality_composure",
    "defending_marking_awareness",
    "defending_standing_tackle",
    "defending_sliding_tackle",
)
INJURY_COLUMNS = (
    PLAYER_KEY,
    "short_name",
    "long_name",
    "season",
    "gender",
    "source_file",
    "player_traits",
    *INJURY_FEATURES,
)


def build_future_risk_response(repository: PlayerRepository) -> FutureRiskResponse:
    import pandas as pd

    records = repository.load_player_columns(INJURY_COLUMNS)
    frame = _prepare_frame(pd.DataFrame.from_records(records))
    if frame.empty:
        return _empty_response(repository, "No male FIFA 15-22 player records were available.")

    frame = _add_future_labels(frame)
    model_frame = frame[
        (frame["injury_status"] == -1) & (frame["has_future_record"])
    ].copy()
    x, feature_names = _feature_matrix(model_frame)

    injury_model, injury_probs = _train_future_model(
        model_frame,
        x,
        feature_names,
        target="future_injury",
        label="Future Injury Model",
        probability_name="injury_probability",
    )
    solid_model, solid_probs = _train_future_model(
        model_frame,
        x,
        feature_names,
        target="future_solid",
        label="Future Solid Model",
        probability_name="solid_probability",
    )
    probability_frame = _merge_probability_frames(model_frame, injury_probs, solid_probs)

    return FutureRiskResponse(
        source=repository.source_name(),
        seasons=sorted(int(item) for item in frame["season_year"].dropna().unique()),
        player_count=int(frame[PLAYER_KEY].nunique()),
        total_records=int(frame.shape[0]),
        modeling_records=int(model_frame.shape[0]),
        feature_count=len(feature_names),
        features=list(feature_names),
        status_counts=_status_counts(frame),
        injury_model=injury_model,
        solid_model=solid_model,
        timelines=_build_timelines(frame, probability_frame, injury_model, solid_model),
        notes=[
            "Input records are early unlabeled male players from FIFA 15-22.",
            "future_injury and future_solid are trained as separate binary targets.",
            "Validation uses player-group holdout splits so a player cannot appear in both train and test rows.",
        ],
    )


def _prepare_frame(frame: Any) -> Any:
    import pandas as pd

    if frame.empty or PLAYER_KEY not in frame.columns or "season" not in frame.columns:
        return pd.DataFrame()

    frame = frame.copy()
    if "source_file" in frame.columns and frame["source_file"].notna().any():
        frame = frame[frame["source_file"].isin(MALE_SOURCE_FILES)]
    if "gender" in frame.columns and frame["gender"].notna().any():
        frame = frame[frame["gender"].fillna("male") == "male"]
    if frame.empty:
        return frame

    frame["season_sort"] = pd.to_numeric(frame["season"], errors="coerce")
    frame = frame.dropna(subset=[PLAYER_KEY, "season_sort"]).copy()
    frame["season_sort"] = frame["season_sort"].astype(int)
    frame["season_year"] = frame["season_sort"].map(
        lambda value: value if value >= 100 else 2000 + value
    )
    frame["injury_status"] = frame["player_traits"].map(_label_injury_status)
    frame.sort_values(by=[PLAYER_KEY, "season_sort"], inplace=True)
    frame.reset_index(drop=True, inplace=True)
    return frame


def _label_injury_status(traits: object) -> int:
    if traits is None:
        return -1
    text = str(traits).lower()
    if "injury prone" in text:
        return 1
    if "solid player" in text:
        return 0
    return -1


def _add_future_labels(frame: Any) -> Any:
    import numpy as np
    import pandas as pd

    groups = []
    for _, group in frame.groupby(PLAYER_KEY, sort=False):
        group = group.sort_values("season_sort").copy()
        statuses = group["injury_status"].to_numpy()
        future_injury = []
        future_solid = []
        has_future_record = []
        for index in range(len(group)):
            future_statuses = statuses[index + 1 :]
            has_future_record.append(len(future_statuses) > 0)
            future_injury.append(int(np.any(future_statuses == 1)))
            future_solid.append(int(np.any(future_statuses == 0)))
        group["has_future_record"] = has_future_record
        group["future_injury"] = future_injury
        group["future_solid"] = future_solid
        groups.append(group)
    return pd.concat(groups, ignore_index=True) if groups else frame


def _feature_matrix(frame: Any) -> tuple[Any, tuple[str, ...]]:
    if frame.empty:
        return frame, ()

    numeric = frame[list(INJURY_FEATURES)].apply(_to_numeric_column)
    feature_names = tuple(
        column for column in INJURY_FEATURES if column in numeric and not numeric[column].isna().all()
    )
    if not feature_names:
        return numeric.iloc[:, 0:0], ()

    selected = numeric.loc[:, list(feature_names)]
    selected = selected.fillna(selected.mean()).fillna(0.0)
    return selected, feature_names


def _to_numeric_column(column: Any) -> Any:
    import pandas as pd

    return pd.to_numeric(column, errors="coerce")


def _train_future_model(
    frame: Any,
    x: Any,
    feature_names: tuple[str, ...],
    *,
    target: str,
    label: str,
    probability_name: str,
) -> tuple[FutureModelSummary, Any]:
    import pandas as pd

    y = frame[target].astype(int) if target in frame else pd.Series(dtype=int)
    positive_records = int(y.sum()) if not y.empty else 0
    negative_records = int(len(y) - positive_records)
    baseline_rate = _round_rate(float(y.mean())) if len(y) else 0.0
    empty_probs = pd.DataFrame(
        columns=[PLAYER_KEY, "season_sort", probability_name],
    )

    if frame.empty or not feature_names or y.nunique() < 2:
        return (
            FutureModelSummary(
                target=target,
                label=label,
                positive_records=positive_records,
                negative_records=negative_records,
                baseline_positive_rate=baseline_rate,
                notes=["Insufficient labeled future outcomes to train this model."],
            ),
            empty_probs,
        )

    split = _player_group_split(frame, y)
    if split is None:
        return (
            FutureModelSummary(
                target=target,
                label=label,
                positive_records=positive_records,
                negative_records=negative_records,
                baseline_positive_rate=baseline_rate,
                notes=["Unable to create a valid player-group train/test split."],
            ),
            empty_probs,
        )

    train_idx, test_idx = split
    x_train = x.iloc[train_idx]
    x_test = x.iloc[test_idx]
    y_train = y.iloc[train_idx]
    y_test = y.iloc[test_idx]

    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import accuracy_score, precision_recall_fscore_support

    model = RandomForestClassifier(
        n_estimators=100,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        class_weight="balanced",
        max_depth=8,
    )
    model.fit(x_train, y_train)
    probabilities = _positive_probabilities(model, x_test)
    predictions = model.predict(x_test)
    precision, recall, f1_score, _ = precision_recall_fscore_support(
        y_test,
        predictions,
        average="binary",
        zero_division=0,
    )
    threshold = float(pd.Series(probabilities).quantile(0.9))
    high_mask = probabilities >= threshold
    high_positive_rate = (
        _round_rate(float(y_test.iloc[high_mask].mean())) if high_mask.any() else None
    )
    top_features = _top_features(model.feature_importances_, feature_names)
    test_frame = frame.iloc[test_idx].copy()
    test_frame[probability_name] = probabilities
    examples = _examples(test_frame, target, probability_name)
    prob_frame = test_frame[[PLAYER_KEY, "season_sort", probability_name]].copy()

    return (
        FutureModelSummary(
            target=target,
            label=label,
            positive_records=positive_records,
            negative_records=negative_records,
            baseline_positive_rate=baseline_rate,
            training_rows=len(train_idx),
            test_rows=len(test_idx),
            train_players=int(frame.iloc[train_idx][PLAYER_KEY].nunique()),
            test_players=int(frame.iloc[test_idx][PLAYER_KEY].nunique()),
            high_risk_threshold=_round_float(threshold, 3),
            high_risk_records=int(high_mask.sum()),
            high_risk_positive_rate=high_positive_rate,
            metrics=FutureRiskMetrics(
                accuracy=_round_float(float(accuracy_score(y_test, predictions)), 3),
                precision=_round_float(float(precision), 3),
                recall=_round_float(float(recall), 3),
                f1_score=_round_float(float(f1_score), 3),
            ),
            top_features=top_features,
            examples=examples,
            notes=[
                "High-risk lift is computed only on held-out players.",
            ],
        ),
        prob_frame,
    )


def _player_group_split(frame: Any, y: Any) -> tuple[Any, Any] | None:
    from sklearn.model_selection import GroupShuffleSplit

    groups = frame[PLAYER_KEY].astype(str).to_numpy()
    if len(set(groups)) < 2:
        return None

    fallback_split = None
    for offset in range(30):
        splitter = GroupShuffleSplit(
            n_splits=1,
            test_size=0.3,
            random_state=RANDOM_STATE + offset,
        )
        train_idx, test_idx = next(splitter.split(frame, y, groups=groups))
        if fallback_split is None:
            fallback_split = (train_idx, test_idx)
        if y.iloc[train_idx].nunique() >= 2:
            return train_idx, test_idx
    return fallback_split if fallback_split and y.iloc[fallback_split[0]].nunique() >= 2 else None


def _positive_probabilities(model: Any, x_test: Any) -> Any:
    import numpy as np

    probabilities = model.predict_proba(x_test)
    classes = list(model.classes_)
    if 1 not in classes:
        return np.zeros(len(x_test), dtype=float)
    return probabilities[:, classes.index(1)]


def _top_features(importances: Any, feature_names: tuple[str, ...]) -> list[FutureRiskFeature]:
    pairs = sorted(
        zip(feature_names, importances, strict=True),
        key=lambda item: float(item[1]),
        reverse=True,
    )
    return [
        FutureRiskFeature(feature=feature, importance=_round_float(float(value), 4) or 0.0)
        for feature, value in pairs[:10]
    ]


def _examples(frame: Any, target: str, probability_name: str) -> list[FutureRiskExample]:
    high_rows = frame[frame[target] == 1].sort_values(
        by=probability_name,
        ascending=False,
    )
    return [
        FutureRiskExample(
            sofifa_id=_safe_int(row.get(PLAYER_KEY)) or 0,
            short_name=str(row.get("short_name") or "Unknown"),
            long_name=_safe_str(row.get("long_name")),
            season=_safe_int(row.get("season_year")) or 0,
            age=_safe_int(row.get("age")),
            overall=_safe_int(row.get("overall")),
            potential=_safe_int(row.get("potential")),
            pace=_safe_int(row.get("pace")),
            defending=_safe_int(row.get("defending")),
            physic=_safe_int(row.get("physic")),
            probability=_round_float(float(row.get(probability_name) or 0.0), 3) or 0.0,
            future_label=1,
        )
        for _, row in high_rows.head(8).iterrows()
    ]


def _merge_probability_frames(model_frame: Any, injury_probs: Any, solid_probs: Any) -> Any:
    probability_frame = model_frame[
        [PLAYER_KEY, "season_sort", "season_year", "short_name", "long_name"]
    ].copy()
    for probs in (injury_probs, solid_probs):
        if probs.empty:
            continue
        probability_frame = probability_frame.merge(
            probs,
            on=[PLAYER_KEY, "season_sort"],
            how="left",
        )
    for column in ("injury_probability", "solid_probability"):
        if column not in probability_frame.columns:
            probability_frame[column] = None
    return probability_frame



def _timeline_point_from_row(row: Any) -> FutureTimelinePoint:
    status_value = _safe_int(row.get("injury_status"))

    return FutureTimelinePoint(
        season=_safe_int(row.get("season_year")) or 0,
        age=_safe_int(row.get("age")),
        overall=_safe_int(row.get("overall")),
        injury_status=status_value if status_value is not None else -1,
        injury_probability=_safe_float(row.get("injury_probability")),
        solid_probability=_safe_float(row.get("solid_probability")),
  )
def _build_timelines(
    frame: Any,
    probability_frame: Any,
    injury_model: FutureModelSummary,
    solid_model: FutureModelSummary,
) -> list[FutureTimeline]:
    selected_ids: list[int] = []
    for model in (injury_model, solid_model):
        for example in model.examples:
            if example.sofifa_id not in selected_ids:
                selected_ids.append(example.sofifa_id)
            if len(selected_ids) >= 4:
                break
        if len(selected_ids) >= 4:
            break

    timelines = []
    for sofifa_id in selected_ids:
        rows = frame[frame[PLAYER_KEY] == sofifa_id].sort_values("season_sort").copy()
        if rows.empty:
            continue
        rows = rows.merge(
            probability_frame[
                [
                    PLAYER_KEY,
                    "season_sort",
                    "injury_probability",
                    "solid_probability",
                ]
            ],
            on=[PLAYER_KEY, "season_sort"],
            how="left",
        )
        first = rows.iloc[0]
        timelines.append(
            FutureTimeline(
                sofifa_id=sofifa_id,
                short_name=str(first.get("short_name") or "Unknown"),
                long_name=_safe_str(first.get("long_name")),
                points=[
                    _timeline_point_from_row(row)
                    for _, row in rows.iterrows()
                ],
            )
        )
    return timelines




def _status_counts(frame: Any) -> list[InjuryStatusCount]:
    labels = {
        -1: "Unlabeled",
        0: "Solid Player",
        1: "Injury Prone",
    }
    counts = frame["injury_status"].value_counts().to_dict()
    return [
        InjuryStatusCount(
            status=status,
            label=label,
            records=int(counts.get(status, 0)),
        )
        for status, label in labels.items()
    ]


def _empty_response(repository: PlayerRepository, note: str) -> FutureRiskResponse:
    empty_model = FutureModelSummary(
        target="future_injury",
        label="Future Injury Model",
        positive_records=0,
        negative_records=0,
        baseline_positive_rate=0.0,
        notes=[note],
    )
    return FutureRiskResponse(
        source=repository.source_name(),
        seasons=[],
        player_count=0,
        total_records=0,
        modeling_records=0,
        feature_count=0,
        features=[],
        status_counts=[],
        injury_model=empty_model,
        solid_model=empty_model.model_copy(
            update={"target": "future_solid", "label": "Future Solid Model"}
        ),
        timelines=[],
        notes=[note],
    )


def _round_float(value: float, digits: int) -> float | None:
    return round(value, digits) if isfinite(value) else None


def _round_rate(value: float) -> float:
    rounded = _round_float(value, 4)
    return rounded if rounded is not None else 0.0


def _safe_int(value: object) -> int | None:
    try:
        if value is None:
            return None
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _safe_float(value: object) -> float | None:
    try:
        if value is None:
            return None
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return _round_float(parsed, 3)


def _safe_str(value: object) -> str | None:
    if value is None:
        return None
    text = str(value)
    return text if text else None
