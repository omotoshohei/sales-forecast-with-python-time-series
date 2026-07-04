from __future__ import annotations

from pathlib import Path

import pandas as pd

from sales_forecast.config import DataConfig

STANDARD_COLUMNS = {
    "week_start_date": "week_start_date",
    "sales": "sales",
    "record_type": "record_type",
}
EXTERNAL_COLUMN_MAP = {
    "TVCM_GPR": "tvcm_gpr",
    "Print_Media": "print_media",
    "Offline_Ads": "offline_ads",
    "Digital_Ads": "digital_ads",
}


def read_sales_csv(path: str | Path, config: DataConfig) -> pd.DataFrame:
    """Read and standardize sales CSV columns.

    Expected raw columns are configured in DataConfig. Output columns include
    week_start_date, sales, record_type, and normalized external feature names.
    """
    raw = pd.read_csv(path, dtype=str, keep_default_na=False)
    return standardize_sales_data(raw, config)


def standardize_sales_data(raw: pd.DataFrame, config: DataConfig) -> pd.DataFrame:
    required = [config.date_column, config.target_column, config.record_type_column]
    missing = [column for column in required if column not in raw.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    df = pd.DataFrame()
    df["week_start_date"] = pd.to_datetime(raw[config.date_column], errors="coerce")
    df["sales"] = to_numeric(raw[config.target_column])
    df["record_type"] = raw[config.record_type_column].astype(str).str.strip()

    for original in config.external_features:
        standard = EXTERNAL_COLUMN_MAP.get(original, _to_snake_case(original))
        if original not in raw.columns:
            df[standard] = pd.NA
        else:
            df[standard] = to_numeric(raw[original])

    return df


def external_feature_columns(config: DataConfig) -> list[str]:
    columns = []
    for name in config.external_features:
        columns.append(EXTERNAL_COLUMN_MAP.get(name, _to_snake_case(name)))
    return columns


def to_numeric(series: pd.Series) -> pd.Series:
    if series.dtype == object or pd.api.types.is_string_dtype(series):
        cleaned = series.astype(str).str.replace(",", "", regex=False).str.strip()
        cleaned = cleaned.replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})
        return pd.to_numeric(cleaned, errors="coerce")
    return pd.to_numeric(series, errors="coerce")


def _to_snake_case(value: str) -> str:
    return value.strip().replace(" ", "_").replace("-", "_").lower()
