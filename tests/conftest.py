from __future__ import annotations

import pandas as pd
import pytest

from sales_forecast.config import DataConfig


@pytest.fixture
def data_config() -> DataConfig:
    return DataConfig(
        path="unused.csv",
        date_column="Date",
        target_column="Sales",
        record_type_column="Record_Type",
        actual_value="Actual",
        forecast_value="Forecast",
        external_features=["TVCM_GPR", "Print_Media", "Offline_Ads", "Digital_Ads"],
    )


@pytest.fixture
def raw_sales() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Date": pd.date_range("2024-01-01", periods=60, freq="7D").strftime("%Y-%m-%d"),
            "Sales": [f"{1000 + i:,}" for i in range(60)],
            "TVCM_GPR": [0] * 60,
            "Print_Media": [100] * 60,
            "Offline_Ads": [50] * 60,
            "Digital_Ads": [25] * 60,
            "Record_Type": ["Actual"] * 58 + ["Forecast", "Forecast"],
        }
    )
