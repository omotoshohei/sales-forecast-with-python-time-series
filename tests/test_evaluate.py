from __future__ import annotations

from dataclasses import replace

import pandas as pd

from sales_forecast.config import OutputConfig, load_config
from sales_forecast.evaluate import evaluate_models


def test_evaluate_models_saves_predictions(tmp_path):
    config = load_config("configs/base.yaml")
    output = OutputConfig(
        models_dir=tmp_path / "models",
        evaluation_dir=tmp_path / "evaluation",
        forecast_dir=tmp_path / "forecast",
        figures_dir=tmp_path / "figures",
        report_path=tmp_path / "model_comparison_report.md",
    )
    data_config = replace(config.data, path=tmp_path / "sales_data.csv")
    config = replace(
        config,
        output=output,
        models_enabled=["baseline", "linear_regression"],
        data=data_config,
    )

    pd.DataFrame(
        {
            "Date": pd.date_range("2025-01-01", periods=100, freq="W-MON").strftime("%Y-%m-%d"),
            "Sales": [1000 + i * 10 for i in range(100)],
            "Record_Type": ["Actual"] * 100,
            "TVCM_GPR": [0.0] * 100,
            "Print_Media": [0.0] * 100,
            "Offline_Ads": [0.0] * 100,
            "Digital_Ads": [0.0] * 100,
        }
    ).to_csv(config.data.path, index=False)

    comparison_path = evaluate_models(config)

    assert comparison_path.exists()
    comparison_df = pd.read_csv(comparison_path)
    assert set(comparison_df["model_name"]) == {"baseline", "linear_regression"}

    for model_name in ["baseline", "linear_regression"]:
        eval_path = config.output.evaluation_dir / f"{model_name}_evaluation.csv"
        assert eval_path.exists()

        eval_df = pd.read_csv(eval_path)
        assert list(eval_df.columns) == ["week_start_date", "actual", "prediction"]
        assert len(eval_df) > 0
        assert not eval_df["week_start_date"].isna().any()
