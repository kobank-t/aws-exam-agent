"""
共通定数定義

プロジェクト全体で使用される定数を定義します。
"""

from enum import Enum


class QuestionType(str, Enum):
    """問題タイプ"""

    MULTIPLE_CHOICE = "multiple_choice"
    SCENARIO_BASED = "scenario_based"
    DRAG_DROP = "drag_drop"


class DifficultyLevel(str, Enum):
    """難易度レベル"""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class DeliveryStatus(str, Enum):
    """配信ステータス"""

    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"


class QualityStatus(str, Enum):
    """品質検証ステータス"""

    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    NEEDS_REVIEW = "needs_review"


# AWS サービス関連
AWS_SERVICES = [
    "EC2",
    "S3",
    "VPC",
    "RDS",
    "Lambda",
    "CloudFormation",
    "IAM",
    "CloudWatch",
    "ELB",
    "Auto Scaling",
    "Route 53",
    "CloudFront",
    "API Gateway",
    "DynamoDB",
    "SQS",
    "SNS",
    "ECS",
    "EKS",
    "Fargate",
    "ElastiCache",
]

# 問題生成関連
DEFAULT_QUESTION_COUNT = 1
MAX_QUESTION_LENGTH = 2000
MAX_OPTION_COUNT = 6
MIN_OPTION_COUNT = 2
MAX_EXPLANATION_LENGTH = 1000

# Teams 関連
TEAMS_REACTION_EMOJIS = ["🅰️", "🅱️", "🇨", "🇩"]
TEAMS_MESSAGE_MAX_LENGTH = 4000

# キャッシュ関連
CACHE_TTL_SECONDS = 3600  # 1時間
MEMORY_CACHE_MAX_SIZE = 100

# ログ関連
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_LOG_LEVEL = "INFO"
