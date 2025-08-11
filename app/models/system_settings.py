"""
システム設定データモデル

アプリケーション全体の設定を管理するPydanticモデル
"""

from datetime import time

from pydantic import ConfigDict, Field, field_validator, model_validator

from .base import DynamoDBBaseModel, TimestampMixin


class SystemSettings(DynamoDBBaseModel, TimestampMixin):
    """システム設定データモデル"""

    # DynamoDB キー（固定値、aliasでDynamoDB実際のフィールド名にマッピング）
    pk: str = Field(default="SETTINGS", alias="PK", description="パーティションキー")
    sk: str = Field(default="CONFIG", alias="SK", description="ソートキー")
    entity_type: str = Field(
        default="SystemSettings", alias="EntityType", description="エンティティタイプ"
    )

    # Teams 設定
    teams_channel_id: str = Field(..., description="Teams チャネルID")

    # 配信設定
    daily_question_time: str = Field(
        default="10:00", description="日次問題配信時刻（HH:MM形式）"
    )
    answer_reveal_delay: int = Field(
        default=24, ge=1, le=168, description="解答公開までの時間（時間）"
    )
    max_questions_per_day: int = Field(
        default=1, ge=1, le=10, description="1日あたりの最大問題数"
    )

    # 品質設定
    quality_threshold: float = Field(
        default=0.8, ge=0.0, le=1.0, description="品質閾値"
    )

    # 管理情報
    updated_by: str = Field(default="admin", description="更新者")

    @field_validator("teams_channel_id")
    @classmethod
    def validate_teams_channel_id(cls, v: str) -> str:
        """Teams チャネルIDの形式チェック"""
        if not v.startswith("19:") or "@thread.tacv2" not in v:
            raise ValueError("Teams チャネルIDの形式が正しくありません")
        return v

    @field_validator("daily_question_time")
    @classmethod
    def validate_daily_question_time(cls, v: str) -> str:
        """時刻形式の妥当性チェック"""
        try:
            time.fromisoformat(v)
        except ValueError as e:
            raise ValueError("時刻は HH:MM 形式で指定してください") from e
        return v

    @model_validator(mode="after")
    def set_dynamodb_keys(self) -> "SystemSettings":
        """DynamoDBキーを設定（固定値）"""
        self.pk = "SETTINGS"
        self.sk = "CONFIG"
        self.entity_type = "SystemSettings"
        return self

    def get_question_time_as_time(self) -> time:
        """配信時刻をtimeオブジェクトとして取得"""
        return time.fromisoformat(self.daily_question_time)

    def update_teams_channel(self, channel_id: str, updated_by: str = "admin") -> None:
        """Teams チャネルを更新"""
        self.teams_channel_id = channel_id
        self.updated_by = updated_by
        self.update_timestamp()

    def update_quality_threshold(
        self, threshold: float, updated_by: str = "admin"
    ) -> None:
        """品質閾値を更新"""
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("品質閾値は0.0-1.0の範囲で指定してください")

        self.quality_threshold = threshold
        self.updated_by = updated_by
        self.update_timestamp()

    def update_schedule_settings(
        self,
        question_time: str | None = None,
        reveal_delay: int | None = None,
        max_questions: int | None = None,
        updated_by: str = "admin",
    ) -> None:
        """スケジュール設定を更新"""
        if question_time is not None:
            self.daily_question_time = question_time
        if reveal_delay is not None:
            self.answer_reveal_delay = reveal_delay
        if max_questions is not None:
            self.max_questions_per_day = max_questions

        self.updated_by = updated_by
        self.update_timestamp()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "teams_channel_id": "19:abc123@thread.tacv2",
                "daily_question_time": "10:00",
                "answer_reveal_delay": 24,
                "max_questions_per_day": 1,
                "quality_threshold": 0.8,
                "updated_by": "admin",
            }
        }
    )
