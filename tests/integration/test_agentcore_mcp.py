"""
AgentCore + MCP 統合テスト

AgentCore Runtime と MCP Server の統合動作をテストします。
"""

import asyncio

import pytest

from app.agentcore.agent_main import aws_info_agent


@pytest.mark.integration
class TestAgentCoreMCPIntegration:
    """AgentCore + MCP 統合テストクラス"""

    async def test_aws_info_agent_with_mcp(self) -> None:
        """AWS情報取得エージェントの MCP 統合テスト"""
        result = await aws_info_agent(service="EC2", topic="instances")

        assert isinstance(result, dict)
        assert "service" in result
        assert result["service"] == "EC2"
        assert "topic" in result
        assert result["topic"] == "instances"
        assert "mcp_integration" in result

        # MCP 統合状態の確認
        mcp_integration = result["mcp_integration"]
        assert "aws_docs_server" in mcp_integration
        assert "aws_knowledge_server" in mcp_integration

        # 接続状態は環境によって異なるため、値の存在のみ確認
        assert mcp_integration["aws_docs_server"] in ["connected", "error"]
        assert mcp_integration["aws_knowledge_server"] in ["connected", "error"]

    async def test_aws_info_agent_fallback(self) -> None:
        """AWS情報取得エージェントのフォールバック動作テスト"""
        # 無効なサービス名でテスト（フォールバック動作を確認）
        result = await aws_info_agent(service="InvalidService", topic="test")

        assert isinstance(result, dict)
        assert "service" in result
        assert result["service"] == "InvalidService"

        # フォールバックまたは正常な MCP 統合のいずれかが動作
        assert "mcp_integration" in result or "description" in result

    async def test_aws_info_agent_multiple_services(self) -> None:
        """複数サービスでの AWS情報取得エージェントテスト"""
        services = ["EC2", "S3", "Lambda", "DynamoDB"]

        tasks = [
            aws_info_agent(service=service, topic="overview") for service in services
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        assert len(results) == len(services)

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                pytest.fail(f"Service {services[i]} request failed: {result}")

            assert isinstance(result, dict)
            assert "service" in result
            assert result["service"] == services[i]

    async def test_aws_info_agent_with_empty_topic(self) -> None:
        """空のトピックでの AWS情報取得エージェントテスト"""
        result = await aws_info_agent(service="EC2", topic="")

        assert isinstance(result, dict)
        assert "service" in result
        assert result["service"] == "EC2"
        assert "topic" in result
        assert result["topic"] == ""

    async def test_aws_info_agent_error_handling(self) -> None:
        """AWS情報取得エージェントのエラーハンドリングテスト"""
        # 空のサービス名でテスト
        result = await aws_info_agent(service="", topic="test")

        assert isinstance(result, dict)
        assert "service" in result
        assert result["service"] == ""

        # エラーが発生してもレスポンスが返されることを確認
        assert "mcp_integration" in result or "description" in result

    async def test_aws_info_agent_concurrent_requests(self) -> None:
        """AWS情報取得エージェントの並行リクエストテスト"""
        # 同じサービスに対する並行リクエスト
        tasks = [aws_info_agent(service="EC2", topic=f"topic_{i}") for i in range(3)]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        assert len(results) == 3

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                pytest.fail(f"Concurrent request {i} failed: {result}")

            assert isinstance(result, dict)
            assert "service" in result
            assert result["service"] == "EC2"
            assert "topic" in result
            assert result["topic"] == f"topic_{i}"

    async def test_mcp_integration_status_validation(self) -> None:
        """MCP 統合状態の検証テスト"""
        result = await aws_info_agent(service="EC2")

        assert isinstance(result, dict)

        if "mcp_integration" in result:
            mcp_integration = result["mcp_integration"]

            # MCP 統合情報の構造確認
            assert isinstance(mcp_integration, dict)

            # 必要なキーの存在確認
            if "aws_docs_server" in mcp_integration:
                assert mcp_integration["aws_docs_server"] in ["connected", "error"]

            if "aws_knowledge_server" in mcp_integration:
                assert mcp_integration["aws_knowledge_server"] in ["connected", "error"]

        # フォールバック動作の場合
        elif "description" in result:
            assert isinstance(result["description"], str)
            assert "AWS" in result["description"]
