"""
pytest 設定ファイル

テスト全体で使用される共通フィクスチャを定義します。
"""

import asyncio
import os
import sys
from collections.abc import Generator
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

try:
    from moto import mock_dynamodb
except ImportError:
    try:
        # moto v5では mock_dynamodb の場所が変更された
        from moto.mock_dynamodb import mock_dynamodb
    except ImportError:
        mock_dynamodb = None

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """セッション全体で使用するイベントループ"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_agent_context() -> AsyncMock:
    """AgentContext のモック"""
    context = AsyncMock()
    context.session_id = "test-session-123"
    context.user_id = "test-user-456"
    context.metadata = {"test": True}
    return context


@pytest.fixture
def sample_question_data() -> dict[str, Any]:
    """テスト用問題データ"""
    return {
        "id": "q_test_001",
        "topic": "EC2",
        "question_text": "Which EC2 instance type is most suitable for CPU-intensive workloads?",
        "question_type": "multiple_choice",
        "difficulty": "intermediate",
        "options": ["A. t3.micro", "B. c5.large", "C. r5.large", "D. i3.large"],
        "correct_answer": "B",
        "explanation": "C5 instances are optimized for compute-intensive workloads with high-performance processors.",
        "created_at": "2025-08-03T10:00:00Z",
    }


@pytest.fixture
def sample_aws_info() -> dict[str, Any]:
    """テスト用 AWS 情報データ"""
    return {
        "topic": "EC2",
        "service_info": "Amazon EC2 provides scalable computing capacity in the cloud.",
        "best_practices": [
            "Use appropriate instance types for your workload",
            "Enable detailed monitoring",
            "Use Auto Scaling for high availability",
        ],
        "common_scenarios": [
            "Web application hosting",
            "Batch processing",
            "High-performance computing",
        ],
        "key_features": [
            "Multiple instance types",
            "Elastic IP addresses",
            "Security groups",
            "Key pairs",
        ],
    }


@pytest.fixture
def mock_bedrock_client() -> AsyncMock:
    """Bedrock クライアントのモック"""
    client = AsyncMock()
    client.invoke_model.return_value = {
        "body": MagicMock(),
        "contentType": "application/json",
    }
    return client


@pytest.fixture
def mock_dynamodb_table() -> Any:
    """DynamoDB テーブルのモック"""
    if mock_dynamodb is None:
        pytest.skip("moto mock_dynamodb not available")

    with mock_dynamodb():
        import boto3

        dynamodb = boto3.resource("dynamodb", region_name="ap-northeast-1")
        table = dynamodb.create_table(
            TableName="test-questions",
            KeySchema=[
                {"AttributeName": "PK", "KeyType": "HASH"},
                {"AttributeName": "SK", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "PK", "AttributeType": "S"},
                {"AttributeName": "SK", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        yield table


@pytest.fixture
def mock_teams_webhook() -> AsyncMock:
    """Teams Webhook のモック"""
    webhook = AsyncMock()
    webhook.post.return_value.status_code = 200
    webhook.post.return_value.json.return_value = {"status": "success"}
    return webhook


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """テスト環境の自動セットアップ"""
    # テスト用環境変数の設定
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("DYNAMODB_TABLE_NAME", "test-questions")
    monkeypatch.setenv("AWS_REGION", "ap-northeast-1")
    monkeypatch.setenv("BEDROCK_REGION", "us-east-1")
