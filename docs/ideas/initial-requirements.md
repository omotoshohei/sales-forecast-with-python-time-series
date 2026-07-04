# 要件定義書

## Retail Sales Forecasting Pipeline

## 1. プロジェクト概要

本プロジェクトは、小売・マーケティング領域における週次売上予測を目的とした、再利用可能なPythonベースの予測パイプラインである。

過去の売上データに加えて、デジタル広告、オフライン広告、TVCM、印刷媒体などの外部要因を組み込み、複数の統計モデル・機械学習モデルを比較する。

本プロジェクトは、単なるJupyter Notebookによる学習記録ではなく、実務で再利用可能な売上予測テンプレートとして設計する。CLI実行、設定ファイル管理、モデル評価、レポート生成、テスト、AIコーディングエージェントによる拡張を想定した構成を目指す。

---

## 2. 背景と目的

### 2.1 背景

現在のプロジェクトでは、週次売上データを用いて、Linear Regression、Prophet、LightGBM、SARIMAXなど複数の予測モデルを検証している。

一方で、現状はモデルごとのJupyter Notebookが中心であり、ポートフォリオとして見た場合、学習ログとしての印象が強い。今後は、実務で使える予測パイプラインとして再構成し、マーケティング領域の売上予測に活用できる形へ発展させる。

### 2.2 目的

本プロジェクトの目的は以下の通り。

1. 小売・マーケティング領域における売上予測パイプラインを構築する。
2. 複数の予測モデルを同一条件で比較・評価できるようにする。
3. CLIでデータ検証、学習、評価、予測、レポート生成を再現可能にする。
4. ポートフォリオとして、Python、時系列予測、機械学習、マーケティング分析、MLOps的な設計力を示す。
5. Codex、Antigravity、CursorなどのAIコーディングエージェントが拡張しやすい構造にする。

---

## 3. 想定ユーザー

### 3.1 主な利用者

* デジタルマーケティング担当者
* SEO / Paid Media / CRMなどのマーケティング分析担当者
* 小売企業の販売計画担当者
* データアナリスト
* Pythonで売上予測を学びたい人
* AIコーディングエージェントを使って予測モデルを拡張したい開発者

### 3.2 ポートフォリオ上の閲覧者

* 採用担当者
* データ分析・マーケティング領域の面接官
* Python / ML / Analytics Engineeringのスキルを確認したい人
* AI活用開発の実践例を確認したい人

---

## 4. スコープ

### 4.1 対象範囲

本プロジェクトで対象とする範囲は以下の通り。

* 週次売上データと外部要因データを含むCSVの読み込み
* データバリデーション
* 前処理
* 特徴量エンジニアリング
* 複数モデルの学習
* 時系列に配慮した検証
* モデル評価
* 将来売上予測
* HTMLまたはMarkdown形式のレポート生成
* CLI実行
* テスト
* AIエージェント向けの開発ルール整備

### 4.2 対象外

以下は初期スコープでは対象外とする。

* 本番環境への自動デプロイ
* リアルタイム予測API
* データベース連携
* ダッシュボードアプリの本格開発
* 機密性の高い実データの利用
* 本番データを使った自動モデル再学習のスケジューリング
* 大規模MLOps基盤の構築

ただし、将来的な拡張余地として、API化、Streamlitダッシュボード化などは検討可能とする。

---

## 5. 成果物

本プロジェクトの成果物は以下とする。

1. 再利用可能なPythonパッケージ構成
2. CLIコマンド
3. サンプルデータ
4. データ仕様書
5. モデル比較結果
6. 予測結果
7. 自動生成レポート
8. README
9. 要件定義書
10. 開発者向けドキュメント
11. AIエージェント向け `AGENTS.md`
12. 単体テスト

---

## 6. 機能要件

### 6.1 データ読み込み機能

#### 概要

CSV形式の週次データを読み込む。1行を1週として扱い、日付、売上、外部要因、実績/予測区分を同一ファイルで管理する。

#### 要件

* CSVファイルを読み込めること。
* 日付列を週次単位として扱えること。
* 実績期間は売上と外部要因を読み込めること。
* 将来予測期間は売上が空欄で、外部要因のみが入力された行を読み込めること。
* 欠損値を検出できること。
* カンマ区切りの数値文字列を数値型へ変換できること。
* 必須カラムが存在しない場合はエラーを出すこと。
* サンプルデータで動作確認できること。

#### 想定入力

* `data/sales_data.csv`

#### 必須カラム

* `Date`
* `Sales`
* `Record_Type`

#### 外部要因カラム

以下の列を外部要因として扱う。

* `TVCM_GPR`
* `Print_Media`
* `Offline_Ads`
* `Digital_Ads`

#### 内部標準カラム

読み込み後は、必要に応じて以下の標準カラム名へ変換する。

* `Date` -> `week_start_date`
* `Sales` -> `sales`
* `TVCM_GPR` -> `tvcm_gpr`
* `Print_Media` -> `print_media`
* `Offline_Ads` -> `offline_ads`
* `Digital_Ads` -> `digital_ads`
* `Record_Type` -> `record_type`

---

### 6.2 データバリデーション機能

#### 概要

入力データが予測モデルに利用可能な形式になっているかを検証する。

#### 要件

* 日付列が正しい日付形式であることを確認する。
* 売上列が数値に変換可能であることを確認する。
* 必須カラムの欠損を検出する。
* 重複した週がないことを確認する。
* 週次データに欠落週がないか確認する。
* `Record_Type` が `Actual` または `Forecast` のいずれかであることを確認する。
* `Actual` 行では `Sales` が存在することを確認する。
* `Forecast` 行では `Sales` の欠損を許容し、外部要因が予測期間分存在するか確認する。
* 検証結果をCLI上に表示できること。

#### CLI例

```bash
python -m sales_forecast validate-data --config configs/base.yaml
```

---

### 6.3 前処理機能

#### 概要

モデル学習に必要なデータ整形を行う。

#### 要件

* 日付順にデータを並び替える。
* 欠損値を処理する。
* 数値列を適切な型に変換する。
* カテゴリ変数を扱えるようにする。
* モデル別に必要なデータ形式へ変換する。
* 学習期間、検証期間、テスト期間に分割する。

---

### 6.4 特徴量エンジニアリング機能

#### 概要

時系列予測およびマーケティング要因の分析に必要な特徴量を作成する。

#### 要件

以下の特徴量を生成できること。

* ラグ特徴量

  * 前週売上
  * 4週前売上
  * 12週前売上
  * 52週前売上
* 移動平均

  * 4週移動平均
  * 8週移動平均
  * 12週移動平均
* カレンダー特徴量

  * 年
  * 月
  * 週番号
  * 四半期
  * 年末年始フラグ
* マーケティング特徴量

  * デジタル広告費
  * オフライン広告費
  * TVCM GPR
  * 印刷媒体費
* 季節性特徴量

  * 月次季節性
  * 年次季節性
* 任意の外部変数

---

### 6.5 モデル学習機能

#### 概要

複数の予測モデルを同一のインターフェースで学習できるようにする。

#### 対象モデル

初期実装では以下を対象とする。

1. Baseline Model
2. Linear Regression
3. LightGBM
4. Prophet
5. SARIMAX

#### 要件

* 各モデルは共通インターフェースを持つこと。
* モデルごとに学習処理を分離すること。
* 設定ファイルから利用モデルを選択できること。
* 学習済みモデルを保存できること。
* モデルごとのパラメータを設定ファイルで管理できること。

#### 共通インターフェース

各モデルは少なくとも以下のメソッドを持つこと。評価指標の計算はモデルクラスではなく、共通の評価機能で実行する。

```python
fit(train_data)
predict(future_data)
```

---

### 6.6 Baseline Model

#### 概要

高度なモデルとの比較対象として、シンプルなベースラインモデルを実装する。

#### 要件

以下のベースラインを実装する。

* 前週売上をそのまま予測値とするNaive Forecast
* 前年同週売上を予測値とするSeasonal Naive Forecast
* 過去4週平均を予測値とするMoving Average Forecast

#### 目的

高度なモデルが本当に価値を出しているかを検証するための比較基準とする。

---

### 6.7 モデル評価機能

#### 概要

予測精度を複数の指標で評価する。

#### 評価指標

以下の指標を実装する。

* RMSE
* MAE
* MAPE
* sMAPE
* WAPE
* Bias
* Baseline比改善率

#### 要件

* モデル別の評価結果を表形式で出力する。
* 評価結果をCSVまたはJSONで保存できる。
* 実績値と予測値のグラフを生成できる。
* 誤差の大きい週を特定できる。
* Baseline Modelとの差分を表示できる。

---

### 6.8 時系列検証機能

#### 概要

通常のランダム分割ではなく、時系列データに適した検証を行う。

#### 要件

* train / validation / testを時系列順に分割する。
* walk-forward validationを実装する。
* 複数期間での平均スコアを算出する。
* 各検証期間ごとのスコアを保存する。
* データリークを避ける設計にする。

---

### 6.9 将来予測機能

#### 概要

学習済みモデルを使って、将来の週次売上を予測する。

#### 要件

* 予測期間を指定できること。
* デフォルトの予測期間は12週間とする。
* `Record_Type=Forecast` の行を将来予測用の外部要因として利用できること。
* 予測結果をCSVで出力できること。
* 実績値と将来予測を連続したグラフで表示できること。

#### CLI例

```bash
python -m sales_forecast forecast --horizon 12
```

---

### 6.10 レポート生成機能

#### 概要

分析結果をHTMLまたはMarkdown形式で自動生成する。

#### 要件

レポートには以下を含める。

1. プロジェクト概要
2. 使用データの概要
3. モデル別評価結果
4. 実績値と予測値の比較グラフ
5. 誤差分析
6. 特徴量重要度
7. 将来12週間の売上予測
8. ビジネス上の示唆
9. 今後の改善案

#### CLI例

```bash
python -m sales_forecast report --output reports/sample_report.html
```

---

### 6.11 CLI機能

#### 概要

主要処理をコマンドラインから実行できるようにする。

#### 必須コマンド

```bash
python -m sales_forecast validate-data
python -m sales_forecast train
python -m sales_forecast evaluate
python -m sales_forecast forecast
python -m sales_forecast report
```

#### 要件

* `--config` で設定ファイルを指定できること。
* `--model` でモデルを指定できること。
* `--horizon` で予測期間を指定できること。
* `--output` で出力先を指定できること。
* エラー時に原因が分かるメッセージを表示すること。

---

### 6.12 設定ファイル管理

#### 概要

モデルやデータパス、評価条件をYAMLファイルで管理する。

#### 想定ファイル

```text
configs/base.yaml
```

#### 設定項目

* データパス
* 日付列
* 目的変数
* レコード種別列
* 実績データを示す値
* 将来予測データを示す値
* 外部変数
* 学習期間
* 検証期間
* テスト期間
* 利用モデル
* モデルパラメータ
* 評価指標
* レポート出力先

---

### 6.13 AIエージェント向け開発ルール

#### 概要

Codex、Antigravity、CursorなどのAIコーディングエージェントが安全にプロジェクトを拡張できるようにする。

#### 要件

* `AGENTS.md` を作成する。
* プロジェクト構造を明記する。
* Notebookは探索用、production codeは `src/` 配下に置くルールを定義する。
* 新規モデル追加時のルールを定義する。
* テスト追加ルールを定義する。
* 機密データをコミットしないルールを明記する。
* サンプルデータのみ利用する方針を明記する。

#### `AGENTS.md` に含める内容

* Project overview
* Directory structure
* Development rules
* Model interface
* Testing rules
* Data privacy rules
* How to add a new forecasting model
* How to update reports

---

### 6.14 テスト機能

#### 概要

主要処理に対して単体テストを実装する。

#### 対象

* データ読み込み
* データバリデーション
* 特徴量生成
* 評価指標
* ベースラインモデル
* CLIの基本動作

#### 要件

* `pytest` で実行できること。
* サンプルデータでテストが通ること。

#### CLI例

```bash
pytest
```

---

## 7. 非機能要件

### 7.1 再現性

* サンプルデータを使って誰でも同じ結果を再現できること。
* 実行手順をREADMEに明記すること。
* 依存ライブラリを `pyproject.toml` または `requirements.txt` で管理すること。

### 7.2 保守性

* モデルごとの処理を分離すること。
* 共通処理を重複させないこと。
* 関数とクラスに適切な責務を持たせること。
* Notebookに依存しすぎない構成にすること。

### 7.3 拡張性

* 新しいモデルを追加しやすい構成にすること。
* 新しい評価指標を追加しやすい構成にすること。
* 新しい外部変数を追加しやすい構成にすること。
* 将来的にStreamlitやAPI化へ拡張できる余地を残すこと。

### 7.4 可読性

* Pythonコードは型ヒントを可能な範囲で付与する。
* 関数名・変数名は意味が分かる名前にする。
* READMEでプロジェクトの価値がすぐ伝わるようにする。
* ポートフォリオ閲覧者が短時間で理解できる構成にする。

### 7.5 データプライバシー

* 実在企業の機密データは使用しない。
* サンプルデータはダミーデータまたは公開可能なデータとする。
* READMEにデータの扱いを明記する。
* `.gitignore` でraw dataやprivate dataを除外する。

---

## 8. 推奨ディレクトリ構成

```text
sales-forecast-with-python-time-series/
├── README.md
├── pyproject.toml
├── AGENTS.md
├── .gitignore
├── configs/
│   └── base.yaml
├── data/
│   ├── sales_data.csv
│   └── README.md
├── docs/
│   ├── requirements.md
│   ├── model_design.md
│   ├── data_schema.md
│   └── notebooks/
│       └── 01_exploratory_analysis.ipynb
├── outputs/
│   └── reports/
│       └── sample_report.html
├── src/
│   └── sales_forecast/
│       ├── __init__.py
│       ├── cli.py
│       ├── config.py
│       ├── data.py
│       ├── validation.py
│       ├── features.py
│       ├── metrics.py
│       ├── evaluate.py
│       ├── forecast.py
│       ├── report.py
│       └── models/
│           ├── __init__.py
│           ├── base.py
│           ├── baseline.py
│           ├── linear_regression.py
│           ├── lightgbm_model.py
│           ├── prophet_model.py
│           └── sarimax_model.py
└── tests/
    ├── test_data.py
    ├── test_validation.py
    ├── test_features.py
    ├── test_metrics.py
    └── test_baseline.py
```

---

## 9. 主要CLI仕様

### 9.1 データ検証

```bash
python -m sales_forecast validate-data --config configs/base.yaml
```

#### 処理内容

* データファイルの存在確認
* 必須カラム確認
* 欠損値確認
* 日付形式確認
* 週次データの連続性確認
* `Actual` / `Forecast` 区分と将来行の外部要因確認

---

### 9.2 モデル学習

```bash
python -m sales_forecast train --config configs/base.yaml --model lightgbm
```

#### 処理内容

* データ読み込み
* 前処理
* 特徴量生成
* train / validation / test分割
* 指定モデルの学習
* 学習済みモデルの保存

---

### 9.3 モデル評価

```bash
python -m sales_forecast evaluate --config configs/base.yaml
```

#### 処理内容

* 複数モデルの評価
* 評価指標の計算
* 比較表の生成
* 予測グラフの生成
* 評価結果の保存

---

### 9.4 将来予測

```bash
python -m sales_forecast forecast --config configs/base.yaml --model lightgbm --horizon 12
```

#### 処理内容

* 学習済みモデルの読み込み
* `Record_Type=Forecast` 行の外部要因読み込み
* 12週間先までの売上予測
* 結果CSVの出力
* グラフ生成

---

### 9.5 レポート生成

```bash
python -m sales_forecast report --config configs/base.yaml --output reports/sample_report.html
```

#### 処理内容

* 評価結果の読み込み
* 予測結果の読み込み
* HTMLレポートの生成

---

## 10. モデル設計

### 10.1 Base Model Interface

すべてのモデルは、共通の抽象クラスを継承する。

```python
class BaseForecastModel:
    def fit(self, train_data):
        raise NotImplementedError

    def predict(self, future_data):
        raise NotImplementedError
```

### 10.2 モデル追加ルール

新しいモデルを追加する場合は、以下を満たすこと。

* `src/sales_forecast/models/` 配下にファイルを追加する。
* `BaseForecastModel` を継承する。
* `fit()`、`predict()` を実装する。
* 設定ファイルから呼び出せるようにする。
* テストを追加する。
* READMEにモデル説明を追加する。

---

## 11. レポート要件

レポートはポートフォリオ上で閲覧しやすいことを重視する。

### 11.1 レポート構成

1. Executive Summary
2. Dataset Overview
3. Forecasting Approach
4. Model Comparison
5. Best Model Result
6. Error Analysis
7. Feature Importance
8. 12-week Forecast
9. Business Insights
10. Limitations
11. Next Steps

### 11.2 ビジネス示唆の例

* LightGBMは非線形な広告効果を捉えやすい。
* SARIMAXは季節性が安定している場合に有効。
* Prophetはトレンドや季節性の説明がしやすい。
* 広告施策の将来値がない場合、外部要因を使った予測は難しくなる。
* 広告出稿が大きく変動する週は売上予測の誤差が大きくなりやすい。
* Baselineを上回らないモデルは実務導入すべきではない。

---

## 12. README要件

READMEでは、以下の情報を分かりやすく記載する。

### 必須項目

* プロジェクト概要
* なぜ作ったか
* 解決する課題
* 主な機能
* 使用技術
* ディレクトリ構成
* セットアップ方法
* 実行方法
* サンプル出力
* モデル比較結果
* 今後の改善案
* データに関する注意事項

### READMEの冒頭文案

```text
This project is a reusable sales forecasting pipeline for retail and marketing planning. It compares statistical and machine learning models, evaluates forecast accuracy using time-series validation, and generates business-ready forecast reports.
```

---

## 13. 使用技術

### 言語

* Python

### 主要ライブラリ

* pandas
* numpy
* scikit-learn
* lightgbm
* prophet
* statsmodels
* matplotlib
* plotly
* pyyaml
* pytest

### 開発支援

* GitHub
* Codex
* Antigravity
* Cursor

---

## 14. 成功基準

本プロジェクトの成功基準は以下とする。

1. サンプルデータでCLIが正常に動作する。
2. 複数モデルの学習・評価が再現できる。
3. Baseline Modelとの比較ができる。
4. 将来12週間の売上予測が出力できる。
5. HTMLレポートが生成できる。
6. READMEを読むだけでプロジェクトの価値が伝わる。
7. テストが通る。
8. AIエージェントが新規モデルを追加しやすい構造になっている。
9. ポートフォリオとして、Python、機械学習、時系列分析、マーケティング分析、設計力を示せる。

---

## 15. 開発フェーズ

### Phase 1: プロジェクト再構成

#### 目的

Notebook中心の構成から、Pythonパッケージ構成へ変更する。

#### 作業内容

* `src/` 構成の作成
* `docs/notebooks/` へのNotebook移動
* `data/` の整理
* `configs/` の作成
* `docs/` の作成
* READMEの方向性修正

#### 完了条件

* プロジェクト構造が整理されている。
* 既存Notebookが保持されている。
* 今後の実装先が明確になっている。

---

### Phase 2: CLIとBaseline Modelの実装

#### 目的

最小構成で予測パイプラインを動かせるようにする。

#### 作業内容

* CLIの実装
* データ読み込み機能
* データバリデーション機能
* 特徴量生成機能
* Baseline Model実装
* 評価指標実装

#### 完了条件

* `validate-data` が実行できる。
* `train` が実行できる。
* `evaluate` が実行できる。
* Baseline Modelの評価結果が出力される。

---

### Phase 3: 複数モデル対応

#### 目的

既存のLinear Regression、LightGBM、Prophet、SARIMAXを共通インターフェースで実装する。

#### 作業内容

* Linear Regression実装
* LightGBM実装
* Prophet実装
* SARIMAX実装
* モデル設定管理
* モデル比較表の出力

#### 完了条件

* 複数モデルを同じCLIから実行できる。
* モデル比較結果がCSVで出力される。
* Baselineとの比較ができる。

---

### Phase 4: 将来予測

#### 目的

将来12週間の週次売上予測を実装する。

#### 作業内容

* 12週間予測機能
* `Record_Type=Forecast` 行の外部要因読み込み

#### 完了条件

* 将来予測がCSVで出力される。
* 実績値と将来予測を連続したグラフで確認できる。

---

### Phase 5: レポート生成とポートフォリオ化

#### 目的

GitHub上で見たときに、成果物として分かりやすい状態にする。

#### 作業内容

* HTMLレポート生成
* グラフ出力
* サンプルレポート作成
* README改善
* docs整備
* AGENTS.md作成

#### 完了条件

* `reports/sample_report.html` が生成される。
* READMEからプロジェクトの価値が伝わる。
* ポートフォリオページに掲載できる状態になっている。

---

## 16. リスクと対応策

### リスク1: 実データが使えない

#### 内容

実在企業の売上データや広告データは機密情報に該当する可能性がある。

#### 対応策

* ダミーデータを作成する。
* データ生成スクリプトを用意する。
* READMEにサンプルデータであることを明記する。

---

### リスク2: モデルが複雑になりすぎる

#### 内容

複数モデルを扱うことで、実装が複雑化する可能性がある。

#### 対応策

* 最初はBaselineとLightGBMを優先する。
* ProphetとSARIMAXはPhase 3以降に実装する。
* 共通インターフェースを先に定義する。

---

### リスク3: レポートが分析寄りになりすぎる

#### 内容

技術的な評価に偏ると、ビジネス価値が伝わりにくくなる。

#### 対応策

* Executive Summaryを入れる。
* ビジネス上の示唆を明記する。
* モデル精度だけでなく、意思決定への使い方を説明する。

---

### リスク4: AIエージェントでの改修が不安定になる

#### 内容

構造が曖昧だと、AIコーディングエージェントが意図しない場所を編集する可能性がある。

#### 対応策

* `AGENTS.md` を用意する。
* ディレクトリ構成を明確にする。
* Notebookとproduction codeの役割を分ける。
* テストを整備する。

---

## 17. 将来的な拡張案

初期スコープ完了後、以下の拡張を検討する。

1. Streamlitによる簡易ダッシュボード化
2. GitHub Pagesでレポート公開
3. FastAPIによる予測API化
4. Optunaによるハイパーパラメータチューニング
5. SHAPによる特徴量説明
6. 需要予測と在庫最適化への拡張
7. 複数店舗・複数カテゴリ対応
8. SEO traffic forecastへの応用

---

## 18. 完成時のポートフォリオ訴求ポイント

本プロジェクトでは、以下のスキルを示すことができる。

* Pythonによるデータ分析
* 時系列予測
* 機械学習モデル比較
* マーケティングデータの活用
* 売上予測
* CLI設計
* レポート自動生成
* テスト設計
* AIコーディングエージェントを前提とした開発設計
* Notebookから再利用可能なプロダクトへのリファクタリング

---

## 19. まとめ

本プロジェクトは、既存の売上予測学習ノートブックを、実務で再利用可能な売上予測パイプラインへ発展させることを目的とする。

単に複数のモデルを比較するだけでなく、外部要因を考慮した将来売上予測を行い、意思決定に活用できる形を目指す。

また、CLI、設定ファイル、テスト、レポート生成、AIエージェント向け開発ルールを整備することで、ポートフォリオとしての完成度を高める。

最終的には、Python、機械学習、マーケティング分析、時系列予測、AI活用開発を横断的に示せるプロジェクトとする。
