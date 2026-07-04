# Sales Forecast With Python Time Series

小売・マーケティング領域の週次売上を予測するための、再利用可能なPythonパイプラインです。Notebookでの単発分析ではなく、CSV入力、データ検証、特徴量生成、複数モデルの比較、将来予測、Markdownレポート生成までをCLIから再現できる構成にしています。

このプロジェクトは、売上実績だけでなく、TVCM、印刷媒体、オフライン広告、デジタル広告のような外部要因も使って、今後の週次売上を予測することを目的にしています。Baselineを基準に、シンプルな回帰モデル、機械学習モデル、時系列モデルを同じデータ分割と評価指標で比較できます。

## What This Project Does

- 週次売上CSVを読み込み、日付、売上、実績/予測区分、外部特徴量を標準化します。
- 学習前に必須カラム、日付、数値、重複週、欠落週、`Record_Type`、将来予測行の外部特徴量を検証します。
- ラグ特徴量、移動平均、カレンダー特徴量、広告系の外部特徴量を生成します。
- 時系列順を保ったまま train / validation / test に分割し、未来の売上値を特徴量に混ぜない設計にしています。
- `baseline`、`linear_regression`、`lightgbm`、`prophet`、`sarimax` を共通インターフェースで学習・予測します。
- RMSE、MAE、MAPE、sMAPE、WAPE、Bias、Baseline比改善率でモデルを比較します。
- 12週間先をデフォルトとして将来売上を予測し、CSVに出力します。
- モデル比較レポートとモデル別レポートを、グラフ付きのMarkdownとして生成します。

## Project Structure

```text
configs/                 YAML runtime settings
data/                    Public sample datasets only
docs/                    Requirements, design docs, glossary, archived notebooks
src/sales_forecast/      Production package
tests/                   pytest coverage for MVP behavior
outputs/                 Generated artifacts
outputs/reports/         Dated Markdown reports and figures
```

Production code belongs in `src/sales_forecast/`. Notebooks under `docs/notebooks/` are exploratory or archived references only.

## Pipeline Flow

1. `validate-data`: 入力CSVの形式と品質を確認します。
2. `train`: 指定モデルを学習し、`outputs/models/` に保存します。
3. `evaluate`: 設定ファイルの `models.enabled` にあるモデルを同一条件で評価します。
4. `forecast`: 指定モデルで将来期間の売上を予測します。
5. `report`: 評価結果と予測結果を読み込み、比較レポートとモデル別レポートを生成します。

## Data Format

標準設定では `data/sales_data.csv` を使います。入力CSVは次の列を想定しています。

| Column | Meaning |
| --- | --- |
| `Date` | 週開始日 |
| `Sales` | 週次売上。`Actual` 行では必須、`Forecast` 行では欠損可 |
| `TVCM_GPR` | TVCM出稿量・到達量の指標 |
| `Print_Media` | 印刷媒体の出稿量または費用 |
| `Offline_Ads` | オフライン広告の出稿量または費用 |
| `Digital_Ads` | デジタル広告の出稿量または費用 |
| `Record_Type` | `Actual` または `Forecast` |

`Actual` 行は学習・評価に使う実績期間です。`Forecast` 行は将来予測に使う期間で、売上は未確定でも、外部特徴量は予測期間分を入れておく想定です。

## Models

| Model name | Role |
| --- | --- |
| `baseline` | Naive、seasonal naive、moving averageの比較基準モデル |
| `linear_regression` | ラグ、移動平均、カレンダー、外部特徴量を使う透明性の高い回帰モデル |
| `lightgbm` | 非線形な広告効果や特徴量間の相互作用を扱う勾配ブースティングモデル |
| `prophet` | トレンド・季節性と外部回帰変数を扱う時系列モデル |
| `sarimax` | 季節性、自己相関、外生変数を扱う統計的時系列モデル |

新しいモデルを追加する場合は、`src/sales_forecast/models/` に `fit(train_data)` と `predict(future_data)` を実装し、`registry.py` に登録します。あわせて `configs/base.yaml` の設定例とテストを追加してください。

## Setup

Python 3.10以上を想定しています。

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

`uv` を使う場合:

```bash
uv sync --extra dev
```

パッケージをインストールせずに `src/` 配下だけを直接実行したい場合:

```bash
PYTHONPATH=src python -m sales_forecast validate-data --config configs/base.yaml
```

## Usage

```bash
python -m sales_forecast validate-data --config configs/base.yaml
python -m sales_forecast train --config configs/base.yaml --model baseline
python -m sales_forecast evaluate --config configs/base.yaml
python -m sales_forecast forecast --config configs/base.yaml --model baseline --horizon 12
python -m sales_forecast report --config configs/base.yaml
```

モデルを変えて実行する例:

```bash
python -m sales_forecast train --config configs/base.yaml --model lightgbm
python -m sales_forecast forecast --config configs/base.yaml --model prophet --horizon 12
```

評価対象モデル、モデルパラメータ、データパス、外部特徴量、分割週数、出力先は `configs/base.yaml` で変更できます。

## Outputs

主な生成物は次の場所に出力されます。

| Path | Content |
| --- | --- |
| `outputs/models/{model_name}.pkl` | 学習済みモデル |
| `outputs/evaluation/model_comparison.csv` | モデル別の評価指標 |
| `outputs/evaluation/{model_name}_evaluation.csv` | テスト期間の実績値と予測値 |
| `outputs/forecast/{model_name}_forecast.csv` | 将来予測結果 |
| `outputs/reports/YYYYMMDD/model_comparison_report_YYYYMMDD.md` | モデル比較レポート |
| `outputs/reports/YYYYMMDD/{model_name}_report_YYYYMMDD.md` | モデル別レポート |
| `outputs/reports/YYYYMMDD/figures/` | レポート用グラフ |

`report` コマンドは、比較レポート1本と、`linear_regression`、`lightgbm`、`prophet`、`sarimax` の個別レポート4本を、日付ディレクトリ配下に生成します。

## Development Checks

変更後は次を実行します。

```bash
pytest
ruff check src/
ruff format --check src/
```

## Data Privacy

`data/` には公開可能なサンプルデータだけを置きます。実在企業の非公開データ、顧客データ、認証情報、APIキーはコミットしないでください。
