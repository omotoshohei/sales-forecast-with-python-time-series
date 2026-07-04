from __future__ import annotations

from typing import Any

import pandas as pd

from sales_forecast.config import DataConfig
from sales_forecast.data import external_feature_columns
from sales_forecast.models.optional import import_optional_dependency


class ProphetForecastModel:
    def __init__(self, data_config: DataConfig, parameters: dict[str, Any] | None = None) -> None:
        self.data_config = data_config
        self.parameters = parameters or {}
        self.model: Any | None = None
        self.regressors = external_feature_columns(data_config)

    def fit(self, train_data: pd.DataFrame) -> None:
        train = train_data.dropna(subset=["sales"]).copy()
        if train.empty:
            raise ValueError("Prophet requires non-null sales in training data.")

        prophet = import_optional_dependency("prophet", "prophet", "prophet")
        self.model = prophet.Prophet(**self.parameters)
        for regressor in self.regressors:
            self.model.add_regressor(regressor)
        self.model.fit(self._to_prophet_frame(train, include_target=True))

    def predict(self, future_data: pd.DataFrame) -> pd.Series:
        if self.model is None:
            raise ValueError("Model is not fitted.")

        forecast = self.model.predict(self._to_prophet_frame(future_data, include_target=False))
        return pd.Series(forecast["yhat"].to_numpy(), index=future_data.index, name="prediction")

    def _to_prophet_frame(self, frame: pd.DataFrame, include_target: bool) -> pd.DataFrame:
        columns = ["week_start_date", *self.regressors]
        if include_target:
            columns.append("sales")
        prophet_frame = (
            frame[columns].rename(columns={"week_start_date": "ds", "sales": "y"}).copy()
        )
        for regressor in self.regressors:
            prophet_frame[regressor] = prophet_frame[regressor].astype(float).fillna(0)
        return prophet_frame
