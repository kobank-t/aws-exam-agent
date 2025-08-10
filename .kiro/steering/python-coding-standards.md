---
inclusion: fileMatch
fileMatchPattern: "*.py"
---

# Python コーディング規約

## 概要

AWS Exam Coach プロジェクトにおける Python コーディング規約です。PEP8 を基準とし、FastAPI ベストプラクティスと AWS サーバーレス開発に最適化された規約を定義します。

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

- **詳細は `type-safety-standards.md` を参照**
- 本番コードとテストコードで同等の型チェック基準を適用
- IDE 上でのエラー表示ゼロを目指す（チーム開発の精神衛生上重要）
- `# type: ignore` の使用は原則禁止

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
]
ignore = [
    "E501",  # line too long, handled by formatter
    "B008",  # do not perform function calls in argument defaults
]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
skip-string-normalization = false
line-ending = "auto"
```

## プロジェクト構造

### ドメイン駆動設計

```
app/
├── lambda/                    # Lambda関数
│   ├── question_generator/    # 問題生成Lambda
│   ├── teams_webhook/         # Teams連携Lambda
│   └── shared/                # 共通モジュール
├── agent/                     # AgentCore用
│   ├── agents/                # エージェント定義
│   ├── tools/                 # MCP Tools
│   └── config/                # 設定ファイル
└── shared/                    # 全体共通モジュール
    ├── models/                # データモデル
    ├── services/              # ビジネスロジック
    ├── utils/                 # ユーティリティ
    └── exceptions/            # 例外定義
```

### モジュール間インポート

```python
# 明確なモジュール名を使用
from app.shared.models import Question, QuestionType
from app.shared.services import aws_service
from app.shared.exceptions import QuestionGenerationError

# エイリアスを使用して名前衝突を回避
from app.lambda.question_generator import constants as qg_constants
from app.shared import constants as shared_constants
```

## 型ヒント・Pydantic

### 型注釈の必須化

**重要**: 型安全性の詳細なガイドラインは `type-safety-standards.md` を参照してください。

```python
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
```

### 基本的な型ヒント

```python
from typing import Any
from uuid import UUID
from datetime import datetime

# Python 3.12+ の新しい型注釈を使用
# ❌ 古い書き方
from typing import Dict, List, Optional, Union
def generate_question(topic: Optional[str]) -> Dict[str, Any]:
    pass

# ✅ 新しい書き方
def generate_question(topic: str | None) -> dict[str, Any]:
    """問題を生成する"""
    pass

# 変数の型ヒント
questions: list[dict[str, Any]] = []
user_id: UUID | None = None
```

### Pydantic モデル

```python
from datetime import datetime
from enum import Enum
from typing import Optional
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

    def serializable_dict(self, **kwargs) -> Dict[str, Any]:
        """シリアライズ可能な辞書を返す"""
        from fastapi.encoders import jsonable_encoder
        return jsonable_encoder(self.model_dump())


class Question(CustomBaseModel):
    """問題モデル"""
    id: UUID
    topic: str = Field(min_length=1, max_length=200)
    question_text: str = Field(min_length=10, max_length=2000)
    question_type: QuestionType
    difficulty: str = Field(pattern="^(beginner|intermediate|advanced)$")
    options: List[str] = Field(min_length=2, max_length=6)
    correct_answer: str
    explanation: str = Field(min_length=10, max_length=1000)
    created_at: datetime
    updated_at: Optional[datetime] = None
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

## 非同期プログラミング

### async/await の適切な使用

```python
import asyncio
from typing import Any, Dict

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
from typing import Optional

logger = logging.getLogger(__name__)

async def safe_api_call(url: str) -> Optional[Dict[str, Any]]:
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
from typing import Any, Dict

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
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
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

def process_request(body: Dict[str, Any]) -> Dict[str, Any]:
    """ビジネスロジック（テスト可能な純粋関数）"""
    # 実装
    pass
```

### 環境変数・設定管理

```python
from pydantic_settings import BaseSettings
from typing import Optional

class LambdaConfig(BaseSettings):
    """Lambda 環境設定"""
    # DynamoDB
    DYNAMODB_TABLE_NAME: str
    DYNAMODB_REGION: str = "ap-northeast-1"

    # Bedrock
    BEDROCK_REGION: str = "us-east-1"
    BEDROCK_MODEL_ID: str = "anthropic.claude-3-5-sonnet-20241022-v2:0"

    # Teams
    TEAMS_WEBHOOK_URL: Optional[str] = None

    # ログレベル
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True

# グローバル設定インスタンス
config = LambdaConfig()
```

## テスト

### テスト構造

```python
import pytest
from unittest.mock import AsyncMock, patch
from typing import Dict, Any

from app.lambda.question_generator.handler import lambda_handler
from app.shared.models import Question

class TestQuestionGenerator:
    """問題生成機能のテスト"""

    @pytest.fixture
    def sample_event(self) -> Dict[str, Any]:
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
        sample_event: Dict[str, Any],
        lambda_context: Any
    ):
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

    @pytest.mark.asyncio
    async def test_invalid_input_handling(
        self,
        lambda_context: Any
    ):
        """不正な入力の処理テスト"""
        invalid_event = {
            "body": json.dumps({
                "topic": "",  # 空のトピック
                "difficulty": "invalid"  # 不正な難易度
            })
        }

        response = lambda_handler(invalid_event, lambda_context)

        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert "error" in body
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

## ログ・監視

### 構造化ログ

```python
import logging
from aws_lambda_powertools import Logger

# PowerTools Logger の使用
logger = Logger(service="question-generator")

def process_question_generation(topic: str, difficulty: str):
    """問題生成処理"""
    logger.info(
        "Starting question generation",
        extra={
            "topic": topic,
            "difficulty": difficulty,
            "operation": "generate_question"
        }
    )

    try:
        # 処理実行
        result = generate_question(topic, difficulty)

        logger.info(
            "Question generation completed",
            extra={
                "topic": topic,
                "difficulty": difficulty,
                "question_id": result.get("id"),
                "operation": "generate_question"
            }
        )

        return result

    except Exception as e:
        logger.error(
            "Question generation failed",
            extra={
                "topic": topic,
                "difficulty": difficulty,
                "error": str(e),
                "operation": "generate_question"
            }
        )
        raise
```

## セキュリティ

### 入力検証

```python
from pydantic import BaseModel, Field, field_validator
import re

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

## パフォーマンス

### 効率的なデータ処理

```python
from typing import List, Dict, Any
import asyncio

async def batch_process_questions(
    questions: List[Dict[str, Any]],
    batch_size: int = 10
) -> List[Dict[str, Any]]:
    """問題の一括処理"""
    results = []

    # バッチ処理で並行実行
    for i in range(0, len(questions), batch_size):
        batch = questions[i:i + batch_size]

        # 並行実行
        tasks = [process_single_question(q) for q in batch]
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)

        # エラーハンドリング
        for result in batch_results:
            if isinstance(result, Exception):
                logger.error(f"Batch processing error: {result}")
            else:
                results.append(result)

    return results
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

## 開発ツール設定

### VS Code 設定 (.vscode/settings.json)

```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "none",
  "[python]": {
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": true,
      "source.fixAll": true
    }
  },
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"]
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

---

**適用範囲**: AWS Exam Coach プロジェクト全体  
**更新日**: 2025 年 8 月 1 日  
**バージョン**: 1.0
