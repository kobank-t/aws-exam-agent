"""
問題データモデル

AWS試験問題の構造化データを管理するPydanticモデル
"""

from decimal import Decimal
from enum import Enum
from typing import Any

from pydantic import ConfigDict, Field, field_validator, model_validator

from .base import DynamoDBBaseModel, TimestampMixin


class DifficultyLevel(str, Enum):
    """難易度レベル"""

    PRACTITIONER = "Practitioner"
    ASSOCIATE = "Associate"
    PROFESSIONAL = "Professional"
    SPECIALTY = "Specialty"


class AWSService(str, Enum):
    """AWSサービス"""

    EC2 = "EC2"
    S3 = "S3"
    RDS = "RDS"
    LAMBDA = "Lambda"
    VPC = "VPC"
    IAM = "IAM"
    CLOUDFORMATION = "CloudFormation"
    CLOUDWATCH = "CloudWatch"
    ELB = "ELB"
    AUTOSCALING = "AutoScaling"
    ROUTE53 = "Route53"
    CLOUDFRONT = "CloudFront"
    API_GATEWAY = "API Gateway"
    DYNAMODB = "DynamoDB"
    SNS = "SNS"
    SQS = "SQS"
    KINESIS = "Kinesis"
    REDSHIFT = "Redshift"
    ELASTICSEARCH = "Elasticsearch"
    ECS = "ECS"
    EKS = "EKS"
    FARGATE = "Fargate"
    BATCH = "Batch"
    GLUE = "Glue"
    EMR = "EMR"
    SAGEMAKER = "SageMaker"
    COMPREHEND = "Comprehend"
    REKOGNITION = "Rekognition"
    POLLY = "Polly"
    LEX = "Lex"
    CONNECT = "Connect"
    WORKSPACES = "WorkSpaces"
    DIRECTORY_SERVICE = "Directory Service"
    ORGANIZATIONS = "Organizations"
    CONTROL_TOWER = "Control Tower"
    CONFIG = "Config"
    CLOUDTRAIL = "CloudTrail"
    TRUSTED_ADVISOR = "Trusted Advisor"
    SUPPORT = "Support"
    WELL_ARCHITECTED = "Well-Architected"


class Question(DynamoDBBaseModel, TimestampMixin):
    """問題データモデル"""

    # DynamoDB キー（自動生成、aliasでDynamoDB実際のフィールド名にマッピング）
    pk: str = Field(default="", alias="PK", description="パーティションキー")
    sk: str = Field(default="METADATA", alias="SK", description="ソートキー")
    entity_type: str = Field(
        default="Question", alias="EntityType", description="エンティティタイプ"
    )
    gsi1_pk: str = Field(
        default="", alias="GSI1PK", description="GSI1パーティションキー"
    )
    gsi1_sk: str = Field(default="", alias="GSI1SK", description="GSI1ソートキー")
    gsi2_pk: str = Field(
        default="", alias="GSI2PK", description="GSI2パーティションキー"
    )
    gsi2_sk: str = Field(default="", alias="GSI2SK", description="GSI2ソートキー")

    # 問題固有フィールド
    question_id: str = Field(..., description="問題ID（例: q_20250729_001）")
    question_text: str = Field(
        ..., min_length=10, max_length=2000, description="問題文"
    )
    choices: list[str] = Field(
        ..., min_length=2, max_length=6, description="選択肢リスト"
    )
    correct_answer: str = Field(..., description="正解（A, B, C, D等）")
    explanation: str = Field(..., min_length=10, max_length=1000, description="解説")

    # 分類情報
    service: AWSService = Field(..., description="対象AWSサービス")
    topic: str = Field(..., min_length=2, max_length=100, description="トピック")
    difficulty: DifficultyLevel = Field(..., description="難易度")

    # メタデータ
    source_documents: list[str] = Field(
        default_factory=list, description="参照ドキュメント"
    )
    quality_score: Decimal = Field(
        default=Decimal("0.0"), ge=0.0, le=1.0, description="品質スコア"
    )

    @field_validator("correct_answer")
    @classmethod
    def validate_correct_answer(cls, v: str, info: Any) -> str:
        """正解の妥当性チェック"""
        if "choices" in info.data:
            choices = info.data["choices"]
            # A, B, C, D形式の場合
            if v.upper() in ["A", "B", "C", "D", "E", "F"]:
                choice_index = ord(v.upper()) - ord("A")
                if choice_index >= len(choices):
                    raise ValueError(
                        f"正解 '{v}' が選択肢数 {len(choices)} を超えています"
                    )
            # 数値形式の場合
            elif v.isdigit():
                choice_index = int(v) - 1
                if choice_index >= len(choices) or choice_index < 0:
                    raise ValueError(
                        f"正解 '{v}' が選択肢範囲 1-{len(choices)} を超えています"
                    )
        return v.upper()

    @field_validator("choices")
    @classmethod
    def validate_choices(cls, v: list[str]) -> list[str]:
        """選択肢の妥当性チェック"""
        if len(v) < 2:
            raise ValueError("選択肢は最低2つ必要です")
        if len(v) > 6:
            raise ValueError("選択肢は最大6つまでです")

        # 空の選択肢チェック
        for i, choice in enumerate(v):
            if not choice.strip():
                raise ValueError(f"選択肢 {i + 1} が空です")

        return v

    @model_validator(mode="after")
    def set_dynamodb_keys(self) -> "Question":
        """DynamoDBキーを自動設定"""
        self.pk = f"QUESTION#{self.question_id}"
        self.sk = "METADATA"
        self.entity_type = "Question"
        self.gsi1_pk = f"SERVICE#{self.service.value}"
        self.gsi1_sk = f"CREATED#{self.created_at.isoformat()}"
        self.gsi2_pk = f"DIFFICULTY#{self.difficulty.value}"
        self.gsi2_sk = f"QUALITY#{self.quality_score:.3f}"
        return self

    def get_choice_by_answer(self) -> str:
        """正解に対応する選択肢テキストを取得"""
        if self.correct_answer.upper() in ["A", "B", "C", "D", "E", "F"]:
            choice_index = ord(self.correct_answer.upper()) - ord("A")
        elif self.correct_answer.isdigit():
            choice_index = int(self.correct_answer) - 1
        else:
            raise ValueError(f"不正な正解形式: {self.correct_answer}")

        if 0 <= choice_index < len(self.choices):
            return self.choices[choice_index]
        else:
            raise ValueError(f"正解インデックス {choice_index} が選択肢範囲外です")

    def is_high_quality(self, threshold: Decimal = Decimal("0.8")) -> bool:
        """高品質問題かどうかを判定"""
        return self.quality_score >= threshold

    def update_quality_score(self, new_score: Decimal) -> None:
        """品質スコアを更新"""
        if not Decimal("0.0") <= new_score <= Decimal("1.0"):
            raise ValueError("品質スコアは0.0-1.0の範囲で指定してください")

        self.quality_score = new_score
        self.update_timestamp()
        # GSI2SKも更新
        self.gsi2_sk = f"QUALITY#{self.quality_score:.3f}"

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "question_id": "q_20250729_001",
                "question_text": "Amazon VPCで複数のアベイラビリティゾーンにまたがるサブネットを作成する際の制約は何ですか？",
                "choices": [
                    "サブネットは単一のアベイラビリティゾーン内にのみ作成できる",
                    "サブネットは複数のアベイラビリティゾーンにまたがって作成できる",
                    "サブネットは同一リージョン内の全てのアベイラビリティゾーンに自動的に作成される",
                    "サブネットのアベイラビリティゾーンは後から変更できる",
                ],
                "correct_answer": "A",
                "explanation": "Amazon VPCのサブネットは、単一のアベイラビリティゾーン内にのみ作成できます。複数のAZにまたがるサブネットは作成できません。",
                "service": "VPC",
                "topic": "サブネット設計",
                "difficulty": "Associate",
                "source_documents": ["vpc-user-guide", "exam-guide"],
                "quality_score": "0.85",
            }
        }
    )
