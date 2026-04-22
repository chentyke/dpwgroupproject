from __future__ import annotations

from pydantic import BaseModel


class RadarMetric(BaseModel):
    label: str
    value: float


class VfmCandidate(BaseModel):
    short_name: str
    club_name: str
    league_name: str
    nationality_name: str
    value_eur: int
    wage_eur: int
    overall: int
    potential: int
    player_positions: str
    vfm_index: float
    metrics: list[RadarMetric]


class ScatterPoint(BaseModel):
    short_name: str
    overall: int
    value_eur: int
    vfm_index: float
    highlight: bool


class VfmResponse(BaseModel):
    position: str
    max_value: int
    benchmark_name: str
    benchmark_metrics: list[RadarMetric]
    candidates: list[VfmCandidate]
    scatter_points: list[ScatterPoint]
    notes: list[str]

