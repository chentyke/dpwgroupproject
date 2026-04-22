from __future__ import annotations

from pydantic import BaseModel


class LeagueDistribution(BaseModel):
    league_name: str
    sample_size: int
    min_wage: int
    median_wage: int
    average_wage: int
    max_wage: int


class StatisticalTestSummary(BaseModel):
    method: str
    statistic: float | None
    p_value: float | None
    note: str


class FairnessByLeagueResponse(BaseModel):
    overall_min: int
    overall_max: int
    distributions: list[LeagueDistribution]
    test: StatisticalTestSummary
    notes: list[str]


class HeatmapCell(BaseModel):
    nationality_name: str
    league_name: str
    average_wage: int
    sample_size: int


class NationalityHeatmapResponse(BaseModel):
    cells: list[HeatmapCell]
    notes: list[str]

