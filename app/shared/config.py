"""
設定管理

環境変数からの設定読み込みと設定クラスを定義します。
"""

from typing import Any

from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """アプリケーション設定"""

    # 基本設定
    APP_NAME: str = "aws-exam-agent"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # AWS 設定
    AWS_REGION: str = "us-east-1"  # Virginia - Bedrock AgentCore対応リージョン
    AWS_PROFILE: str | None = None

    # DynamoDB 設定
    DYNAMODB_TABLE_NAME: str = "aws-exam-agent-questions"
    DYNAMODB_REGION: str = "us-east-1"  # AgentCoreと統一

    # Bedrock 設定
    BEDROCK_REGION: str = "us-east-1"  # AgentCoreと統一
    BEDROCK_MODEL_ID: str = "anthropic.claude-3-5-sonnet-20241022-v2:0"
    BEDROCK_MAX_TOKENS: int = 4000
    BEDROCK_TEMPERATURE: float = 0.7

    # Teams 設定
    TEAMS_WEBHOOK_URL: str | None = None
    TEAMS_CHANNEL_ID: str | None = None

    # MCP 設定
    MCP_AWS_DOCS_SERVER_ENABLED: bool = True
    MCP_AWS_KNOWLEDGE_SERVER_ENABLED: bool = True
    MCP_SERVER_TIMEOUT: int = 30

    # キャッシュ設定
    CACHE_TTL_SECONDS: int = 3600
    MEMORY_CACHE_MAX_SIZE: int = 100

    # 問題生成設定
    QUESTION_GENERATION_MAX_RETRIES: int = 3
    QUALITY_THRESHOLD: float = 0.8
    SIMILARITY_THRESHOLD: float = 0.7

    model_config = {"env_file": ".env", "case_sensitive": True}


class AgentCoreConfig(BaseSettings):
    """AgentCore 固有の設定"""

    # AgentCore Runtime 設定
    AGENTCORE_RUNTIME_NAME: str = "aws-exam-agent-runtime"
    AGENTCORE_AGENT_NAME: str = "supervisor-agent"
    AGENTCORE_TIMEOUT: int = 300
    AGENTCORE_MEMORY_SIZE: int = 1024
    AGENTCORE_EPHEMERAL_STORAGE: int = 512

    # IAM 設定
    AGENTCORE_EXECUTION_ROLE: str | None = None
    AGENTCORE_EXECUTION_ROLE_NAME: str = "BedrockAgentCoreExecutionRole"

    # VPC 設定（必要に応じて）
    AGENTCORE_VPC_CONFIG: dict | None = None
    AGENTCORE_SUBNET_IDS: list[str] | None = None
    AGENTCORE_SECURITY_GROUP_IDS: list[str] | None = None

    # エージェント設定
    AGENTCORE_AGENT_DESCRIPTION: str = "AWS Exam Agent の監督者エージェント。専門エージェントを統合して問題生成・配信を行います。"
    AGENTCORE_AGENT_INSTRUCTION: str = "AWS試験問題の生成・品質管理・配信を行う監督者エージェントとして動作してください。"

    # LLM モデル設定
    AGENTCORE_PRIMARY_MODEL_ID: str = "anthropic.claude-3-5-sonnet-20241022-v2:0"
    AGENTCORE_FALLBACK_MODEL_ID: str = "anthropic.claude-3-haiku-20240307-v1:0"
    AGENTCORE_MAX_TOKENS: int = 4000
    AGENTCORE_TEMPERATURE: float = 0.7

    # MCP Server 設定
    AGENTCORE_MCP_AWS_DOCS_ENABLED: bool = True
    AGENTCORE_MCP_AWS_KNOWLEDGE_ENABLED: bool = True
    AGENTCORE_MCP_SERVER_TIMEOUT: int = 30

    # ストリーミング設定
    AGENTCORE_STREAMING_ENABLED: bool = True
    AGENTCORE_STREAMING_CHUNK_SIZE: int = 1024

    # エラーハンドリング設定
    AGENTCORE_MAX_RETRIES: int = 3
    AGENTCORE_RETRY_DELAY: float = 1.0
    AGENTCORE_CIRCUIT_BREAKER_THRESHOLD: int = 5

    # ログ設定
    AGENTCORE_LOG_LEVEL: str = "INFO"
    AGENTCORE_LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    model_config = {"env_file": ".env", "case_sensitive": True}


class LambdaConfig(BaseSettings):
    """Lambda 固有の設定"""

    # Lambda 基本設定
    LAMBDA_TIMEOUT: int = 300
    LAMBDA_MEMORY_SIZE: int = 512

    # API Gateway 設定
    API_GATEWAY_STAGE: str = "prod"
    API_KEY_REQUIRED: bool = True

    model_config = {"env_file": ".env", "case_sensitive": True}


# グローバル設定インスタンス
config = Config()
agentcore_config = AgentCoreConfig()
lambda_config = LambdaConfig()


def get_agentcore_runtime_config() -> dict[str, Any]:
    """
    AgentCore Runtime用の設定辞書を取得

    Returns:
        AgentCore Runtime設定の辞書
    """
    return {
        "runtime_name": agentcore_config.AGENTCORE_RUNTIME_NAME,
        "agent_name": agentcore_config.AGENTCORE_AGENT_NAME,
        "timeout": agentcore_config.AGENTCORE_TIMEOUT,
        "memory_size": agentcore_config.AGENTCORE_MEMORY_SIZE,
        "ephemeral_storage": agentcore_config.AGENTCORE_EPHEMERAL_STORAGE,
        "execution_role": agentcore_config.AGENTCORE_EXECUTION_ROLE,
        "execution_role_name": agentcore_config.AGENTCORE_EXECUTION_ROLE_NAME,
        "vpc_config": agentcore_config.AGENTCORE_VPC_CONFIG,
        "subnet_ids": agentcore_config.AGENTCORE_SUBNET_IDS,
        "security_group_ids": agentcore_config.AGENTCORE_SECURITY_GROUP_IDS,
    }


def get_agentcore_agent_config() -> dict[str, Any]:
    """
    AgentCore エージェント用の設定辞書を取得

    Returns:
        AgentCore エージェント設定の辞書
    """
    return {
        "agent_name": agentcore_config.AGENTCORE_AGENT_NAME,
        "description": agentcore_config.AGENTCORE_AGENT_DESCRIPTION,
        "instruction": agentcore_config.AGENTCORE_AGENT_INSTRUCTION,
        "primary_model_id": agentcore_config.AGENTCORE_PRIMARY_MODEL_ID,
        "fallback_model_id": agentcore_config.AGENTCORE_FALLBACK_MODEL_ID,
        "max_tokens": agentcore_config.AGENTCORE_MAX_TOKENS,
        "temperature": agentcore_config.AGENTCORE_TEMPERATURE,
        "streaming_enabled": agentcore_config.AGENTCORE_STREAMING_ENABLED,
        "streaming_chunk_size": agentcore_config.AGENTCORE_STREAMING_CHUNK_SIZE,
    }


def get_agentcore_mcp_config() -> dict[str, Any]:
    """
    AgentCore MCP Server用の設定辞書を取得

    Returns:
        MCP Server設定の辞書
    """
    return {
        "aws_docs_enabled": agentcore_config.AGENTCORE_MCP_AWS_DOCS_ENABLED,
        "aws_knowledge_enabled": agentcore_config.AGENTCORE_MCP_AWS_KNOWLEDGE_ENABLED,
        "server_timeout": agentcore_config.AGENTCORE_MCP_SERVER_TIMEOUT,
    }


def get_agentcore_error_handling_config() -> dict[str, Any]:
    """
    AgentCore エラーハンドリング用の設定辞書を取得

    Returns:
        エラーハンドリング設定の辞書
    """
    return {
        "max_retries": agentcore_config.AGENTCORE_MAX_RETRIES,
        "retry_delay": agentcore_config.AGENTCORE_RETRY_DELAY,
        "circuit_breaker_threshold": agentcore_config.AGENTCORE_CIRCUIT_BREAKER_THRESHOLD,
    }


def get_agentcore_log_config() -> dict[str, Any]:
    """
    AgentCore ログ用の設定辞書を取得

    Returns:
        ログ設定の辞書
    """
    return {
        "log_level": agentcore_config.AGENTCORE_LOG_LEVEL,
        "log_format": agentcore_config.AGENTCORE_LOG_FORMAT,
    }
