# 技術仕様書 (Architecture Design Document)

## テクノロジースタック

### 言語・ランタイム

| 技術 | バージョン方針 | 用途 |
|------|----------------|------|
| Python | 3.10+ | パイプライン本体、CLI、モデル実装 |
| pip / uv | プロジェクト方針に合わせて固定 | 依存関係管理 |

### ライブラリ

| 技術 | 用途 | 選定理由 |
|------|------|----------|
| pandas | CSV読み込み、前処理、時系列処理 | 表形式データ処理の標準 |
| numpy | 数値計算 | 評価指標や特徴量生成で利用 |
| scikit-learn | Linear Regression、評価補助 | 安定したML APIと前処理機能 |
| LightGBM | 勾配ブースティングモデル | 非線形な広告効果を扱いやすい |
| Prophet | トレンド・季節性モデル | 説明しやすい時系列モデル |
| statsmodels | SARIMAX | 統計的時系列モデルを実装できる |
| matplotlib / plotly | グラフ生成 | 静的画像とHTML向け表現の両方に対応 |
| PyYAML | 設定ファイル | YAML設定を扱う |
| pytest | テスト | Pythonテストの標準 |

## アーキテクチャパターン

### レイヤードアーキテクチャ

```text
┌──────────────────────────────┐
│ CLIレイヤー                   │ ユーザー入力、引数解析、表示
├──────────────────────────────┤
│ アプリケーションレイヤー       │ train/evaluate/forecast/reportの処理調整
├──────────────────────────────┤
│ ドメインレイヤー               │ モデル、特徴量、評価指標、検証ロジック
├──────────────────────────────┤
│ インフラレイヤー               │ CSV/YAML/model/reportの入出力
└──────────────────────────────┘
```

### 依存方向

```text
CLI -> Application -> Domain
CLI -> Application -> Infrastructure
```

**ルール**:
- CLIはデータ処理やモデル評価の詳細を直接実装しない。
- モデルクラスはCLIやレポート生成に依存しない。
- 評価指標はモデルクラス外で計算する。
- ファイルパス、カラム名、モデル名は設定から注入する。
- DomainはファイルシステムやCLIに依存しない。CSV/YAML/model artifactの入出力はApplicationからInfrastructureを呼び出して行う。

## 主要コンポーネント

| コンポーネント | 配置先 | 責務 |
|----------------|--------|------|
| CLI | `src/sales_forecast/cli.py` | コマンド受付 |
| Config | `src/sales_forecast/config.py` | YAML読み込みと検証 |
| Data | `src/sales_forecast/data.py` | CSV読み込みと標準化 |
| Validation | `src/sales_forecast/validation.py` | 入力データ検証 |
| Features | `src/sales_forecast/features.py` | 特徴量生成 |
| Metrics | `src/sales_forecast/metrics.py` | 評価指標 |
| Evaluate | `src/sales_forecast/evaluate.py` | モデル比較と検証 |
| Forecast | `src/sales_forecast/forecast.py` | 将来予測 |
| Report | `src/sales_forecast/report.py` | レポート生成 |
| Models | `src/sales_forecast/models/` | モデル実装 |
| Model Registry | `src/sales_forecast/models/registry.py` | モデル名から実装クラスを解決 |

## データ永続化戦略

| データ種別 | ストレージ | フォーマット | 理由 |
|-----------|------------|--------------|------|
| 入力データ | `data/` | CSV | 利用者が編集しやすい |
| 設定 | `configs/` | YAML | 実行条件をコードから分離できる |
| 学習済みモデル | `outputs/models/` | pickle/joblib | Pythonモデルを保存しやすく、生成物として分離できる |
| 評価結果 | `outputs/evaluation/` | CSV/JSON | レポートや再確認に使いやすい |
| 予測結果 | `outputs/forecast/` | CSV | ビジネス利用・共有しやすい |
| レポート | `reports/` | HTML/Markdown | ポートフォリオで閲覧しやすい |

## 設定設計

`configs/base.yaml` は以下を管理する。

```yaml
data:
  path: data/sales_data.csv
  date_column: Date
  target_column: Sales
  record_type_column: Record_Type
  actual_value: Actual
  forecast_value: Forecast
  external_features:
    - TVCM_GPR
    - Print_Media
    - Offline_Ads
    - Digital_Ads

split:
  train_start: null
  train_end: null
  validation_start: null
  validation_end: null
  test_start: null
  test_end: null

models:
  enabled:
    - baseline
    - linear_regression
  parameters: {}

evaluation:
  metrics:
    - rmse
    - mae
    - mape
    - smape
    - wape
    - bias

output:
  models_dir: outputs/models
  evaluation_dir: outputs/evaluation
  forecast_dir: outputs/forecast
  figures_dir: outputs/figures
  report_path: reports/model_comparison_report.md
```

## パフォーマンス要件

| 操作 | 目標時間 | 測定環境 |
|------|----------|----------|
| データ検証 | 10,000行で10秒以内 | 一般的な開発PC |
| 特徴量生成 | 10,000行で30秒以内 | 一般的な開発PC |
| Baseline評価 | 10,000行で10秒以内 | 一般的な開発PC |
| HTMLレポート生成 | 30秒以内 | 既存の評価・予測結果を利用 |

## セキュリティアーキテクチャ

### データ保護
- 実在企業の機密データは利用しない。
- `data/private/`、`raw/`、認証情報、APIキーはコミット対象外にする。
- サンプルデータはダミーデータまたは公開可能なデータに限定する。

### 入力検証
- CSVパスは設定ファイルから読み込み、存在確認を行う。
- カラム名、日付、数値、`Record_Type` を検証する。
- エラーメッセージには原因を含めるが、ローカル環境の不要な機密情報は出さない。

## スケーラビリティ設計

### データ増加への対応
- 初期想定は週次データのため数百から数万行規模。
- pandasで処理できる範囲を前提とし、大規模分散処理は初期スコープ外。
- 特徴量生成は日付順ソート後にベクトル化処理を優先する。

### 機能拡張性
- 新規モデルは `src/sales_forecast/models/` に追加し、Model Registryに登録する。
- 新規評価指標は `metrics.py` に追加し、設定ファイルから選択可能にする。
- 将来的なAPI化・Streamlit化に備え、CLIとコアロジックを分離する。
- optional dependencyが未インストールのモデルは、CLI上で利用不可理由を明示し、他モデルの実行を妨げない。

## テスト戦略

### ユニットテスト
- フレームワーク: pytest
- 対象: data、validation、features、metrics、models/baseline
- 目標: ドメインロジックの主要分岐をカバーする

### 統合テスト
- サンプルCSVと設定ファイルでCLIの主要コマンドを実行する。
- 出力CSV、JSON、HTMLの存在と最低限の内容を検証する。

### E2Eテスト
- `validate-data`、`train`、`evaluate`、`forecast`、`report` を順番に実行する。
- レポート生成まで破綻しないことを確認する。

## 技術的制約

- 初期スコープでは本番デプロイ、API、DB連携、自動再学習は扱わない。
- Prophet、LightGBM、statsmodelsは環境差でインストール負荷があるため、Phase 2ではBaselineとLinear Regressionを優先できる設計にする。
- `Forecast` 行に外部要因がない場合、外部要因を使うモデルの将来予測は実行不可とする。

## 依存関係管理

- `pyproject.toml` を基本とし、必要に応じて `requirements.txt` を併用する。
- lock fileを採用する場合は `uv.lock` など単一の方式に寄せる。
- 破壊的変更が多いライブラリは上限バージョンを設定する。
- optional dependencyとして重いモデル依存を分離できる構成を検討する。
