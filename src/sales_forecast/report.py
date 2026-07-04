from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd

from sales_forecast.config import AppConfig

COMPARISON_MODELS = ["baseline", "linear_regression", "lightgbm", "prophet", "sarimax"]
INDIVIDUAL_MODELS = ["linear_regression", "lightgbm", "prophet", "sarimax"]
NO_DATA_MESSAGE = "No data available. Run evaluate and forecast first."


@dataclass(frozen=True)
class ModelReportMetadata:
    title: str
    overview: str
    features: str
    interpretation: str
    limitations: str
    next_steps: str


MODEL_METADATA = {
    "linear_regression": ModelReportMetadata(
        title="Linear Regression",
        overview=(
            "A transparent regression baseline that combines calendar, lag, rolling average, "
            "and marketing variables to explain weekly sales."
        ),
        features=(
            "Uses engineered weekly time-series features such as lag sales, rolling means, "
            "calendar signals, and configured external marketing features."
        ),
        interpretation=(
            "This model is useful for checking directional feature effects and whether simple "
            "linear relationships improve on seasonal naive behavior."
        ),
        limitations=(
            "Linear effects can miss nonlinear promotion response, saturation, and interaction "
            "patterns across media channels."
        ),
        next_steps=(
            "Inspect coefficient stability, residual seasonality, and large error weeks before "
            "using the model for planning decisions."
        ),
    ),
    "lightgbm": ModelReportMetadata(
        title="LightGBM",
        overview=(
            "A gradient boosting model designed to capture nonlinear effects and interactions "
            "among calendar, lag, rolling, and marketing features."
        ),
        features=(
            "Uses the same forecast-safe feature set as the tabular models, with tree-based "
            "splits handling nonlinear thresholds."
        ),
        interpretation=(
            "LightGBM results should be read through relative error reduction and, when "
            "available, feature importance or SHAP-style diagnostics."
        ),
        limitations=(
            "Boosted trees can overfit small weekly datasets and do not extrapolate trend or "
            "seasonality as explicitly as time-series models."
        ),
        next_steps=(
            "Review validation-period stability, tune tree depth and learning rate, and add "
            "feature importance output if the model is promoted."
        ),
    ),
    "prophet": ModelReportMetadata(
        title="Prophet",
        overview=(
            "A decomposable time-series model that represents trend and seasonal components "
            "with optional external regressors."
        ),
        features=(
            "Uses the weekly date index, sales history, yearly seasonality settings, and "
            "configured external regressors where available."
        ),
        interpretation=(
            "Prophet is most informative when trend and seasonal decomposition are important "
            "for explaining forecast movement."
        ),
        limitations=(
            "Performance depends on whether the built-in trend and seasonality assumptions fit "
            "the retail series and available history."
        ),
        next_steps=(
            "Check holiday effects, changepoints, and component plots before relying on the "
            "forecast for long-horizon decisions."
        ),
    ),
    "sarimax": ModelReportMetadata(
        title="SARIMAX",
        overview=(
            "A seasonal autoregressive time-series model that uses past sales structure and "
            "optional exogenous regressors."
        ),
        features=(
            "Uses the ordered weekly sales series with configured SARIMAX order, seasonal "
            "order, trend, and any exogenous variables provided by the pipeline."
        ),
        interpretation=(
            "SARIMAX is useful when autocorrelation and annual weekly seasonality explain a "
            "large share of sales movement."
        ),
        limitations=(
            "The model is sensitive to stationarity, parameter choice, and the amount of "
            "historical data available for seasonal estimation."
        ),
        next_steps=(
            "Inspect residual autocorrelation, convergence warnings, and seasonal parameter "
            "sensitivity before operational use."
        ),
    ),
}


def generate_report(
    config: AppConfig,
    output: str | Path | None = None,
    report_date: date | None = None,
) -> list[Path]:
    resolved_date = report_date or date.today()
    date_suffix = resolved_date.strftime("%Y%m%d")

    if output:
        raw_output_path = _markdown_base_path(Path(output))
        parent_dir = raw_output_path.parent
        stem = raw_output_path.stem
    else:
        raw_output_path = _markdown_base_path(config.output.report_path)
        parent_dir = raw_output_path.parent
        stem = raw_output_path.stem

    date_dir = parent_dir / date_suffix
    comparison_path = date_dir / f"{stem}_{date_suffix}.md"
    figures_dir = date_dir / "figures"

    # Create directories
    date_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    evaluation = _read_optional_csv(config.output.evaluation_dir / "model_comparison.csv")
    evaluation_predictions = {
        model_name: _read_optional_csv(
            config.output.evaluation_dir / f"{model_name}_evaluation.csv"
        )
        for model_name in INDIVIDUAL_MODELS
    }
    forecasts = {
        model_name: _read_optional_csv(config.output.forecast_dir / f"{model_name}_forecast.csv")
        for model_name in COMPARISON_MODELS
    }
    source_data = _read_optional_csv(config.data.path)

    # Generate plots
    ranking_plot_success = _generate_accuracy_ranking_plot(
        evaluation, figures_dir / f"accuracy_ranking_{date_suffix}.png"
    )
    range_plot_success = _generate_forecast_range_comparison_plot(
        forecasts, figures_dir / f"forecast_range_comparison_{date_suffix}.png"
    )

    evaluation_plots = {}
    forecast_plots = {}
    for model_name in INDIVIDUAL_MODELS:
        eval_plot_path = figures_dir / f"{model_name}_evaluation_{date_suffix}.png"
        fc_plot_path = figures_dir / f"{model_name}_forecast_{date_suffix}.png"

        evaluation_plots[model_name] = _generate_evaluation_plot(
            model_name, source_data, evaluation_predictions[model_name], eval_plot_path, config
        )
        forecast_plots[model_name] = _generate_forecast_plot(
            model_name, source_data, forecasts[model_name], fc_plot_path, config
        )

    report_paths = [
        comparison_path,
        *(date_dir / f"{model_name}_report_{date_suffix}.md" for model_name in INDIVIDUAL_MODELS),
    ]
    contents = [
        _render_comparison_report(
            config,
            evaluation,
            forecasts,
            resolved_date,
            ranking_plot_success,
            range_plot_success,
            date_suffix,
        ),
        *(
            _render_individual_report(
                config,
                model_name,
                evaluation,
                evaluation_predictions[model_name],
                forecasts[model_name],
                source_data,
                resolved_date,
                evaluation_plots[model_name],
                forecast_plots[model_name],
                date_suffix,
            )
            for model_name in INDIVIDUAL_MODELS
        ),
    ]

    for path, content in zip(report_paths, contents, strict=True):
        path.write_text(content, encoding="utf-8")
    return report_paths


def _markdown_base_path(path: Path) -> Path:
    return path.with_suffix(".md")


def _dated_path(path: Path, date_suffix: str) -> Path:
    suffix = path.suffix
    stem = path.stem if path.suffix else path.name
    return path.with_name(f"{stem}_{date_suffix}{suffix}")


def _render_individual_report(
    config: AppConfig,
    model_name: str,
    evaluation: pd.DataFrame,
    evaluation_prediction: pd.DataFrame,
    forecast: pd.DataFrame,
    source_data: pd.DataFrame,
    report_date: date,
    evaluation_plot_success: bool,
    forecast_plot_success: bool,
    date_suffix: str,
) -> str:
    metadata = MODEL_METADATA[model_name]
    evaluation_row = _model_evaluation_row(evaluation, model_name)

    return "\n".join(
        [
            f"# {metadata.title} Report",
            "",
            f"Report date: {report_date.isoformat()}",
            "",
            "## Model Overview",
            metadata.overview,
            "",
            "## Features and Preprocessing",
            metadata.features,
            f"Configured external features: {_list_text(config.data.external_features)}.",
            "Forecast-safe lag and rolling features must be derived only from past sales values.",
            "",
            "## Dataset Overview",
            _render_dataset_overview(config, source_data),
            "",
            "## External Regressor Review",
            _render_external_regressor_review(config, source_data),
            "",
            "## Training and Evaluation Conditions",
            f"Validation weeks: {config.split.validation_weeks}",
            f"Test weeks: {config.split.test_weeks}",
            f"Forecast horizon: {config.forecast.default_horizon} weeks",
            f"Evaluation metrics: {_list_text(config.metrics)}.",
            "",
            "## Evaluation Metrics",
            _render_evaluation_section(evaluation_row),
            "",
            "## Evaluation Interpretation",
            _render_evaluation_interpretation(evaluation_row),
            "",
            _render_test_evaluation_section(
                config,
                model_name,
                evaluation_row,
                evaluation_prediction,
                evaluation_plot_success,
                date_suffix,
            ),
            "",
            "## 12-Week Forecast Summary",
            _render_forecast_summary(forecast),
            "",
            "### Forecast Visualization",
            (
                f"![Actual and Forecasted Sales](figures/{model_name}_forecast_{date_suffix}.png)"
                if forecast_plot_success
                else "*No forecast visualization available. Run forecast first.*"
            ),
            "",
            "## Forecast Pattern Analysis",
            _render_forecast_pattern_analysis(forecast),
            "",
            "## Model-Specific Interpretation",
            metadata.interpretation,
            "",
            "## Notebook-Inspired Diagnostic Checklist",
            _render_model_diagnostic_checklist(model_name),
            "",
            "## Limitations",
            metadata.limitations,
            "",
            "## Next Things to Review",
            metadata.next_steps,
            "",
        ]
    )


def _render_test_evaluation_section(
    config: AppConfig,
    model_name: str,
    evaluation_row: dict[str, Any] | None,
    evaluation_prediction: pd.DataFrame,
    evaluation_plot_success: bool,
    date_suffix: str,
) -> str:
    explanation = (
        "The model is fitted on the combined training and validation sets (train + validation) "
        "and evaluated on the holdout test period. This process ensures the metrics represent "
        "generalization performance on unseen data before executing the final forecast."
    )

    has_date_col = {"week_start_date"}.issubset(evaluation_prediction.columns)
    if not evaluation_prediction.empty and has_date_col:
        eval_df = evaluation_prediction.dropna(subset=["week_start_date"])
        if not eval_df.empty:
            test_start = eval_df["week_start_date"].min()
            test_end = eval_df["week_start_date"].max()
            test_rows = len(eval_df)
            test_period_info = (
                f"- **Test Period**: {test_start} to {test_end}\n- **Number of Weeks**: {test_rows}"
            )
        else:
            test_period_info = "- **Test Period**: N/A\n- **Number of Weeks**: 0"
    else:
        test_period_info = "- **Test Period**: N/A\n- **Number of Weeks**: 0"

    config_info = (
        f"- **Validation Configuration**: {config.split.validation_weeks} weeks\n"
        f"- **Test Configuration**: {config.split.test_weeks} weeks"
    )

    if evaluation_row is not None:
        rmse_val = _format_number(evaluation_row.get("rmse"))
        wape_val = _format_percent(evaluation_row.get("wape"))
        bias_val = _format_number(evaluation_row.get("bias"))
        metrics_info = f"- **RMSE**: {rmse_val}\n- **WAPE**: {wape_val}\n- **Bias**: {bias_val}"

        bias_num = _to_float(evaluation_row.get("bias"))
        if bias_num is not None:
            if bias_num > 0:
                bias_dir = "under-forecasting (actual sales exceeded prediction)"
            elif bias_num < 0:
                bias_dir = "over-forecasting (predicted sales exceeded actual)"
            else:
                bias_dir = "balanced forecasting with zero net bias"
            trend_info = (
                f"During the evaluation period, the model shows a net bias of {bias_val}, "
                f"indicating a tendency toward {bias_dir}."
            )
        else:
            trend_info = "Net bias direction is not available."
    else:
        metrics_info = "- **RMSE**: N/A\n- **WAPE**: N/A\n- **Bias**: N/A"
        trend_info = "Metrics are not available to determine deviation trends."

    plot_markdown = (
        f"![Actual vs Predicted Plot](figures/{model_name}_evaluation_{date_suffix}.png)"
        if evaluation_plot_success
        else "*No evaluation visualization available. Run evaluate first.*"
    )

    return "\n".join(
        [
            "## Train / Test Split and Test Evaluation",
            "",
            explanation,
            "",
            "### Evaluation Conditions & Period",
            config_info,
            test_period_info,
            "",
            "### Representative Metrics",
            metrics_info,
            "",
            "### Deviation Trend Analysis",
            trend_info,
            "",
            "### Test Evaluation Visualization",
            plot_markdown,
        ]
    )


def _render_comparison_report(
    config: AppConfig,
    evaluation: pd.DataFrame,
    forecasts: dict[str, pd.DataFrame],
    report_date: date,
    ranking_plot_success: bool,
    range_plot_success: bool,
    date_suffix: str,
) -> str:
    comparison = _comparison_rows(evaluation)
    best_model = _best_model_name(comparison)
    baseline_improvement = _baseline_improvement_text(comparison, best_model)
    best_forecast = forecasts.get(best_model or "", pd.DataFrame())

    return "\n".join(
        [
            "# Model Comparison Report",
            "",
            f"Report date: {report_date.isoformat()}",
            "",
            "## Model Comparison",
            _markdown_table(comparison)
            if comparison
            else "No evaluation data available. Run evaluate first.",
            "",
            "## Accuracy Ranking",
            _render_accuracy_ranking(comparison),
            "",
            "### Accuracy Ranking Visualization",
            f"![Accuracy Ranking Plot](figures/accuracy_ranking_{date_suffix}.png)"
            if ranking_plot_success
            else "*No ranking visualization available. Run evaluate first.*",
            "",
            "## Best Model",
            f"Best model by RMSE: **{best_model or 'N/A'}**.",
            "",
            "## 12-Week Forecast",
            (
                f"Forecast generated by the best model: **{best_model}**."
                if best_model
                else "No best model available."
            ),
            "",
            _render_forecast_summary(best_forecast),
            "",
            "## Baseline Improvement",
            baseline_improvement,
            "",
            "## Forecast Range Comparison",
            _render_forecast_range_comparison(forecasts),
            "",
            "### Forecast Range Comparison Visualization",
            (
                f"![Forecast Range Comparison Plot]"
                f"(figures/forecast_range_comparison_{date_suffix}.png)"
            )
            if range_plot_success
            else "*No forecast range comparison visualization available. Run forecast first.*",
            "",
            "## Forecast Result Reading Guide",
            (
                f"Use the 12-week forecasts in `{config.output.forecast_dir}` alongside RMSE, MAE, "
                "WAPE, and bias to judge both accuracy and planning risk."
            ),
            "",
            "## Business Insights",
            (
                "Models with positive baseline improvement add value beyond seasonal naive "
                "history. Bias should be reviewed before converting forecasts into inventory or "
                "marketing budget decisions."
            ),
            "",
            "## Limitations",
            (
                "This report summarizes existing evaluation and forecast CSV files only. Missing "
                "or stale outputs are reported as unavailable rather than triggering model runs."
            ),
            "",
            "## Next Steps",
            "- Run evaluate after changing training data, feature logic, or model parameters.",
            "- Review model-specific Markdown reports before selecting a production candidate.",
            "- Investigate high-bias models even when their RMSE is competitive.",
            "",
        ]
    )


def _read_optional_csv(path: Path) -> pd.DataFrame:
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def _render_dataset_overview(config: AppConfig, source_data: pd.DataFrame) -> str:
    date_column = config.data.date_column
    target_column = config.data.target_column
    record_type_column = config.data.record_type_column
    required_columns = {date_column, target_column, record_type_column}
    if source_data.empty or not required_columns.issubset(source_data.columns):
        return NO_DATA_MESSAGE

    data = source_data.copy()
    data[date_column] = pd.to_datetime(data[date_column], errors="coerce")
    data[target_column] = _numeric_series(data[target_column])
    actual = data[data[record_type_column] == config.data.actual_value]
    forecast = data[data[record_type_column] == config.data.forecast_value]

    rows = [
        {
            "Segment": "Actual",
            "Rows": str(len(actual)),
            "Start": _date_text(actual[date_column].min()),
            "End": _date_text(actual[date_column].max()),
            "Average Sales": _format_number(actual[target_column].mean()),
            "Minimum Sales": _format_number(actual[target_column].min()),
            "Maximum Sales": _format_number(actual[target_column].max()),
        },
        {
            "Segment": "Forecast Inputs",
            "Rows": str(len(forecast)),
            "Start": _date_text(forecast[date_column].min()),
            "End": _date_text(forecast[date_column].max()),
            "Average Sales": "N/A",
            "Minimum Sales": "N/A",
            "Maximum Sales": "N/A",
        },
    ]
    return "\n\n".join(
        [
            _markdown_table(rows),
            (
                "Actual rows are used for backtesting and model fitting. Forecast-input rows "
                "provide future dates and external assumptions; future Sales values are not "
                "used as features."
            ),
        ]
    )


def _render_external_regressor_review(config: AppConfig, source_data: pd.DataFrame) -> str:
    if source_data.empty:
        return NO_DATA_MESSAGE

    rows = []
    for feature in config.data.external_features:
        if feature not in source_data.columns:
            rows.append({"Feature": feature, "Status": "Missing from source data"})
            continue
        values = _numeric_series(source_data[feature])
        non_zero_share = (values.fillna(0) != 0).mean()
        rows.append(
            {
                "Feature": feature,
                "Average": _format_number(values.mean()),
                "Minimum": _format_number(values.min()),
                "Maximum": _format_number(values.max()),
                "Non-Zero Weeks": _format_percent(non_zero_share),
            }
        )

    return "\n\n".join(
        [
            _markdown_table(rows),
            (
                "Notebook experiments treated these variables as external regressors and tested "
                "lagged or residual advertising effects. This report summarizes their available "
                "signal before interpreting model accuracy."
            ),
        ]
    )


def _model_evaluation_row(evaluation: pd.DataFrame, model_name: str) -> dict[str, Any] | None:
    if evaluation.empty or "model_name" not in evaluation:
        return None
    rows = evaluation[evaluation["model_name"] == model_name]
    if rows.empty:
        return None
    return rows.iloc[0].to_dict()


def _render_evaluation_section(row: dict[str, Any] | None) -> str:
    if row is None:
        return NO_DATA_MESSAGE
    return _markdown_table([_format_evaluation_row(row)])


def _render_evaluation_interpretation(row: dict[str, Any] | None) -> str:
    if row is None:
        return NO_DATA_MESSAGE

    rmse = _to_float(row.get("rmse"))
    mae = _to_float(row.get("mae"))
    wape = _to_float(row.get("wape"))
    bias = _to_float(row.get("bias"))
    improvement = _to_float(row.get("baseline_improvement_rate"))
    model_name = str(row.get("model_name", "This model"))

    lines = [
        (
            f"- Error scale: RMSE is {_format_number(rmse)} and MAE is "
            f"{_format_number(mae)}. A large gap between RMSE and MAE means a few weeks have "
            "outsized errors and should be inspected individually."
        ),
        (
            f"- Relative accuracy: WAPE is {_format_percent(wape)}, which expresses absolute "
            "error as a share of actual sales volume."
        ),
        (
            f"- Baseline value: {model_name} shows "
            f"{_format_percent(improvement)} baseline improvement by RMSE. Positive values mean "
            "the model improves on the configured baseline; negative values mean the baseline is "
            "still stronger."
        ),
        (f"- Bias direction: average bias is {_format_number(bias)}. {_bias_interpretation(bias)}"),
    ]
    return "\n".join(lines)


def _render_forecast_summary(forecast: pd.DataFrame) -> str:
    required_columns = {"week_start_date", "prediction"}
    if forecast.empty or not required_columns.issubset(forecast.columns):
        return NO_DATA_MESSAGE

    forecast_12 = forecast.head(12).copy()
    values = pd.to_numeric(forecast_12["prediction"], errors="coerce")
    forecast_start = forecast_12.iloc[0]["week_start_date"]
    forecast_end = forecast_12.iloc[-1]["week_start_date"]
    summary_rows = [
        {"Metric": "Weeks", "Value": str(len(forecast_12))},
        {"Metric": "Average Prediction", "Value": _format_number(values.mean())},
        {"Metric": "Minimum Prediction", "Value": _format_number(values.min())},
        {"Metric": "Maximum Prediction", "Value": _format_number(values.max())},
        {
            "Metric": "Forecast Window",
            "Value": f"{forecast_start} to {forecast_end}",
        },
    ]
    preview_rows = [
        {
            "Week Start Date": str(row["week_start_date"]),
            "Prediction": _format_number(row["prediction"]),
        }
        for _, row in forecast_12.iterrows()
    ]
    return "\n\n".join(
        [
            _markdown_table(summary_rows),
            "### 12-Week Forecast Preview",
            _markdown_table(preview_rows),
        ]
    )


def _render_forecast_pattern_analysis(forecast: pd.DataFrame) -> str:
    required_columns = {"week_start_date", "prediction"}
    if forecast.empty or not required_columns.issubset(forecast.columns):
        return NO_DATA_MESSAGE

    forecast_12 = forecast.head(12).copy()
    values = pd.to_numeric(forecast_12["prediction"], errors="coerce")
    first_half = values.head(6)
    second_half = values.tail(6)
    first_value = values.iloc[0]
    last_value = values.iloc[-1]
    rows = [
        {"Metric": "First Week", "Value": _format_number(first_value)},
        {"Metric": "Final Week", "Value": _format_number(last_value)},
        {"Metric": "Final vs First", "Value": _format_number(last_value - first_value)},
        {"Metric": "First 6 Week Average", "Value": _format_number(first_half.mean())},
        {"Metric": "Last 6 Week Average", "Value": _format_number(second_half.mean())},
        {
            "Metric": "Back-Half Lift",
            "Value": _format_number(second_half.mean() - first_half.mean()),
        },
    ]
    return "\n\n".join(
        [
            _markdown_table(rows),
            (
                "Use this pattern check with campaign calendars and inventory plans. A rising "
                "back half may reflect future regressor assumptions or seasonal structure; a flat "
                "line can indicate conservative extrapolation."
            ),
        ]
    )


def _render_model_diagnostic_checklist(model_name: str) -> str:
    checklists = {
        "linear_regression": [
            "Review coefficient signs for TVCM, Print, Offline, and Digital regressors.",
            (
                "Check whether residual-effect or lagged advertising variables explain "
                "delayed sales response."
            ),
            (
                "Inspect residual plots for remaining seasonality, holiday spikes, and "
                "high-leverage weeks."
            ),
            (
                "Confirm monthly and holiday dummies are not absorbing marketing effects "
                "that should be interpreted separately."
            ),
        ],
        "lightgbm": [
            (
                "Review feature importance for lag sales, rolling means, calendar variables, "
                "and advertising inputs."
            ),
            (
                "Check early-stopping behavior and whether tree depth is appropriate for the "
                "small weekly dataset."
            ),
            (
                "Compare test-week actual vs predicted lines to find nonlinear promotion "
                "response failures."
            ),
            (
                "Watch for overfitting when boosted trees outperform training history but do "
                "not improve holdout WAPE."
            ),
        ],
        "prophet": [
            (
                "Inspect trend, changepoint, and yearly seasonality components before using "
                "the forecast operationally."
            ),
            (
                "Confirm external regressors are available for every forecast week and are "
                "on the same scale as training data."
            ),
            (
                "Compare additive vs multiplicative seasonality when sales peaks scale with "
                "the overall level."
            ),
            "Check uncertainty intervals if they are exported in a future artifact.",
        ],
        "sarimax": [
            (
                "Review selected order and seasonal_order against weekly annual seasonality "
                "assumptions."
            ),
            "Inspect residual autocorrelation and convergence warnings after fitting.",
            (
                "Confirm exogenous regressors are aligned by week and known for the full "
                "forecast horizon."
            ),
            (
                "Treat short history as a limitation because seasonal differencing with m=52 "
                "needs enough annual cycles."
            ),
        ],
    }
    items = checklists.get(
        model_name, ["Review residuals, feature inputs, and forecast stability."]
    )
    return "\n".join(f"- {item}" for item in items)


def _comparison_rows(evaluation: pd.DataFrame) -> list[dict[str, str]]:
    if evaluation.empty or "model_name" not in evaluation:
        return []

    rows = []
    for model_name in COMPARISON_MODELS:
        evaluation_row = _model_evaluation_row(evaluation, model_name)
        if evaluation_row is None:
            rows.append({"Model": model_name, "Status": "No evaluation data available"})
        else:
            rows.append(_format_evaluation_row(evaluation_row))
    return rows


def _render_accuracy_ranking(comparison_rows: list[dict[str, str]]) -> str:
    ranked = [
        row
        for row in comparison_rows
        if row.get("RMSE") not in {None, "", "N/A"} and row.get("Model")
    ]
    ranked.sort(key=lambda row: _parse_formatted_number(row.get("RMSE")) or float("inf"))
    if not ranked:
        return "No evaluation data available. Run evaluate first."

    rows = []
    for rank, row in enumerate(ranked, start=1):
        rows.append(
            {
                "Rank": str(rank),
                "Model": row["Model"],
                "RMSE": row.get("RMSE", "N/A"),
                "WAPE": row.get("WAPE", "N/A"),
                "Bias": row.get("Bias", "N/A"),
                "Baseline Improvement": row.get("Baseline Improvement", "N/A"),
            }
        )
    return _markdown_table(rows)


def _render_forecast_range_comparison(forecasts: dict[str, pd.DataFrame]) -> str:
    rows = []
    for model_name in COMPARISON_MODELS:
        forecast = forecasts.get(model_name, pd.DataFrame()).head(12)
        if forecast.empty or "prediction" not in forecast.columns:
            rows.append({"Model": model_name, "Status": "No forecast data available"})
            continue
        values = pd.to_numeric(forecast["prediction"], errors="coerce")
        rows.append(
            {
                "Model": model_name,
                "Average Prediction": _format_number(values.mean()),
                "Minimum Prediction": _format_number(values.min()),
                "Maximum Prediction": _format_number(values.max()),
                "Range": _format_number(values.max() - values.min()),
            }
        )
    return _markdown_table(rows)


def _format_evaluation_row(row: dict[str, Any]) -> dict[str, str]:
    return {
        "Model": str(row.get("model_name", "N/A")),
        "RMSE": _format_number(row.get("rmse")),
        "MAE": _format_number(row.get("mae")),
        "MAPE": _format_percent(row.get("mape")),
        "SMAPE": _format_percent(row.get("smape")),
        "WAPE": _format_percent(row.get("wape")),
        "Bias": _format_number(row.get("bias")),
        "Baseline Improvement": _format_percent(row.get("baseline_improvement_rate")),
    }


def _best_model_name(comparison_rows: list[dict[str, str]]) -> str | None:
    candidates = [
        row["Model"]
        for row in comparison_rows
        if row.get("RMSE") not in {None, "", "N/A"} and row.get("Model")
    ]
    if not candidates:
        return None
    return candidates[0] if len(candidates) == 1 else _lowest_rmse_model(comparison_rows)


def _lowest_rmse_model(comparison_rows: list[dict[str, str]]) -> str | None:
    best_model = None
    best_rmse = None
    for row in comparison_rows:
        rmse = _parse_formatted_number(row.get("RMSE"))
        if rmse is None:
            continue
        if best_rmse is None or rmse < best_rmse:
            best_rmse = rmse
            best_model = row["Model"]
    return best_model


def _baseline_improvement_text(
    comparison_rows: list[dict[str, str]], best_model: str | None
) -> str:
    if not comparison_rows or not best_model:
        return "No evaluation data available. Run evaluate first."
    for row in comparison_rows:
        if row.get("Model") == best_model:
            return (
                f"{best_model} baseline improvement: **{row.get('Baseline Improvement', 'N/A')}**."
            )
    return "No baseline improvement data available."


def _markdown_table(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return NO_DATA_MESSAGE
    headers = []
    for row in rows:
        for header in row:
            if header not in headers:
                headers.append(header)
    normalized_rows = [
        [_escape_markdown(str(row.get(header, ""))) for header in headers] for row in rows
    ]
    normalized_headers = [_escape_markdown(header) for header in headers]
    lines = [
        "| " + " | ".join(normalized_headers) + " |",
        "| " + " | ".join("---" for _ in normalized_headers) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in normalized_rows)
    return "\n".join(lines)


def _format_number(value: Any) -> str:
    if pd.isna(value):
        return "N/A"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    return f"{number:,.2f}"


def _format_percent(value: Any) -> str:
    if pd.isna(value):
        return "N/A"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    return f"{number:.2%}"


def _parse_formatted_number(value: str | None) -> float | None:
    if not value or value == "N/A":
        return None
    try:
        return float(value.replace(",", ""))
    except ValueError:
        return None


def _to_float(value: Any) -> float | None:
    if value is None or pd.isna(value):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _numeric_series(series: pd.Series) -> pd.Series:
    if series.dtype == object:
        series = series.astype(str).str.replace(",", "", regex=False)
    return pd.to_numeric(series, errors="coerce")


def _date_text(value: Any) -> str:
    if pd.isna(value):
        return "N/A"
    return pd.Timestamp(value).date().isoformat()


def _bias_interpretation(bias: float | None) -> str:
    if bias is None:
        return "Bias is unavailable, so forecast direction risk cannot be assessed."
    if bias > 0:
        return "Positive bias means the model tends to under-forecast actual sales."
    if bias < 0:
        return "Negative bias means the model tends to over-forecast actual sales."
    return "Bias is near zero, so average over- and under-forecasting are balanced."


def _escape_markdown(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def _list_text(values: list[str]) -> str:
    return ", ".join(values) if values else "none"


def _generate_forecast_plot(
    model_name: str,
    source_data: pd.DataFrame,
    forecast: pd.DataFrame,
    output_path: Path,
    config: AppConfig,
) -> bool:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        if source_data.empty or forecast.empty:
            return False

        date_col = config.data.date_column
        target_col = config.data.target_column
        type_col = config.data.record_type_column

        if not {date_col, target_col, type_col}.issubset(source_data.columns):
            return False
        if not {"week_start_date", "prediction"}.issubset(forecast.columns):
            return False

        # Extract actual data
        actual_df = source_data[source_data[type_col] == config.data.actual_value].copy()
        actual_df[date_col] = pd.to_datetime(actual_df[date_col])
        cleaned_target = (
            actual_df[target_col].astype(str).str.replace(",", "", regex=False).str.strip()
        )
        actual_df[target_col] = pd.to_numeric(cleaned_target, errors="coerce")
        actual_df = actual_df.dropna(subset=[date_col, target_col]).sort_values(date_col)

        # Restrict to last 52 weeks to keep plot legible
        actual_df = actual_df.tail(52)

        if actual_df.empty:
            return False

        # Extract forecast data
        fc_df = forecast.copy()
        fc_df["week_start_date"] = pd.to_datetime(fc_df["week_start_date"])
        fc_df["prediction"] = pd.to_numeric(fc_df["prediction"], errors="coerce")
        fc_df = fc_df.dropna(subset=["week_start_date", "prediction"]).sort_values(
            "week_start_date"
        )

        if fc_df.empty:
            return False

        plt.figure(figsize=(10, 5))
        plt.plot(
            actual_df[date_col],
            actual_df[target_col],
            label="Actual Sales",
            color="blue",
            marker="o",
            markersize=3,
        )
        plt.plot(
            fc_df["week_start_date"],
            fc_df["prediction"],
            label="Forecasted Sales",
            color="orange",
            linestyle="--",
            marker="x",
        )

        plt.title(f"{model_name.replace('_', ' ').title()} - Actual vs Forecast")
        plt.xlabel("Date")
        plt.ylabel("Sales")
        plt.legend()
        plt.grid(True, linestyle=":")
        plt.tight_layout()

        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=150)
        plt.close()
        return True
    except Exception as e:
        print(f"Error generating individual plot for {model_name}: {e}")
        return False


def _generate_evaluation_plot(
    model_name: str,
    source_data: pd.DataFrame,
    evaluation_prediction: pd.DataFrame,
    output_path: Path,
    config: AppConfig,
) -> bool:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        if source_data.empty or evaluation_prediction.empty:
            return False

        date_col = config.data.date_column
        target_col = config.data.target_column
        type_col = config.data.record_type_column

        if not {date_col, target_col, type_col}.issubset(source_data.columns):
            return False
        if not {"week_start_date", "actual", "prediction"}.issubset(evaluation_prediction.columns):
            return False

        # Extract actual data
        actual_df = source_data[source_data[type_col] == config.data.actual_value].copy()
        actual_df[date_col] = pd.to_datetime(actual_df[date_col])
        cleaned_target = (
            actual_df[target_col].astype(str).str.replace(",", "", regex=False).str.strip()
        )
        actual_df[target_col] = pd.to_numeric(cleaned_target, errors="coerce")
        actual_df = actual_df.dropna(subset=[date_col, target_col]).sort_values(date_col)

        # Restrict to last 52 weeks to keep plot legible
        actual_df = actual_df.tail(52)

        if actual_df.empty:
            return False

        # Extract evaluation prediction data
        eval_df = evaluation_prediction.copy()
        eval_df["week_start_date"] = pd.to_datetime(eval_df["week_start_date"])
        eval_df["actual"] = pd.to_numeric(eval_df["actual"], errors="coerce")
        eval_df["prediction"] = pd.to_numeric(eval_df["prediction"], errors="coerce")
        eval_df = eval_df.dropna(subset=["week_start_date", "actual", "prediction"]).sort_values(
            "week_start_date"
        )

        if eval_df.empty:
            return False

        plt.figure(figsize=(10, 5))
        plt.plot(
            actual_df[date_col],
            actual_df[target_col],
            label="Actual",
            color="blue",
            marker="o",
            markersize=3,
        )
        plt.plot(
            eval_df["week_start_date"],
            eval_df["prediction"],
            label="Predicted",
            color="orange",
            linestyle="--",
            marker="x",
        )

        plt.title(f"{model_name.replace('_', ' ').title()} - Actual vs Predicted")
        plt.xlabel("Date")
        plt.ylabel("Sales")
        plt.legend()
        plt.grid(True, linestyle=":")
        plt.tight_layout()

        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=150)
        plt.close()
        return True
    except Exception as e:
        print(f"Error generating evaluation plot for {model_name}: {e}")
        return False


def _generate_accuracy_ranking_plot(evaluation: pd.DataFrame, output_path: Path) -> bool:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        if evaluation.empty or "model_name" not in evaluation or "rmse" not in evaluation:
            return False

        df = evaluation.copy()
        df["rmse"] = pd.to_numeric(df["rmse"], errors="coerce")
        df = df.dropna(subset=["rmse"]).sort_values("rmse", ascending=True)

        if df.empty:
            return False

        plt.figure(figsize=(8, 4))
        colors = [
            "green" if name == df.iloc[0]["model_name"] else "skyblue" for name in df["model_name"]
        ]
        bars = plt.barh(df["model_name"], df["rmse"], color=colors)
        plt.xlabel("RMSE (Lower is Better)")
        plt.title("Model Accuracy Comparison (RMSE)")
        plt.gca().invert_yaxis()
        plt.grid(True, axis="x", linestyle=":")

        for bar in bars:
            width = bar.get_width()
            plt.text(
                width,
                bar.get_y() + bar.get_height() / 2,
                f" {width:,.2f}",
                va="center",
                ha="left",
                fontsize=9,
            )

        plt.tight_layout()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=150)
        plt.close()
        return True
    except Exception as e:
        print(f"Error generating accuracy ranking plot: {e}")
        return False


def _generate_forecast_range_comparison_plot(
    forecasts: dict[str, pd.DataFrame], output_path: Path
) -> bool:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        plt.figure(figsize=(10, 5))
        has_data = False

        colors = {
            "baseline": "gray",
            "linear_regression": "blue",
            "lightgbm": "green",
            "prophet": "purple",
            "sarimax": "red",
        }

        for model_name, fc_df in forecasts.items():
            required_cols = {"week_start_date", "prediction"}
            if fc_df.empty or not required_cols.issubset(fc_df.columns):
                continue
            df = fc_df.head(12).copy()
            df["week_start_date"] = pd.to_datetime(df["week_start_date"])
            df["prediction"] = pd.to_numeric(df["prediction"], errors="coerce")
            df = df.dropna(subset=["week_start_date", "prediction"]).sort_values("week_start_date")

            if df.empty:
                continue

            plt.plot(
                df["week_start_date"],
                df["prediction"],
                label=model_name.replace("_", " ").title(),
                color=colors.get(model_name, "black"),
                marker="o",
                markersize=4,
            )
            has_data = True

        if not has_data:
            plt.close()
            return False

        plt.title("12-Week Forecast Comparison Across Models")
        plt.xlabel("Date")
        plt.ylabel("Sales")
        plt.legend()
        plt.grid(True, linestyle=":")
        plt.tight_layout()

        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=150)
        plt.close()
        return True
    except Exception as e:
        print(f"Error generating forecast range comparison plot: {e}")
        return False
