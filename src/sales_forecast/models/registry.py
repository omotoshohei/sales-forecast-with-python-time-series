from __future__ import annotations

from typing import Any

from sales_forecast.config import DataConfig
from sales_forecast.models.baseline import BaselineForecastModel
from sales_forecast.models.lightgbm import LightGBMForecastModel
from sales_forecast.models.linear_regression import LinearRegressionForecastModel
from sales_forecast.models.prophet import ProphetForecastModel
from sales_forecast.models.sarimax import SarimaxForecastModel


def create_model(name: str, data_config: DataConfig, parameters: dict[str, Any] | None = None):
    params = parameters or {}
    if name == "baseline":
        return BaselineForecastModel(strategy=params.get("strategy", "seasonal_naive"))
    if name == "linear_regression":
        return LinearRegressionForecastModel(data_config=data_config)
    if name == "lightgbm":
        return LightGBMForecastModel(data_config=data_config, parameters=params)
    if name == "prophet":
        return ProphetForecastModel(data_config=data_config, parameters=params)
    if name == "sarimax":
        return SarimaxForecastModel(data_config=data_config, parameters=params)
    raise ValueError(f"Unknown model: {name}")
