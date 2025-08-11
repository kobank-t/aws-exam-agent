"""
配信リポジトリの単体テスト

外部依存のない純粋なロジックのテスト
"""

from datetime import UTC, datetime
from decimal import Decimal

from app.models.delivery import Delivery, DeliveryStatus
from app.repositories.delivery_repository import DeliveryRepository


class TestDeliveryRepository:
    """配信リポジトリの純粋ロジックテスト"""

    def test_to_model_conversion(self) -> None:
        """DynamoDBアイテム → Deliveryモデル変換ロジック"""
        repository = DeliveryRepository("dummy-table")

        item = {
            "PK": "DELIVERY#d001",
            "SK": "METADATA",
            "delivery_id": "d001",
            "question_id": "q001",
            "teams_channel_id": "19:test123@thread.tacv2",
            "status": "posted",
            "posted_at": "2025-08-11T15:30:00+00:00",
            "total_responses": 10,
            "correct_responses": 7,
            "correct_rate": 0.7,
            "created_at": "2025-08-11T15:30:00+00:00",
            "updated_at": "2025-08-11T15:30:00+00:00",
            "GSI1PK": "STATUS#posted",
            "GSI1SK": "2025-08-11T15:30:00+00:00",
        }

        result = repository._to_model(item)

        assert isinstance(result, Delivery)
        assert result.delivery_id == "d001"
        assert result.question_id == "q001"
        assert result.teams_channel_id == "19:test123@thread.tacv2"
        assert result.status == DeliveryStatus.POSTED
        assert result.posted_at == datetime(2025, 8, 11, 15, 30, 0, tzinfo=UTC)
        assert result.total_responses == 10
        assert result.correct_responses == 7
        assert result.correct_rate == 0.7

    def test_from_model_conversion(self) -> None:
        """Deliveryモデル → DynamoDBアイテム変換ロジック"""
        repository = DeliveryRepository("dummy-table")

        delivery = Delivery(
            delivery_id="d001",
            question_id="q001",
            teams_channel_id="19:test123@thread.tacv2",
            status=DeliveryStatus.POSTED,
            posted_at=datetime(2025, 8, 11, 15, 30, 0, tzinfo=UTC),
            total_responses=10,
            correct_responses=7,
            correct_rate=0.7,
            created_at=datetime(2025, 8, 11, 15, 30, 0, tzinfo=UTC),
            updated_at=datetime(2025, 8, 11, 15, 30, 0, tzinfo=UTC),
        )

        result = repository._from_model(delivery)

        assert result["PK"] == "DELIVERY#d001"
        assert result["SK"] == "METADATA"
        assert result["delivery_id"] == "d001"
        assert result["question_id"] == "q001"
        assert result["teams_channel_id"] == "19:test123@thread.tacv2"
        assert result["status"] == "posted"
        assert result["posted_at"] == "2025-08-11T15:30:00+00:00"
        assert result["total_responses"] == 10
        assert result["correct_responses"] == 7
        assert result["correct_rate"] == Decimal("0.7")
        assert result["GSI1PK"] == "QUESTION#q001"
        assert result["GSI1SK"] == "DELIVERY#d001"

    def test_status_enum_conversion(self) -> None:
        """DeliveryStatus列挙型変換テスト"""
        repository = DeliveryRepository("dummy-table")

        test_cases = [
            ("pending", DeliveryStatus.PENDING),
            ("posted", DeliveryStatus.POSTED),
            ("answered", DeliveryStatus.ANSWERED),
            ("failed", DeliveryStatus.FAILED),
            ("cancelled", DeliveryStatus.CANCELLED),
        ]

        for status_str, expected_enum in test_cases:
            item = {
                "PK": "DELIVERY#d001",
                "SK": "METADATA",
                "delivery_id": "d001",
                "question_id": "q001",
                "teams_channel_id": "19:test123@thread.tacv2",
                "status": status_str,
                "posted_at": "2025-08-11T15:30:00+00:00",
                "total_responses": 0,
                "correct_responses": 0,
                "correct_rate": 0.0,
                "created_at": "2025-08-11T15:30:00+00:00",
                "updated_at": "2025-08-11T15:30:00+00:00",
                "GSI1PK": f"STATUS#{status_str}",
                "GSI1SK": "2025-08-11T15:30:00+00:00",
            }

            result = repository._to_model(item)
            assert result.status == expected_enum
