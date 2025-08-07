"""
設定管理

環境変数からの設定読み込みと設定クラスを定義します。
"""

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
    AWS_REGION: str = "ap-northeast-1"
    AWS_PROFILE: str | None = None

    # DynamoDB 設定
    DYNAMODB_TABLE_NAME: str = "aws-exam-agent-questions"
    DYNAMODB_REGION: str = "ap-northeast-1"

    # Bedrock 設定
    BEDROCK_REGION: str = "us-east-1"
    BEDROCK_MODEL_ID: str = "anthropic.claude-3-5-sonnet-20241022-v2:0"
    BEDROCK_MAX_TOKENS: int = 4000
    BEDROCK_TEMPERATURE: float = 0.7

    # Teams 設定
    TEAMS_WEBHOOK_URL: str | None = None
    TEAMS_CHANNEL_ID: str | None = None

    # GitHub 設定
    GITHUB_PERSONAL_ACCESS_TOKEN: str | None = None

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

    # IAM 設定
    AGENTCORE_EXECUTION_ROLE: str | None = None

    # VPC 設定（必要に応じて）
    AGENTCORE_VPC_CONFIG: dict | None = None

    # GitHub 設定
    GITHUB_PERSONAL_ACCESS_TOKEN: str | None = None

    model_config = {"env_file": ".env", "case_sensitive": True}


class LambdaConfig(BaseSettings):
    """Lambda 固有の設定"""

    # Lambda 基本設定
    LAMBDA_TIMEOUT: int = 300
    LAMBDA_MEMORY_SIZE: int = 512

    # API Gateway 設定
    API_GATEWAY_STAGE: str = "prod"
    API_KEY_REQUIRED: bool = True

    # GitHub 設定
    GITHUB_PERSONAL_ACCESS_TOKEN: str | None = None

    model_config = {"env_file": ".env", "case_sensitive": True}


# グローバル設定インスタンス
config = Config()
agentcore_config = AgentCoreConfig()
lambda_config = LambdaConfig()
