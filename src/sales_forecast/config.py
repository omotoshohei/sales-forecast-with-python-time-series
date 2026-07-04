from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class DataConfig:
    path: Path
    date_column: str
    target_column: str
    record_type_column: str
    actual_value: str
    forecast_value: str
    external_features: list[str]


@dataclass(frozen=True)
class SplitConfig:
    validation_weeks: int = 12
    test_weeks: int = 12


@dataclass(frozen=True)
class OutputConfig:
    models_dir: Path
    evaluation_dir: Path
    forecast_dir: Path
    figures_dir: Path
    report_path: Path


@dataclass(frozen=True)
class ForecastConfig:
    default_horizon: int = 12


@dataclass(frozen=True)
class AppConfig:
    data: DataConfig
    split: SplitConfig
    models_enabled: list[str]
    model_parameters: dict[str, dict[str, Any]]
    metrics: list[str]
    forecast: ForecastConfig
    output: OutputConfig


def load_config(path: str | Path) -> AppConfig:
    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as file:
        raw = yaml.safe_load(file) or {}

    data = raw.get("data", {})
    output = raw.get("output", {})
    split = raw.get("split", {})
    models = raw.get("models", {})
    evaluation = raw.get("evaluation", {})
    forecast = raw.get("forecast", {})

    required = ["path", "date_column", "target_column", "record_type_column"]
    missing = [key for key in required if not data.get(key)]
    if missing:
        raise ValueError(f"Missing data config keys: {', '.join(missing)}")

    return AppConfig(
        data=DataConfig(
            path=Path(data["path"]),
            date_column=data["date_column"],
            target_column=data["target_column"],
            record_type_column=data["record_type_column"],
            actual_value=data.get("actual_value", "Actual"),
            forecast_value=data.get("forecast_value", "Forecast"),
            external_features=list(data.get("external_features", [])),
        ),
        split=SplitConfig(
            validation_weeks=int(split.get("validation_weeks", 12)),
            test_weeks=int(split.get("test_weeks", 12)),
        ),
        models_enabled=list(models.get("enabled", ["baseline"])),
        model_parameters=dict(models.get("parameters", {})),
        metrics=list(evaluation.get("metrics", ["rmse", "mae", "mape", "smape", "wape", "bias"])),
        forecast=ForecastConfig(default_horizon=int(forecast.get("default_horizon", 12))),
        output=OutputConfig(
            models_dir=Path(output.get("models_dir", "outputs/models")),
            evaluation_dir=Path(output.get("evaluation_dir", "outputs/evaluation")),
            forecast_dir=Path(output.get("forecast_dir", "outputs/forecast")),
            figures_dir=Path(output.get("figures_dir", "outputs/figures")),
            report_path=Path(
                output.get("report_path", "outputs/reports/model_comparison_report.md")
            ),
        ),
    )
