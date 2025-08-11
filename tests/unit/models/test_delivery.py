"""
配信履歴データモデルの単体テスト

Deliveryモデルの機能とバリデーションをテスト
"""

from datetime import datetime

import pytest

from app.models.delivery import Delivery, DeliveryStatus


class TestDelivery:
    """Deliveryモデルのテストクラス"""

    def test_delivery_creation_valid(self) -> None:
        """有効なデータでの配信履歴作成をテスト"""
        delivery = Delivery(
            delivery_id="d_test_001",
            question_id="q_test_001",
            teams_channel_id="19:abc123@thread.tacv2",
            status=DeliveryStatus.PENDING,
        )

        # 基本フィールドの確認
        assert delivery.delivery_id == "d_test_001"
        assert delivery.question_id == "q_test_001"
        assert delivery.teams_channel_id == "19:abc123@thread.tacv2"
        assert delivery.status == DeliveryStatus.PENDING
        assert delivery.total_responses == 0
        assert delivery.correct_responses == 0
        assert delivery.correct_rate is None

        # DynamoDBキーの自動生成確認
        assert delivery.pk == "DELIVERY#d_test_001"
        assert delivery.sk == "METADATA"
        assert delivery.entity_type == "Delivery"
        assert delivery.gsi1_pk == "QUESTION#q_test_001"
        assert delivery.gsi1_sk == "DELIVERY#d_test_001"
        assert delivery.gsi2_pk == "STATUS#pending"

    def test_delivery_validation_teams_channel_id_invalid(self) -> None:
        """無効なTeamsチャネルIDのバリデーションエラーをテスト"""
        with pytest.raises(
            ValueError, match="Teams チャネルIDの形式が正しくありません"
        ):
            Delivery(
                delivery_id="d_test_002",
                question_id="q_test_001",
                teams_channel_id="invalid_channel_id",  # 無効な形式
                status=DeliveryStatus.PENDING,
            )

    def test_delivery_validation_correct_responses_exceeds_total(self) -> None:
        """正解数が総回答数を超える場合のエラーをテスト"""
        with pytest.raises(ValueError, match="正解数 15 が総回答数 10 を超えています"):
            Delivery(
                delivery_id="d_test_003",
                question_id="q_test_001",
                teams_channel_id="19:abc123@thread.tacv2",
                total_responses=10,
                correct_responses=15,  # 総回答数を超えている
            )

    def test_calculate_correct_rate(self) -> None:
        """正解率計算をテスト"""
        delivery = Delivery(
            delivery_id="d_test_004",
            question_id="q_test_001",
            teams_channel_id="19:abc123@thread.tacv2",
            total_responses=20,
            correct_responses=16,
        )

        rate = delivery.calculate_correct_rate()
        assert rate == 0.8

        # 総回答数が0の場合
        delivery_zero = Delivery(
            delivery_id="d_test_005",
            question_id="q_test_001",
            teams_channel_id="19:abc123@thread.tacv2",
            total_responses=0,
            correct_responses=0,
        )

        assert delivery_zero.calculate_correct_rate() is None

    def test_update_response_stats(self) -> None:
        """回答統計更新をテスト"""
        delivery = Delivery(
            delivery_id="d_test_006",
            question_id="q_test_001",
            teams_channel_id="19:abc123@thread.tacv2",
        )

        original_updated_at = delivery.updated_at

        # 統計を更新
        import time

        time.sleep(0.01)
        delivery.update_response_stats(total=25, correct=20)

        assert delivery.total_responses == 25
        assert delivery.correct_responses == 20
        assert delivery.correct_rate == 0.8
        assert delivery.updated_at > original_updated_at

    def test_update_response_stats_invalid(self) -> None:
        """無効な回答統計更新のエラーをテスト"""
        delivery = Delivery(
            delivery_id="d_test_007",
            question_id="q_test_001",
            teams_channel_id="19:abc123@thread.tacv2",
        )

        with pytest.raises(ValueError, match="正解数 30 が総回答数 25 を超えています"):
            delivery.update_response_stats(total=25, correct=30)

    def test_mark_as_posted(self) -> None:
        """配信完了マークをテスト"""
        delivery = Delivery(
            delivery_id="d_test_008",
            question_id="q_test_001",
            teams_channel_id="19:abc123@thread.tacv2",
            status=DeliveryStatus.PENDING,
        )

        original_updated_at = delivery.updated_at

        # 配信完了としてマーク
        import time

        time.sleep(0.01)
        delivery.mark_as_posted("teams_msg_12345")

        assert delivery.status == DeliveryStatus.POSTED
        assert delivery.teams_message_id == "teams_msg_12345"
        assert delivery.posted_at is not None
        assert delivery.updated_at > original_updated_at
        assert delivery.gsi2_pk == "STATUS#posted"
        assert delivery.gsi2_sk.startswith("POSTED#")

    def test_mark_as_answered(self) -> None:
        """解答公開完了マークをテスト"""
        delivery = Delivery(
            delivery_id="d_test_009",
            question_id="q_test_001",
            teams_channel_id="19:abc123@thread.tacv2",
            status=DeliveryStatus.POSTED,
        )

        original_updated_at = delivery.updated_at

        # 解答公開完了としてマーク
        import time

        time.sleep(0.01)
        delivery.mark_as_answered()

        assert delivery.status == DeliveryStatus.ANSWERED
        assert delivery.answered_at is not None
        assert delivery.updated_at > original_updated_at
        assert delivery.gsi2_pk == "STATUS#answered"

    def test_mark_as_failed(self) -> None:
        """配信失敗マークをテスト"""
        delivery = Delivery(
            delivery_id="d_test_010",
            question_id="q_test_001",
            teams_channel_id="19:abc123@thread.tacv2",
            status=DeliveryStatus.PENDING,
        )

        original_updated_at = delivery.updated_at

        # 配信失敗としてマーク
        import time

        time.sleep(0.01)
        delivery.mark_as_failed("Teams API エラー")

        assert delivery.status == DeliveryStatus.FAILED
        assert delivery.error_message == "Teams API エラー"
        assert delivery.updated_at > original_updated_at
        assert delivery.gsi2_pk == "STATUS#failed"

    def test_is_active(self) -> None:
        """アクティブな配信の判定をテスト"""
        pending_delivery = Delivery(
            delivery_id="d_test_011",
            question_id="q_test_001",
            teams_channel_id="19:abc123@thread.tacv2",
            status=DeliveryStatus.PENDING,
        )

        posted_delivery = Delivery(
            delivery_id="d_test_012",
            question_id="q_test_001",
            teams_channel_id="19:abc123@thread.tacv2",
            status=DeliveryStatus.POSTED,
        )

        answered_delivery = Delivery(
            delivery_id="d_test_013",
            question_id="q_test_001",
            teams_channel_id="19:abc123@thread.tacv2",
            status=DeliveryStatus.ANSWERED,
        )

        assert pending_delivery.is_active() is True
        assert posted_delivery.is_active() is True
        assert answered_delivery.is_active() is False

    def test_is_completed(self) -> None:
        """完了した配信の判定をテスト"""
        pending_delivery = Delivery(
            delivery_id="d_test_014",
            question_id="q_test_001",
            teams_channel_id="19:abc123@thread.tacv2",
            status=DeliveryStatus.PENDING,
        )

        answered_delivery = Delivery(
            delivery_id="d_test_015",
            question_id="q_test_001",
            teams_channel_id="19:abc123@thread.tacv2",
            status=DeliveryStatus.ANSWERED,
        )

        failed_delivery = Delivery(
            delivery_id="d_test_016",
            question_id="q_test_001",
            teams_channel_id="19:abc123@thread.tacv2",
            status=DeliveryStatus.FAILED,
        )

        assert pending_delivery.is_completed() is False
        assert answered_delivery.is_completed() is True
        assert failed_delivery.is_completed() is True

    def test_get_response_summary(self) -> None:
        """回答サマリー取得をテスト"""
        delivery = Delivery(
            delivery_id="d_test_017",
            question_id="q_test_001",
            teams_channel_id="19:abc123@thread.tacv2",
            status=DeliveryStatus.POSTED,
            total_responses=15,
            correct_responses=12,
            correct_rate=0.8,
        )
        delivery.posted_at = datetime(2025, 8, 10, 10, 0, 0)
        delivery.answered_at = datetime(2025, 8, 11, 10, 0, 0)

        summary = delivery.get_response_summary()

        assert summary["delivery_id"] == "d_test_017"
        assert summary["question_id"] == "q_test_001"
        assert summary["status"] == "posted"
        assert summary["total_responses"] == 15
        assert summary["correct_responses"] == 12
        assert summary["correct_rate"] == 0.8
        assert summary["posted_at"] == "2025-08-10T10:00:00"
        assert summary["answered_at"] == "2025-08-11T10:00:00"

    def test_alias_functionality(self) -> None:
        """Pydantic aliasの動作をテスト"""
        delivery = Delivery(
            delivery_id="d_test_018",
            question_id="q_test_001",
            teams_channel_id="19:abc123@thread.tacv2",
        )

        # Python変数名でアクセス
        assert delivery.pk.startswith("DELIVERY#")
        assert delivery.sk == "METADATA"
        assert delivery.entity_type == "Delivery"

        # DynamoDB形式での出力
        dynamodb_data = delivery.model_dump(by_alias=True, exclude_none=True)
        assert "PK" in dynamodb_data
        assert "SK" in dynamodb_data
        assert "EntityType" in dynamodb_data

        # DynamoDBデータからの復元
        restored = Delivery.model_validate(dynamodb_data)
        assert restored.delivery_id == delivery.delivery_id
        assert restored.pk == delivery.pk
