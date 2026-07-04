from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from sales_forecast.config import DataConfig
from sales_forecast.data import external_feature_columns


@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not self.errors

    def raise_if_invalid(self) -> None:
        if self.errors:
            raise ValueError("Data validation failed:\n- " + "\n- ".join(self.errors))


def validate_sales_data(df: pd.DataFrame, config: DataConfig) -> ValidationResult:
    result = ValidationResult()
    required = ["week_start_date", "sales", "record_type", *external_feature_columns(config)]
    missing_columns = [column for column in required if column not in df.columns]
    if missing_columns:
        result.errors.append(f"Missing standardized columns: {', '.join(missing_columns)}")
        return result

    if df["week_start_date"].isna().any():
        rows = _rows(df["week_start_date"].isna())
        result.errors.append(f"Invalid date values at rows: {rows}")

    invalid_record = ~df["record_type"].isin([config.actual_value, config.forecast_value])
    if invalid_record.any():
        values = sorted(df.loc[invalid_record, "record_type"].dropna().unique())
        result.errors.append(f"Record_Type must be Actual or Forecast. Invalid values: {values}")

    actual_rows = df["record_type"] == config.actual_value
    if df.loc[actual_rows, "sales"].isna().any():
        rows = _rows(actual_rows & df["sales"].isna())
        result.errors.append(f"Actual rows require Sales values. Missing rows: {rows}")

    forecast_rows = df["record_type"] == config.forecast_value
    feature_columns = external_feature_columns(config)
    missing_forecast_features = df.loc[forecast_rows, feature_columns].isna()
    if not missing_forecast_features.empty and missing_forecast_features.any(axis=None):
        result.errors.append("Forecast rows require external feature values.")

    duplicate_dates = df["week_start_date"].duplicated(keep=False) & df["week_start_date"].notna()
    if duplicate_dates.any():
        dates = df.loc[duplicate_dates, "week_start_date"].dt.strftime("%Y-%m-%d").unique().tolist()
        result.errors.append(f"Duplicate weekly dates found: {dates}")

    _validate_weekly_gaps(df, result)
    return result


def _validate_weekly_gaps(df: pd.DataFrame, result: ValidationResult) -> None:
    dates = df["week_start_date"].dropna().sort_values()
    if len(dates) < 2:
        return
    diffs = dates.diff().dropna()
    non_weekly = diffs[diffs != pd.Timedelta(days=7)]
    if not non_weekly.empty:
        result.warnings.append("Some consecutive records are not exactly 7 days apart.")
    full = pd.date_range(dates.min(), dates.max(), freq="7D")
    missing = full.difference(pd.DatetimeIndex(dates))
    if len(missing) > 0:
        preview = [date.strftime("%Y-%m-%d") for date in missing[:5]]
        result.warnings.append(f"Missing weekly dates detected: {preview}")


def _rows(mask: pd.Series) -> list[int]:
    return [int(index) + 2 for index in mask[mask].index]
