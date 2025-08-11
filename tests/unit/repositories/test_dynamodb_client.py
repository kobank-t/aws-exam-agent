"""
DynamoDB統合クライアントの単体テスト
"""

from collections.abc import Generator
from unittest.mock import patch

import pytest
from moto import mock_aws

from app.repositories.delivery_repository import DeliveryRepository
from app.repositories.dynamodb_client import (
    DynamoDBClient,
    get_dynamodb_client,
    reset_dynamodb_client,
)
from app.repositories.question_repository import QuestionRepository
from app.repositories.user_response_repository import UserResponseRepository


@pytest.fixture
def dynamodb_client() -> Generator[DynamoDBClient, None, None]:
    """DynamoDBクライアントフィクスチャ"""
    with mock_aws():
        # テーブル作成
        import boto3

        dynamodb = boto3.resource("dynamodb", region_name="ap-northeast-1")

        table = dynamodb.create_table(
            TableName="test-client-table",
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
        yield DynamoDBClient("test-client-table")


class TestDynamoDBClient:
    """DynamoDB統合クライアントのテスト"""

    def test_client_initialization(self, dynamodb_client: DynamoDBClient) -> None:
        """クライアント初期化のテスト"""
        assert dynamodb_client.table_name == "test-client-table"
        assert dynamodb_client.region == "ap-northeast-1"

        # リポジトリインスタンスが正しく作成されていることを確認
        assert isinstance(dynamodb_client.questions, QuestionRepository)
        assert isinstance(dynamodb_client.deliveries, DeliveryRepository)
        assert isinstance(dynamodb_client.user_responses, UserResponseRepository)

    @pytest.mark.asyncio
    async def test_health_check_healthy(self, dynamodb_client: DynamoDBClient) -> None:
        """健全性チェック（正常）のテスト"""
        health_result = await dynamodb_client.health_check()

        assert health_result["status"] == "healthy"
        assert health_result["table_name"] == "test-client-table"
        assert health_result["region"] == "ap-northeast-1"
        assert "table_info" in health_result

    @pytest.mark.asyncio
    async def test_health_check_unhealthy(
        self, dynamodb_client: DynamoDBClient
    ) -> None:
        """健全性チェック（異常）のテスト"""
        # テーブル情報取得でエラーを発生させる
        with patch.object(dynamodb_client.questions, "get_table_info") as mock_get_info:
            mock_get_info.side_effect = Exception("Connection failed")

            health_result = await dynamodb_client.health_check()

            assert health_result["status"] == "unhealthy"
            assert "error" in health_result

    @pytest.mark.asyncio
    async def test_initialize_table_existing(
        self, dynamodb_client: DynamoDBClient
    ) -> None:
        """既存テーブルの初期化テスト"""
        # テーブルが既に存在する場合
        success = await dynamodb_client.initialize_table()
        assert success is True

    @pytest.mark.asyncio
    async def test_initialize_table_new(self) -> None:
        """新規テーブルの初期化テスト"""
        with mock_aws():
            # テーブルが存在しない状態でクライアントを作成
            client = DynamoDBClient("new-test-table")

            # テーブル初期化
            success = await client.initialize_table()
            assert success is True

            # テーブルが作成されたことを確認
            health_result = await client.health_check()
            assert health_result["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_get_system_statistics(self, dynamodb_client: DynamoDBClient) -> None:
        """システム統計取得のテスト"""
        # モックデータを準備
        with patch.object(
            dynamodb_client.questions, "get_questions_count_by_service"
        ) as mock_q_stats:
            with patch.object(
                dynamodb_client.deliveries, "get_delivery_statistics"
            ) as mock_d_stats:
                mock_q_stats.return_value = {"EC2": 5, "S3": 3}
                mock_d_stats.return_value = {
                    "total_deliveries": 10,
                    "success_rate": 0.9,
                }

                stats = await dynamodb_client.get_system_statistics()

                assert "table_info" in stats
                assert "question_statistics" in stats
                assert "delivery_statistics" in stats
                assert stats["question_statistics"]["EC2"] == 5
                assert stats["delivery_statistics"]["total_deliveries"] == 10

    @pytest.mark.asyncio
    async def test_get_system_statistics_error(
        self, dynamodb_client: DynamoDBClient
    ) -> None:
        """システム統計取得エラーのテスト"""
        with patch.object(
            dynamodb_client.questions, "get_questions_count_by_service"
        ) as mock_stats:
            mock_stats.side_effect = Exception("Statistics error")

            stats = await dynamodb_client.get_system_statistics()

            assert "error" in stats
            assert "Statistics error" in stats["error"]

    @pytest.mark.asyncio
    async def test_cleanup_old_data(self, dynamodb_client: DynamoDBClient) -> None:
        """古いデータクリーンアップのテスト"""
        with patch.object(
            dynamodb_client.deliveries, "cleanup_old_deliveries"
        ) as mock_d_cleanup:
            with patch.object(
                dynamodb_client.user_responses, "cleanup_old_responses"
            ) as mock_r_cleanup:
                mock_d_cleanup.return_value = 5
                mock_r_cleanup.return_value = 10

                cleanup_result = await dynamodb_client.cleanup_old_data(30)

                assert cleanup_result["deleted_deliveries"] == 5
                assert cleanup_result["deleted_responses"] == 10
                assert cleanup_result["total_deleted"] == 15

    @pytest.mark.asyncio
    async def test_cleanup_old_data_error(
        self, dynamodb_client: DynamoDBClient
    ) -> None:
        """データクリーンアップエラーのテスト"""
        with patch.object(
            dynamodb_client.deliveries, "cleanup_old_deliveries"
        ) as mock_cleanup:
            mock_cleanup.side_effect = Exception("Cleanup error")

            cleanup_result = await dynamodb_client.cleanup_old_data(30)

            assert "error" in cleanup_result
            assert cleanup_result["total_deleted"] == 0

    def test_get_repository_info(self, dynamodb_client: DynamoDBClient) -> None:
        """リポジトリ情報取得のテスト"""
        repo_info = dynamodb_client.get_repository_info()

        assert repo_info["table_name"] == "test-client-table"
        assert repo_info["region"] == "ap-northeast-1"
        assert "repositories" in repo_info
        assert repo_info["repositories"]["questions"] == "QuestionRepository"
        assert repo_info["repositories"]["deliveries"] == "DeliveryRepository"
        assert repo_info["repositories"]["user_responses"] == "UserResponseRepository"


class TestSingletonPattern:
    """シングルトンパターンのテスト"""

    def test_get_dynamodb_client_singleton(self) -> None:
        """シングルトンパターンのテスト"""
        # リセットしてクリーンな状態から開始
        reset_dynamodb_client()

        with mock_aws():
            # テーブル作成
            import boto3

            dynamodb = boto3.resource("dynamodb", region_name="ap-northeast-1")

            table = dynamodb.create_table(
                TableName="singleton-test-table",
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

            # 最初の取得
            client1 = get_dynamodb_client("singleton-test-table")

            # 2回目の取得（同じインスタンスが返されるはず）
            client2 = get_dynamodb_client("different-table")  # テーブル名は無視される

            # 同じインスタンスであることを確認
            assert client1 is client2
            assert client1.table_name == "singleton-test-table"

    def test_reset_dynamodb_client(self) -> None:
        """クライアントリセットのテスト"""
        reset_dynamodb_client()

        with mock_aws():
            # テーブル作成
            import boto3

            dynamodb = boto3.resource("dynamodb", region_name="ap-northeast-1")

            table = dynamodb.create_table(
                TableName="reset-test-table",
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

            # クライアント取得
            client1 = get_dynamodb_client("reset-test-table")

            # リセット
            reset_dynamodb_client()

            # 新しいクライアント取得
            client2 = get_dynamodb_client("reset-test-table")

            # 異なるインスタンスであることを確認
            assert client1 is not client2

    def teardown_method(self) -> None:
        """各テスト後のクリーンアップ"""
        reset_dynamodb_client()
