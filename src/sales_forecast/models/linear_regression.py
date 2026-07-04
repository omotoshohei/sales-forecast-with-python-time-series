from __future__ import annotations

import numpy as np
import pandas as pd

from sales_forecast.config import DataConfig
from sales_forecast.features import feature_columns


class LinearRegressionForecastModel:
    def __init__(self, data_config: DataConfig) -> None:
        self.data_config = data_config
        self.coefficients: np.ndarray | None = None

    def fit(self, train_data: pd.DataFrame) -> None:
        columns = feature_columns(self.data_config)
        train = train_data.dropna(subset=["sales"]).copy()
        if train.empty:
            raise ValueError("Linear regression requires non-null sales in training data.")
        x = _with_intercept(train[columns].astype(float).to_numpy())
        y = train["sales"].astype(float).to_numpy()
        self.coefficients = np.linalg.lstsq(x, y, rcond=None)[0]

    def predict(self, future_data: pd.DataFrame) -> pd.Series:
        if self.coefficients is None:
            raise ValueError("Model is not fitted.")
        columns = feature_columns(self.data_config)
        x = _with_intercept(future_data[columns].astype(float).to_numpy())
        return pd.Series(x @ self.coefficients, index=future_data.index, name="prediction")


def _with_intercept(values: np.ndarray) -> np.ndarray:
    return np.column_stack([np.ones(values.shape[0]), values])
