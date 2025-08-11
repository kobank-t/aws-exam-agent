"""
DynamoDB統合クライアント

全リポジトリを統合管理するクライアントクラス
"""

import logging
from datetime import datetime
from typing import Any

import boto3
from botocore.exceptions import ClientError

from app.shared.config import config
from app.shared.exceptions import DataAccessError

from .delivery_repository import DeliveryRepository
from .question_repository import QuestionRepository
from .user_response_repository import UserResponseRepository

logger = logging.getLogger(__name__)


class DynamoDBClient:
    """DynamoDB統合クライアント"""

    def __init__(self, table_name: str | None = None):
        """
        DynamoDBクライアントを初期化

        Args:
            table_name: DynamoDBテーブル名（Noneの場合は設定から取得）
        """
        self.table_name = table_name or config.DYNAMODB_TABLE_NAME
        self.region = config.DYNAMODB_REGION

        # リポジトリインスタンスを初期化
        self.questions = QuestionRepository(self.table_name)
        self.deliveries = DeliveryRepository(self.table_name)
        self.user_responses = UserResponseRepository(self.table_name)

        logger.info(f"DynamoDBClient初期化完了: {self.table_name} ({self.region})")

    async def health_check(self) -> dict[str, Any]:
        """
        DynamoDB接続の健全性チェック

        Returns:
            健全性チェック結果の辞書
        """
        try:
            # テーブル情報を取得して接続確認
            table_info = self.questions.get_table_info()

            return {
                "status": "healthy",
                "table_name": self.table_name,
                "region": self.region,
                "table_info": table_info,
            }

        except Exception as e:
            logger.error(f"DynamoDB健全性チェック失敗: {e}")
            return {
                "status": "unhealthy",
                "table_name": self.table_name,
                "region": self.region,
                "error": str(e),
            }

    async def initialize_table(self) -> bool:
        """
        テーブルの初期化（開発・テスト用）

        Returns:
            初期化成功の場合True

        Note:
            本番環境では、SAMテンプレートでテーブルを作成するため、
            この機能は開発・テスト環境でのみ使用
        """
        try:
            if config.AWS_PROFILE:
                session = boto3.Session(profile_name=config.AWS_PROFILE)
                dynamodb = session.client("dynamodb", region_name=self.region)
            else:
                dynamodb = boto3.client("dynamodb", region_name=self.region)

            # テーブル存在確認
            try:
                dynamodb.describe_table(TableName=self.table_name)
                logger.info(f"テーブル '{self.table_name}' は既に存在します")
                return True
            except ClientError as e:
                if e.response["Error"]["Code"] != "ResourceNotFoundException":
                    raise

            # テーブル作成
            table_definition = {
                "TableName": self.table_name,
                "KeySchema": [
                    {"AttributeName": "PK", "KeyType": "HASH"},
                    {"AttributeName": "SK", "KeyType": "RANGE"},
                ],
                "AttributeDefinitions": [
                    {"AttributeName": "PK", "AttributeType": "S"},
                    {"AttributeName": "SK", "AttributeType": "S"},
                    {"AttributeName": "GSI1PK", "AttributeType": "S"},
                    {"AttributeName": "GSI1SK", "AttributeType": "S"},
                    {"AttributeName": "GSI2PK", "AttributeType": "S"},
                    {"AttributeName": "GSI2SK", "AttributeType": "S"},
                ],
                "GlobalSecondaryIndexes": [
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
                "BillingMode": "PAY_PER_REQUEST",
            }

            dynamodb.create_table(**table_definition)
            logger.info(f"テーブル '{self.table_name}' を作成しました")

            # テーブルがアクティブになるまで待機
            waiter = dynamodb.get_waiter("table_exists")
            waiter.wait(TableName=self.table_name)

            logger.info(f"テーブル '{self.table_name}' がアクティブになりました")
            return True

        except Exception as e:
            logger.error(f"テーブル初期化エラー: {e}")
            raise DataAccessError(f"テーブル初期化に失敗しました: {e}") from e

    async def get_system_statistics(self) -> dict[str, Any]:
        """
        システム全体の統計情報を取得

        Returns:
            システム統計の辞書
        """
        try:
            # 各リポジトリから統計を取得
            question_stats = await self.questions.get_questions_count_by_service()
            delivery_stats = await self.deliveries.get_delivery_statistics()

            # テーブル情報
            table_info = self.questions.get_table_info()

            return {
                "table_info": table_info,
                "question_statistics": question_stats,
                "delivery_statistics": delivery_stats,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"システム統計取得エラー: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def cleanup_old_data(self, days: int = 90) -> dict[str, Any]:
        """
        古いデータをクリーンアップ

        Args:
            days: 保持期間（日数）

        Returns:
            削除件数の辞書
        """
        try:
            # 各リポジトリでクリーンアップ実行
            deleted_deliveries = await self.deliveries.cleanup_old_deliveries(days)
            deleted_responses = await self.user_responses.cleanup_old_responses(days)

            cleanup_result = {
                "deleted_deliveries": deleted_deliveries,
                "deleted_responses": deleted_responses,
                "total_deleted": deleted_deliveries + deleted_responses,
            }

            logger.info(f"データクリーンアップ完了: {cleanup_result}")
            return cleanup_result

        except Exception as e:
            logger.error(f"データクリーンアップエラー: {e}")
            return {
                "error": str(e),
                "deleted_deliveries": 0,
                "deleted_responses": 0,
                "total_deleted": 0,
            }

    def get_repository_info(self) -> dict[str, Any]:
        """
        リポジトリ情報を取得

        Returns:
            リポジトリ情報の辞書
        """
        return {
            "table_name": self.table_name,
            "region": self.region,
            "repositories": {
                "questions": type(self.questions).__name__,
                "deliveries": type(self.deliveries).__name__,
                "user_responses": type(self.user_responses).__name__,
            },
        }


# グローバルクライアントインスタンス（シングルトンパターン）
_dynamodb_client: DynamoDBClient | None = None


def get_dynamodb_client(table_name: str | None = None) -> DynamoDBClient:
    """
    DynamoDBクライアントのシングルトンインスタンスを取得

    Args:
        table_name: DynamoDBテーブル名（初回のみ有効）

    Returns:
        DynamoDBクライアントインスタンス
    """
    global _dynamodb_client

    if _dynamodb_client is None:
        _dynamodb_client = DynamoDBClient(table_name)

    return _dynamodb_client


def reset_dynamodb_client() -> None:
    """
    DynamoDBクライアントをリセット（テスト用）
    """
    global _dynamodb_client
    _dynamodb_client = None
