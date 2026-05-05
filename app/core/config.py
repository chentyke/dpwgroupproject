from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    api_title: str = "FIFA Player Data Analysis API"
    api_description: str = (
        "FastAPI backend for the Software Development Workshop II FIFA "
        "Player Data Analysis System."
    )
    api_version: str = "0.2.0"
    api_prefix: str = "/api"
    frontend_origin: str = "http://127.0.0.1:3000"

    @property
    def project_root(self) -> Path:
        return Path(__file__).resolve().parents[2]

    @property
    def sample_data_path(self) -> Path:
        return self.project_root / "data" / "sample" / "player_snapshots.json"

    @property
    def raw_data_dir(self) -> Path:
        env_path = os.getenv("FIFA_DATA_DIR")
        if env_path:
            return Path(env_path).expanduser().resolve()
        return self.project_root / "data" / "raw"

    @property
    def tidy_cache_path(self) -> Path:
        return self.project_root / "data" / "processed" / "players_tidy.parquet"


@lru_cache
def get_settings() -> Settings:
    return Settings()
