from __future__ import annotations

import pandas as pd

from sales_forecast.config import DataConfig, SplitConfig
from sales_forecast.data import external_feature_columns

LAG_WEEKS = [1, 4, 12, 52]
ROLLING_WINDOWS = [4, 8, 12]


def build_features(df: pd.DataFrame, config: DataConfig) -> pd.DataFrame:
    """Build time-series features from standardized sales data."""
    featured = df.sort_values("week_start_date").reset_index(drop=True).copy()
    for lag in LAG_WEEKS:
        featured[f"sales_lag_{lag}"] = featured["sales"].shift(lag)
    for window in ROLLING_WINDOWS:
        featured[f"sales_ma_{window}"] = featured["sales"].shift(1).rolling(window=window).mean()

    dates = featured["week_start_date"].dt
    featured["year"] = dates.year
    featured["month"] = dates.month
    featured["week"] = dates.isocalendar().week.astype("int64")
    featured["quarter"] = dates.quarter
    featured["is_year_end"] = featured["month"].isin([12, 1]).astype(int)

    for column in external_feature_columns(config):
        if column in featured.columns:
            featured[column] = featured[column].fillna(0)
    return featured


def feature_columns(config: DataConfig) -> list[str]:
    lag_columns = [f"sales_lag_{lag}" for lag in LAG_WEEKS]
    rolling_columns = [f"sales_ma_{window}" for window in ROLLING_WINDOWS]
    calendar_columns = ["year", "month", "week", "quarter", "is_year_end"]
    return [
        *lag_columns,
        *rolling_columns,
        *calendar_columns,
        *external_feature_columns(config),
    ]


def split_actuals(
    df: pd.DataFrame, split: SplitConfig
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    actual = df[df["record_type"] == "Actual"].sort_values("week_start_date").copy()
    test_size = min(split.test_weeks, max(len(actual) // 5, 1))
    validation_size = min(
        split.validation_weeks,
        max((len(actual) - test_size) // 5, 1),
    )
    train_end = max(len(actual) - validation_size - test_size, 1)
    validation_end = max(len(actual) - test_size, train_end)
    return (
        actual.iloc[:train_end].copy(),
        actual.iloc[train_end:validation_end].copy(),
        actual.iloc[validation_end:].copy(),
    )


def model_ready(
    frame: pd.DataFrame, config: DataConfig, require_target: bool = True
) -> pd.DataFrame:
    columns = feature_columns(config)
    ready = frame.copy()
    ready[columns] = ready[columns].ffill().fillna(0)
    if require_target:
        ready = ready[ready["sales"].notna()]
    return ready
