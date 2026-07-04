from __future__ import annotations

from pathlib import Path

import pandas as pd

from sales_forecast.config import AppConfig
from sales_forecast.features import model_ready
from sales_forecast.models.registry import create_model
from sales_forecast.pipeline import load_validated_features, training_frame


def forecast_sales(config: AppConfig, model_name: str, horizon: int | None = None) -> Path:
    features = load_validated_features(config)
    train_data = training_frame(features, config)
    model = create_model(model_name, config.data, config.model_parameters.get(model_name, {}))
    model.fit(train_data)

    periods = horizon or config.forecast.default_horizon
    future = features[features["record_type"] == config.data.forecast_value].head(periods).copy()
    if future.empty:
        future = _make_future_rows(features, periods)
    future_ready = model_ready(future, config.data, require_target=False)
    prediction = model.predict(future_ready).clip(lower=0)

    output = pd.DataFrame(
        {
            "week_start_date": future_ready["week_start_date"].dt.strftime("%Y-%m-%d"),
            "model_name": model_name,
            "prediction": prediction.round(2),
        }
    )
    config.output.forecast_dir.mkdir(parents=True, exist_ok=True)
    output_path = config.output.forecast_dir / f"{model_name}_forecast.csv"
    output.to_csv(output_path, index=False)
    return output_path


def _make_future_rows(features: pd.DataFrame, periods: int) -> pd.DataFrame:
    last = features.sort_values("week_start_date").iloc[-1:].copy()
    rows = []
    for step in range(1, periods + 1):
        row = last.copy()
        row["week_start_date"] = row["week_start_date"] + pd.Timedelta(days=7 * step)
        row["sales"] = pd.NA
        row["record_type"] = "Forecast"
        rows.append(row)
    return pd.concat(rows, ignore_index=True)
