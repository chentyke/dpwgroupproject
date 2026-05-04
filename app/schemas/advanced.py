from __future__ import annotations

from pydantic import BaseModel, Field


class ClusterRequest(BaseModel):
    k: int = Field(default=5, ge=2, le=6)


class ClusterPoint(BaseModel):
    short_name: str
    label: str
    x: float
    y: float
    season: int


class ClusterSummary(BaseModel):
    label: str
    count: int
    description: str


class ClusterResponse(BaseModel):
    k: int
    points: list[ClusterPoint]
    summaries: list[ClusterSummary]
    notes: list[str]


class PredictRequest(BaseModel):
    overall: int = Field(ge=1, le=99)
    potential: int = Field(ge=1, le=99)
    age: int = Field(ge=15, le=45)
    wage_eur: int = Field(ge=0)
    pace: int = Field(ge=1, le=99)
    shooting: int | None = Field(default=None, ge=1, le=99)
    dribbling: int = Field(ge=1, le=99)
    passing: int = Field(ge=1, le=99)
    defending: int | None = Field(default=None, ge=1, le=99)
    physic: int | None = Field(default=None, ge=1, le=99)


class FeatureContribution(BaseModel):
    feature: str
    weight: float


class ResidualPoint(BaseModel):
    predicted_log_value: float
    residual: float


class PredictionResponse(BaseModel):
    estimated_value_eur: int
    band: str
    contributions: list[FeatureContribution]
    r2_score: float | None = None
    mae_eur: float | None = None
    residuals: list[ResidualPoint] = Field(default_factory=list)
    training_rows: int = 0
    test_rows: int = 0
    notes: list[str]
