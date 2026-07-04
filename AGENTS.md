# AI Agent Guide

## Project Overview

This repository implements a reusable weekly retail sales forecasting pipeline. Production code belongs in `src/sales_forecast/`; notebooks are exploratory only and located in `docs/notebooks/`.

## Directory Structure

- `configs/`: YAML runtime settings.
- `data/`: public sample datasets only.
- `src/sales_forecast/`: CLI, data loading, validation, features, metrics, models, and reporting.
- `tests/`: pytest coverage for MVP behavior.
- `outputs/`: generated artifacts (including `outputs/reports/`).

## Development Rules

- Keep CLI orchestration separate from model, metric, and feature logic.
- Do not put reusable production logic in `docs/notebooks/`.
- Do not commit private, raw, customer, or credential-bearing data.
- Preserve time ordering; never create features from future sales values.

## Model Interface

Models implement:

```python
fit(train_data)
predict(future_data)
```

Add new models under `src/sales_forecast/models/`, register them in `registry.py`, add config examples, and cover them with tests.

## Testing Rules

Run `pytest` before handing off changes. Run `ruff check src/` and `ruff format --check src/` when ruff is installed.

## Report Updates

Report generation belongs in `src/sales_forecast/report.py`. Keep generated output reproducible from CLI commands.
