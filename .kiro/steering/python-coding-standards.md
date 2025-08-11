---
inclusion: fileMatch
fileMatchPattern: "*.py"
---

# Python コーディング規約

## 概要

AWS Exam Agent プロジェクトにおける Python コーディング規約です。PEP8 を基準とし、Python 3.12 の最新機能を活用した型安全性と AWS サーバーレス開発に最適化された規約を定義します。

## 基本原則

### 1. PEP8 準拠

- Python Enhancement Proposal 8 (PEP8) を基本とする
- 自動フォーマッター・リンターによる品質保証を必須とする

### 2. 可読性重視

- コードは書くよりも読まれることが多い
- 明確で理解しやすいコードを優先する
- 適切なコメントと型ヒントを活用する

### 3. 一貫性の確保

- プロジェクト全体で統一されたスタイルを維持
- チーム開発における認知負荷を軽減

### 4. 型安全性の徹底

- 本番コードとテストコードで同等の型チェック基準を適用
- IDE 上でのエラー表示ゼロを目指す（チーム開発の精神衛生上重要）
- `# type: ignore` の使用は原則禁止
- Python 3.11+の`Self`型を積極的に活用
- Python 3.12+の新しい型パラメータ構文を推奨

## 型安全性とタイプヒント

### 基本的な型注釈

```python
from typing import Any, Self
from uuid import UUID
from datetime import datetime

# ✅ 基本的な型注釈
def process_data(data: dict[str, Any]) -> dict[str, Any]:
    """データを処理する"""
    return data

# ✅ テスト関数の型注釈
def test_config(self) -> None:
    config = Config()
    assert config.APP_NAME == "aws-exam-agent"

# ✅ 非同期関数の型注釈
async def fetch_data(url: str) -> dict[str, Any]:
    """データを非同期で取得する"""
    pass

# 変数の型ヒント
questions: list[dict[str, Any]] = []
user_id: UUID | None = None
```

### Python 3.9+ の現代的な型注釈

```python
# ❌ 古い書き方（Python 3.8以前）
from typing import Dict, List, Optional, Union, TypeVar

def generate_question(topic: Optional[str]) -> Dict[str, Any]:
    pass

# ✅ 新しい書き方（Python 3.9+）
def generate_question(topic: str | None) -> dict[str, Any]:
    """問題を生成する"""
    pass

# ✅ リスト・辞書の型注釈
options: list[str] = ["A", "B", "C", "D"]
config: dict[str, Any] = {"debug": True}
```

### Python 3.11+ の Self 型

```python
from typing import Self

class BaseModel:
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """辞書からインスタンスを作成"""
        return cls(**data)

    def copy(self) -> Self:
        """インスタンスをコピー"""
        return self.__class__(**self.__dict__)

    def copy_with_updates(self, **updates) -> Self:
        """更新されたコピーを作成"""
        data = self.__dict__.copy()
        data.update(updates)
        return self.__class__(**data)
```

### Python 3.12+ の新しい型パラメータ構文

```python
# ✅ 新しい型パラメータ構文（Python 3.12+）
def process_data[T](data: T) -> T:
    """汎用的なデータ処理"""
    return data

# ✅ 新しい型エイリアス構文（Python 3.12+）
type DataProcessor[T] = Callable[[T], T]
type ResultDict[T] = dict[str, T]

# ✅ 複数の型パラメータ
class Container[T, U]:
    def __init__(self, first: T, second: U):
        self.first = first
        self.second = second

# ✅ 制約付き型パラメータ
def process_numeric[T: (int, float)](value: T) -> T:
    return value * 2
```

### 型安全性のベストプラクティス

#### 1. `# type: ignore` の原則禁止

**基本方針**: `# type: ignore` は原則として使用禁止

**例外条件**: 以下の条件を全て満たす場合のみ使用可能

1. 他の解決策（型ガード、cast、型注釈）では解決不可能
2. 使用理由を詳細なコメントで説明
3. コードレビューでの承認取得
4. 将来的な解決策の検討・記録

#### 2. 適切な解決策

**型ガード（isinstance）の使用**:

```python
# ❌ 不適切
result = some_function()  # type: ignore[assignment]

# ✅ 適切
if isinstance(result, Exception):
    # エラー処理
    error_info = {"error": str(result)}
else:
    # 正常処理（型が自動的に絞り込まれる）
    success_info = result
```

**cast 関数の活用**:

```python
from typing import cast

# ❌ 不適切
data = complex_operation()  # type: ignore[assignment]

# ✅ 適切
if isinstance(results[0], Exception):
    data = {"error": str(results[0])}
else:
    # 理由を明記したcast
    # asyncio.gatherの結果は正常時にdict[str, Any]を返すことが保証されている
    data = cast(dict[str, Any], results[0])
```

#### 3. 外部ライブラリの型チェック無視

**pyproject.toml での設定**:

```toml
[[tool.mypy.overrides]]
module = [
    "moto.*",                    # テスト用AWSモック（型スタブなし）
    "aws_lambda_powertools.*",   # AWS Lambda用ユーティリティ（型スタブ不完全）
    "strands_agents.*",          # エージェントフレームワーク（型スタブなし）
    "boto3.*",                   # AWS SDK（型スタブは別パッケージで複雑）
]
ignore_missing_imports = true
```

### 非同期プログラミングの型安全性

#### 1. 非同期関数の適切なテスト

```python
# ❌ 不適切
mock_async_func.return_value = {"result": "data"}  # 同期的な戻り値

# ✅ 適切
import asyncio
from typing import Any

future: asyncio.Future[Any] = asyncio.Future()
future.set_result({"result": "data"})
mock_async_func.return_value = future
```

#### 2. asyncio.gather の型安全な処理

```python
# ❌ 不適切
results = await asyncio.gather(task1, task2, return_exceptions=True)
data1 = results[0]  # type: ignore[assignment]
data2 = results[1]  # type: ignore[assignment]

# ✅ 適切
results = await asyncio.gather(task1, task2, return_exceptions=True)

if isinstance(results[0], Exception):
    data1 = {"error": str(results[0])}
else:
    data1 = cast(dict[str, Any], results[0])

if isinstance(results[1], Exception):
    data2 = {"error": str(results[1])}
else:
    data2 = cast(dict[str, Any], results[1])
```

### テストコードの型安全性

#### 1. テストコードも本番コード同等の品質

**基本方針**:

- テストコードも本番コードと同等の型チェック基準を適用
- 「テストだから緩くても良い」という考えを排除
- 長期的な保守性を重視

```python
# ❌ 不適切
def test_example():
    pass

# ✅ 適切
def test_example(self) -> None:
    pass

async def test_async_example(self) -> None:
    pass
```

#### 2. モックオブジェクトの型安全な使用

```python
from unittest.mock import Mock
import pytest

# ✅ 適切
def test_with_mock(self, mock_service: Mock) -> None:
    mock_service.return_value = {"expected": "result"}
    result = service_function()
    assert result["expected"] == "result"
```

## Pydantic モデル

### 基本的なモデル定義

```python
from datetime import datetime
from enum import Enum
from typing import Any, Self
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    SCENARIO_BASED = "scenario_based"
    DRAG_DROP = "drag_drop"


class CustomBaseModel(BaseModel):
    """プロジェクト共通のベースモデル"""
    model_config = ConfigDict(
        # JSON エンコーダー設定
        json_encoders={datetime: lambda dt: dt.isoformat()},
        # フィールド名の変換を許可
        populate_by_name=True,
        # 追加フィールドを禁止
        extra="forbid",
    )

    def serializable_dict(self, **kwargs) -> dict[str, Any]:
        """シリアライズ可能な辞書を返す"""
        from fastapi.encoders import jsonable_encoder
        return jsonable_encoder(self.model_dump())

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """辞書からインスタンスを作成（Self型使用）"""
        return cls(**data)

    def copy_with_updates(self, **updates) -> Self:
        """更新されたコピーを作成（Self型使用）"""
        data = self.model_dump()
        data.update(updates)
        return self.__class__(**data)


class Question(CustomBaseModel):
    """問題モデル"""
    id: UUID
    topic: str = Field(min_length=1, max_length=200)
    question_text: str = Field(min_length=10, max_length=2000)
    question_type: QuestionType
    difficulty: str = Field(pattern="^(beginner|intermediate|advanced)$")
    options: list[str] = Field(min_length=2, max_length=6)  # Python 3.9+の新しい型注釈
    correct_answer: str
    explanation: str = Field(min_length=10, max_length=1000)
    created_at: datetime
    updated_at: datetime | None = None  # Python 3.10+のUnion構文
```

### バリデーション

```python
from pydantic import field_validator, model_validator

class QuestionCreate(CustomBaseModel):
    topic: str
    difficulty: str

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, v: str) -> str:
        allowed_values = ["beginner", "intermediate", "advanced"]
        if v not in allowed_values:
            raise ValueError(f"Difficulty must be one of: {allowed_values}")
        return v

    @model_validator(mode="after")
    def validate_question_consistency(self):
        # 複数フィールドにまたがるバリデーション
        if self.question_type == QuestionType.MULTIPLE_CHOICE:
            if len(self.options) < 2:
                raise ValueError("Multiple choice questions need at least 2 options")
        return self
```

## コードフォーマット・リンター

### Ruff の採用

```bash
#!/bin/sh -e
set -x

# リンティング（自動修正付き）
ruff check --fix src

# フォーマッティング
ruff format src
```

**採用理由:**

- 高速な Python リンター・フォーマッター
- Black、isort、flake8 の機能を統合
- 設定が簡単で保守性が高い

### 設定ファイル (pyproject.toml)

```toml
[tool.ruff]
line-length = 88
target-version = "py312"

[tool.ruff.lint]
select = [
    "E",  # pycodestyle errors
    "W",  # pycodestyle warnings
    "F",  # pyflakes
    "I",  # isort
    "B",  # flake8-bugbear
    "C4", # flake8-comprehensions
    "UP", # pyupgrade
    "N",  # pep8-naming
]
ignore = [
    "E501",  # line too long, handled by formatter
    "B008",  # do not perform function calls in argument defaults
]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
line-ending = "auto"

[tool.mypy]
python_version = "3.12"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = false
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true
plugins = ["pydantic.mypy"]

[tool.pydantic-mypy]
init_forbid_extra = true
init_typed = true
warn_required_dynamic_aliases = true
```

## プロジェクト構造

### ドメイン駆動設計

```
app/
├── models/                    # データモデル
│   ├── base.py               # 基底モデル
│   ├── question.py           # 問題モデル
│   ├── delivery.py           # 配信履歴モデル
│   └── user_response.py      # ユーザー回答モデル
├── agentcore/                # AgentCore用
│   ├── agent_main.py         # メインエージェント
│   └── mcp/                  # MCP統合
└── shared/                   # 全体共通モジュール
    ├── config.py             # 設定管理
    ├── constants.py          # 定数定義
    └── exceptions.py         # 例外定義
```

### モジュール間インポート

```python
# 明確なモジュール名を使用
from app.models import Question, QuestionType
from app.shared.config import Config
from app.shared.exceptions import ValidationError

# エイリアスを使用して名前衝突を回避
from app.models import constants as model_constants
from app.shared import constants as shared_constants
```

## 非同期プログラミング

### async/await の適切な使用

```python
import asyncio
from typing import Any

# ❌ 悪い例: 非同期関数内でブロッキング操作
async def bad_example():
    import time
    time.sleep(10)  # イベントループをブロック
    return {"result": "bad"}

# ✅ 良い例: 非ブロッキング操作
async def good_example():
    await asyncio.sleep(10)  # 非ブロッキング
    return {"result": "good"}

# ✅ 同期ライブラリの適切な使用
from starlette.concurrency import run_in_threadpool

async def use_sync_library():
    # 同期ライブラリをスレッドプールで実行
    result = await run_in_threadpool(sync_heavy_operation, data)
    return result
```

### エラーハンドリング

```python
import logging
from typing import Any

logger = logging.getLogger(__name__)

async def safe_api_call(url: str) -> dict[str, Any] | None:
    """安全なAPI呼び出し"""
    try:
        # 非同期HTTP呼び出し
        response = await http_client.get(url)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error occurred: {e.response.status_code}")
        return None
    except httpx.RequestError as e:
        logger.error(f"Request error occurred: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None
```

## AWS Lambda 固有の規約

### Lambda ハンドラー

```python
import json
import logging
from typing import Any

from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.metrics import MetricUnit

# PowerTools の初期化
logger = Logger()
tracer = Tracer()
metrics = Metrics()

@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
@metrics.log_metrics(capture_cold_start_metric=True)
def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Lambda ハンドラー"""
    try:
        # リクエストの解析
        body = json.loads(event.get("body", "{}"))

        # メトリクス記録
        metrics.add_metric(name="QuestionGenerated", unit=MetricUnit.Count, value=1)

        # ビジネスロジック実行
        result = process_request(body)

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps(result)
        }

    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Internal server error"})
        }

def process_request(body: dict[str, Any]) -> dict[str, Any]:
    """ビジネスロジック（テスト可能な純粋関数）"""
    # 実装
    pass
```

### 環境変数・設定管理

```python
from pydantic_settings import BaseSettings

class Config(BaseSettings):
    """アプリケーション設定"""
    # DynamoDB
    DYNAMODB_TABLE_NAME: str
    DYNAMODB_REGION: str = "ap-northeast-1"

    # Bedrock
    BEDROCK_REGION: str = "us-east-1"
    BEDROCK_MODEL_ID: str = "anthropic.claude-3-5-sonnet-20241022-v2:0"

    # Teams
    TEAMS_WEBHOOK_URL: str | None = None

    # ログレベル
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True

# グローバル設定インスタンス
config = Config()
```

## テスト

### テスト構造

```python
import pytest
from unittest.mock import AsyncMock, patch
from typing import Any

from app.lambda.question_generator.handler import lambda_handler
from app.models import Question

class TestQuestionGenerator:
    """問題生成機能のテスト"""

    @pytest.fixture
    def sample_event(self) -> dict[str, Any]:
        """テスト用イベント"""
        return {
            "body": json.dumps({
                "topic": "EC2",
                "difficulty": "intermediate"
            })
        }

    @pytest.fixture
    def lambda_context(self):
        """Lambda コンテキストのモック"""
        context = AsyncMock()
        context.function_name = "test-function"
        context.aws_request_id = "test-request-id"
        return context

    @pytest.mark.asyncio
    async def test_successful_question_generation(
        self,
        sample_event: dict[str, Any],
        lambda_context: Any
    ) -> None:
        """正常な問題生成のテスト"""
        with patch("app.shared.services.bedrock_service.generate_question") as mock_generate:
            # モックの設定
            mock_generate.return_value = {
                "question": "What is EC2?",
                "options": ["A", "B", "C", "D"],
                "correct_answer": "A",
                "explanation": "EC2 is..."
            }

            # 実行
            response = lambda_handler(sample_event, lambda_context)

            # 検証
            assert response["statusCode"] == 200
            body = json.loads(response["body"])
            assert "question" in body
            assert len(body["options"]) == 4
```

### モック・フィクスチャ

```python
import pytest
from unittest.mock import AsyncMock
import boto3
from moto import mock_dynamodb

@pytest.fixture
def mock_bedrock_client():
    """Bedrock クライアントのモック"""
    client = AsyncMock()
    client.invoke_model.return_value = {
        "body": json.dumps({
            "content": [{"text": "Generated question..."}]
        })
    }
    return client

@pytest.fixture
def dynamodb_table():
    """DynamoDB テーブルのモック"""
    with mock_dynamodb():
        dynamodb = boto3.resource("dynamodb", region_name="ap-northeast-1")
        table = dynamodb.create_table(
            TableName="test-questions",
            KeySchema=[
                {"AttributeName": "PK", "KeyType": "HASH"},
                {"AttributeName": "SK", "KeyType": "RANGE"}
            ],
            AttributeDefinitions=[
                {"AttributeName": "PK", "AttributeType": "S"},
                {"AttributeName": "SK", "AttributeType": "S"}
            ],
            BillingMode="PAY_PER_REQUEST"
        )
        yield table
```

## セキュリティ

### 入力検証

```python
from pydantic import BaseModel, Field, field_validator

class SecureInput(BaseModel):
    """セキュアな入力モデル"""
    topic: str = Field(
        min_length=1,
        max_length=100,
        pattern="^[A-Za-z0-9\\s\\-_]+$"  # 英数字、スペース、ハイフン、アンダースコアのみ
    )

    @field_validator("topic")
    @classmethod
    def validate_topic(cls, v: str) -> str:
        # SQLインジェクション対策
        dangerous_patterns = ["'", '"', ";", "--", "/*", "*/"]
        for pattern in dangerous_patterns:
            if pattern in v:
                raise ValueError(f"Invalid character detected: {pattern}")
        return v.strip()
```

### 機密情報の取り扱い

```python
import boto3
from botocore.exceptions import ClientError

class SecretsManager:
    """AWS Secrets Manager からの機密情報取得"""

    def __init__(self, region_name: str = "ap-northeast-1"):
        self.client = boto3.client("secretsmanager", region_name=region_name)

    async def get_secret(self, secret_name: str) -> str:
        """機密情報を取得"""
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            return response["SecretString"]
        except ClientError as e:
            logger.error(f"Failed to retrieve secret {secret_name}: {e}")
            raise

# 使用例
secrets = SecretsManager()
api_key = await secrets.get_secret("teams-webhook-url")
```

## 品質保証

### 開発時の必須チェック

- [ ] `uv run mypy app/ tests/` でエラー 0 件
- [ ] `uv run ruff check app/ tests/` でエラー 0 件
- [ ] IDE 上でエラー表示がない
- [ ] `# type: ignore` の使用がない（または適切な理由付き）

### CI/CD パイプラインでの自動チェック

```bash
# 型チェック
uv run mypy app/ tests/ --show-error-codes

# リンターチェック
uv run ruff check app/ tests/

# type: ignore の使用チェック
if grep -r "# type: ignore" app/ tests/; then
    echo "ERROR: # type: ignore found. Please use proper type safety techniques."
    exit 1
fi
```

## 開発ツール設定

### VS Code 設定 (.vscode/settings.json)

```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "[python]": {
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": "explicit",
      "source.fixAll": "explicit"
    },
    "editor.rulers": [88],
    "editor.defaultFormatter": "charliermarsh.ruff"
  },
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"],
  "python.testing.unittestEnabled": false
}
```

### pre-commit 設定 (.pre-commit-config.yaml)

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

## コミット・ブランチ規約

### コミットメッセージ

```
feat: 問題生成機能にEC2トピック対応を追加
fix: DynamoDB接続エラーの修正
docs: README.mdにデプロイ手順を追加
test: 問題生成機能のユニットテスト追加
refactor: 共通ユーティリティ関数の整理
```

### ブランチ命名

```
feature/question-generation-ec2
bugfix/dynamodb-connection-error
hotfix/security-vulnerability
docs/deployment-guide
```

## トラブルシューティング

### 1. Union 型の処理エラー

**症状**: `Union[T, Exception]` 型での assignment エラー

**解決策**:

```python
# isinstance による型ガード使用
if isinstance(result, Exception):
    # Exception の場合の処理
else:
    # T 型の場合の処理（型が自動的に絞り込まれる）
```

### 2. asyncio.gather の型エラー

**症状**: `asyncio.gather` の戻り値での型エラー

**解決策**:

```python
# cast関数を使用した明示的キャスト
if isinstance(results[0], Exception):
    data = {"error": str(results[0])}
else:
    data = cast(ExpectedType, results[0])
```

### 3. 外部ライブラリの型エラー

**症状**: boto3、moto 等の外部ライブラリでの型エラー

**解決策**:

```toml
# pyproject.toml での設定
[[tool.mypy.overrides]]
module = ["problematic_library.*"]
ignore_missing_imports = true
```

## 成功事例

### プロジェクト実績（2025 年 8 月 10 日）

**型安全性向上の成果**:

- `# type: ignore` 使用箇所: 0 箇所（完全削除）
- Mypy エラー: 0 件
- Ruff エラー: 0 件
- テスト通過率: 100%

**学習効果**:

- 適切な型ガード手法の習得
- cast 関数の効果的な活用
- 非同期プログラミングの型安全性向上
- Python 3.12 の新機能活用

---

**適用範囲**: AWS Exam Agent プロジェクト全体  
**更新日**: 2025 年 8 月 10 日  
**バージョン**: 2.0 - 統合版・Python 3.12 対応
