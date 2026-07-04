from __future__ import annotations

import numpy as np
import pandas as pd


def calculate_metrics(actual: pd.Series, predicted: pd.Series) -> dict[str, float]:
    aligned_actual, aligned_predicted = _align(actual, predicted)
    error = aligned_predicted - aligned_actual
    return {
        "rmse": float(np.sqrt(np.mean(np.square(error)))),
        "mae": float(np.mean(np.abs(error))),
        "mape": _mape(aligned_actual, aligned_predicted),
        "smape": _smape(aligned_actual, aligned_predicted),
        "wape": _wape(aligned_actual, aligned_predicted),
        "bias": float(np.mean(error)),
    }


def baseline_improvement(model_value: float, baseline_value: float) -> float:
    if pd.isna(model_value) or pd.isna(baseline_value) or baseline_value == 0:
        return float("nan")
    return float((baseline_value - model_value) / baseline_value)


def _align(actual: pd.Series, predicted: pd.Series) -> tuple[pd.Series, pd.Series]:
    frame = pd.concat([actual.rename("actual"), predicted.rename("predicted")], axis=1).dropna()
    if frame.empty:
        raise ValueError("No overlapping non-null actual and predicted values for metrics.")
    return frame["actual"].astype(float), frame["predicted"].astype(float)


def _mape(actual: pd.Series, predicted: pd.Series) -> float:
    mask = actual != 0
    if not mask.any():
        return float("nan")
    return float((np.abs((actual[mask] - predicted[mask]) / actual[mask])).mean())


def _smape(actual: pd.Series, predicted: pd.Series) -> float:
    denominator = np.abs(actual) + np.abs(predicted)
    mask = denominator != 0
    if not mask.any():
        return float("nan")
    return float((2 * np.abs(predicted[mask] - actual[mask]) / denominator[mask]).mean())


def _wape(actual: pd.Series, predicted: pd.Series) -> float:
    denominator = np.abs(actual).sum()
    if denominator == 0:
        return float("nan")
    return float(np.abs(predicted - actual).sum() / denominator)
