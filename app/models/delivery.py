"""
配信履歴データモデル

Teams への問題配信履歴を管理するPydanticモデル
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import (
    ConfigDict,
    Field,
    field_serializer,
    field_validator,
    model_validator,
)

from .base import DynamoDBBaseModel, TimestampMixin


class DeliveryStatus(str, Enum):
    """配信ステータス"""

    PENDING = "pending"  # 配信待ち
    POSTED = "posted"  # 配信済み
    ANSWERED = "answered"  # 解答公開済み
    FAILED = "failed"  # 配信失敗
    CANCELLED = "cancelled"  # 配信キャンセル


class Delivery(DynamoDBBaseModel, TimestampMixin):
    """配信履歴データモデル"""

    # DynamoDB キー（自動生成、aliasでDynamoDB実際のフィールド名にマッピング）
    pk: str = Field(default="", alias="PK", description="パーティションキー")
    sk: str = Field(default="METADATA", alias="SK", description="ソートキー")
    entity_type: str = Field(
        default="Delivery", alias="EntityType", description="エンティティタイプ"
    )
    gsi1_pk: str = Field(
        default="", alias="GSI1PK", description="GSI1パーティションキー"
    )
    gsi1_sk: str = Field(default="", alias="GSI1SK", description="GSI1ソートキー")
    gsi2_pk: str = Field(
        default="", alias="GSI2PK", description="GSI2パーティションキー"
    )
    gsi2_sk: str = Field(default="", alias="GSI2SK", description="GSI2ソートキー")

    # 配信固有フィールド
    delivery_id: str = Field(..., description="配信ID（例: d_20250729_001）")
    question_id: str = Field(..., description="問題ID")

    # Teams 関連情報
    teams_message_id: str | None = Field(default=None, description="Teams メッセージID")
    teams_channel_id: str = Field(..., description="Teams チャネルID")

    # 配信情報
    posted_at: datetime | None = Field(default=None, description="配信日時")
    status: DeliveryStatus = Field(
        default=DeliveryStatus.PENDING, description="配信ステータス"
    )

    # 回答統計
    total_responses: int = Field(default=0, ge=0, description="総回答数")
    correct_responses: int = Field(default=0, ge=0, description="正解数")
    correct_rate: float | None = Field(
        default=None, ge=0.0, le=1.0, description="正解率"
    )

    # 詳細情報
    response_details: dict[str, Any] = Field(
        default_factory=dict, description="回答詳細"
    )
    error_message: str | None = Field(default=None, description="エラーメッセージ")
    answered_at: datetime | None = Field(default=None, description="解答公開日時")

    @field_serializer("posted_at", "answered_at", when_used="json")
    def serialize_datetime(self, value: datetime | None) -> str | None:
        """datetime を ISO 形式文字列にシリアライズ"""
        return value.isoformat() if value else None

    @field_validator("correct_responses")
    @classmethod
    def validate_correct_responses(cls, v: int, info: Any) -> int:
        """正解数の妥当性チェック"""
        if "total_responses" in info.data:
            total = info.data["total_responses"]
            if v > total:
                raise ValueError(f"正解数 {v} が総回答数 {total} を超えています")
        return v

    @field_validator("teams_channel_id")
    @classmethod
    def validate_teams_channel_id(cls, v: str) -> str:
        """Teams チャネルIDの形式チェック"""
        if not v.startswith("19:") or "@thread.tacv2" not in v:
            raise ValueError("Teams チャネルIDの形式が正しくありません")
        return v

    @model_validator(mode="after")
    def set_dynamodb_keys(self) -> "Delivery":
        """DynamoDBキーを自動設定"""
        self.pk = f"DELIVERY#{self.delivery_id}"
        self.sk = "METADATA"
        self.entity_type = "Delivery"
        self.gsi1_pk = f"QUESTION#{self.question_id}"
        self.gsi1_sk = f"DELIVERY#{self.delivery_id}"
        self.gsi2_pk = f"STATUS#{self.status.value}"
        posted_time = self.posted_at or self.created_at
        self.gsi2_sk = f"POSTED#{posted_time.isoformat()}"
        return self

    def calculate_correct_rate(self) -> float | None:
        """正解率を計算"""
        if self.total_responses == 0:
            return None
        return self.correct_responses / self.total_responses

    def update_response_stats(self, total: int, correct: int) -> None:
        """回答統計を更新"""
        if correct > total:
            raise ValueError(f"正解数 {correct} が総回答数 {total} を超えています")

        self.total_responses = total
        self.correct_responses = correct
        self.correct_rate = self.calculate_correct_rate()
        self.update_timestamp()

    def mark_as_posted(self, teams_message_id: str) -> None:
        """配信完了としてマーク"""
        self.status = DeliveryStatus.POSTED
        self.teams_message_id = teams_message_id
        self.posted_at = datetime.now()
        self.update_timestamp()
        # GSI2キーも更新
        self.gsi2_pk = f"STATUS#{self.status.value}"
        self.gsi2_sk = f"POSTED#{self.posted_at.isoformat()}"

    def mark_as_answered(self) -> None:
        """解答公開完了としてマーク"""
        self.status = DeliveryStatus.ANSWERED
        self.answered_at = datetime.now()
        self.update_timestamp()
        # GSI2キーも更新
        self.gsi2_pk = f"STATUS#{self.status.value}"

    def mark_as_failed(self, error_message: str) -> None:
        """配信失敗としてマーク"""
        self.status = DeliveryStatus.FAILED
        self.error_message = error_message
        self.update_timestamp()
        # GSI2キーも更新
        self.gsi2_pk = f"STATUS#{self.status.value}"

    def is_active(self) -> bool:
        """アクティブな配信かどうか"""
        return self.status in [DeliveryStatus.POSTED, DeliveryStatus.PENDING]

    def is_completed(self) -> bool:
        """完了した配信かどうか"""
        return self.status in [
            DeliveryStatus.ANSWERED,
            DeliveryStatus.FAILED,
            DeliveryStatus.CANCELLED,
        ]

    def get_response_summary(self) -> dict[str, Any]:
        """回答サマリーを取得"""
        return {
            "delivery_id": self.delivery_id,
            "question_id": self.question_id,
            "status": self.status.value,
            "total_responses": self.total_responses,
            "correct_responses": self.correct_responses,
            "correct_rate": self.correct_rate,
            "posted_at": self.posted_at.isoformat() if self.posted_at else None,
            "answered_at": self.answered_at.isoformat() if self.answered_at else None,
        }

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "delivery_id": "d_20250729_001",
                "question_id": "q_20250729_001",
                "teams_message_id": "teams_msg_12345",
                "teams_channel_id": "19:abc123@thread.tacv2",
                "posted_at": "2025-07-29T10:05:00Z",
                "status": "posted",
                "total_responses": 15,
                "correct_responses": 12,
                "correct_rate": 0.8,
                "response_details": {"A": 2, "B": 12, "C": 1, "D": 0},
            }
        }
    )
