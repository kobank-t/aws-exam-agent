"""
MCP 統合テスト

AgentCore と MCP Server の統合動作をテストします。
"""

import asyncio
from collections.abc import AsyncGenerator

import pytest

from app.mcp.client import MCPClient, get_mcp_client


@pytest.mark.integration
class TestMCPIntegration:
    """MCP 統合テストクラス"""

    @pytest.fixture
    async def mcp_client(self) -> AsyncGenerator[MCPClient, None]:
        """MCP Client フィクスチャ"""
        client = MCPClient()
        yield client
        await client.disconnect()

    async def test_mcp_client_initialization(self, mcp_client: MCPClient) -> None:
        """MCP Client の初期化テスト"""
        assert mcp_client is not None
        assert not mcp_client.is_connected

    async def test_aws_docs_server_connection(self, mcp_client: MCPClient) -> None:
        """AWS Documentation MCP Server 接続テスト"""
        result = await mcp_client.connect_aws_docs_server()

        # uvx が利用可能な場合は True、そうでなければ False
        assert isinstance(result, bool)

    async def test_aws_knowledge_server_connection(self, mcp_client: MCPClient) -> None:
        """AWS Knowledge MCP Server 接続テスト"""
        result = await mcp_client.connect_aws_knowledge_server()

        # uvx が利用可能な場合は True、そうでなければ False
        assert isinstance(result, bool)

    async def test_connect_all_servers(self, mcp_client: MCPClient) -> None:
        """全 MCP Server 接続テスト"""
        result = await mcp_client.connect_all_servers()

        # uvx が利用可能な場合は True、そうでなければ False
        assert isinstance(result, bool)
        assert mcp_client.is_connected == result

    async def test_get_aws_documentation(self, mcp_client: MCPClient) -> None:
        """AWS Documentation 取得テスト"""
        await mcp_client.connect_all_servers()

        result = await mcp_client.get_aws_documentation("EC2", "instances")

        assert isinstance(result, dict)
        assert "service" in result
        assert result["service"] == "EC2"
        assert "topic" in result
        assert result["topic"] == "instances"

    async def test_get_aws_knowledge(self, mcp_client: MCPClient) -> None:
        """AWS Knowledge 取得テスト"""
        await mcp_client.connect_all_servers()

        result = await mcp_client.get_aws_knowledge("EC2 best practices")

        assert isinstance(result, dict)
        assert "query" in result
        assert result["query"] == "EC2 best practices"
        assert "knowledge" in result

    async def test_global_mcp_client(self) -> None:
        """グローバル MCP Client テスト"""
        client = await get_mcp_client()

        assert client is not None
        assert isinstance(client, MCPClient)

        # 接続状態の確認
        # 実際の環境では接続が成功する可能性があります
        assert isinstance(client.is_connected, bool)

    async def test_mcp_client_error_handling(self, mcp_client: MCPClient) -> None:
        """MCP Client エラーハンドリングテスト"""
        # 無効なサービス名でのテスト
        result = await mcp_client.get_aws_documentation("", "")

        assert isinstance(result, dict)
        assert "service" in result

        # 無効なクエリでのテスト
        result = await mcp_client.get_aws_knowledge("")

        assert isinstance(result, dict)
        assert "query" in result

    async def test_concurrent_mcp_requests(self, mcp_client: MCPClient) -> None:
        """並行 MCP リクエストテスト"""
        await mcp_client.connect_all_servers()

        # 複数のリクエストを並行実行
        tasks = [
            mcp_client.get_aws_documentation("EC2", "instances"),
            mcp_client.get_aws_documentation("S3", "buckets"),
            mcp_client.get_aws_knowledge("Lambda functions"),
            mcp_client.get_aws_knowledge("DynamoDB tables"),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        assert len(results) == 4
        for result in results:
            if isinstance(result, Exception):
                pytest.fail(f"Concurrent request failed: {result}")
            assert isinstance(result, dict)

    async def test_mcp_client_disconnect(self, mcp_client: MCPClient) -> None:
        """MCP Client 切断テスト"""
        await mcp_client.connect_all_servers()

        await mcp_client.disconnect()

        assert not mcp_client.is_connected
        assert mcp_client.aws_docs_server_process is None
        assert mcp_client.aws_knowledge_server_process is None
