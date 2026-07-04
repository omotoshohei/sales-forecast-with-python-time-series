# リポジトリ構造定義書 (Repository Structure Document)

## プロジェクト構造

```text
sales-forecast-with-python-time-series/
├── README.md
├── AGENTS.md
├── pyproject.toml
├── .gitignore
├── configs/
│   └── base.yaml
├── data/
│   ├── sales_data.csv
│   └── sales-data-simple.csv
├── docs/
│   ├── ideas/
│   │   └── initial-requirements.md
│   ├── notebooks/
│   │   └── archive/
│   │       └── legacy-model-experiments/
│   │           ├── linear-regression/
│   │           ├── light-gbm/
│   │           ├── prophet/
│   │           └── sarimax/
│   ├── product-requirements.md
│   ├── functional-design.md
│   ├── architecture.md
│   ├── repository-structure.md
│   ├── development-guidelines.md
│   └── glossary.md
├── outputs/
│   ├── evaluation/
│   ├── forecast/
│   ├── figures/
│   ├── models/
│   └── reports/
│       ├── model_comparison_report_YYYYMMDD.md
│       ├── linear_regression_report_YYYYMMDD.md
│       ├── lightgbm_report_YYYYMMDD.md
│       ├── prophet_report_YYYYMMDD.md
│       └── sarimax_report_YYYYMMDD.md
├── src/
│   └── sales_forecast/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── config.py
│       ├── data.py
│       ├── validation.py
│       ├── features.py
│       ├── metrics.py
│       ├── evaluate.py
│       ├── forecast.py
│       ├── pipeline.py
│       ├── report.py
│       ├── train.py
│       └── models/
│           ├── __init__.py
│           ├── base.py
│           ├── registry.py
│           ├── baseline.py
│           └── linear_regression.py
└── tests/
    ├── test_data.py
    ├── test_validation.py
    ├── test_features.py
    ├── test_metrics.py
    ├── test_baseline.py
    └── test_cli.py
```

## ディレクトリ詳細

### `src/sales_forecast/`

**役割**: production codeを配置するPythonパッケージ。

**配置ファイル**:
- `cli.py`: CLIコマンド定義
- `config.py`: YAML設定の読み込みと検証
- `data.py`: CSV読み込み、カラム標準化、型変換
- `validation.py`: データ検証
- `features.py`: 特徴量生成
- `metrics.py`: 評価指標
- `evaluate.py`: 評価フロー
- `forecast.py`: 将来予測フロー
- `report.py`: レポート生成

**命名規則**:
- Pythonファイルは `snake_case.py`。
- クラスは `PascalCase`。
- 関数・変数は `snake_case`。

**依存関係**:
- 依存可能: 標準ライブラリ、外部ライブラリ、同一パッケージ内の下位責務。
- 依存禁止: `tests/`、`notebooks/`、ユーザー固有のローカルファイル。

### `src/sales_forecast/models/`

**役割**: 予測モデルの実装を配置する。

**配置ファイル**:
- `base.py`: `BaseForecastModel` またはProtocol定義
- `registry.py`: 設定ファイルのモデル名からモデルクラスを解決
- `baseline.py`: Naive、Seasonal Naive、Moving Average
- `linear_regression.py`: Linear Regression

**ルール**:
- 各モデルは `fit(train_data)` と `predict(future_data)` を実装する。
- 評価指標はモデル内で計算しない。
- 新規モデル追加時はテストと設定例を追加する。
- optional dependencyが必要なモデルは、import時ではなくモデル解決または初期化時に分かりやすいエラーを返す。

### `configs/`

**役割**: 実行条件を管理する。

**配置ファイル**:
- `base.yaml`: 標準設定
- 必要に応じて `local.yaml`、`experiment-*.yaml`

**ルール**:
- 機密情報を含めない。
- パス、カラム名、モデル、評価指標、出力先を設定する。

### `data/`

**役割**: サンプルデータとデータ説明を配置する。

**ルール**:
- コミット対象は公開可能なサンプルデータのみ。
- 実データやprivate dataは `.gitignore` で除外する。
- データ仕様や利用方針はREADMEまたは専用ドキュメントに記載する。

### `outputs/`

**役割**: CLI実行で生成される成果物や中間成果物を配置する。

**ルール**:
- 評価結果、予測結果、図、モデルartifact、レポートを分けて保存する。
- 大きいartifactや再生成可能な成果物は原則コミットしない。
- 学習済みモデルは `outputs/models/` に保存し、production code用の `src/sales_forecast/models/` と混同しない。

### `outputs/reports/`

**役割**: 閲覧用レポートを配置する。

**ルール**:
- 日付付きMarkdownレポートをCLIから再生成できる代表成果物として管理する。
- 自動生成レポートの上書き方針はREADMEに記載する。

### `tests/`

**役割**: pytestのテストコードを配置する。

**命名規則**:
- `test_*.py`。
- テスト関数は `test_` で始める。

**対象**:
- データ読み込み
- データ検証
- 特徴量生成
- 評価指標
- Baseline Model
- CLI基本動作

### `docs/`

**役割**: 永続ドキュメントおよび探索的分析ファイルを配置する。

**配置ドキュメント/ディレクトリ**:
- `product-requirements.md`: プロダクト要求定義書
- `functional-design.md`: 機能設計書
- `architecture.md`: アーキテクチャ設計書
- `repository-structure.md`: リポジトリ構造定義書
- `development-guidelines.md`: 開発ガイドライン
- `glossary.md`: 用語集
- `notebooks/`: 探索的分析と試行錯誤の Jupyter Notebook を配置する。
  - `docs/notebooks/archive/legacy-model-experiments/`: 移行前の探索・検証Notebookを履歴資産として保持する。
    - `linear-regression/`
    - `light-gbm/`
    - `prophet/`
    - `sarimax/`
  - 新規Notebookは原則 `docs/notebooks/` 配下に追加し、再利用するロジックは `src/` に移植する。旧Notebookはルートや他のパスに戻さない。
  - `.ipynb_checkpoints/` と `.DS_Store` はコミット対象外にする。

## ファイル配置規則

| ファイル種別 | 配置先 | 命名規則 | 例 |
|--------------|--------|----------|-----|
| CLI | `src/sales_forecast/` | `snake_case.py` | `cli.py` |
| モデル | `src/sales_forecast/models/` | `snake_case.py` | `baseline.py` |
| テスト | `tests/` | `test_*.py` | `test_metrics.py` |
| 設定 | `configs/` | `kebab-case.yaml` または `snake_case.yaml` | `base.yaml` |
| レポート | `outputs/reports/` | `snake_case_YYYYMMDD.md` | `model_comparison_report_20260704.md` |

## 依存関係のルール

```text
cli.py
  -> config.py
  -> application modules
      -> data.py / validation.py / features.py / metrics.py / models
      -> infrastructure output modules
```

**禁止される依存**:
- `src/sales_forecast/models/` から `cli.py` への依存。
- `metrics.py` から個別モデル実装への依存。
- `src/` から `tests/` や `docs/notebooks/` への依存。
- production codeにローカル絶対パスをハードコードすること。

## スケーリング戦略

- 小規模な機能追加は既存モジュールに追加する。
- 1ファイルが300行を超えたら責務分割を検討する。
- 500行を超える場合は分割を強く推奨する。
- 新規モデルは `src/sales_forecast/models/` に1ファイル1モデルで追加する。
- 共通処理は曖昧な `utils.py` に集約せず、責務名が分かるモジュールに置く。
