from __future__ import annotations

import pickle
from pathlib import Path

import pandas as pd

from sales_forecast.config import AppConfig
from sales_forecast.data import read_sales_csv
from sales_forecast.features import build_features, model_ready, split_actuals
from sales_forecast.validation import validate_sales_data


def load_validated_features(config: AppConfig) -> pd.DataFrame:
    df = read_sales_csv(config.data.path, config.data)
    result = validate_sales_data(df, config.data)
    result.raise_if_invalid()
    return build_features(df, config.data)


def save_model(model: object, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as file:
        pickle.dump(model, file)


def load_model(path: Path) -> object:
    with path.open("rb") as file:
        return pickle.load(file)


def training_frame(features: pd.DataFrame, config: AppConfig) -> pd.DataFrame:
    train, validation, _test = split_actuals(features, config.split)
    combined = pd.concat([train, validation], ignore_index=True)
    return model_ready(combined, config.data)
