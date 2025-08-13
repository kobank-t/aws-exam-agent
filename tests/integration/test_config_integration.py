"""
設定統合テスト

Config クラスと各コンポーネントでの設定値利用の統合動作をテストします。
"""

import os

import pytest

from app.mcp.client import MCPClient
from app.shared.config import Config


@pytest.mark.integration
class TestConfigIntegration:
    """設定統合テストクラス"""

    def test_config_initialization_integration(self) -> None:
        """Config 初期化統合テスト"""
        config = Config()

        # 必須設定項目の確認
        assert hasattr(config, "ENVIRONMENT")
        assert hasattr(config, "MCP_AWS_DOCS_SERVER_ENABLED")

        # AgentCore設定の確認
        from app.shared.config import agentcore_config

        assert hasattr(agentcore_config, "AGENTCORE_STREAMING_ENABLED")

        # 型の確認
        assert isinstance(config.ENVIRONMENT, str)
        assert isinstance(config.MCP_AWS_DOCS_SERVER_ENABLED, bool)
        assert isinstance(agentcore_config.AGENTCORE_STREAMING_ENABLED, bool)

    def test_environment_specific_config_integration(self) -> None:
        """環境固有設定統合テスト"""
        config = Config()

        # テスト環境での設定確認
        if config.ENVIRONMENT == "test":
            assert config.MCP_AWS_DOCS_SERVER_ENABLED is True

            from app.shared.config import agentcore_config

            assert agentcore_config.AGENTCORE_STREAMING_ENABLED is True

        # 設定値の妥当性確認
        assert config.ENVIRONMENT in ["development", "test", "production"]

    async def test_mcp_client_config_integration(self) -> None:
        """MCP Client 設定統合テスト"""
        config = Config()
        mcp_client = MCPClient()

        # 設定に基づくMCP Client動作確認
        if config.MCP_AWS_DOCS_SERVER_ENABLED:
            # AWS Docs Server接続設定の確認
            result = await mcp_client.connect_aws_docs_server()
            assert isinstance(result, bool)

            # 接続結果に関わらず、設定が正しく反映されていることを確認
            assert hasattr(mcp_client, "aws_docs_server_process")

        # MCP Client切断
        await mcp_client.disconnect()

    def test_config_validation_integration(self) -> None:
        """Config バリデーション統合テスト"""
        config = Config()

        # 環境変数の設定確認
        assert config.ENVIRONMENT == os.getenv("ENVIRONMENT", "development")

    def test_config_defaults_integration(self) -> None:
        """Config デフォルト値統合テスト"""
        # 環境変数を一時的にクリア
        original_env = os.environ.copy()

        try:
            # 特定の環境変数を削除
            if "MCP_AWS_DOCS_SERVER_ENABLED" in os.environ:
                del os.environ["MCP_AWS_DOCS_SERVER_ENABLED"]
            if "AGENTCORE_STREAMING_ENABLED" in os.environ:
                del os.environ["AGENTCORE_STREAMING_ENABLED"]

            config = Config()
            from app.shared.config import AgentCoreConfig

            agentcore_config = AgentCoreConfig()

            # デフォルト値の確認
            assert isinstance(config.MCP_AWS_DOCS_SERVER_ENABLED, bool)
            assert isinstance(agentcore_config.AGENTCORE_STREAMING_ENABLED, bool)

        finally:
            # 環境変数を復元
            os.environ.clear()
            os.environ.update(original_env)

    def test_config_type_conversion_integration(self) -> None:
        """Config 型変換統合テスト"""
        config = Config()

        # ブール値の型変換確認
        assert isinstance(config.MCP_AWS_DOCS_SERVER_ENABLED, bool)

        from app.shared.config import agentcore_config

        assert isinstance(agentcore_config.AGENTCORE_STREAMING_ENABLED, bool)

        # 文字列の型確認
        assert isinstance(config.ENVIRONMENT, str)

    async def test_config_runtime_modification_integration(self) -> None:
        """Config 実行時変更統合テスト"""
        config = Config()
        original_mcp_enabled = config.MCP_AWS_DOCS_SERVER_ENABLED

        # 設定値の一時的変更
        config.MCP_AWS_DOCS_SERVER_ENABLED = not original_mcp_enabled

        # MCP Clientでの変更された設定の利用確認
        mcp_client = MCPClient()

        # 変更された設定に基づく動作確認
        if config.MCP_AWS_DOCS_SERVER_ENABLED:
            result = await mcp_client.connect_aws_docs_server()
            assert isinstance(result, bool)

        # 設定を元に戻す
        config.MCP_AWS_DOCS_SERVER_ENABLED = original_mcp_enabled

        # MCP Client切断
        await mcp_client.disconnect()

    def test_config_singleton_behavior_integration(self) -> None:
        """Config シングルトン動作統合テスト"""
        config1 = Config()
        config2 = Config()

        # 同じインスタンスかどうかの確認
        # （Configクラスがシングルトンパターンを使用している場合）
        assert config1.ENVIRONMENT == config2.ENVIRONMENT
        assert (
            config1.MCP_AWS_DOCS_SERVER_ENABLED == config2.MCP_AWS_DOCS_SERVER_ENABLED
        )

        # 設定値の一貫性確認
        config1.MCP_AWS_DOCS_SERVER_ENABLED = True
        assert (
            config2.MCP_AWS_DOCS_SERVER_ENABLED == config1.MCP_AWS_DOCS_SERVER_ENABLED
        )

    def test_config_error_handling_integration(self) -> None:
        """Config エラーハンドリング統合テスト"""
        # 設定の初期化確認
        config = Config()

        # 基本設定項目の存在確認
        assert hasattr(config, "ENVIRONMENT")
        assert hasattr(config, "MCP_AWS_DOCS_SERVER_ENABLED")

    def test_config_logging_integration(self) -> None:
        """Config ログ統合テスト"""
        config = Config()

        # ログレベル設定の確認（実装されている場合）
        if hasattr(config, "LOG_LEVEL"):
            assert isinstance(config.LOG_LEVEL, str)
            assert config.LOG_LEVEL in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

        # ログ設定の妥当性確認
        if hasattr(config, "ENABLE_LOGGING"):
            assert isinstance(config.ENABLE_LOGGING, bool)
