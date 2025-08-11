"""
ユーザー回答データモデルの単体テスト

UserResponseモデルの機能とバリデーションをテスト
"""

from datetime import datetime, timedelta

import pytest

from app.models.user_response import ReactionType, UserResponse


class TestUserResponse:
    """UserResponseモデルのテストクラス"""

    def test_user_response_creation_valid(self) -> None:
        """有効なデータでのユーザー回答作成をテスト"""
        response = UserResponse(
            delivery_id="d_test_001",
            user_id="user123",
            user_name="田中太郎",
            selected_answer="B",
            is_correct=True,
            reaction_type=ReactionType.B,
        )

        # 基本フィールドの確認
        assert response.delivery_id == "d_test_001"
        assert response.user_id == "user123"
        assert response.user_name == "田中太郎"
        assert response.selected_answer == "B"
        assert response.is_correct is True
        assert response.reaction_type == ReactionType.B
        assert isinstance(response.responded_at, datetime)

        # DynamoDBキーの自動生成確認
        assert response.pk == "DELIVERY#d_test_001"
        assert response.sk == "USER#user123"
        assert response.entity_type == "UserResponse"
        assert response.gsi1_pk == "USER#user123"
        assert response.gsi2_pk == "DELIVERY#d_test_001"

    def test_user_response_validation_selected_answer_invalid(self) -> None:
        """無効な選択回答のバリデーションエラーをテスト"""
        with pytest.raises(
            ValueError, match="選択回答は A-F の範囲で指定してください: G"
        ):
            UserResponse(
                delivery_id="d_test_001",
                user_id="user123",
                user_name="田中太郎",
                selected_answer="G",  # 無効な選択肢
                is_correct=False,
                reaction_type=ReactionType.A,
            )

    def test_user_response_validation_selected_answer_lowercase(self) -> None:
        """小文字の選択回答が大文字に変換されることをテスト"""
        response = UserResponse(
            delivery_id="d_test_001",
            user_id="user123",
            user_name="田中太郎",
            selected_answer="c",  # 小文字
            is_correct=True,
            reaction_type=ReactionType.C,
        )

        assert response.selected_answer == "C"  # 大文字に変換される

    def test_user_response_validation_user_id_empty(self) -> None:
        """空のユーザーIDのバリデーションエラーをテスト"""
        with pytest.raises(ValueError, match="ユーザーIDは空にできません"):
            UserResponse(
                delivery_id="d_test_001",
                user_id="   ",  # 空白のみ
                user_name="田中太郎",
                selected_answer="A",
                is_correct=True,
                reaction_type=ReactionType.A,
            )

    def test_user_response_validation_user_name_empty(self) -> None:
        """空のユーザー名のバリデーションエラーをテスト"""
        with pytest.raises(ValueError, match="String should have at least 1 character"):
            UserResponse(
                delivery_id="d_test_001",
                user_id="user123",
                user_name="",  # 空文字
                selected_answer="A",
                is_correct=True,
                reaction_type=ReactionType.A,
            )

    def test_user_response_validation_whitespace_trimming(self) -> None:
        """ユーザーIDとユーザー名の空白トリミングをテスト"""
        response = UserResponse(
            delivery_id="d_test_001",
            user_id="  user123  ",  # 前後に空白
            user_name="  田中太郎  ",  # 前後に空白
            selected_answer="A",
            is_correct=True,
            reaction_type=ReactionType.A,
        )

        assert response.user_id == "user123"
        assert response.user_name == "田中太郎"

    def test_create_from_reaction_valid(self) -> None:
        """リアクション絵文字からの回答作成をテスト"""
        response = UserResponse.create_from_reaction(
            delivery_id="d_test_001",
            user_id="user123",
            user_name="田中太郎",
            reaction_emoji="🅱️",
            correct_answer="B",
        )

        assert response.delivery_id == "d_test_001"
        assert response.user_id == "user123"
        assert response.user_name == "田中太郎"
        assert response.selected_answer == "B"
        assert response.is_correct is True
        assert response.reaction_type == ReactionType.B

    def test_create_from_reaction_incorrect(self) -> None:
        """不正解の場合のリアクション作成をテスト"""
        response = UserResponse.create_from_reaction(
            delivery_id="d_test_001",
            user_id="user123",
            user_name="田中太郎",
            reaction_emoji="🅰️",
            correct_answer="B",
        )

        assert response.selected_answer == "A"
        assert response.is_correct is False
        assert response.reaction_type == ReactionType.A

    def test_create_from_reaction_invalid_emoji(self) -> None:
        """サポートされていない絵文字のエラーをテスト"""
        with pytest.raises(
            ValueError, match="サポートされていないリアクション絵文字: 😀"
        ):
            UserResponse.create_from_reaction(
                delivery_id="d_test_001",
                user_id="user123",
                user_name="田中太郎",
                reaction_emoji="😀",  # サポートされていない絵文字
                correct_answer="B",
            )

    def test_get_response_summary(self) -> None:
        """回答サマリー取得をテスト"""
        response = UserResponse(
            delivery_id="d_test_001",
            user_id="user123",
            user_name="田中太郎",
            selected_answer="B",
            is_correct=True,
            reaction_type=ReactionType.B,
        )
        response.responded_at = datetime(2025, 8, 10, 11, 30, 0)

        summary = response.get_response_summary()

        assert summary["user_id"] == "user123"
        assert summary["user_name"] == "田中太郎"
        assert summary["selected_answer"] == "B"
        assert summary["is_correct"] is True
        assert summary["responded_at"] == "2025-08-10T11:30:00"
        assert summary["reaction_type"] == "🅱️"

    def test_is_recent_response(self) -> None:
        """最近の回答判定をテスト"""
        # 現在時刻の回答
        recent_response = UserResponse(
            delivery_id="d_test_001",
            user_id="user123",
            user_name="田中太郎",
            selected_answer="A",
            is_correct=True,
            reaction_type=ReactionType.A,
        )

        # 古い回答
        old_response = UserResponse(
            delivery_id="d_test_001",
            user_id="user456",
            user_name="佐藤花子",
            selected_answer="B",
            is_correct=False,
            reaction_type=ReactionType.B,
        )
        old_response.responded_at = datetime.now() - timedelta(
            hours=25
        )  # 25時間前（1日以上前だが48時間以内）

        assert recent_response.is_recent_response() is True
        assert old_response.is_recent_response() is False
        assert old_response.is_recent_response(hours=48) is True  # 48時間以内なら True

    def test_reaction_type_enum_values(self) -> None:
        """ReactionType列挙型の値をテスト"""
        assert ReactionType.A.value == "🅰️"
        assert ReactionType.B.value == "🅱️"
        assert ReactionType.C.value == "🇨"
        assert ReactionType.D.value == "🇩"
        assert ReactionType.E.value == "🇪"
        assert ReactionType.F.value == "🇫"

    def test_alias_functionality(self) -> None:
        """Pydantic aliasの動作をテスト"""
        response = UserResponse(
            delivery_id="d_test_001",
            user_id="user123",
            user_name="田中太郎",
            selected_answer="A",
            is_correct=True,
            reaction_type=ReactionType.A,
        )

        # Python変数名でアクセス
        assert response.pk.startswith("DELIVERY#")
        assert response.sk.startswith("USER#")
        assert response.entity_type == "UserResponse"

        # DynamoDB形式での出力
        dynamodb_data = response.model_dump(by_alias=True, exclude_none=True)
        assert "PK" in dynamodb_data
        assert "SK" in dynamodb_data
        assert "EntityType" in dynamodb_data

        # DynamoDBデータからの復元
        restored = UserResponse.model_validate(dynamodb_data)
        assert restored.user_id == response.user_id
        assert restored.pk == response.pk
