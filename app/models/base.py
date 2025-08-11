"""
基底データモデル定義

DynamoDB単一テーブル設計に対応したPydanticモデルの基底クラス
"""

from datetime import datetime
from typing import Any, Self

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class DynamoDBBaseModel(BaseModel):
    """DynamoDB用基底モデル"""

    model_config = ConfigDict(
        # 追加フィールドを許可（DynamoDBの柔軟性を活用）
        extra="allow",
        # aliasとフィールド名の両方でアクセス可能にする
        populate_by_name=True,
    )

    # 共通メタデータ
    created_at: datetime = Field(default_factory=datetime.now, description="作成日時")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新日時")
    created_by: str = Field(default="system", description="作成者")

    @field_serializer("created_at", "updated_at", when_used="json")
    def serialize_datetime(self, value: datetime | None) -> str | None:
        """datetime を ISO 形式文字列にシリアライズ"""
        return value.isoformat() if value else None

    def to_dynamodb_item(self) -> dict[str, Any]:
        """DynamoDB用のアイテム形式に変換"""
        from decimal import Decimal

        # aliasを使用してDynamoDB用のフィールド名でダンプ
        data = self.model_dump(exclude_none=True, by_alias=True)

        # datetime を ISO 文字列に変換、float を Decimal に変換、Enum を文字列に変換
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            elif isinstance(value, float):
                data[key] = Decimal(str(value))
            elif hasattr(value, "value"):  # Enum対応
                data[key] = value.value

        return data

    @classmethod
    def from_dynamodb_item(cls, item: dict[str, Any]) -> Self:
        """DynamoDBアイテムからモデルを作成"""
        # ISO 文字列を datetime に変換
        for key, value in item.items():
            if key in [
                "created_at",
                "updated_at",
                "posted_at",
                "responded_at",
                "answered_at",
            ]:
                if isinstance(value, str):
                    try:
                        item[key] = datetime.fromisoformat(value.replace("Z", "+00:00"))
                    except (ValueError, AttributeError):
                        # 変換に失敗した場合はそのまま
                        pass
            # float型をDecimal型に変換（DynamoDBのNumber型対応）
            elif key in ["quality_score", "correct_rate"] and isinstance(value, float):
                from decimal import Decimal

                item[key] = Decimal(str(value))

        return cls(**item)


class TimestampMixin(BaseModel):
    """タイムスタンプ関連のミックスイン"""

    def update_timestamp(self) -> None:
        """更新日時を現在時刻に設定"""
        self.updated_at = datetime.now()
