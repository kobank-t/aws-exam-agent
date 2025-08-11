"""
データアクセス統合テスト

DynamoDB操作の統合テスト（moto使用）
"""

from collections.abc import Generator
from decimal import Decimal

import pytest
from freezegun import freeze_time
from moto import mock_aws

from app.models.delivery import Delivery, DeliveryStatus
from app.models.question import AWSService, DifficultyLevel, Question
from app.models.user_response import ReactionType, UserResponse
from app.repositories.dynamodb_client import DynamoDBClient


@pytest.fixture
def dynamodb_client() -> Generator[DynamoDBClient, None, None]:
    with mock_aws():
        client = DynamoDBClient("integration-test-table")
        # テーブル初期化を同期的に実行
        import asyncio

        asyncio.run(client.initialize_table())
        yield client


@pytest.fixture
def sample_question() -> Question:
    return Question(
        question_id="q_integration_001",
        question_text="これは統合テスト用の詳細な問題文です",
        choices=["選択肢A", "選択肢B", "選択肢C", "選択肢D"],
        correct_answer="B",
        explanation="正解はBです。これは詳細な解説文です。",
        service=AWSService.EC2,
        topic="統合テスト",
        difficulty=DifficultyLevel.ASSOCIATE,
        quality_score=Decimal("0.85"),
    )


@pytest.fixture
def sample_delivery() -> Delivery:
    return Delivery(
        delivery_id="d_integration_001",
        question_id="q_integration_001",
        teams_channel_id="19:integration@thread.tacv2",
        status=DeliveryStatus.PENDING,
    )


@pytest.fixture
def sample_user_responses() -> list[UserResponse]:
    return [
        UserResponse(
            delivery_id="d_integration_001",
            user_id="user001",
            user_name="テストユーザー1",
            selected_answer="B",
            is_correct=True,
            reaction_type=ReactionType.B,
        ),
        UserResponse(
            delivery_id="d_integration_001",
            user_id="user002",
            user_name="テストユーザー2",
            selected_answer="A",
            is_correct=False,
            reaction_type=ReactionType.A,
        ),
        UserResponse(
            delivery_id="d_integration_001",
            user_id="user003",
            user_name="テストユーザー3",
            selected_answer="B",
            is_correct=True,
            reaction_type=ReactionType.B,
        ),
    ]


@pytest.mark.integration
class TestDataAccessIntegration:
    """データアクセス統合テスト"""

    @pytest.mark.asyncio
    async def test_full_question_lifecycle(
        self, dynamodb_client: DynamoDBClient, sample_question: Question
    ) -> None:
        """問題の完全なライフサイクルテスト"""
        # 1. 問題作成
        created = await dynamodb_client.questions.create_question(sample_question)
        assert created.question_id == sample_question.question_id

        # 2. 問題取得
        retrieved = await dynamodb_client.questions.get_by_question_id(
            sample_question.question_id
        )
        assert retrieved is not None
        assert retrieved.question_text == sample_question.question_text

        # 3. 問題更新
        retrieved.quality_score = Decimal("0.95")
        updated = await dynamodb_client.questions.update_question(retrieved)
        assert updated.quality_score == Decimal("0.95")

        # 4. サービス別検索
        service_questions = await dynamodb_client.questions.get_questions_by_service(
            AWSService.EC2
        )
        assert len(service_questions) >= 1
        assert any(
            q.question_id == sample_question.question_id for q in service_questions
        )

        # 5. 問題削除
        success = await dynamodb_client.questions.delete_question(
            sample_question.question_id
        )
        assert success is True

        # 6. 削除確認
        deleted = await dynamodb_client.questions.get_by_question_id(
            sample_question.question_id
        )
        assert deleted is None

    @pytest.mark.asyncio
    async def test_full_delivery_lifecycle(
        self,
        dynamodb_client: DynamoDBClient,
        sample_question: Question,
        sample_delivery: Delivery,
    ) -> None:
        """配信履歴の完全なライフサイクルテスト"""
        # 前提: 問題を作成
        await dynamodb_client.questions.create_question(sample_question)

        # 1. 配信履歴作成
        created = await dynamodb_client.deliveries.create_delivery(sample_delivery)
        assert created.delivery_id == sample_delivery.delivery_id
        assert created.status == DeliveryStatus.PENDING

        # 2. 配信履歴取得
        retrieved = await dynamodb_client.deliveries.get_by_delivery_id(
            sample_delivery.delivery_id
        )
        assert retrieved is not None
        assert retrieved.question_id == sample_question.question_id

        # 3. ステータス更新（配信完了）
        success = await dynamodb_client.deliveries.update_delivery_status(
            sample_delivery.delivery_id,
            DeliveryStatus.POSTED,
            teams_message_id="teams_msg_123",
        )
        assert success is True

        # 4. 更新確認
        updated = await dynamodb_client.deliveries.get_by_delivery_id(
            sample_delivery.delivery_id
        )
        assert updated is not None
        assert updated.status == DeliveryStatus.POSTED
        assert updated.teams_message_id == "teams_msg_123"
        assert updated.posted_at is not None

        # 5. 問題別配信履歴検索
        question_deliveries = (
            await dynamodb_client.deliveries.get_deliveries_by_question(
                sample_question.question_id
            )
        )
        assert len(question_deliveries) >= 1
        assert any(
            d.delivery_id == sample_delivery.delivery_id for d in question_deliveries
        )

        # 6. ステータス別検索
        posted_deliveries = await dynamodb_client.deliveries.get_deliveries_by_status(
            DeliveryStatus.POSTED
        )
        assert len(posted_deliveries) >= 1
        assert any(
            d.delivery_id == sample_delivery.delivery_id for d in posted_deliveries
        )

    @pytest.mark.asyncio
    async def test_user_response_integration(
        self,
        dynamodb_client: DynamoDBClient,
        sample_question: Question,
        sample_delivery: Delivery,
        sample_user_responses: list[UserResponse],
    ) -> None:
        """ユーザー回答の統合テスト"""
        with freeze_time("2025-08-11 15:30:00"):
            # 前提: 問題と配信履歴を作成
            await dynamodb_client.questions.create_question(sample_question)
            await dynamodb_client.deliveries.create_delivery(sample_delivery)

            # 1. ユーザー回答作成
            created_responses = []
            for response in sample_user_responses:
                created = await dynamodb_client.user_responses.create_user_response(
                    response
                )
                created_responses.append(created)
                assert created.delivery_id == sample_delivery.delivery_id

            # 2. 配信別回答取得
            delivery_responses = (
                await dynamodb_client.user_responses.get_responses_by_delivery(
                    sample_delivery.delivery_id
                )
            )
            assert len(delivery_responses) == 3

            # 3. 回答サマリー取得
            summary = (
                await dynamodb_client.user_responses.get_delivery_response_summary(
                    sample_delivery.delivery_id
                )
            )
            assert summary["total_responses"] == 3
            assert summary["correct_responses"] == 2  # user001とuser003が正解
            assert summary["correct_rate"] == 2 / 3

            # 4. 配信の回答統計更新
            success = await dynamodb_client.deliveries.update_response_stats(
                sample_delivery.delivery_id, total_responses=3, correct_responses=2
            )
            assert success is True

            # 5. 更新された配信履歴確認
            updated_delivery = await dynamodb_client.deliveries.get_by_delivery_id(
                sample_delivery.delivery_id
            )
            assert updated_delivery is not None
            assert updated_delivery.total_responses == 3
            assert updated_delivery.correct_responses == 2
            assert updated_delivery.correct_rate == 2 / 3

            # 6. ユーザー別回答履歴
            user_responses = await dynamodb_client.user_responses.get_responses_by_user(
                "user001"
            )
            assert len(user_responses) >= 1
            assert any(
                r.delivery_id == sample_delivery.delivery_id for r in user_responses
            )

    @pytest.mark.asyncio
    async def test_cross_repository_queries(
        self,
        dynamodb_client: DynamoDBClient,
        sample_question: Question,
        sample_delivery: Delivery,
        sample_user_responses: list[UserResponse],
    ) -> None:
        """リポジトリ間連携クエリのテスト"""
        with freeze_time("2025-08-11 15:30:00"):
            # データ準備
            await dynamodb_client.questions.create_question(sample_question)
            await dynamodb_client.deliveries.create_delivery(sample_delivery)

            for response in sample_user_responses:
                await dynamodb_client.user_responses.create_user_response(response)

            # 1. 問題から配信履歴を検索
            question_deliveries = (
                await dynamodb_client.deliveries.get_deliveries_by_question(
                    sample_question.question_id
                )
            )
            assert len(question_deliveries) >= 1

            # 2. 配信履歴から回答を検索
            for delivery in question_deliveries:
                responses = (
                    await dynamodb_client.user_responses.get_responses_by_delivery(
                        delivery.delivery_id
                    )
                )
                assert len(responses) >= 0

            # 3. 統計情報の整合性確認
            delivery_summary = (
                await dynamodb_client.user_responses.get_delivery_response_summary(
                    sample_delivery.delivery_id
                )
            )

            # 配信履歴の統計を更新
            await dynamodb_client.deliveries.update_response_stats(
                sample_delivery.delivery_id,
                delivery_summary["total_responses"],
                delivery_summary["correct_responses"],
            )

            # 更新された配信履歴を確認
            updated_delivery = await dynamodb_client.deliveries.get_by_delivery_id(
                sample_delivery.delivery_id
            )
            assert updated_delivery is not None
            assert (
                updated_delivery.total_responses == delivery_summary["total_responses"]
            )
            assert (
                updated_delivery.correct_responses
                == delivery_summary["correct_responses"]
            )

    @pytest.mark.asyncio
    async def test_gsi_queries_integration(
        self, dynamodb_client: DynamoDBClient
    ) -> None:
        """GSIクエリの統合テスト"""
        # 複数のサービス・難易度の問題を作成
        questions = []
        for i, service in enumerate([AWSService.EC2, AWSService.S3, AWSService.RDS]):
            for j, difficulty in enumerate(
                [DifficultyLevel.ASSOCIATE, DifficultyLevel.PROFESSIONAL]
            ):
                question = Question(
                    question_id=f"q_gsi_{service.value}_{difficulty.value}_{i}_{j}",
                    question_text=f"これは{service.value}の{difficulty.value}レベル問題です",
                    choices=["A", "B", "C", "D"],
                    correct_answer="A",
                    explanation="これは詳細な解説文です",
                    service=service,
                    topic=f"{service.value}トピック",
                    difficulty=difficulty,
                    quality_score=Decimal(str(0.7 + (i * 0.1) + (j * 0.05))),
                )
                questions.append(question)
                await dynamodb_client.questions.create_question(question)

        # GSI1（サービス別）クエリテスト
        ec2_questions = await dynamodb_client.questions.get_questions_by_service(
            AWSService.EC2
        )
        assert len(ec2_questions) == 2  # Associate + Professional

        s3_questions = await dynamodb_client.questions.get_questions_by_service(
            AWSService.S3
        )
        assert len(s3_questions) == 2

        # GSI2（難易度別）クエリテスト
        associate_questions = (
            await dynamodb_client.questions.get_questions_by_difficulty(
                DifficultyLevel.ASSOCIATE
            )
        )
        assert len(associate_questions) == 3  # EC2 + S3 + RDS

        professional_questions = (
            await dynamodb_client.questions.get_questions_by_difficulty(
                DifficultyLevel.PROFESSIONAL
            )
        )
        assert len(professional_questions) == 3

        # 高品質問題検索
        high_quality = await dynamodb_client.questions.get_high_quality_questions(
            quality_threshold=Decimal("0.8")
        )
        # 品質スコア0.8以上の問題を確認
        for question in high_quality:
            assert question.quality_score >= Decimal("0.8")

    @pytest.mark.asyncio
    async def test_batch_operations_integration(
        self, dynamodb_client: DynamoDBClient
    ) -> None:
        """一括操作の統合テスト"""
        # 一括作成用の問題を準備
        questions = []
        for i in range(5):
            question = Question(
                question_id=f"q_batch_{i:03d}",
                question_text=f"これは一括テスト問題{i}の詳細な説明文です",
                choices=["A", "B", "C", "D"],
                correct_answer="A",
                explanation="これは一括テスト用の詳細な解説文です",
                service=AWSService.EC2,
                topic="一括テスト",
                difficulty=DifficultyLevel.ASSOCIATE,
                quality_score=Decimal("0.8"),
            )
            questions.append(question)

        # 個別作成（一括保存はBaseRepositoryレベルでのみサポート）
        for question in questions:
            await dynamodb_client.questions.create_question(question)

        # 一括取得用のキーを準備
        keys = []
        for question in questions:
            keys.append({"PK": f"QUESTION#{question.question_id}", "SK": "METADATA"})

        # 一括取得
        retrieved_questions = await dynamodb_client.questions.batch_get_items(keys)
        assert len(retrieved_questions) == 5

        # 取得した問題のIDを確認
        retrieved_ids = {q.question_id for q in retrieved_questions}
        expected_ids = {q.question_id for q in questions}
        assert retrieved_ids == expected_ids

    @pytest.mark.asyncio
    async def test_system_statistics_integration(
        self, dynamodb_client: DynamoDBClient
    ) -> None:
        """システム統計の統合テスト"""
        with freeze_time("2025-08-11 15:30:00"):
            # テストデータを作成
            # 問題作成
            question = Question(
                question_id="q_stats_001",
                question_text="これは統計テスト用の詳細な問題文です",
                choices=["A", "B", "C", "D"],
                correct_answer="A",
                explanation="これは統計テスト用の詳細な解説文です",
                service=AWSService.EC2,
                topic="統計テスト",
                difficulty=DifficultyLevel.ASSOCIATE,
            )
            await dynamodb_client.questions.create_question(question)

            # 配信履歴作成
            delivery = Delivery(
                delivery_id="d_stats_001",
                question_id="q_stats_001",
                teams_channel_id="19:stats@thread.tacv2",
                status=DeliveryStatus.POSTED,
            )
            await dynamodb_client.deliveries.create_delivery(delivery)

            # システム統計取得
            stats = await dynamodb_client.get_system_statistics()

            assert "table_info" in stats
            assert "question_statistics" in stats
            assert "delivery_statistics" in stats

            # 問題統計の確認
            question_stats = stats["question_statistics"]
            assert question_stats[AWSService.EC2.value] >= 1

            # 健全性チェック
            health = await dynamodb_client.health_check()
            assert health["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_error_scenarios_integration(
        self, dynamodb_client: DynamoDBClient
    ) -> None:
        """エラーシナリオの統合テスト"""
        # 存在しない問題の取得
        nonexistent = await dynamodb_client.questions.get_by_question_id("nonexistent")
        assert nonexistent is None

        # 存在しない配信履歴の取得
        nonexistent_delivery = await dynamodb_client.deliveries.get_by_delivery_id(
            "nonexistent"
        )
        assert nonexistent_delivery is None

        # 存在しないユーザー回答の取得
        nonexistent_response = await dynamodb_client.user_responses.get_user_response(
            "nonexistent_delivery", "nonexistent_user"
        )
        assert nonexistent_response is None

        # 重複作成エラー
        question = Question(
            question_id="q_duplicate_test",
            question_text="これは重複テスト用の詳細な問題文です",
            choices=["A", "B"],
            correct_answer="A",
            explanation="これは重複テスト用の詳細な解説文です",
            service=AWSService.EC2,
            topic="重複テスト",
            difficulty=DifficultyLevel.ASSOCIATE,
        )

        # 最初の作成は成功
        await dynamodb_client.questions.create_question(question)

        # 重複作成は失敗
        from app.shared.exceptions import ValidationError

        with pytest.raises(ValidationError):
            await dynamodb_client.questions.create_question(question)

    @pytest.mark.asyncio
    async def test_data_consistency_integration(
        self, dynamodb_client: DynamoDBClient
    ) -> None:
        """データ整合性の統合テスト"""
        with freeze_time("2025-08-11 15:30:00"):
            # 問題作成
            question = Question(
                question_id="q_consistency_001",
                question_text="これは整合性テスト用の詳細な問題文です",
                choices=["A", "B", "C", "D"],
                correct_answer="B",
                explanation="これは整合性テスト用の詳細な解説文です",
                service=AWSService.S3,
                topic="整合性テスト",
                difficulty=DifficultyLevel.PROFESSIONAL,
                quality_score=Decimal("0.9"),
            )
            await dynamodb_client.questions.create_question(question)

            # 配信履歴作成
            delivery = Delivery(
                delivery_id="d_consistency_001",
                question_id="q_consistency_001",
                teams_channel_id="19:consistency@thread.tacv2",
                status=DeliveryStatus.POSTED,
            )
            await dynamodb_client.deliveries.create_delivery(delivery)

            # ユーザー回答作成
            user_response = UserResponse(
                delivery_id="d_consistency_001",
                user_id="consistency_user",
                user_name="整合性テストユーザー",
                selected_answer="B",
                is_correct=True,
                reaction_type=ReactionType.B,
            )
            await dynamodb_client.user_responses.create_user_response(user_response)

            # データ整合性確認
            # 1. 問題から配信履歴への参照
            deliveries = await dynamodb_client.deliveries.get_deliveries_by_question(
                question.question_id
            )
            assert len(deliveries) == 1
            assert deliveries[0].delivery_id == delivery.delivery_id

            # 2. 配信履歴からユーザー回答への参照
            responses = await dynamodb_client.user_responses.get_responses_by_delivery(
                delivery.delivery_id
            )
            assert len(responses) == 1
            assert responses[0].user_id == user_response.user_id

            # 3. 統計の整合性
            summary = (
                await dynamodb_client.user_responses.get_delivery_response_summary(
                    delivery.delivery_id
                )
            )
            assert summary["total_responses"] == 1
            assert summary["correct_responses"] == 1
            assert summary["correct_rate"] == 1.0

            # 配信履歴の統計を更新
            await dynamodb_client.deliveries.update_response_stats(
                delivery.delivery_id,
                summary["total_responses"],
                summary["correct_responses"],
            )

            # 更新後の整合性確認
            updated_delivery = await dynamodb_client.deliveries.get_by_delivery_id(
                delivery.delivery_id
            )
            assert updated_delivery is not None
            assert updated_delivery.total_responses == summary["total_responses"]
            assert updated_delivery.correct_responses == summary["correct_responses"]
            assert updated_delivery.correct_rate == summary["correct_rate"]
