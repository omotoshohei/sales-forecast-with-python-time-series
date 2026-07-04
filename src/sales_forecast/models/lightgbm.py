from __future__ import annotations

from typing import Any

import pandas as pd

from sales_forecast.config import DataConfig
from sales_forecast.features import feature_columns
from sales_forecast.models.optional import import_optional_dependency


class LightGBMForecastModel:
    def __init__(self, data_config: DataConfig, parameters: dict[str, Any] | None = None) -> None:
        self.data_config = data_config
        self.parameters = parameters or {}
        self.model: Any | None = None

    def fit(self, train_data: pd.DataFrame) -> None:
        train = train_data.dropna(subset=["sales"]).copy()
        if train.empty:
            raise ValueError("LightGBM requires non-null sales in training data.")

        lightgbm = import_optional_dependency("lightgbm", "lightgbm", "lightgbm")
        columns = feature_columns(self.data_config)
        self.model = lightgbm.LGBMRegressor(**self.parameters)
        self.model.fit(train[columns].astype(float), train["sales"].astype(float))

    def predict(self, future_data: pd.DataFrame) -> pd.Series:
        if self.model is None:
            raise ValueError("Model is not fitted.")

        columns = feature_columns(self.data_config)
        predictions = self.model.predict(future_data[columns].astype(float))
        return pd.Series(predictions, index=future_data.index, name="prediction")
