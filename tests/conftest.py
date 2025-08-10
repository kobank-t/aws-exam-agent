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
    import moto  # noqa: F401

    mock_dynamodb_available = True
except ImportError:
    mock_dynamodb_available = False

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


# DynamoDB フィクスチャは削除済み
# 実際のリポジトリクラスのテストは、タスク 4 で実装予定：
# - app/repositories/question_repository.py 用のフィクスチャ
# - 単一テーブル設計に対応したテストデータ


@pytest.fixture
def mock_teams_webhook() -> AsyncMock:
    """Teams Webhook のモック"""
    webhook = AsyncMock()
    webhook.post.return_value.status_code = 200
    webhook.post.return_value.json.return_value = {"status": "success"}
    return webhook


@pytest.fixture
def mock_mcp_server() -> AsyncMock:
    """MCP Server のモック（統合テスト用）"""
    server = AsyncMock()
    server.connect.return_value = True
    server.list_tools.return_value = [
        {"name": "aws_docs_search", "description": "Search AWS documentation"},
        {"name": "aws_knowledge_query", "description": "Query AWS knowledge base"},
    ]
    server.call_tool.return_value = {
        "content": [{"type": "text", "text": "Mock AWS documentation content"}]
    }
    return server


@pytest.fixture
def mock_strands_agent() -> AsyncMock:
    """Strands Agent のモック（統合テスト用）"""
    agent = AsyncMock()
    agent.name = "test-agent"
    agent.description = "Test agent for integration testing"
    agent.invoke.return_value = {
        "status": "success",
        "result": "Mock agent execution result",
        "metadata": {"execution_time": 1.5},
    }
    return agent


@pytest.fixture
def integration_test_data() -> dict[str, Any]:
    """統合テスト用の複合データ"""
    return {
        "request": {
            "topic": "EC2",
            "difficulty": "intermediate",
            "question_count": 1,
        },
        "expected_response": {
            "questions": [
                {
                    "id": "q_integration_001",
                    "topic": "EC2",
                    "question_text": "Integration test question",
                    "options": [
                        "A. Option 1",
                        "B. Option 2",
                        "C. Option 3",
                        "D. Option 4",
                    ],
                    "correct_answer": "B",
                    "explanation": "Integration test explanation",
                }
            ],
            "metadata": {"generation_time": 2.5, "quality_score": 0.85},
        },
    }


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

    # MCP Server 設定（統合テスト用）
    monkeypatch.setenv("MCP_AWS_DOCS_ENABLED", "true")
    monkeypatch.setenv("MCP_AWS_KNOWLEDGE_ENABLED", "true")
    monkeypatch.setenv("MCP_SERVER_TIMEOUT", "30")

    # AgentCore 設定（統合テスト用）
    monkeypatch.setenv("AGENTCORE_RUNTIME_MEMORY", "512")
    monkeypatch.setenv("AGENTCORE_RUNTIME_TIMEOUT", "300")
    monkeypatch.setenv("AGENTCORE_STREAMING_ENABLED", "true")
