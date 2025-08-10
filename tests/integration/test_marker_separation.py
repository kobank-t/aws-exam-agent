"""
統合テストマーカー分離テスト

pytest マーカーによるテスト分離が正しく動作することを確認します。
"""

from typing import Any
from unittest.mock import AsyncMock

import pytest


@pytest.mark.integration
def test_integration_marker_works() -> None:
    """統合テストマーカーが正しく動作することを確認"""
    assert True, "Integration test marker is working"


@pytest.mark.integration
@pytest.mark.slow
def test_integration_with_slow_marker() -> None:
    """統合テスト + slow マーカーの組み合わせテスト"""
    assert True, "Integration test with slow marker is working"


@pytest.mark.integration
def test_integration_test_environment(setup_test_environment: None) -> None:
    """統合テスト環境設定の確認"""
    import os

    assert os.getenv("ENVIRONMENT") == "test"
    assert os.getenv("MCP_AWS_DOCS_ENABLED") == "true"
    assert os.getenv("AGENTCORE_STREAMING_ENABLED") == "true"


@pytest.mark.integration
def test_integration_fixtures_available(
    mock_mcp_server: AsyncMock,
    mock_strands_agent: AsyncMock,
    integration_test_data: dict[str, Any],
) -> None:
    """統合テスト用フィクスチャが利用可能であることを確認"""
    # MCP Server モックの確認
    assert mock_mcp_server is not None
    assert hasattr(mock_mcp_server, "connect")
    assert hasattr(mock_mcp_server, "call_tool")

    # Strands Agent モックの確認
    assert mock_strands_agent is not None
    assert hasattr(mock_strands_agent, "invoke")

    # 統合テストデータの確認
    assert "request" in integration_test_data
    assert "expected_response" in integration_test_data
    assert integration_test_data["request"]["topic"] == "EC2"
