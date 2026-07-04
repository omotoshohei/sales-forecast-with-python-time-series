# Sales Forecast With Python Time Series

Reusable weekly retail sales forecasting pipeline for sample sales data. Production code lives in `src/sales_forecast/`; notebooks are exploratory or archived references only in `docs/notebooks/`.

## Structure

- `src/sales_forecast/`: CLI, data loading, validation, features, metrics, models, and reporting.
- `tests/`: pytest coverage for MVP behavior.
- `configs/`: YAML runtime settings.
- `data/`: public sample datasets only.
- `docs/notebooks/archive/legacy-model-experiments/`: legacy model exploration notebooks.
- `outputs/`: generated evaluation, forecast, figure, and model artifacts.
- `outputs/reports/`: generated Markdown model reports and representative sample reports.

## Commands

```bash
python -m sales_forecast validate-data --config configs/base.yaml
python -m sales_forecast train --config configs/base.yaml --model baseline
python -m sales_forecast evaluate --config configs/base.yaml
python -m sales_forecast forecast --config configs/base.yaml --model baseline
python -m sales_forecast report --config configs/base.yaml
```

The `report` command writes five dated Markdown files: one comparison report
(`model_comparison_report_YYYYMMDD.md`) and individual reports for
`linear_regression`, `lightgbm`, `prophet`, and `sarimax`.

## Optional Models

The default configuration enables `baseline` and `linear_regression`. Advanced models are available when their optional dependencies are installed:

```bash
pip install -e ".[lightgbm]"
pip install -e ".[prophet]"
pip install -e ".[sarimax]"
pip install -e ".[advanced-models]"
```

Then run them by name:

```bash
python -m sales_forecast train --config configs/base.yaml --model lightgbm
python -m sales_forecast forecast --config configs/base.yaml --model prophet
python -m sales_forecast evaluate --config configs/base.yaml
```

To include `lightgbm`, `prophet`, or `sarimax` in evaluation, add them to `models.enabled` in `configs/base.yaml`.

To execute only the `src/` package without the root compatibility shim:

```bash
PYTHONPATH=src python -m sales_forecast validate-data --config configs/base.yaml
```

## Development Checks

```bash
pytest
ruff check src/
ruff format --check src/
```
