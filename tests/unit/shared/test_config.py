"""
設定管理のテスト
"""

import pytest

from app.shared.config import AgentCoreConfig, Config, LambdaConfig


@pytest.mark.unit
class TestConfig:
    """設定クラスのテスト"""

    def test_default_config_values(self) -> None:
        """デフォルト設定値のテスト"""
        config = Config()

        assert config.APP_NAME == "aws-exam-agent"
        assert config.APP_VERSION == "0.1.0"
        # テスト環境では ENVIRONMENT が "test" に設定される
        assert config.ENVIRONMENT in ["development", "test"]
        # テスト環境では DEBUG が True に設定される場合がある
        assert isinstance(config.DEBUG, bool)
        # テスト環境では LOG_LEVEL が "DEBUG" に設定される場合がある
        assert config.LOG_LEVEL in ["INFO", "DEBUG"]
        assert config.AWS_REGION == "ap-northeast-1"
        assert config.BEDROCK_REGION == "us-east-1"

    def test_environment_variable_override(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """環境変数による設定上書きのテスト"""
        monkeypatch.setenv("APP_NAME", "test-app")
        monkeypatch.setenv("DEBUG", "true")
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        monkeypatch.setenv("AWS_REGION", "us-west-2")

        config = Config()

        assert config.APP_NAME == "test-app"
        assert config.DEBUG is True
        assert config.LOG_LEVEL == "DEBUG"
        assert config.AWS_REGION == "us-west-2"

    def test_bedrock_config(self) -> None:
        """Bedrock 設定のテスト"""
        config = Config()

        assert config.BEDROCK_REGION == "us-east-1"
        assert config.BEDROCK_MODEL_ID == "anthropic.claude-3-5-sonnet-20241022-v2:0"
        assert config.BEDROCK_MAX_TOKENS == 4000
        assert config.BEDROCK_TEMPERATURE == 0.7

    def test_teams_config(self) -> None:
        """Teams 設定のテスト"""
        config = Config()

        assert config.TEAMS_WEBHOOK_URL is None
        assert config.TEAMS_CHANNEL_ID is None

    def test_mcp_config(self) -> None:
        """MCP 設定のテスト"""
        config = Config()

        assert config.MCP_AWS_DOCS_SERVER_ENABLED is True
        assert config.MCP_AWS_KNOWLEDGE_SERVER_ENABLED is True
        assert config.MCP_SERVER_TIMEOUT == 30


@pytest.mark.unit
class TestAgentCoreConfig:
    """AgentCore 設定のテスト"""

    def test_default_agentcore_config(self) -> None:
        """デフォルト AgentCore 設定のテスト"""
        config = AgentCoreConfig()

        assert config.AGENTCORE_RUNTIME_NAME == "aws-exam-agent-runtime"
        assert config.AGENTCORE_AGENT_NAME == "supervisor-agent"
        assert config.AGENTCORE_TIMEOUT == 300
        assert config.AGENTCORE_EXECUTION_ROLE is None
        assert config.AGENTCORE_VPC_CONFIG is None


@pytest.mark.unit
class TestLambdaConfig:
    """Lambda 設定のテスト"""

    def test_default_lambda_config(self) -> None:
        """デフォルト Lambda 設定のテスト"""
        config = LambdaConfig()

        assert config.LAMBDA_TIMEOUT == 300
        assert config.LAMBDA_MEMORY_SIZE == 512
        assert config.API_GATEWAY_STAGE == "prod"
        assert config.API_KEY_REQUIRED is True
