"""
シンプルな統合テスト

実際のユースケースの基本的な統合テスト
"""

from collections.abc import Generator
from datetime import UTC, datetime
from decimal import Decimal

import pytest
from freezegun import freeze_time
from moto import mock_aws

from app.models.delivery import Delivery, DeliveryStatus
from app.models.question import AWSService, DifficultyLevel, Question
from app.models.user_response import ReactionType, UserResponse
from app.repositories.delivery_repository import DeliveryRepository
from app.repositories.question_repository import QuestionRepository
from app.repositories.user_response_repository import UserResponseRepository


@pytest.fixture
def repositories() -> Generator[
    tuple[QuestionRepository, DeliveryRepository, UserResponseRepository], None, None
]:
    """統合テスト用リポジトリセット"""
    with mock_aws():
        # DynamoDBテーブル作成
        import boto3

        dynamodb = boto3.resource("dynamodb", region_name="ap-northeast-1")
        table = dynamodb.create_table(
            TableName="integration-test-table",
            KeySchema=[
                {"AttributeName": "PK", "KeyType": "HASH"},
                {"AttributeName": "SK", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "PK", "AttributeType": "S"},
                {"AttributeName": "SK", "AttributeType": "S"},
                {"AttributeName": "GSI1PK", "AttributeType": "S"},
                {"AttributeName": "GSI1SK", "AttributeType": "S"},
                {"AttributeName": "GSI2PK", "AttributeType": "S"},
                {"AttributeName": "GSI2SK", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "GSI1",
                    "KeySchema": [
                        {"AttributeName": "GSI1PK", "KeyType": "HASH"},
                        {"AttributeName": "GSI1SK", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                },
                {
                    "IndexName": "GSI2",
                    "KeySchema": [
                        {"AttributeName": "GSI2PK", "KeyType": "HASH"},
                        {"AttributeName": "GSI2SK", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                },
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        table.wait_until_exists()

        # リポジトリインスタンス作成
        question_repo = QuestionRepository("integration-test-table")
        delivery_repo = DeliveryRepository("integration-test-table")
        response_repo = UserResponseRepository("integration-test-table")

        yield question_repo, delivery_repo, response_repo


@pytest.mark.integration
class TestSimpleIntegration:
    """シンプルな統合テスト"""

    @freeze_time("2025-08-11 15:30:00")
    async def test_basic_question_creation(
        self,
        repositories: tuple[
            QuestionRepository, DeliveryRepository, UserResponseRepository
        ],
    ) -> None:
        """基本的な問題作成テスト"""
        question_repo, delivery_repo, response_repo = repositories

        # 問題作成
        question = Question(
            question_id="q_simple_001",
            question_text="Amazon VPCの特徴として正しいものはどれですか？",
            choices=[
                "A: 仮想プライベートクラウド環境を提供する",
                "B: 物理サーバーを直接管理する",
                "C: ストレージサービスを提供する",
                "D: データベースサービスを提供する",
            ],
            correct_answer="A",
            explanation="VPCは仮想プライベートクラウド（Virtual Private Cloud）環境を提供するサービスです。",
            service=AWSService.EC2,
            topic="VPC基礎",
            difficulty=DifficultyLevel.ASSOCIATE,
            quality_score=Decimal("0.85"),
        )

        created_question = await question_repo.create_question(question)
        assert created_question.question_id == "q_simple_001"
        assert created_question.service == AWSService.EC2
        assert created_question.difficulty == DifficultyLevel.ASSOCIATE

    @freeze_time("2025-08-11 15:30:00")
    async def test_basic_delivery_creation(
        self,
        repositories: tuple[
            QuestionRepository, DeliveryRepository, UserResponseRepository
        ],
    ) -> None:
        """基本的な配信作成テスト"""
        question_repo, delivery_repo, response_repo = repositories

        # 配信作成
        delivery = Delivery(
            delivery_id="d_simple_001",
            question_id="q_simple_001",
            teams_channel_id="19:test123@thread.tacv2",
            status=DeliveryStatus.POSTED,
            posted_at=datetime.now(UTC),
        )

        created_delivery = await delivery_repo.create_delivery(delivery)
        assert created_delivery.delivery_id == "d_simple_001"
        assert created_delivery.status == DeliveryStatus.POSTED
        assert created_delivery.teams_channel_id == "19:test123@thread.tacv2"

    @freeze_time("2025-08-11 15:30:00")
    async def test_basic_user_response_creation(
        self,
        repositories: tuple[
            QuestionRepository, DeliveryRepository, UserResponseRepository
        ],
    ) -> None:
        """基本的なユーザー回答作成テスト"""
        question_repo, delivery_repo, response_repo = repositories

        # ユーザー回答作成
        user_response = UserResponse(
            delivery_id="d_simple_001",
            user_id="user_simple_001",
            user_name="テストユーザー名前",
            selected_answer="A",
            is_correct=True,
            reaction_type=ReactionType.A,
            responded_at=datetime.now(UTC),
        )

        created_response = await response_repo.create_user_response(user_response)
        assert created_response.delivery_id == "d_simple_001"
        assert created_response.user_id == "user_simple_001"
        assert created_response.is_correct is True
        assert created_response.reaction_type == ReactionType.A
