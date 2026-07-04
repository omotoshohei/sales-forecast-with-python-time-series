from __future__ import annotations

from typing import Protocol

import pandas as pd


class BaseForecastModel(Protocol):
    def fit(self, train_data: pd.DataFrame) -> None:
        """Fit model with standardized feature data."""

    def predict(self, future_data: pd.DataFrame) -> pd.Series:
        """Predict sales for standardized feature data."""
