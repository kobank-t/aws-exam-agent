"""
定数のテスト
"""

from app.shared.constants import (
    AWS_SERVICES,
    TEAMS_REACTION_EMOJIS,
    DeliveryStatus,
    DifficultyLevel,
    QualityStatus,
    QuestionType,
)


class TestEnums:
    """列挙型のテスト"""

    def test_question_type_enum(self) -> None:
        """問題タイプ列挙型のテスト"""
        assert QuestionType.MULTIPLE_CHOICE.value == "multiple_choice"
        assert QuestionType.SCENARIO_BASED.value == "scenario_based"
        assert QuestionType.DRAG_DROP.value == "drag_drop"

    def test_difficulty_level_enum(self) -> None:
        """難易度レベル列挙型のテスト"""
        assert DifficultyLevel.BEGINNER.value == "beginner"
        assert DifficultyLevel.INTERMEDIATE.value == "intermediate"
        assert DifficultyLevel.ADVANCED.value == "advanced"

    def test_delivery_status_enum(self) -> None:
        """配信ステータス列挙型のテスト"""
        assert DeliveryStatus.PENDING.value == "pending"
        assert DeliveryStatus.DELIVERED.value == "delivered"
        assert DeliveryStatus.FAILED.value == "failed"
        assert DeliveryStatus.CANCELLED.value == "cancelled"

    def test_quality_status_enum(self) -> None:
        """品質検証ステータス列挙型のテスト"""
        assert QualityStatus.PENDING.value == "pending"
        assert QualityStatus.PASSED.value == "passed"
        assert QualityStatus.FAILED.value == "failed"
        assert QualityStatus.NEEDS_REVIEW.value == "needs_review"


class TestConstants:
    """定数のテスト"""

    def test_aws_services_list(self) -> None:
        """AWS サービスリストのテスト"""
        assert isinstance(AWS_SERVICES, list)
        assert len(AWS_SERVICES) > 0
        assert "EC2" in AWS_SERVICES
        assert "S3" in AWS_SERVICES
        assert "Lambda" in AWS_SERVICES

    def test_teams_reaction_emojis(self) -> None:
        """Teams リアクション絵文字のテスト"""
        assert isinstance(TEAMS_REACTION_EMOJIS, list)
        assert len(TEAMS_REACTION_EMOJIS) == 4
        assert "🅰️" in TEAMS_REACTION_EMOJIS
        assert "🅱️" in TEAMS_REACTION_EMOJIS
