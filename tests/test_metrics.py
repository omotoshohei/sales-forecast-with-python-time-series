import pandas as pd

from sales_forecast.metrics import baseline_improvement, calculate_metrics


def test_calculate_metrics_handles_zero_denominators():
    metrics = calculate_metrics(pd.Series([0.0, 10.0]), pd.Series([1.0, 12.0]))

    assert metrics["rmse"] > 0
    assert metrics["mape"] == 0.2
    assert pd.isna(baseline_improvement(1.0, 0.0))
