from __future__ import annotations

import pandas as pd


class BaselineForecastModel:
    def __init__(self, strategy: str = "seasonal_naive") -> None:
        self.strategy = strategy
        self.fallback_value = 0.0

    def fit(self, train_data: pd.DataFrame) -> None:
        if train_data["sales"].dropna().empty:
            raise ValueError("Baseline model requires non-null sales in training data.")
        self.fallback_value = float(train_data["sales"].dropna().iloc[-1])

    def predict(self, future_data: pd.DataFrame) -> pd.Series:
        if self.strategy == "naive":
            values = future_data["sales_lag_1"]
        elif self.strategy == "moving_average":
            values = future_data["sales_ma_4"]
        elif self.strategy == "seasonal_naive":
            values = future_data["sales_lag_52"]
        else:
            raise ValueError(f"Unsupported baseline strategy: {self.strategy}")
        return values.fillna(self.fallback_value).astype(float).rename("prediction")
