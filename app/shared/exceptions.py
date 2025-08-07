"""
カスタム例外定義

プロジェクト固有の例外クラスを定義します。
"""

from typing import Any


class AWSExamAgentError(Exception):
    """AWS Exam Agent 基底例外クラス"""

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class AgentError(AWSExamAgentError):
    """エージェント関連エラー"""

    pass


class QuestionGenerationError(AWSExamAgentError):
    """問題生成エラー"""

    pass


class QualityValidationError(AWSExamAgentError):
    """品質検証エラー"""

    pass


class MCPIntegrationError(AWSExamAgentError):
    """MCP 統合エラー"""

    pass


class TeamsIntegrationError(AWSExamAgentError):
    """Teams 統合エラー"""

    pass


class DataModelError(AWSExamAgentError):
    """データモデルエラー"""

    pass


class CacheError(AWSExamAgentError):
    """キャッシュエラー"""

    pass


class ConfigurationError(AWSExamAgentError):
    """設定エラー"""

    pass


class AWSServiceError(AWSExamAgentError):
    """AWS サービスエラー"""

    pass
