"""
コンポーネント連携統合テスト

複数のコンポーネント間の連携動作をテストします。
- SupervisorAgent → AWS情報取得エージェント → MCP Client の連携
- Config → AgentCore → MCP接続設定の連携
- エラーハンドリングとフォールバック機能の連携
"""

import asyncio
from unittest.mock import patch

import pytest

from app.agentcore.agent_main import aws_info_agent
from app.agentcore.mcp.client import MCPClient, get_mcp_client
from app.shared.config import Config


@pytest.mark.integration
class TestComponentIntegration:
    """コンポーネント連携統合テストクラス"""

    async def test_supervisor_to_aws_info_agent_integration(self) -> None:
        """SupervisorAgent → AWS情報取得エージェント の連携テスト"""
        # AWS情報取得エージェントを直接テスト（invoke関数は@app.entrypointのため直接呼び出し不可）
        result = await aws_info_agent(service="EC2", topic="instances")

        assert isinstance(result, dict)
        assert "service" in result
        assert result["service"] == "EC2"
        assert "topic" in result
        assert result["topic"] == "instances"

        # MCP統合状態の確認
        if "mcp_integration" in result:
            mcp_integration = result["mcp_integration"]
            assert isinstance(mcp_integration, dict)

    async def test_aws_info_agent_to_mcp_client_integration(self) -> None:
        """AWS情報取得エージェント → MCP Client の連携テスト"""
        # MCP Clientの取得
        mcp_client = await get_mcp_client()
        assert isinstance(mcp_client, MCPClient)

        # AWS情報取得エージェントの実行
        result = await aws_info_agent(service="EC2", topic="instances")

        assert isinstance(result, dict)
        assert "service" in result
        assert result["service"] == "EC2"
        assert "topic" in result
        assert result["topic"] == "instances"

        # MCP統合状態の確認
        if "mcp_integration" in result:
            mcp_integration = result["mcp_integration"]
            assert isinstance(mcp_integration, dict)

    async def test_config_to_mcp_integration(self) -> None:
        """Config → MCP Client 設定連携テスト"""
        config = Config()

        # 設定値の確認
        assert hasattr(config, "MCP_AWS_DOCS_SERVER_ENABLED")

        # AgentCore設定の確認
        from app.shared.config import agentcore_config

        assert hasattr(agentcore_config, "AGENTCORE_STREAMING_ENABLED")

        # MCP Clientでの設定値利用確認
        mcp_client = MCPClient()

        # 設定に基づく動作確認
        if config.MCP_AWS_DOCS_SERVER_ENABLED:
            # AWS Docs Server接続試行
            result = await mcp_client.connect_aws_docs_server()
            assert isinstance(result, bool)

    async def test_error_handling_integration(self) -> None:
        """エラーハンドリング統合テスト"""
        # 無効な入力でのエラーハンドリング確認
        result = await aws_info_agent(service="", topic="")

        assert isinstance(result, dict)
        assert "service" in result
        assert result["service"] == ""

        # エラー状態でもレスポンスが返されることを確認
        assert "mcp_integration" in result or "description" in result

    async def test_concurrent_component_integration(self) -> None:
        """並行処理でのコンポーネント連携テスト"""
        # 複数のAWS情報取得エージェントを並行実行
        tasks = [
            aws_info_agent(service="EC2", topic="instances"),
            aws_info_agent(service="S3", topic="buckets"),
            aws_info_agent(service="Lambda", topic="functions"),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        assert len(results) == 3

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                pytest.fail(f"Concurrent request {i} failed: {result}")

            assert isinstance(result, dict)
            assert "service" in result
            assert "topic" in result

    async def test_supervisor_agent_full_flow_integration(self) -> None:
        """SupervisorAgent 全体フロー統合テスト"""
        # 複数のサービスでのAWS情報取得エージェントテスト
        topics = ["EC2", "S3", "Lambda"]

        for topic in topics:
            result = await aws_info_agent(service=topic, topic="overview")

            assert isinstance(result, dict)
            assert "service" in result
            assert result["service"] == topic

            # MCP統合状態の確認
            if "mcp_integration" in result:
                mcp_integration = result["mcp_integration"]
                assert isinstance(mcp_integration, dict)

    async def test_mcp_client_lifecycle_integration(self) -> None:
        """MCP Client ライフサイクル統合テスト"""
        mcp_client = MCPClient()

        # 初期状態確認
        assert not mcp_client.is_connected

        # 接続試行
        connection_result = await mcp_client.connect_all_servers()
        assert isinstance(connection_result, bool)

        # 接続状態に応じた動作確認
        # 接続成功時のテスト（現在のモック実装では常に接続可能）
        # AWS Documentation取得テスト
        doc_result = await mcp_client.get_aws_documentation("EC2", "overview")
        assert isinstance(doc_result, dict)

        # AWS Knowledge取得テスト
        knowledge_result = await mcp_client.get_aws_knowledge("EC2 best practices")
        assert isinstance(knowledge_result, dict)

        # 接続状態の基本確認（接続結果に関わらず実行）
        assert isinstance(mcp_client.is_connected, bool)

        # 切断テスト（接続状態に関わらず実行）
        await mcp_client.disconnect()
        assert not mcp_client.is_connected

    async def test_config_environment_integration(self) -> None:
        """Config 環境変数統合テスト"""
        config = Config()

        # 環境変数の設定確認
        assert hasattr(config, "ENVIRONMENT")
        assert config.ENVIRONMENT == "test"

        # テスト環境固有の設定確認
        assert hasattr(config, "MCP_AWS_DOCS_SERVER_ENABLED")
        assert config.MCP_AWS_DOCS_SERVER_ENABLED is True

        # AgentCore設定の確認
        from app.shared.config import agentcore_config

        assert hasattr(agentcore_config, "AGENTCORE_STREAMING_ENABLED")
        assert agentcore_config.AGENTCORE_STREAMING_ENABLED is True

    async def test_error_propagation_integration(self) -> None:
        """エラー伝播統合テスト"""
        # MCP接続エラー時のフォールバック動作確認
        with (
            patch(
                "app.agentcore.mcp.client.MCPClient.get_aws_documentation"
            ) as mock_docs,
            patch(
                "app.agentcore.mcp.client.MCPClient.get_aws_knowledge"
            ) as mock_knowledge,
        ):
            # MCP Server呼び出し時にエラーを発生させる
            mock_docs.return_value = {"error": "Documentation server connection failed"}
            mock_knowledge.return_value = {
                "error": "Knowledge server connection failed"
            }

            result = await aws_info_agent(service="EC2", topic="instances")

            assert isinstance(result, dict)
            assert "service" in result
            assert result["service"] == "EC2"

            # エラー状態の確認
            assert "mcp_integration" in result
            mcp_integration = result["mcp_integration"]

            # 両方のサーバーでエラーが発生していることを確認
            assert mcp_integration["aws_docs_server"] == "error"
            assert mcp_integration["aws_knowledge_server"] == "error"

            # documentationとknowledgeにエラー情報が含まれていることを確認
            assert "documentation" in result
            assert "error" in result["documentation"]
            assert "knowledge" in result
            assert "error" in result["knowledge"]

    async def test_streaming_integration(self) -> None:
        """ストリーミング機能統合テスト"""
        from app.shared.config import agentcore_config

        if agentcore_config.AGENTCORE_STREAMING_ENABLED:
            # ストリーミング設定が有効な場合のAWS情報取得エージェントテスト
            result = await aws_info_agent(service="EC2", topic="instances")

            assert isinstance(result, dict)
            assert "service" in result

            # ストリーミング情報の確認（実装に応じて）
            if "streaming_info" in result:
                streaming_info = result["streaming_info"]
                assert isinstance(streaming_info, dict)
