from sales_forecast.data import standardize_sales_data


def test_standardize_sales_data_converts_columns_and_numbers(raw_sales, data_config):
    df = standardize_sales_data(raw_sales, data_config)

    assert list(df.columns) == [
        "week_start_date",
        "sales",
        "record_type",
        "tvcm_gpr",
        "print_media",
        "offline_ads",
        "digital_ads",
    ]
    assert df.loc[0, "sales"] == 1000
    assert df.loc[0, "week_start_date"].year == 2024
