"""
例外クラスのテスト
"""

from app.shared.exceptions import (
    AgentError,
    AWSExamAgentError,
    AWSServiceError,
    CacheError,
    ConfigurationError,
    DataModelError,
    MCPIntegrationError,
    QualityValidationError,
    QuestionGenerationError,
    TeamsIntegrationError,
)


class TestExceptions:
    """例外クラスのテスト"""

    def test_base_exception(self) -> None:
        """基底例外クラスのテスト"""
        message = "Test error message"
        error_code = "TEST_ERROR"
        details = {"key": "value"}

        error = AWSExamAgentError(message, error_code, details)

        assert str(error) == message
        assert error.message == message
        assert error.error_code == error_code
        assert error.details == details

    def test_base_exception_minimal(self) -> None:
        """基底例外クラスの最小構成テスト"""
        message = "Test error"

        error = AWSExamAgentError(message)

        assert str(error) == message
        assert error.message == message
        assert error.error_code is None
        assert error.details == {}

    def test_agent_error(self) -> None:
        """エージェントエラーのテスト"""
        error = AgentError("Agent failed")

        assert isinstance(error, AWSExamAgentError)
        assert str(error) == "Agent failed"

    def test_question_generation_error(self) -> None:
        """問題生成エラーのテスト"""
        error = QuestionGenerationError("Failed to generate question")

        assert isinstance(error, AWSExamAgentError)
        assert str(error) == "Failed to generate question"

    def test_quality_validation_error(self) -> None:
        """品質検証エラーのテスト"""
        error = QualityValidationError("Quality check failed")

        assert isinstance(error, AWSExamAgentError)
        assert str(error) == "Quality check failed"

    def test_mcp_integration_error(self) -> None:
        """MCP 統合エラーのテスト"""
        error = MCPIntegrationError("MCP server connection failed")

        assert isinstance(error, AWSExamAgentError)
        assert str(error) == "MCP server connection failed"

    def test_teams_integration_error(self) -> None:
        """Teams 統合エラーのテスト"""
        error = TeamsIntegrationError("Teams webhook failed")

        assert isinstance(error, AWSExamAgentError)
        assert str(error) == "Teams webhook failed"

    def test_data_model_error(self) -> None:
        """データモデルエラーのテスト"""
        error = DataModelError("Invalid data format")

        assert isinstance(error, AWSExamAgentError)
        assert str(error) == "Invalid data format"

    def test_cache_error(self) -> None:
        """キャッシュエラーのテスト"""
        error = CacheError("Cache operation failed")

        assert isinstance(error, AWSExamAgentError)
        assert str(error) == "Cache operation failed"

    def test_configuration_error(self) -> None:
        """設定エラーのテスト"""
        error = ConfigurationError("Invalid configuration")

        assert isinstance(error, AWSExamAgentError)
        assert str(error) == "Invalid configuration"

    def test_aws_service_error(self) -> None:
        """AWS サービスエラーのテスト"""
        error = AWSServiceError("AWS API call failed")

        assert isinstance(error, AWSExamAgentError)
        assert str(error) == "AWS API call failed"
