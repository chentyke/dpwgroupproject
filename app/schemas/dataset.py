from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ColumnProfile(BaseModel):
    name: str
    dtype: str
    null_count: int


class DatasetSummary(BaseModel):
    source: str
    total_rows: int
    total_columns: int
    seasons: list[int]
    genders: list[str]
    columns: list[ColumnProfile]
    preview: list[dict[str, Any]]


class CleaningStep(BaseModel):
    title: str
    detail: str
    status: str


class NullHotspot(BaseModel):
    column: str
    null_rate: float
    note: str


class CleaningReport(BaseModel):
    source: str
    tidy_cache_path: str
    position_columns: list[str]
    steps: list[CleaningStep]
    null_hotspots: list[NullHotspot]
    notes: list[str]

