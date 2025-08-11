"""
システム設定データモデルの単体テスト

SystemSettingsモデルの機能とバリデーションをテスト
"""

from datetime import time

import pytest

from app.models.system_settings import SystemSettings


class TestSystemSettings:
    """SystemSettingsモデルのテストクラス"""

    def test_system_settings_creation_valid(self) -> None:
        """有効なデータでのシステム設定作成をテスト"""
        settings = SystemSettings(
            teams_channel_id="19:abc123@thread.tacv2",
            daily_question_time="10:00",
            answer_reveal_delay=24,
            max_questions_per_day=1,
            quality_threshold=0.8,
            updated_by="admin",
        )

        # 基本フィールドの確認
        assert settings.teams_channel_id == "19:abc123@thread.tacv2"
        assert settings.daily_question_time == "10:00"
        assert settings.answer_reveal_delay == 24
        assert settings.max_questions_per_day == 1
        assert settings.quality_threshold == 0.8
        assert settings.updated_by == "admin"

        # DynamoDBキーの確認（固定値）
        assert settings.pk == "SETTINGS"
        assert settings.sk == "CONFIG"
        assert settings.entity_type == "SystemSettings"

    def test_system_settings_default_values(self) -> None:
        """デフォルト値の確認をテスト"""
        settings = SystemSettings(teams_channel_id="19:abc123@thread.tacv2")

        # デフォルト値の確認
        assert settings.daily_question_time == "10:00"
        assert settings.answer_reveal_delay == 24
        assert settings.max_questions_per_day == 1
        assert settings.quality_threshold == 0.8
        assert settings.updated_by == "admin"

    def test_system_settings_validation_teams_channel_id_invalid(self) -> None:
        """無効なTeamsチャネルIDのバリデーションエラーをテスト"""
        with pytest.raises(
            ValueError, match="Teams チャネルIDの形式が正しくありません"
        ):
            SystemSettings(
                teams_channel_id="invalid_channel_id"  # 無効な形式
            )

    def test_system_settings_validation_daily_question_time_invalid(self) -> None:
        """無効な時刻形式のバリデーションエラーをテスト"""
        with pytest.raises(ValueError, match="時刻は HH:MM 形式で指定してください"):
            SystemSettings(
                teams_channel_id="19:abc123@thread.tacv2",
                daily_question_time="25:00",  # 無効な時刻
            )

        with pytest.raises(ValueError, match="時刻は HH:MM 形式で指定してください"):
            SystemSettings(
                teams_channel_id="19:abc123@thread.tacv2",
                daily_question_time="10:70",  # 無効な分
            )

        with pytest.raises(ValueError, match="時刻は HH:MM 形式で指定してください"):
            SystemSettings(
                teams_channel_id="19:abc123@thread.tacv2",
                daily_question_time="invalid_time",  # 無効な形式
            )

    def test_system_settings_validation_answer_reveal_delay_range(self) -> None:
        """解答公開遅延時間の範囲チェックをテスト"""
        # 最小値（1時間）
        settings_min = SystemSettings(
            teams_channel_id="19:abc123@thread.tacv2", answer_reveal_delay=1
        )
        assert settings_min.answer_reveal_delay == 1

        # 最大値（168時間 = 1週間）
        settings_max = SystemSettings(
            teams_channel_id="19:abc123@thread.tacv2", answer_reveal_delay=168
        )
        assert settings_max.answer_reveal_delay == 168

        # 範囲外の値はPydanticのバリデーションでエラーになる
        with pytest.raises(ValueError):
            SystemSettings(
                teams_channel_id="19:abc123@thread.tacv2",
                answer_reveal_delay=0,  # 最小値未満
            )

        with pytest.raises(ValueError):
            SystemSettings(
                teams_channel_id="19:abc123@thread.tacv2",
                answer_reveal_delay=169,  # 最大値超過
            )

    def test_system_settings_validation_max_questions_per_day_range(self) -> None:
        """1日あたりの最大問題数の範囲チェックをテスト"""
        # 最小値（1問）
        settings_min = SystemSettings(
            teams_channel_id="19:abc123@thread.tacv2", max_questions_per_day=1
        )
        assert settings_min.max_questions_per_day == 1

        # 最大値（10問）
        settings_max = SystemSettings(
            teams_channel_id="19:abc123@thread.tacv2", max_questions_per_day=10
        )
        assert settings_max.max_questions_per_day == 10

        # 範囲外の値はPydanticのバリデーションでエラーになる
        with pytest.raises(ValueError):
            SystemSettings(
                teams_channel_id="19:abc123@thread.tacv2",
                max_questions_per_day=0,  # 最小値未満
            )

        with pytest.raises(ValueError):
            SystemSettings(
                teams_channel_id="19:abc123@thread.tacv2",
                max_questions_per_day=11,  # 最大値超過
            )

    def test_system_settings_validation_quality_threshold_range(self) -> None:
        """品質閾値の範囲チェックをテスト"""
        # 最小値（0.0）
        settings_min = SystemSettings(
            teams_channel_id="19:abc123@thread.tacv2", quality_threshold=0.0
        )
        assert settings_min.quality_threshold == 0.0

        # 最大値（1.0）
        settings_max = SystemSettings(
            teams_channel_id="19:abc123@thread.tacv2", quality_threshold=1.0
        )
        assert settings_max.quality_threshold == 1.0

        # 範囲外の値はPydanticのバリデーションでエラーになる
        with pytest.raises(ValueError):
            SystemSettings(
                teams_channel_id="19:abc123@thread.tacv2",
                quality_threshold=-0.1,  # 最小値未満
            )

        with pytest.raises(ValueError):
            SystemSettings(
                teams_channel_id="19:abc123@thread.tacv2",
                quality_threshold=1.1,  # 最大値超過
            )

    def test_get_question_time_as_time(self) -> None:
        """配信時刻のtimeオブジェクト取得をテスト"""
        settings = SystemSettings(
            teams_channel_id="19:abc123@thread.tacv2", daily_question_time="14:30"
        )

        question_time = settings.get_question_time_as_time()
        assert isinstance(question_time, time)
        assert question_time.hour == 14
        assert question_time.minute == 30

    def test_update_teams_channel(self) -> None:
        """Teamsチャネル更新をテスト"""
        settings = SystemSettings(teams_channel_id="19:abc123@thread.tacv2")

        original_updated_at = settings.updated_at

        # チャネルを更新
        import time as time_module

        time_module.sleep(0.01)
        settings.update_teams_channel("19:def456@thread.tacv2", "test_admin")

        assert settings.teams_channel_id == "19:def456@thread.tacv2"
        assert settings.updated_by == "test_admin"
        assert settings.updated_at > original_updated_at

    def test_update_quality_threshold(self) -> None:
        """品質閾値更新をテスト"""
        settings = SystemSettings(
            teams_channel_id="19:abc123@thread.tacv2", quality_threshold=0.8
        )

        original_updated_at = settings.updated_at

        # 品質閾値を更新
        import time as time_module

        time_module.sleep(0.01)
        settings.update_quality_threshold(0.9, "test_admin")

        assert settings.quality_threshold == 0.9
        assert settings.updated_by == "test_admin"
        assert settings.updated_at > original_updated_at

    def test_update_quality_threshold_invalid(self) -> None:
        """無効な品質閾値更新のエラーをテスト"""
        settings = SystemSettings(teams_channel_id="19:abc123@thread.tacv2")

        with pytest.raises(
            ValueError, match="品質閾値は0.0-1.0の範囲で指定してください"
        ):
            settings.update_quality_threshold(1.5)

        with pytest.raises(
            ValueError, match="品質閾値は0.0-1.0の範囲で指定してください"
        ):
            settings.update_quality_threshold(-0.1)

    def test_update_schedule_settings(self) -> None:
        """スケジュール設定更新をテスト"""
        settings = SystemSettings(teams_channel_id="19:abc123@thread.tacv2")

        original_updated_at = settings.updated_at

        # スケジュール設定を更新
        import time as time_module

        time_module.sleep(0.01)
        settings.update_schedule_settings(
            question_time="15:00",
            reveal_delay=48,
            max_questions=2,
            updated_by="test_admin",
        )

        assert settings.daily_question_time == "15:00"
        assert settings.answer_reveal_delay == 48
        assert settings.max_questions_per_day == 2
        assert settings.updated_by == "test_admin"
        assert settings.updated_at > original_updated_at

    def test_update_schedule_settings_partial(self) -> None:
        """部分的なスケジュール設定更新をテスト"""
        settings = SystemSettings(
            teams_channel_id="19:abc123@thread.tacv2",
            daily_question_time="10:00",
            answer_reveal_delay=24,
            max_questions_per_day=1,
        )

        # 一部のみ更新
        settings.update_schedule_settings(
            question_time="16:00", updated_by="partial_admin"
        )

        # 指定した項目のみ更新される
        assert settings.daily_question_time == "16:00"
        assert settings.answer_reveal_delay == 24  # 変更されない
        assert settings.max_questions_per_day == 1  # 変更されない
        assert settings.updated_by == "partial_admin"

    def test_alias_functionality(self) -> None:
        """Pydantic aliasの動作をテスト"""
        settings = SystemSettings(teams_channel_id="19:abc123@thread.tacv2")

        # Python変数名でアクセス
        assert settings.pk == "SETTINGS"
        assert settings.sk == "CONFIG"
        assert settings.entity_type == "SystemSettings"

        # DynamoDB形式での出力
        dynamodb_data = settings.model_dump(by_alias=True, exclude_none=True)
        assert "PK" in dynamodb_data
        assert "SK" in dynamodb_data
        assert "EntityType" in dynamodb_data

        # DynamoDBデータからの復元
        restored = SystemSettings.model_validate(dynamodb_data)
        assert restored.teams_channel_id == settings.teams_channel_id
        assert restored.pk == settings.pk
