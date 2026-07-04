from sales_forecast.data import standardize_sales_data
from sales_forecast.features import build_features


def test_build_features_adds_lag_rolling_and_calendar(raw_sales, data_config):
    df = standardize_sales_data(raw_sales, data_config)
    featured = build_features(df, data_config)

    assert featured.loc[1, "sales_lag_1"] == 1000
    assert "sales_ma_4" in featured
    assert "is_year_end" in featured
