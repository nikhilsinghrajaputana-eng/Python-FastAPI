"""Application configuration loaded from environment and YAML files."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PROJECT_ROOT / "config"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "ECADS-v3"
    app_version: str = "3.0.0"
    debug: bool = False

    database_url: str = "postgresql://ecads:ecads@localhost:5432/ecads"
    redis_url: str = "redis://localhost:6379/0"

    default_decision_timezone: str = "Asia/Kolkata"
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()


def load_yaml_config(filename: str) -> dict[str, Any]:
    path = CONFIG_DIR / filename
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def get_scoring_weights() -> dict[str, float]:
    cfg = load_yaml_config("scoring_weights.yaml")
    return cfg.get("opportunity_weights", {})
