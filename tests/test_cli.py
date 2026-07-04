from datetime import date

from sales_forecast.cli import main


def test_cli_validate_data_passes():
    assert main(["validate-data", "--config", "configs/base.yaml"]) == 0


def test_cli_report_writes_file(tmp_path):
    output = tmp_path / "model_comparison_report.md"

    assert main(["report", "--config", "configs/base.yaml", "--output", str(output)]) == 0
    reports = {
        "model_comparison_report",
        "linear_regression_report",
        "lightgbm_report",
        "prophet_report",
        "sarimax_report",
    }
    date_suffix = date.today().strftime("%Y%m%d")
    target_dir = tmp_path / date_suffix

    generated = {path.name.rsplit("_", 1)[0] for path in target_dir.glob("*.md")}

    assert reports == generated
    comparison = next(target_dir.glob("model_comparison_report_*.md"))
    assert "## Model Comparison" in comparison.read_text(encoding="utf-8")
