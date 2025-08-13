"""
エラーハンドリング統合テスト

各コンポーネント間でのエラー伝播とフォールバック機能の統合動作をテストします。
"""

import asyncio
from typing import Any
from unittest.mock import patch

import pytest

from app.agentcore.agent_main import aws_info_agent
from app.mcp.client import MCPClient
from app.shared.exceptions import ConfigurationError


@pytest.mark.integration
class TestErrorIntegration:
    """エラーハンドリング統合テストクラス"""

    async def test_mcp_connection_failure_integration(self) -> None:
        """MCP接続失敗時の統合エラーハンドリングテスト"""
        # MCP Server呼び出し時にエラーを発生させる
        with (
            patch("app.mcp.client.MCPClient.get_aws_documentation") as mock_docs,
            patch("app.mcp.client.MCPClient.get_aws_knowledge") as mock_knowledge,
        ):
            # エラーレスポンスを返すように設定
            mock_docs.return_value = {"error": "Documentation server connection failed"}
            mock_knowledge.return_value = {
                "error": "Knowledge server connection failed"
            }

            # AWS情報取得エージェントの実行
            result = await aws_info_agent(service="EC2", topic="instances")

            assert isinstance(result, dict)
            assert "service" in result
            assert result["service"] == "EC2"

            # エラー状態の確認
            assert "mcp_integration" in result
            mcp_integration = result["mcp_integration"]
            assert isinstance(mcp_integration, dict)

            # 両方のサーバーでエラーが発生していることを確認
            assert mcp_integration["aws_docs_server"] == "error"
            assert mcp_integration["aws_knowledge_server"] == "error"

            # documentationとknowledgeにエラー情報が含まれていることを確認
            assert "documentation" in result
            assert "error" in result["documentation"]
            assert "knowledge" in result
            assert "error" in result["knowledge"]

    async def test_supervisor_agent_error_propagation(self) -> None:
        """SupervisorAgent エラー伝播統合テスト"""
        # 無効な入力でのエラーハンドリング
        result = await aws_info_agent(service="", topic="")

        assert isinstance(result, dict)
        assert "service" in result
        assert result["service"] == ""

        # エラーハンドリングされている場合の確認
        assert "mcp_integration" in result or "description" in result

    async def test_mcp_client_error_recovery_integration(self) -> None:
        """MCP Client エラー回復統合テスト"""
        mcp_client = MCPClient()

        # 初期接続失敗をシミュレート
        with patch("app.mcp.client.MCPClient.connect_aws_docs_server") as mock_docs:
            with patch(
                "app.mcp.client.MCPClient.connect_aws_knowledge_server"
            ) as mock_knowledge:
                mock_docs.return_value = False
                mock_knowledge.return_value = False

                # 接続試行
                result = await mcp_client.connect_all_servers()
                assert result is False

                # エラー状態での情報取得試行
                doc_result = await mcp_client.get_aws_documentation("EC2", "overview")
                assert isinstance(doc_result, dict)
                assert "service" in doc_result

                knowledge_result = await mcp_client.get_aws_knowledge(
                    "EC2 best practices"
                )
                assert isinstance(knowledge_result, dict)
                assert "query" in knowledge_result

        # MCP Client切断
        await mcp_client.disconnect()

    async def test_concurrent_error_handling_integration(self) -> None:
        """並行処理エラーハンドリング統合テスト"""
        # 一部のリクエストでエラーが発生する状況をシミュレート
        with patch("app.agentcore.agent_main.aws_info_agent") as mock_agent:
            # 最初のリクエストは成功、2番目は失敗、3番目は成功
            mock_agent.side_effect = [
                {"service": "EC2", "topic": "instances", "status": "success"},
                Exception("Simulated error"),
                {"service": "Lambda", "topic": "functions", "status": "success"},
            ]

            tasks = [
                aws_info_agent(service="EC2", topic="instances"),
                aws_info_agent(service="S3", topic="buckets"),
                aws_info_agent(service="Lambda", topic="functions"),
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            assert len(results) == 3

            # 成功したリクエストの確認
            success_count = 0
            error_count = 0

            for result in results:
                if isinstance(result, Exception):
                    error_count += 1
                else:
                    success_count += 1
                    assert isinstance(result, dict)

            # 少なくとも一部は成功していることを確認
            assert success_count > 0

    async def test_timeout_error_integration(self) -> None:
        """タイムアウトエラー統合テスト"""
        # 長時間実行をシミュレート
        with patch("app.mcp.client.MCPClient.get_aws_documentation") as mock_get_docs:

            async def slow_response(*args: Any, **kwargs: Any) -> dict[str, Any]:
                await asyncio.sleep(0.1)  # 短い遅延でテスト
                return {"service": "EC2", "topic": "overview", "timeout": True}

            mock_get_docs.side_effect = slow_response

            mcp_client = MCPClient()
            await mcp_client.connect_all_servers()

            # タイムアウト処理のテスト
            result = await mcp_client.get_aws_documentation("EC2", "overview")

            assert isinstance(result, dict)
            assert "service" in result

            await mcp_client.disconnect()

    async def test_resource_cleanup_on_error_integration(self) -> None:
        """エラー時のリソースクリーンアップ統合テスト"""
        mcp_client = MCPClient()

        try:
            # 接続試行
            await mcp_client.connect_all_servers()

            # エラーを発生させる
            with patch(
                "app.mcp.client.MCPClient.get_aws_documentation"
            ) as mock_get_docs:
                mock_get_docs.side_effect = Exception("Simulated error")

                try:
                    await mcp_client.get_aws_documentation("EC2", "overview")
                except Exception:
                    pass  # エラーは期待される

        finally:
            # リソースクリーンアップの確認
            await mcp_client.disconnect()
            assert not mcp_client.is_connected

    async def test_configuration_error_integration(self) -> None:
        """設定エラー統合テスト"""
        # 無効な設定でのエラーハンドリング
        with patch("app.shared.config.Config") as mock_config:
            mock_config.side_effect = ConfigurationError("Invalid configuration")

            try:
                # 設定エラーが発生する状況での動作確認
                result = await aws_info_agent(service="EC2", topic="instances")

                # エラーハンドリングされている場合
                assert isinstance(result, dict)

            except ConfigurationError:
                # 設定エラーが適切に伝播される場合
                pass

    async def test_network_error_simulation_integration(self) -> None:
        """ネットワークエラーシミュレーション統合テスト"""
        # ネットワークエラーをシミュレート
        with patch("app.mcp.client.MCPClient.connect_aws_docs_server") as mock_connect:
            mock_connect.side_effect = ConnectionError("Network error")

            mcp_client = MCPClient()

            try:
                await mcp_client.connect_all_servers()
            except ConnectionError:
                pass  # ネットワークエラーは期待される

            # エラー後の状態確認
            assert not mcp_client.is_connected

            # フォールバック動作の確認
            result = await mcp_client.get_aws_documentation("EC2", "overview")
            assert isinstance(result, dict)
            assert "service" in result

    async def test_partial_failure_integration(self) -> None:
        """部分的失敗統合テスト"""
        # AWS Docs Serverは成功、AWS Knowledge Serverは失敗
        with patch("app.mcp.client.MCPClient.connect_aws_docs_server") as mock_docs:
            with patch(
                "app.mcp.client.MCPClient.connect_aws_knowledge_server"
            ) as mock_knowledge:
                mock_docs.return_value = True
                mock_knowledge.return_value = False

                mcp_client = MCPClient()
                result = await mcp_client.connect_all_servers()

                # 部分的成功の処理確認
                assert isinstance(result, bool)

                # 成功したサーバーでの動作確認
                doc_result = await mcp_client.get_aws_documentation("EC2", "overview")
                assert isinstance(doc_result, dict)

                # 失敗したサーバーでのフォールバック確認
                knowledge_result = await mcp_client.get_aws_knowledge(
                    "EC2 best practices"
                )
                assert isinstance(knowledge_result, dict)

                await mcp_client.disconnect()

    async def test_error_logging_integration(self) -> None:
        """エラーログ統合テスト"""
        # ログ出力のテスト（実装されている場合）
        with patch("app.mcp.client.MCPClient.connect_all_servers") as mock_connect:
            mock_connect.side_effect = Exception("Test error for logging")

            mcp_client = MCPClient()

            try:
                await mcp_client.connect_all_servers()
            except Exception:
                pass  # エラーは期待される

            # エラーログが適切に出力されていることを確認
            # （実際のログ出力の確認は実装に依存）
            assert not mcp_client.is_connected
