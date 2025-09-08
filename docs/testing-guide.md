# Cloud CoPassAgent テストガイド

Cloud CoPassAgent のテスト戦略と実装手順について説明します。

> **📍 テスト実装標準**: 汎用的なテスト実装ルールは [テスト設計標準](.kiro/steering/test-design-standards.md) を参照

## 🎯 プロジェクト固有のテスト戦略

### 基本方針

- **契約による設計**: [テスト設計標準](.kiro/steering/test-design-standards.md) に準拠
- **AgentCore 中心**: シンプル化されたアーキテクチャに対応したテスト構成
- **品質チェック自動化**: `./scripts/python-quality-check.sh` による継続的評価

### テスト構成

```
tests/
├── unit/                    # 単体テスト（メイン）
│   ├── agentcore/          # AgentCore関連テスト
│   ├── trigger/            # Lambda関数テスト
│   └── shared/             # 共通モジュールテスト
└── fixtures/               # テスト用データ・モック
```

## 🧪 単体テスト実装ガイド

### ディレクトリ構造とファイル命名

#### 1. ディレクトリ構造の原則

```bash
# アプリ本体の構造に対応
app/agentcore/agent_main.py     → tests/unit/agentcore/test_agent_main.py
app/agentcore/teams_client.py   → tests/unit/agentcore/test_teams_client.py
app/trigger/lambda_function.py → tests/unit/trigger/test_lambda_function.py
```

#### 2. ファイル命名規則

- **テストファイル**: `test_` + `元のファイル名`
- **テストクラス**: `Test` + `元のクラス名` または `Test` + `機能名`
- **テストメソッド**: `test_` + `機能名` + `_contract` (契約検証の場合)

#### 3. 必要な**init**.py ファイル

```bash
# 各テストディレクトリに__init__.pyを作成
touch tests/unit/trigger/__init__.py
```

### インポート方法の統一

#### 1. 基本的なインポート（推奨）

```python
# pyproject.tomlの設定に従った標準的なインポート
from app.agentcore.agent_main import AgentOutput, Question
from app.agentcore.teams_client import TeamsClient
from app.trigger.lambda_function import lambda_handler
```

#### 2. 予約語回避のインポート（不要になりました）

構造変更により、予約語問題が解決されたため、特殊なインポート処理は不要です：

```python
# 以前は必要だった動的インポート（現在は不要）
# import importlib
# lambda_module = importlib.import_module("app.lambda.trigger.lambda_function")
# lambda_handler = lambda_module.lambda_handler

# 現在はシンプルなインポートが可能
from app.trigger.lambda_function import lambda_handler
```

#### 3. pyproject.toml 設定（参考）

構造変更により予約語問題が解決されたため、特別な設定は不要ですが、
将来的に予約語を含むモジュールがある場合の参考として：

```toml
[[tool.mypy.overrides]]
module = [
    # 既存の設定...
    # 予約語回避（現在は不要）
    # "lambda_function",
]
ignore_missing_imports = true
```

### テストファイルのテンプレート

#### 1. ファイルヘッダー（必須）

```python
"""
[機能名] の単体テスト - 契約による設計（例外ベースアプローチ）

[機能の説明]の例外ベースアプローチに基づく契約検証テスト実装。

このテストモジュールは以下の契約を検証します：
- 事前条件: [具体的な事前条件]
- 事後条件: [具体的な事後条件]
- 不変条件: [具体的な不変条件]
"""
```

#### 2. インポートセクション（標準化）

```python
import json  # 必要に応じて
from typing import Any
from unittest.mock import Mock, patch

import pytest

# テスト対象のインポート - pyproject.tomlの設定に従った統一的なアプローチ
from app.module.target import target_function
```

#### 3. テストクラス構造

```python
class TestTargetFunction:
    """
    [対象機能]の契約検証（例外ベースアプローチ）

    [対象機能の説明]の動作を契約による設計の観点から検証する。
    """

    def test_successful_operation_contract(self) -> None:
        """
        契約による設計: 正常実行時の事後条件検証

        Given: [具体的な事前条件]
        When: [実行する操作]
        Then: [期待される結果]

        事前条件:
        - [具体的な事前条件1]
        - [具体的な事前条件2]

        事後条件:
        - [具体的な事後条件1]
        - [具体的な事後条件2]

        不変条件:
        - [具体的な不変条件1]
        - [具体的な不変条件2]
        """
        # Given - 事前条件設定: [具体的な説明]
        # [テストデータの準備]

        # When - [操作の実行]
        # [実際の処理実行]

        # Then - 事後条件検証: [具体的な説明]
        # [結果の検証]

        # 不変条件検証: [具体的な説明]
        # [不変条件の検証]
```

### 契約による設計の実装パターン

#### 1. 事前条件の検証

```python
def test_missing_required_parameter_precondition_violation(self) -> None:
    """
    契約による設計: 必須パラメータ不足時の事前条件違反検証

    Given: [必須パラメータが不足した状態]
    When: [関数を実行する]
    Then: [適切な例外が発生する]

    事前条件違反: [具体的な違反内容]
    事後条件: [例外発生時の期待される状態]
    不変条件: [例外発生時も維持される条件]
    """
    # Given - 事前条件違反: [具体的な説明]
    invalid_data = {
        # 意図的に必須パラメータを不足させる
    }

    # When & Then - 事前条件違反で例外が発生
    with pytest.raises(ValueError, match="具体的なエラーメッセージ"):
        target_function(invalid_data)
```

#### 2. 事後条件の検証

```python
def test_response_structure_postcondition(self) -> None:
    """
    契約による設計: レスポンス構造の事後条件検証

    Given: [有効な入力データ]
    When: [関数を実行する]
    Then: [期待される構造のレスポンスが返される]

    事前条件: [具体的な事前条件]
    事後条件: [具体的な事後条件]
    不変条件: [具体的な不変条件]
    """
    # Given - 事前条件設定: [具体的な説明]
    valid_input = {
        # 有効なテストデータ
    }

    # When - [操作の実行]
    result = target_function(valid_input)

    # Then - 事後条件検証: [具体的な説明]
    assert "expected_field" in result, "期待されるフィールドが含まれるべき"
    assert isinstance(result["expected_field"], expected_type), "期待される型であるべき"

    # 不変条件検証: [具体的な説明]
    assert len(result) > 0, "結果は空でないべき"
```

#### 3. 不変条件の検証

```python
def test_invariant_conditions_across_scenarios(self) -> None:
    """
    契約による設計: 複数シナリオでの不変条件検証

    Given: [様々なシナリオのテストケース]
    When: [各シナリオで関数を実行する]
    Then: [全てのケースで不変条件が維持される]

    不変条件:
    - [具体的な不変条件1]
    - [具体的な不変条件2]
    """
    # Given - 様々なシナリオの定義
    test_scenarios = [
        {"name": "シナリオ1", "input": {...}, "expected": {...}},
        {"name": "シナリオ2", "input": {...}, "expected": {...}},
    ]

    # When & Then - 各シナリオで不変条件を検証
    for scenario in test_scenarios:
        result = target_function(scenario["input"])

        # 不変条件検証: [具体的な説明]
        assert "invariant_field" in result, f"{scenario['name']}: 不変条件が維持されるべき"
        assert result["invariant_field"] is not None, f"{scenario['name']}: 不変条件が維持されるべき"
```

### モックとパッチの統一パターン

#### 1. 外部サービスのモック

```python
def test_external_service_integration_contract(self) -> None:
    """外部サービス統合の契約検証"""

    # Given - 事前条件設定: モックされた外部サービス
    with patch('boto3.client') as mock_boto_client:
        mock_service = Mock()
        mock_service.operation.return_value = {"status": "success"}
        mock_boto_client.return_value = mock_service

        # When - 外部サービスを使用する処理を実行
        result = target_function_with_external_service()

        # Then - 事後条件検証: 正しい呼び出しが行われる
        mock_service.operation.assert_called_once()
        assert result["status"] == "success"
```

#### 2. ログ出力のモック

```python
def test_logging_behavior_contract(self) -> None:
    """ログ出力動作の契約検証"""

    # Given - 事前条件設定: 有効な入力
    valid_input = {...}

    # When - ログをキャプチャしながら実行
    with patch('app.module.target.logger') as mock_logger:
        target_function(valid_input)

        # Then - 事後条件検証: 適切なログが出力される
        mock_logger.info.assert_any_call("期待されるログメッセージ")
        mock_logger.error.assert_not_called()  # エラーログは出力されない
```

## 🔍 品質チェック自動化

### 品質チェックスクリプトの活用

```bash
# 全体的な品質チェック
./scripts/python-quality-check.sh

# 個別チェック
uv run ruff check app/ tests/          # リンティング
uv run ruff format app/ tests/         # フォーマット
uv run mypy app/                       # 型チェック
uv run pytest tests/unit/ --cov=app   # テスト実行
```

### 品質基準

- **テストカバレッジ**: 90%以上（新規実装は 100%を目指す）
- **型チェック**: mypy エラーなし
- **リンティング**: ruff エラーなし
- **フォーマット**: ruff format 適用済み

### 継続的品質管理

#### pre-commit フック設定

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: python-quality-check
        name: Python Quality Check
        entry: ./scripts/python-quality-check.sh
        language: system
        pass_filenames: false
```

#### GitHub Actions 統合

```yaml
# .github/workflows/quality-check.yml
name: Quality Check
on: [push, pull_request]
jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.12"
      - name: Install uv
        run: pip install uv
      - name: Install dependencies
        run: uv sync
      - name: Run quality checks
        run: ./scripts/python-quality-check.sh
```

## 🧩 テスト実装の手順

### ステップ 1: ディレクトリとファイルの作成

```bash
# 1. テスト対象に対応するディレクトリを作成
mkdir -p tests/unit/path/to/module

# 2. __init__.pyファイルを作成
touch tests/unit/path/__init__.py
touch tests/unit/path/to/__init__.py
touch tests/unit/path/to/module/__init__.py

# 3. テストファイルを作成
touch tests/unit/path/to/module/test_target_file.py
```

### ステップ 2: テストファイルの基本構造を実装

```python
# 1. ファイルヘッダーを記述
"""
[機能名] の単体テスト - 契約による設計（例外ベースアプローチ）
...
"""

# 2. インポートセクションを実装
import json
from typing import Any
from unittest.mock import Mock, patch
import pytest
from app.module.target import target_function

# 3. テストクラスを定義
class TestTargetFunction:
    """[対象機能]の契約検証（例外ベースアプローチ）"""

    def test_successful_operation_contract(self) -> None:
        """契約による設計: 正常実行時の事後条件検証"""
        # Given-When-Then パターンで実装
```

### ステップ 3: 契約検証テストの実装

```python
# 1. 正常ケースの事後条件検証
def test_successful_case_contract(self) -> None:
    # Given - 事前条件設定
    # When - 操作実行
    # Then - 事後条件検証
    # 不変条件検証

# 2. 異常ケースの事前条件違反検証
def test_precondition_violation(self) -> None:
    # Given - 事前条件違反
    # When & Then - 適切な例外発生

# 3. エッジケースの処理検証
def test_edge_case_handling(self) -> None:
    # Given - エッジケース
    # When - 処理実行
    # Then - 適切な処理
```

### ステップ 4: 品質チェックと修正

```bash
# 1. 品質チェック実行
./scripts/python-quality-check.sh

# 2. エラーがある場合は修正
uv run ruff check tests/unit/path/to/module/test_target_file.py --fix
uv run ruff format tests/unit/path/to/module/test_target_file.py

# 3. 再度品質チェック
./scripts/python-quality-check.sh
```

### ステップ 5: テストコメントスタイル統一

#### 1. docstring（看板コメント）の統一フォーマット

**必須フォーマット:**

```python
def test_example_contract(self) -> None:
    """
    契約による設計: [具体的な検証内容]

    Given: [条件]
    When: [処理]
    Then: [結果]

    事前条件: [詳細な事前条件]
    事後条件: [詳細な事後条件]
    不変条件: [詳細な不変条件]
    """
```

**重要なポイント:**

- **タイトル**: 必ず `契約による設計: [具体的な検証内容]` で開始
- **Given-When-Then**: 簡潔で明確な記述
- **契約要素**: 事前条件・事後条件・不変条件を必ず記述
- **一貫性**: 全テストファイルで同じフォーマットを使用

#### 2. インラインコメントの統一フォーマット

**必須フォーマット:**

```python
# Given - [具体的な条件設定]
setup_data = {...}

# When - [具体的な処理実行]
result = target_function(setup_data)

# Then - 事後条件検証: [具体的な検証内容]
assert result.status == "success"

# 不変条件検証: [具体的な不変条件]
assert isinstance(result, ExpectedType)
```

**重要なポイント:**

- **Given**: `# Given - [具体的な条件設定]`
- **When**: `# When - [具体的な処理実行]`
- **Then**: `# Then - 事後条件検証: [具体的な検証内容]`
- **不変条件**: `# 不変条件検証: [具体的な不変条件]`

#### 3. 禁止パターン

**❌ 使用禁止:**

```python
# Act (AAA パターン - 使用しない)
# Assert (AAA パターン - 使用しない)
# When - (不完全なコメント - 具体的な説明を追加)
```

**✅ 正しい例:**

```python
# When - AgentInputインスタンスを作成
# When - invoke関数を実行
# When - ログ出力をモックしてinvoke関数を実行
```

#### 4. コメント統一チェックリスト

- [ ] docstring に「契約による設計:」タイトルがある
- [ ] Given-When-Then が明確に記述されている
- [ ] 事前条件・事後条件・不変条件が記述されている
- [ ] インラインコメントが統一フォーマットに従っている
- [ ] AAA パターン（Act/Assert）を使用していない
- [ ] 不完全なコメント（`# When -`のみ）がない

#### 5. 実装例（完全版）

```python
def test_successful_invocation_contract(self) -> None:
    """
    契約による設計: 正常実行時の事後条件検証

    Given: 全ての必須パラメータを含む有効なイベント
    When: lambda_handler()を実行する
    Then: 成功レスポンス（200）と適切な構造のボディが返される

    事前条件:
    - agentRuntimeArn が有効なARN形式である
    - exam_type が文字列である
    - question_count が存在する

    事後条件:
    - statusCode が 200 である
    - body が有効なJSON文字列である
    - レスポンスに必要な情報が含まれる

    不変条件:
    - AgentCore Runtime が正確に1回呼び出される
    - レスポンス構造が一貫している
    """
    # Given - 事前条件設定: 全ての必須パラメータを含む有効なイベント
    valid_event: dict[str, Any] = {
        "agentRuntimeArn": "arn:aws:bedrock-agentcore:us-east-1:123456789012:runtime/test-agent-xyz",
        "exam_type": "AWS-SAP",
        "question_count": 1,
    }
    mock_context = Mock()
    mock_context.function_name = "test-lambda-function"
    mock_context.request_id = "test-request-id-12345"

    # When - lambda_handler()を実行（Bedrockクライアントをモック）
    with patch("boto3.client") as mock_boto_client:
        # Bedrockクライアントの正常レスポンスをモック
        mock_bedrock = Mock()
        mock_boto_client.return_value = mock_bedrock
        mock_bedrock.invoke_agent.return_value = {
            "output": {"text": '{"questions": [{"question": "test"}]}'}
        }

        response = lambda_handler(valid_event, mock_context)

    # Then - 事後条件検証: 成功レスポンス（200）と適切な構造のボディが返される
    assert response["statusCode"] == 200
    assert "body" in response

    # 不変条件検証: AgentCore Runtime が正確に1回呼び出される
    mock_bedrock.invoke_agent.assert_called_once()
```

## 📋 テストチェックリスト

### 実装前チェックリスト

- [ ] テスト対象の機能を理解している
- [ ] 契約（事前条件・事後条件・不変条件）を明確にしている
- [ ] テストディレクトリ構造がアプリ本体と対応している
- [ ] 必要な**init**.py ファイルが存在する

### 実装中チェックリスト

- [ ] ファイルヘッダーに詳細な説明を記述した
- [ ] インポート方法が統一されている（予約語回避含む）
- [ ] Given-When-Then パターンで実装している
- [ ] 契約による設計の観点で検証している
- [ ] 適切なモック・パッチを使用している
- [ ] **docstring が統一フォーマットに従っている**
- [ ] **インラインコメントが統一フォーマットに従っている**
- [ ] **AAA パターン（Act/Assert）を使用していない**

### 実装後チェックリスト

- [ ] 全てのテストがパスしている
- [ ] テストカバレッジが 90%以上である
- [ ] 品質チェックスクリプトが成功している
- [ ] コメントが既存テストと同等レベルで充実している
- [ ] **コメントスタイルが他のテストファイルと統一されている**
- [ ] **docstring 内の Given-When-Then 記述が完備されている**
- [ ] エラーメッセージが具体的で分かりやすい

## 🚨 よくある問題と解決方法

### インポート関連の問題

#### 問題 1: モジュールが見つからないエラー

```python
# ❌ 問題のあるインポート
from wrong.path.module import function  # ModuleNotFoundError

# ✅ 解決方法 - 正しいパス構造を確認
from app.trigger.lambda_function import lambda_handler
```

#### 問題 2: pyproject.toml 設定との不整合

```bash
# pyproject.tomlのsrc設定を確認
# src = ["app", "tests"] が設定されていることを確認
```

### モック関連の問題

#### 問題 1: パッチ対象の指定ミス

```python
# ❌ 間違ったパッチ対象
patch('lambda_function.logger')  # ModuleNotFoundError

# ✅ 正しいパッチ対象
patch('app.trigger.lambda_function.logger')
```

#### 問題 2: モックの設定不足

```python
# ❌ 不完全なモック
mock_client = Mock()
# return_valueが設定されていない

# ✅ 完全なモック
mock_client = Mock()
mock_client.operation.return_value = {"expected": "response"}
```

### テスト構造の問題

#### 問題 1: Given-When-Then の不明確さ

```python
# ❌ 不明確な構造
def test_function():
    data = {...}
    result = target_function(data)
    assert result is not None

# ✅ 明確な構造
def test_function_contract(self) -> None:
    """契約による設計: 具体的な検証内容"""
    # Given - 事前条件設定: 具体的な説明
    data = {...}

    # When - 操作実行: 具体的な説明
    result = target_function(data)

    # Then - 事後条件検証: 具体的な説明
    assert result is not None, "結果が返されるべき"
```

## 📞 サポート

### 関連リソース

- **pytest ドキュメント**: https://docs.pytest.org/
- **ruff ドキュメント**: https://docs.astral.sh/ruff/
- **mypy ドキュメント**: https://mypy.readthedocs.io/

### トラブルシューティング

- **GitHub Issues**: テスト関連の問題報告
- **品質チェックスクリプト**: `./scripts/python-quality-check.sh`
- **開発環境**: `./scripts/setup-dev.sh`

### 実装例の参照

- **AgentCore テスト**: `tests/unit/agentcore/test_*.py`
- **Lambda 関数テスト**: `tests/unit/trigger/test_lambda_function.py`
- **Teams 連携テスト**: `tests/unit/agentcore/test_teams_client.py`
