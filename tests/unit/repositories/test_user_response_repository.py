"""
ユーザー回答リポジトリの単体テスト

外部依存のない純粋なロジックのテスト
"""

from datetime import UTC, datetime

from app.models.user_response import ReactionType, UserResponse
from app.repositories.user_response_repository import UserResponseRepository


class TestUserResponseRepository:
    """ユーザー回答リポジトリの純粋ロジックテスト"""

    def test_to_model_conversion(self) -> None:
        """DynamoDBアイテム → UserResponseモデル変換ロジック"""
        repository = UserResponseRepository("dummy-table")

        # DynamoDBアイテム形式のテストデータ
        item = {
            "PK": "DELIVERY#d001",
            "SK": "USER#u001",
            "delivery_id": "d001",
            "user_id": "u001",
            "user_name": "テストユーザー名前",
            "selected_answer": "A",
            "is_correct": True,
            "reaction_type": "🅰️",
            "responded_at": "2025-08-11T15:30:00+00:00",
            "created_at": "2025-08-11T15:30:00+00:00",
            "updated_at": "2025-08-11T15:30:00+00:00",
            "GSI1PK": "USER#u001",
            "GSI1SK": "DELIVERY#d001",
            "GSI2PK": "DELIVERY#d001",
            "GSI2SK": "2025-08-11T15:30:00+00:00",
        }

        # 変換実行
        result = repository._to_model(item)

        # 変換結果の検証
        assert isinstance(result, UserResponse)
        assert result.delivery_id == "d001"
        assert result.user_id == "u001"
        assert result.user_name == "テストユーザー名前"
        assert result.selected_answer == "A"
        assert result.is_correct is True
        assert result.reaction_type == ReactionType.A
        assert result.responded_at == datetime(2025, 8, 11, 15, 30, 0, tzinfo=UTC)

    def test_from_model_conversion(self) -> None:
        """UserResponseモデル → DynamoDBアイテム変換ロジック"""
        repository = UserResponseRepository("dummy-table")

        # UserResponseモデルのテストデータ
        user_response = UserResponse(
            delivery_id="d001",
            user_id="u001",
            user_name="テストユーザー名前",
            selected_answer="A",
            is_correct=True,
            reaction_type=ReactionType.A,
            responded_at=datetime(2025, 8, 11, 15, 30, 0, tzinfo=UTC),
            created_at=datetime(2025, 8, 11, 15, 30, 0, tzinfo=UTC),
            updated_at=datetime(2025, 8, 11, 15, 30, 0, tzinfo=UTC),
        )

        # 変換実行
        result = repository._from_model(user_response)

        # 変換結果の検証
        assert isinstance(result, dict)
        assert result["PK"] == "DELIVERY#d001"
        assert result["SK"] == "USER#u001"
        assert result["delivery_id"] == "d001"
        assert result["user_id"] == "u001"
        assert result["user_name"] == "テストユーザー名前"
        assert result["selected_answer"] == "A"
        assert result["is_correct"] is True
        assert result["reaction_type"] == "🅰️"
        assert result["responded_at"] == "2025-08-11T15:30:00+00:00"
        assert result["GSI1PK"] == "USER#u001"
        assert result["GSI1SK"] == "RESPONDED#2025-08-11T15:30:00+00:00"
        assert result["GSI2PK"] == "DELIVERY#d001"
        assert result["GSI2SK"] == "RESPONSE#2025-08-11T15:30:00+00:00"

    def test_reaction_type_conversion(self) -> None:
        """ReactionType変換の境界値テスト"""
        repository = UserResponseRepository("dummy-table")

        # 各ReactionTypeの変換テスト
        test_cases = [
            ("🅰️", ReactionType.A),
            ("🅱️", ReactionType.B),
            ("🇨", ReactionType.C),
            ("🇩", ReactionType.D),
        ]

        for reaction_str, expected_enum in test_cases:
            item = {
                "PK": "DELIVERY#d001",
                "SK": "USER#u001",
                "delivery_id": "d001",
                "user_id": "u001",
                "user_name": "テストユーザー名前",
                "selected_answer": "A",
                "is_correct": True,
                "reaction_type": reaction_str,
                "responded_at": "2025-08-11T15:30:00+00:00",
                "created_at": "2025-08-11T15:30:00+00:00",
                "updated_at": "2025-08-11T15:30:00+00:00",
                "GSI1PK": "USER#u001",
                "GSI1SK": "RESPONDED#2025-08-11T15:30:00+00:00",
                "GSI2PK": "DELIVERY#d001",
                "GSI2SK": "RESPONSE#2025-08-11T15:30:00+00:00",
            }

            result = repository._to_model(item)
            assert result.reaction_type == expected_enum

    def test_datetime_conversion_edge_cases(self) -> None:
        """日時変換の境界値テスト"""
        repository = UserResponseRepository("dummy-table")

        # 異なる日時フォーマットのテスト
        test_cases = [
            "2025-08-11T15:30:00+00:00",  # UTC
            "2025-08-11T15:30:00.123456+00:00",  # マイクロ秒付き
            "2025-12-31T23:59:59+00:00",  # 年末
            "2025-01-01T00:00:00+00:00",  # 年始
        ]

        for datetime_str in test_cases:
            item = {
                "PK": "DELIVERY#d001",
                "SK": "USER#u001",
                "delivery_id": "d001",
                "user_id": "u001",
                "user_name": "テストユーザー名前",
                "selected_answer": "A",
                "is_correct": True,
                "reaction_type": "🅰️",
                "responded_at": datetime_str,
                "created_at": datetime_str,
                "updated_at": datetime_str,
                "GSI1PK": "USER#u001",
                "GSI1SK": f"RESPONDED#{datetime_str}",
                "GSI2PK": "DELIVERY#d001",
                "GSI2SK": f"RESPONSE#{datetime_str}",
            }

            result = repository._to_model(item)
            assert isinstance(result.responded_at, datetime)
            assert result.responded_at.tzinfo is not None  # タイムゾーン情報があること
