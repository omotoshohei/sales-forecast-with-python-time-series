from __future__ import annotations

from pathlib import Path

import pandas as pd

from sales_forecast.config import AppConfig
from sales_forecast.features import model_ready, split_actuals
from sales_forecast.metrics import baseline_improvement, calculate_metrics
from sales_forecast.models.registry import create_model
from sales_forecast.pipeline import load_validated_features


def evaluate_models(config: AppConfig) -> Path:
    features = load_validated_features(config)
    train, validation, test = split_actuals(features, config.split)
    train_ready = model_ready(pd.concat([train, validation], ignore_index=True), config.data)
    test_ready = model_ready(test, config.data)

    config.output.evaluation_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    baseline_rmse = None
    for model_name in config.models_enabled:
        model = create_model(model_name, config.data, config.model_parameters.get(model_name, {}))
        model.fit(train_ready)
        predicted = model.predict(test_ready)

        _write_model_evaluation_predictions(config, model_name, test_ready, predicted)

        metrics = calculate_metrics(test_ready["sales"], predicted)
        if model_name == "baseline":
            baseline_rmse = metrics["rmse"]
        rows.append({"model_name": model_name, **metrics})

    for row in rows:
        row["baseline_improvement_rate"] = baseline_improvement(row["rmse"], baseline_rmse)

    output_path = config.output.evaluation_dir / "model_comparison.csv"
    pd.DataFrame(rows).to_csv(output_path, index=False)
    return output_path


def _write_model_evaluation_predictions(
    config: AppConfig,
    model_name: str,
    test_ready: pd.DataFrame,
    predicted: pd.Series,
) -> Path:
    if hasattr(predicted, "reindex"):
        aligned_predicted = predicted.reindex(test_ready.index)
    else:
        aligned_predicted = predicted

    df = pd.DataFrame(
        {
            "week_start_date": test_ready["week_start_date"].dt.strftime("%Y-%m-%d"),
            "actual": test_ready["sales"].astype(float),
            "prediction": aligned_predicted.astype(float),
        }
    )
    output_path = config.output.evaluation_dir / f"{model_name}_evaluation.csv"
    df.to_csv(output_path, index=False)
    return output_path
