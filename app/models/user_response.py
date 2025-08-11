"""
ユーザー回答データモデル

Teams でのユーザー回答を管理するPydanticモデル
"""

from datetime import datetime
from enum import Enum

from pydantic import (
    ConfigDict,
    Field,
    field_serializer,
    field_validator,
    model_validator,
)

from .base import DynamoDBBaseModel, TimestampMixin


class ReactionType(str, Enum):
    """リアクション絵文字タイプ"""

    A = "🅰️"
    B = "🅱️"
    C = "🇨"
    D = "🇩"
    E = "🇪"
    F = "🇫"


class UserResponse(DynamoDBBaseModel, TimestampMixin):
    """ユーザー回答データモデル"""

    # DynamoDB キー（自動生成、aliasでDynamoDB実際のフィールド名にマッピング）
    pk: str = Field(default="", alias="PK", description="パーティションキー")
    sk: str = Field(default="", alias="SK", description="ソートキー")
    entity_type: str = Field(
        default="UserResponse", alias="EntityType", description="エンティティタイプ"
    )
    gsi1_pk: str = Field(
        default="", alias="GSI1PK", description="GSI1パーティションキー"
    )
    gsi1_sk: str = Field(default="", alias="GSI1SK", description="GSI1ソートキー")
    gsi2_pk: str = Field(
        default="", alias="GSI2PK", description="GSI2パーティションキー"
    )
    gsi2_sk: str = Field(default="", alias="GSI2SK", description="GSI2ソートキー")

    # 回答固有フィールド
    delivery_id: str = Field(..., description="配信ID")
    user_id: str = Field(..., description="ユーザーID")
    user_name: str = Field(..., min_length=1, max_length=100, description="ユーザー名")

    # 回答情報
    selected_answer: str = Field(..., description="選択した回答（A, B, C, D等）")
    is_correct: bool = Field(..., description="正解かどうか")
    responded_at: datetime = Field(default_factory=datetime.now, description="回答日時")

    # Teams 関連情報
    reaction_type: ReactionType = Field(..., description="リアクション絵文字")

    @field_serializer("responded_at", when_used="json")
    def serialize_datetime(self, value: datetime | None) -> str | None:
        """datetime を ISO 形式文字列にシリアライズ"""
        return value.isoformat() if value else None

    @field_validator("selected_answer")
    @classmethod
    def validate_selected_answer(cls, v: str) -> str:
        """選択回答の妥当性チェック"""
        v = v.upper().strip()
        if v not in ["A", "B", "C", "D", "E", "F"]:
            raise ValueError(f"選択回答は A-F の範囲で指定してください: {v}")
        return v

    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, v: str) -> str:
        """ユーザーIDの妥当性チェック"""
        if not v.strip():
            raise ValueError("ユーザーIDは空にできません")
        return v.strip()

    @field_validator("user_name")
    @classmethod
    def validate_user_name(cls, v: str) -> str:
        """ユーザー名の妥当性チェック"""
        if not v.strip():
            raise ValueError("ユーザー名は空にできません")
        return v.strip()

    @model_validator(mode="after")
    def set_dynamodb_keys(self) -> "UserResponse":
        """DynamoDBキーを自動設定"""
        self.pk = f"DELIVERY#{self.delivery_id}"
        self.sk = f"USER#{self.user_id}"
        self.entity_type = "UserResponse"
        self.gsi1_pk = f"USER#{self.user_id}"
        self.gsi1_sk = f"RESPONDED#{self.responded_at.isoformat()}"
        self.gsi2_pk = f"DELIVERY#{self.delivery_id}"
        self.gsi2_sk = f"RESPONSE#{self.responded_at.isoformat()}"
        return self

    @classmethod
    def create_from_reaction(
        cls,
        delivery_id: str,
        user_id: str,
        user_name: str,
        reaction_emoji: str,
        correct_answer: str,
    ) -> "UserResponse":
        """リアクション絵文字から回答を作成"""
        # 絵文字から選択肢を判定
        emoji_to_answer = {"🅰️": "A", "🅱️": "B", "🇨": "C", "🇩": "D", "🇪": "E", "🇫": "F"}

        selected_answer = emoji_to_answer.get(reaction_emoji)
        if not selected_answer:
            raise ValueError(
                f"サポートされていないリアクション絵文字: {reaction_emoji}"
            )

        # 正解判定
        is_correct = selected_answer.upper() == correct_answer.upper()

        return cls(
            delivery_id=delivery_id,
            user_id=user_id,
            user_name=user_name,
            selected_answer=selected_answer,
            is_correct=is_correct,
            reaction_type=ReactionType(reaction_emoji),
            responded_at=datetime.now(),
        )

    def get_response_summary(self) -> dict:
        """回答サマリーを取得"""
        return {
            "user_id": self.user_id,
            "user_name": self.user_name,
            "selected_answer": self.selected_answer,
            "is_correct": self.is_correct,
            "responded_at": self.responded_at.isoformat(),
            "reaction_type": self.reaction_type.value,
        }

    def is_recent_response(self, hours: int = 24) -> bool:
        """最近の回答かどうか"""
        time_diff = datetime.now() - self.responded_at
        return time_diff.total_seconds() < (hours * 3600)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "delivery_id": "d_20250729_001",
                "user_id": "user123",
                "user_name": "田中太郎",
                "selected_answer": "B",
                "is_correct": True,
                "responded_at": "2025-07-29T11:30:00Z",
                "reaction_type": "🅱️",
            }
        }
    )
