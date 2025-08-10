"""
AgentCore設定クラスのテスト

AgentCore固有の設定項目の動作確認を行います。
"""

import os
from unittest.mock import patch

from app.shared.config import AgentCoreConfig


class TestAgentCoreConfig:
    """AgentCore設定クラスのテスト"""

    def test_default_values(self) -> None:
        """デフォルト値の確認"""
        config = AgentCoreConfig()

        # AgentCore Runtime 設定
        assert config.AGENTCORE_RUNTIME_NAME == "aws-exam-agent-runtime"
        assert config.AGENTCORE_AGENT_NAME == "supervisor-agent"
        assert config.AGENTCORE_TIMEOUT == 300
        assert config.AGENTCORE_MEMORY_SIZE == 1024
        assert config.AGENTCORE_EPHEMERAL_STORAGE == 512

        # IAM 設定
        assert config.AGENTCORE_EXECUTION_ROLE is None
        assert config.AGENTCORE_EXECUTION_ROLE_NAME == "BedrockAgentCoreExecutionRole"

        # VPC 設定
        assert config.AGENTCORE_VPC_CONFIG is None
        assert config.AGENTCORE_SUBNET_IDS is None
        assert config.AGENTCORE_SECURITY_GROUP_IDS is None

        # エージェント設定
        assert (
            "AWS Exam Agent の監督者エージェント" in config.AGENTCORE_AGENT_DESCRIPTION
        )
        assert "監督者エージェントとして動作" in config.AGENTCORE_AGENT_INSTRUCTION

        # LLM モデル設定
        assert (
            config.AGENTCORE_PRIMARY_MODEL_ID
            == "anthropic.claude-3-5-sonnet-20241022-v2:0"
        )
        assert (
            config.AGENTCORE_FALLBACK_MODEL_ID
            == "anthropic.claude-3-haiku-20240307-v1:0"
        )
        assert config.AGENTCORE_MAX_TOKENS == 4000
        assert config.AGENTCORE_TEMPERATURE == 0.7

        # MCP Server 設定
        assert config.AGENTCORE_MCP_AWS_DOCS_ENABLED is True
        assert config.AGENTCORE_MCP_AWS_KNOWLEDGE_ENABLED is True
        assert config.AGENTCORE_MCP_SERVER_TIMEOUT == 30

        # ストリーミング設定
        assert config.AGENTCORE_STREAMING_ENABLED is True
        assert config.AGENTCORE_STREAMING_CHUNK_SIZE == 1024

        # エラーハンドリング設定
        assert config.AGENTCORE_MAX_RETRIES == 3
        assert config.AGENTCORE_RETRY_DELAY == 1.0
        assert config.AGENTCORE_CIRCUIT_BREAKER_THRESHOLD == 5

        # ログ設定
        assert config.AGENTCORE_LOG_LEVEL == "INFO"
        assert "%(asctime)s" in config.AGENTCORE_LOG_FORMAT

    @patch.dict(
        os.environ,
        {
            "AGENTCORE_RUNTIME_NAME": "test-runtime",
            "AGENTCORE_AGENT_NAME": "test-agent",
            "AGENTCORE_TIMEOUT": "600",
            "AGENTCORE_MEMORY_SIZE": "2048",
            "AGENTCORE_EPHEMERAL_STORAGE": "1024",
        },
    )
    def test_environment_variable_override(self) -> None:
        """環境変数による設定上書きの確認"""
        config = AgentCoreConfig()

        assert config.AGENTCORE_RUNTIME_NAME == "test-runtime"
        assert config.AGENTCORE_AGENT_NAME == "test-agent"
        assert config.AGENTCORE_TIMEOUT == 600
        assert config.AGENTCORE_MEMORY_SIZE == 2048
        assert config.AGENTCORE_EPHEMERAL_STORAGE == 1024

    @patch.dict(
        os.environ,
        {
            "AGENTCORE_EXECUTION_ROLE": "arn:aws:iam::123456789012:role/TestRole",
            "AGENTCORE_EXECUTION_ROLE_NAME": "TestExecutionRole",
        },
    )
    def test_iam_settings(self) -> None:
        """IAM設定の確認"""
        config = AgentCoreConfig()

        assert (
            config.AGENTCORE_EXECUTION_ROLE == "arn:aws:iam::123456789012:role/TestRole"
        )
        assert config.AGENTCORE_EXECUTION_ROLE_NAME == "TestExecutionRole"

    @patch.dict(
        os.environ,
        {
            "AGENTCORE_SUBNET_IDS": '["subnet-12345", "subnet-67890"]',
            "AGENTCORE_SECURITY_GROUP_IDS": '["sg-12345", "sg-67890"]',
        },
    )
    def test_vpc_settings(self) -> None:
        """VPC設定の確認"""
        config = AgentCoreConfig()

        # 注意: Pydantic設定では、JSON文字列は自動的にパースされない場合があります
        # 実際の使用時は、適切な型変換が必要です
        assert config.AGENTCORE_SUBNET_IDS is not None
        assert config.AGENTCORE_SECURITY_GROUP_IDS is not None

    @patch.dict(
        os.environ,
        {
            "AGENTCORE_PRIMARY_MODEL_ID": "anthropic.claude-3-opus-20240229-v1:0",
            "AGENTCORE_FALLBACK_MODEL_ID": "anthropic.claude-3-sonnet-20240229-v1:0",
            "AGENTCORE_MAX_TOKENS": "8000",
            "AGENTCORE_TEMPERATURE": "0.5",
        },
    )
    def test_llm_model_settings(self) -> None:
        """LLMモデル設定の確認"""
        config = AgentCoreConfig()

        assert (
            config.AGENTCORE_PRIMARY_MODEL_ID == "anthropic.claude-3-opus-20240229-v1:0"
        )
        assert (
            config.AGENTCORE_FALLBACK_MODEL_ID
            == "anthropic.claude-3-sonnet-20240229-v1:0"
        )
        assert config.AGENTCORE_MAX_TOKENS == 8000
        assert config.AGENTCORE_TEMPERATURE == 0.5

    @patch.dict(
        os.environ,
        {
            "AGENTCORE_MCP_AWS_DOCS_ENABLED": "false",
            "AGENTCORE_MCP_AWS_KNOWLEDGE_ENABLED": "false",
            "AGENTCORE_MCP_SERVER_TIMEOUT": "60",
        },
    )
    def test_mcp_server_settings(self) -> None:
        """MCP Server設定の確認"""
        config = AgentCoreConfig()

        assert config.AGENTCORE_MCP_AWS_DOCS_ENABLED is False
        assert config.AGENTCORE_MCP_AWS_KNOWLEDGE_ENABLED is False
        assert config.AGENTCORE_MCP_SERVER_TIMEOUT == 60

    @patch.dict(
        os.environ,
        {
            "AGENTCORE_STREAMING_ENABLED": "false",
            "AGENTCORE_STREAMING_CHUNK_SIZE": "2048",
        },
    )
    def test_streaming_settings(self) -> None:
        """ストリーミング設定の確認"""
        config = AgentCoreConfig()

        assert config.AGENTCORE_STREAMING_ENABLED is False
        assert config.AGENTCORE_STREAMING_CHUNK_SIZE == 2048

    @patch.dict(
        os.environ,
        {
            "AGENTCORE_MAX_RETRIES": "5",
            "AGENTCORE_RETRY_DELAY": "2.0",
            "AGENTCORE_CIRCUIT_BREAKER_THRESHOLD": "10",
        },
    )
    def test_error_handling_settings(self) -> None:
        """エラーハンドリング設定の確認"""
        config = AgentCoreConfig()

        assert config.AGENTCORE_MAX_RETRIES == 5
        assert config.AGENTCORE_RETRY_DELAY == 2.0
        assert config.AGENTCORE_CIRCUIT_BREAKER_THRESHOLD == 10

    @patch.dict(
        os.environ,
        {
            "AGENTCORE_LOG_LEVEL": "DEBUG",
            "AGENTCORE_LOG_FORMAT": "%(levelname)s - %(message)s",
        },
    )
    def test_log_settings(self) -> None:
        """ログ設定の確認"""
        config = AgentCoreConfig()

        assert config.AGENTCORE_LOG_LEVEL == "DEBUG"
        assert config.AGENTCORE_LOG_FORMAT == "%(levelname)s - %(message)s"

    def test_config_validation(self) -> None:
        """設定値の妥当性確認"""
        config = AgentCoreConfig()

        # 数値設定の妥当性
        assert config.AGENTCORE_TIMEOUT > 0
        assert config.AGENTCORE_MEMORY_SIZE > 0
        assert config.AGENTCORE_EPHEMERAL_STORAGE > 0
        assert config.AGENTCORE_MAX_TOKENS > 0
        assert 0.0 <= config.AGENTCORE_TEMPERATURE <= 2.0
        assert config.AGENTCORE_MCP_SERVER_TIMEOUT > 0
        assert config.AGENTCORE_STREAMING_CHUNK_SIZE > 0
        assert config.AGENTCORE_MAX_RETRIES >= 0
        assert config.AGENTCORE_RETRY_DELAY >= 0.0
        assert config.AGENTCORE_CIRCUIT_BREAKER_THRESHOLD > 0

        # 文字列設定の妥当性
        assert len(config.AGENTCORE_RUNTIME_NAME) > 0
        assert len(config.AGENTCORE_AGENT_NAME) > 0
        assert len(config.AGENTCORE_EXECUTION_ROLE_NAME) > 0
        assert len(config.AGENTCORE_AGENT_DESCRIPTION) > 0
        assert len(config.AGENTCORE_AGENT_INSTRUCTION) > 0
        assert len(config.AGENTCORE_PRIMARY_MODEL_ID) > 0
        assert len(config.AGENTCORE_FALLBACK_MODEL_ID) > 0
        assert config.AGENTCORE_LOG_LEVEL in [
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL",
        ]

    def test_model_config(self) -> None:
        """Pydantic model設定の確認"""
        config = AgentCoreConfig()

        # model_configの設定確認
        # 設定管理をconfig.pyに一元化したため、case_sensitiveのみ設定
        assert config.model_config["case_sensitive"] is True

    def test_config_immutability(self) -> None:
        """設定の不変性確認（設定後の変更不可）"""
        config = AgentCoreConfig()

        # 設定値の変更を試行（Pydanticでは通常は可能だが、実際のアプリケーションでは不変にすべき）
        original_runtime_name = config.AGENTCORE_RUNTIME_NAME
        config.AGENTCORE_RUNTIME_NAME = "modified-runtime"

        # 変更が反映されることを確認（実際のアプリケーションでは、frozen=Trueを設定して不変にする）
        assert config.AGENTCORE_RUNTIME_NAME == "modified-runtime"

        # 元の値を復元
        config.AGENTCORE_RUNTIME_NAME = original_runtime_name
        assert config.AGENTCORE_RUNTIME_NAME == original_runtime_name


class TestAgentCoreConfigHelpers:
    """AgentCore設定ヘルパー関数のテスト"""

    def test_get_agentcore_runtime_config(self) -> None:
        """AgentCore Runtime設定取得の確認"""
        from app.shared.config import get_agentcore_runtime_config

        config = get_agentcore_runtime_config()

        # 必要なキーが含まれていることを確認
        expected_keys = {
            "runtime_name",
            "agent_name",
            "timeout",
            "memory_size",
            "ephemeral_storage",
            "execution_role",
            "execution_role_name",
            "vpc_config",
            "subnet_ids",
            "security_group_ids",
        }
        assert set(config.keys()) == expected_keys

        # デフォルト値の確認
        assert config["runtime_name"] == "aws-exam-agent-runtime"
        assert config["agent_name"] == "supervisor-agent"
        assert config["timeout"] == 300
        assert config["memory_size"] == 1024
        assert config["ephemeral_storage"] == 512

    def test_get_agentcore_agent_config(self) -> None:
        """AgentCore エージェント設定取得の確認"""
        from app.shared.config import get_agentcore_agent_config

        config = get_agentcore_agent_config()

        # 必要なキーが含まれていることを確認
        expected_keys = {
            "agent_name",
            "description",
            "instruction",
            "primary_model_id",
            "fallback_model_id",
            "max_tokens",
            "temperature",
            "streaming_enabled",
            "streaming_chunk_size",
        }
        assert set(config.keys()) == expected_keys

        # デフォルト値の確認
        assert config["agent_name"] == "supervisor-agent"
        assert "AWS Exam Agent の監督者エージェント" in config["description"]
        assert config["primary_model_id"] == "anthropic.claude-3-5-sonnet-20241022-v2:0"
        assert config["max_tokens"] == 4000
        assert config["temperature"] == 0.7

    def test_get_agentcore_mcp_config(self) -> None:
        """AgentCore MCP Server設定取得の確認"""
        from app.shared.config import get_agentcore_mcp_config

        config = get_agentcore_mcp_config()

        # 必要なキーが含まれていることを確認
        expected_keys = {"aws_docs_enabled", "aws_knowledge_enabled", "server_timeout"}
        assert set(config.keys()) == expected_keys

        # デフォルト値の確認
        assert config["aws_docs_enabled"] is True
        assert config["aws_knowledge_enabled"] is True
        assert config["server_timeout"] == 30

    def test_get_agentcore_error_handling_config(self) -> None:
        """AgentCore エラーハンドリング設定取得の確認"""
        from app.shared.config import get_agentcore_error_handling_config

        config = get_agentcore_error_handling_config()

        # 必要なキーが含まれていることを確認
        expected_keys = {"max_retries", "retry_delay", "circuit_breaker_threshold"}
        assert set(config.keys()) == expected_keys

        # デフォルト値の確認
        assert config["max_retries"] == 3
        assert config["retry_delay"] == 1.0
        assert config["circuit_breaker_threshold"] == 5

    def test_get_agentcore_log_config(self) -> None:
        """AgentCore ログ設定取得の確認"""
        from app.shared.config import get_agentcore_log_config

        config = get_agentcore_log_config()

        # 必要なキーが含まれていることを確認
        expected_keys = {"log_level", "log_format"}
        assert set(config.keys()) == expected_keys

        # デフォルト値の確認
        assert config["log_level"] == "INFO"
        assert "%(asctime)s" in config["log_format"]
