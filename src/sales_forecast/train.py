from __future__ import annotations

from pathlib import Path

from sales_forecast.config import AppConfig
from sales_forecast.models.registry import create_model
from sales_forecast.pipeline import load_validated_features, save_model, training_frame


def train_model(config: AppConfig, model_name: str) -> Path:
    features = load_validated_features(config)
    train_data = training_frame(features, config)
    model = create_model(
        model_name,
        config.data,
        config.model_parameters.get(model_name, {}),
    )
    model.fit(train_data)
    output_path = config.output.models_dir / f"{model_name}.pkl"
    save_model(model, output_path)
    return output_path
