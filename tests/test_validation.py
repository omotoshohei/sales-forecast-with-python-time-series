from sales_forecast.data import standardize_sales_data
from sales_forecast.validation import validate_sales_data


def test_validate_sales_data_accepts_forecast_sales_missing(raw_sales, data_config):
    raw_sales.loc[58:, "Sales"] = ""
    df = standardize_sales_data(raw_sales, data_config)
    result = validate_sales_data(df, data_config)

    assert result.is_valid


def test_validate_sales_data_rejects_missing_actual_sales(raw_sales, data_config):
    raw_sales.loc[0, "Sales"] = ""
    df = standardize_sales_data(raw_sales, data_config)
    result = validate_sales_data(df, data_config)

    assert not result.is_valid
    assert "Actual rows require Sales" in result.errors[0]
