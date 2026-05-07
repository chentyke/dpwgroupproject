from __future__ import annotations

from pydantic import BaseModel, Field


class InjuryStatusCount(BaseModel):
    status: int
    label: str
    records: int


class FutureRiskMetrics(BaseModel):
    accuracy: float | None = None
    precision: float | None = None
    recall: float | None = None
    f1_score: float | None = None


class FutureRiskFeature(BaseModel):
    feature: str
    importance: float


class FutureRiskExample(BaseModel):
    sofifa_id: int
    short_name: str
    long_name: str | None = None
    season: int
    age: int | None = None
    overall: int | None = None
    potential: int | None = None
    pace: int | None = None
    defending: int | None = None
    physic: int | None = None
    probability: float
    future_label: int


class FutureTimelinePoint(BaseModel):
    season: int
    age: int | None = None
    overall: int | None = None
    injury_status: int
    injury_probability: float | None = None
    solid_probability: float | None = None


class FutureTimeline(BaseModel):
    sofifa_id: int
    short_name: str
    long_name: str | None = None
    points: list[FutureTimelinePoint]


class FutureModelSummary(BaseModel):
    target: str
    label: str
    positive_records: int
    negative_records: int
    baseline_positive_rate: float
    training_rows: int = 0
    test_rows: int = 0
    train_players: int = 0
    test_players: int = 0
    high_risk_threshold: float | None = None
    high_risk_records: int = 0
    high_risk_positive_rate: float | None = None
    metrics: FutureRiskMetrics = Field(default_factory=FutureRiskMetrics)
    top_features: list[FutureRiskFeature] = Field(default_factory=list)
    examples: list[FutureRiskExample] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class FutureRiskResponse(BaseModel):
    source: str
    seasons: list[int]
    player_count: int
    total_records: int
    modeling_records: int
    feature_count: int
    features: list[str]
    status_counts: list[InjuryStatusCount]
    injury_model: FutureModelSummary
    solid_model: FutureModelSummary
    timelines: list[FutureTimeline] = Field(default_factory=list)
    notes: list[str]
