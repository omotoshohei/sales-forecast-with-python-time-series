# 開発ガイドライン (Development Guidelines)

## 基本方針

- Notebookは探索用、production codeは `src/sales_forecast/` 配下に置く。
- CLIで再現できない処理は、ポートフォリオ成果物として不十分とみなす。
- モデル精度だけでなく、Baseline比、再現性、説明可能性、データリーク防止を重視する。
- 機密データは扱わず、サンプルデータまたはダミーデータのみをコミットする。

## Pythonコーディング規約

### 型ヒント

- 公開関数、モデルクラス、設定読み込み、評価指標には型ヒントを付ける。
- pandas DataFrameを扱う関数は、docstringで期待カラムを明記する。

```python
def calculate_wape(actual: pd.Series, predicted: pd.Series) -> float:
    """WAPEを計算する。

    Args:
        actual: 実績値。合計が0の場合は計算不可。
        predicted: 予測値。actualと同じindexを持つ。
    """
    ...
```

### 命名規則

| 対象 | 規則 | 例 |
|------|------|-----|
| 変数・関数 | `snake_case` | `build_features` |
| クラス | `PascalCase` | `BaselineForecastModel` |
| 定数 | `UPPER_SNAKE_CASE` | `DEFAULT_HORIZON` |
| Boolean | `is_` / `has_` / `should_` | `is_valid_record` |
| ファイル | `snake_case.py` | `linear_regression.py` |

### 関数設計

- 関数は単一責務にする。
- 目標20行以内、50行を超える場合は分割を検討する。
- データ読み込み、検証、特徴量生成、評価、レポート生成を混在させない。

### コメント

- コメントは「なぜ」を説明するために使う。
- 複雑な時系列分割、データリーク防止、指標計算には短い補足コメントを付ける。
- コードを読めば分かる処理の説明コメントは避ける。

## モデル実装ルール

### 共通インターフェース

すべてのモデルは以下を満たす。

```python
class BaseForecastModel:
    def fit(self, train_data: pd.DataFrame) -> None:
        raise NotImplementedError

    def predict(self, future_data: pd.DataFrame) -> pd.Series:
        raise NotImplementedError
```

### 新規モデル追加手順

1. `src/sales_forecast/models/{model_name}.py` を追加する。
2. `BaseForecastModel` を継承またはProtocolに準拠する。
3. `fit()` と `predict()` を実装する。
4. `src/sales_forecast/models/registry.py` のModel Registryに登録する。
5. `configs/base.yaml` に設定例を追加する。
6. `tests/` にモデル単体テストを追加する。
7. READMEまたはdocsにモデル説明を追加する。

### 禁止事項

- モデルクラス内でRMSEなどの評価指標を計算しない。
- モデルクラスからCLI出力やレポート生成を呼び出さない。
- 未来の売上値を特徴量生成に混入させない。
- 学習済みモデルの保存先は `outputs/models/` に統一する。

## 評価指標実装ルール

- MAPEは `actual = 0` の行を除外し、除外件数を返すかログに残す。
- sMAPEは分母が0の行を除外する。
- WAPEは実績合計が0の場合に `NaN` を返す。
- Baseline比改善率はBaseline指標が0または欠損の場合に `NaN` を返す。
- 指標関数は入力Seriesの長さとindex一致を検証する。

## データ処理ルール

- 入力CSVは必ずバリデーションを通す。
- `Actual` と `Forecast` を明確に分ける。
- `Forecast` 行の `Sales` 欠損は許容する。
- `Actual` 行の `Sales` 欠損はエラーにする。
- 日付は内部では `week_start_date` に標準化する。
- カンマ区切りの数値文字列は読み込み時に数値化する。
- ラグ特徴量と移動平均は、予測対象週より過去の情報だけで作る。
- walk-forward validationでは、foldごとに学習・特徴量生成・予測の境界を明確にする。

## 依存関係管理

- 依存関係は `pyproject.toml` を主に使う。
- lock fileを採用する場合は、`uv.lock` など1方式に統一する。
- LightGBM、Prophet、statsmodelsのような重い依存はoptional dependency化を検討する。
- optional dependencyがない場合は、対象モデルだけを利用不可にし、CLI全体を壊さない。

## エラーハンドリング

- 予期される入力不備は専用例外または明確な `ValueError` で扱う。
- エラーメッセージには、対象カラム、行番号、値、対処の方向性を含める。
- 予期しない例外を握りつぶさない。

```python
raise ValueError(
    "Column 'Sales' contains non-numeric value at row 12: 'abc'"
)
```

## テスト戦略

### テスト対象

- `data.py`: CSV読み込み、カラム標準化、数値変換
- `validation.py`: 必須カラム、欠損、重複週、欠落週、`Record_Type`
- `features.py`: ラグ、移動平均、カレンダー特徴量
- `metrics.py`: RMSE、MAE、MAPE、sMAPE、WAPE、Bias
- `models/baseline.py`: Naive、Seasonal Naive、Moving Average
- `cli.py`: 主要コマンドの基本動作

### テストデータ

- テストでは小さなDataFrameを直接作るか、`tests/fixtures/` に最小CSVを置く。
- 機密データや実企業データをテストに使わない。
- ランダムデータを使う場合はseedを固定する。

### 実行コマンド

```bash
pytest
```

## Git運用ルール

### ブランチ

- `main`: 安定版
- `feature/{topic}`: 新機能
- `fix/{topic}`: バグ修正
- `docs/{topic}`: ドキュメント更新

### コミットメッセージ

Conventional Commitsを推奨する。

```text
feat(model): add baseline forecast model
fix(validation): reject missing sales in actual rows
docs(prd): add sales forecasting requirements
test(metrics): add wape edge cases
```

## PR / レビュー基準

PR前に確認すること。

- [ ] `pytest` が通る。
- [ ] CLI実行例がREADMEまたはdocsと矛盾していない。
- [ ] 新規モデルにはテストと設定例がある。
- [ ] データリークの可能性がない。
- [ ] 評価指標のゼロ除算・欠損ケースをテストしている。
- [ ] 機密データ、APIキー、private pathを含まない。
- [ ] 生成物をコミットする場合、再生成方法が説明されている。

## AIエージェント利用ルール

- 変更前に `docs/product-requirements.md`、`docs/functional-design.md`、`docs/architecture.md` を確認する。
- 新規機能は既存の責務分離に合わせる。
- Notebookではなく `src/` と `tests/` を主な編集対象にする。
- 大きなリファクタリングと機能追加を同時に行わない。
- 既存のユーザー変更を勝手に戻さない。

## データプライバシー

- 実在企業の売上、広告、顧客データをコミットしない。
- `.gitignore` にprivate data、raw data、local config、model artifactを必要に応じて追加する。
- READMEにサンプルデータの性質を明記する。
