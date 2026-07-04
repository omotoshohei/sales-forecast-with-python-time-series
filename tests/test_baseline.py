from sales_forecast.data import standardize_sales_data
from sales_forecast.features import build_features, model_ready
from sales_forecast.models.baseline import BaselineForecastModel


def test_baseline_predicts_with_fallback(raw_sales, data_config):
    df = standardize_sales_data(raw_sales, data_config)
    featured = model_ready(build_features(df, data_config), data_config, require_target=False)
    model = BaselineForecastModel(strategy="naive")
    model.fit(featured.iloc[:10])

    predicted = model.predict(featured.iloc[10:12])

    assert len(predicted) == 2
    assert predicted.notna().all()
