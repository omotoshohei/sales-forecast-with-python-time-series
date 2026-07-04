from __future__ import annotations

import argparse
import sys

from sales_forecast.config import load_config
from sales_forecast.data import read_sales_csv
from sales_forecast.evaluate import evaluate_models
from sales_forecast.forecast import forecast_sales
from sales_forecast.report import generate_report
from sales_forecast.train import train_model
from sales_forecast.validation import validate_sales_data


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
        if args.command == "validate-data":
            df = read_sales_csv(config.data.path, config.data)
            result = validate_sales_data(df, config.data)
            _print_validation(result)
            return 0 if result.is_valid else 1
        if args.command == "train":
            path = train_model(config, args.model)
            print(f"Saved model: {path}")
            return 0
        if args.command == "evaluate":
            path = evaluate_models(config)
            print(f"Saved evaluation: {path}")
            return 0
        if args.command == "forecast":
            path = forecast_sales(config, args.model, args.horizon)
            print(f"Saved forecast: {path}")
            return 0
        if args.command == "report":
            paths = generate_report(config, args.output)
            print("Saved reports:")
            for path in paths:
                print(f"- {path}")
            return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    parser.print_help()
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sales_forecast")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate-data")
    validate.add_argument("--config", default="configs/base.yaml")

    train = subparsers.add_parser("train")
    train.add_argument("--config", default="configs/base.yaml")
    train.add_argument("--model", default="baseline")

    evaluate = subparsers.add_parser("evaluate")
    evaluate.add_argument("--config", default="configs/base.yaml")

    forecast = subparsers.add_parser("forecast")
    forecast.add_argument("--config", default="configs/base.yaml")
    forecast.add_argument("--model", default="baseline")
    forecast.add_argument("--horizon", type=int, default=None)

    report = subparsers.add_parser("report")
    report.add_argument("--config", default="configs/base.yaml")
    report.add_argument("--output", default=None, help="comparison Markdown report base path")
    return parser


def _print_validation(result) -> None:
    if result.is_valid:
        print("Data validation passed.")
    else:
        print("Data validation failed.")
    for warning in result.warnings:
        print(f"Warning: {warning}")
    for error in result.errors:
        print(f"Error: {error}")
