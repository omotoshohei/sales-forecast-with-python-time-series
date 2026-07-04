from __future__ import annotations

from typing import Any

import pandas as pd

from sales_forecast.config import DataConfig
from sales_forecast.data import external_feature_columns
from sales_forecast.models.optional import import_optional_dependency


class SarimaxForecastModel:
    def __init__(self, data_config: DataConfig, parameters: dict[str, Any] | None = None) -> None:
        self.data_config = data_config
        self.parameters = parameters or {}
        self.result: Any | None = None
        self.exogenous_columns = external_feature_columns(data_config)

    def fit(self, train_data: pd.DataFrame) -> None:
        train = train_data.dropna(subset=["sales"]).copy()
        if train.empty:
            raise ValueError("SARIMAX requires non-null sales in training data.")

        sarimax = import_optional_dependency(
            "statsmodels.tsa.statespace.sarimax",
            "sarimax",
            "sarimax",
        )
        model = sarimax.SARIMAX(
            endog=train["sales"].astype(float),
            exog=self._exogenous(train),
            order=tuple(self.parameters.get("order", (1, 0, 0))),
            seasonal_order=tuple(self.parameters.get("seasonal_order", (0, 0, 0, 0))),
            trend=self.parameters.get("trend"),
            enforce_stationarity=self.parameters.get("enforce_stationarity", False),
            enforce_invertibility=self.parameters.get("enforce_invertibility", False),
        )
        self.result = model.fit(disp=self.parameters.get("disp", False))

    def predict(self, future_data: pd.DataFrame) -> pd.Series:
        if self.result is None:
            raise ValueError("Model is not fitted.")

        predictions = self.result.forecast(
            steps=len(future_data),
            exog=self._exogenous(future_data),
        )
        return pd.Series(predictions.to_numpy(), index=future_data.index, name="prediction")

    def _exogenous(self, frame: pd.DataFrame) -> pd.DataFrame | None:
        if not self.exogenous_columns:
            return None
        return frame[self.exogenous_columns].astype(float).fillna(0)
