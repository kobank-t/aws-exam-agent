"""
基底リポジトリクラス

DynamoDB操作の共通機能を提供する基底クラス
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, TypeVar

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.shared.config import config
from app.shared.exceptions import (
    DataAccessError,
    ItemNotFoundError,
    ValidationError,
)

# ジェネリック型変数
T = TypeVar("T")

logger = logging.getLogger(__name__)


class BaseRepository[T](ABC):
    """DynamoDB操作の基底リポジトリクラス"""

    def __init__(self, table_name: str | None = None):
        """
        リポジトリを初期化

        Args:
            table_name: DynamoDBテーブル名（Noneの場合は設定から取得）
        """
        self.table_name = table_name or config.DYNAMODB_TABLE_NAME
        self.region = config.DYNAMODB_REGION

        # DynamoDBクライアントの初期化
        try:
            # テスト環境（moto）ではプロファイルを使用しない
            try:
                # プロファイル付きで試行
                self.dynamodb = boto3.resource(
                    "dynamodb",
                    region_name=self.region,
                    **(
                        {"profile_name": config.AWS_PROFILE}
                        if config.AWS_PROFILE
                        else {}
                    ),
                )
            except TypeError:
                # moto環境ではprofile_nameが使用できないため、プロファイルなしで再試行
                self.dynamodb = boto3.resource("dynamodb", region_name=self.region)
            self.table = self.dynamodb.Table(self.table_name)
            logger.info(f"DynamoDB接続成功: {self.table_name} ({self.region})")
        except Exception as e:
            logger.error(f"DynamoDB接続失敗: {e}")
            raise DataAccessError(f"DynamoDB接続に失敗しました: {e}") from e

    @abstractmethod
    def _to_model(self, item: dict[str, Any]) -> T:
        """DynamoDBアイテムをモデルオブジェクトに変換"""
        pass

    @abstractmethod
    def _from_model(self, model: T) -> dict[str, Any]:
        """モデルオブジェクトをDynamoDBアイテムに変換"""
        pass

    def _handle_dynamodb_error(self, error: Exception, operation: str) -> None:
        """DynamoDBエラーを適切な例外に変換"""
        if isinstance(error, ClientError):
            error_code = error.response["Error"]["Code"]
            error_message = error.response["Error"]["Message"]

            if error_code == "ResourceNotFoundException":
                raise ItemNotFoundError(f"テーブルが見つかりません: {self.table_name}")
            elif error_code == "ValidationException":
                raise ValidationError(f"バリデーションエラー: {error_message}")
            elif error_code == "ConditionalCheckFailedException":
                raise ValidationError(f"条件チェック失敗: {error_message}")
            elif error_code == "ProvisionedThroughputExceededException":
                raise DataAccessError(f"スループット制限に達しました: {error_message}")
            else:
                raise DataAccessError(
                    f"{operation}操作でエラーが発生しました: {error_message}"
                )
        elif isinstance(error, BotoCoreError):
            raise DataAccessError(
                f"{operation}操作でBotoCoreエラーが発生しました: {error}"
            )
        elif isinstance(error, ValidationError):
            # ValidationErrorはそのまま再発生
            raise error
        else:
            raise DataAccessError(
                f"{operation}操作で予期しないエラーが発生しました: {error}"
            )

    async def get_by_key(self, pk: str, sk: str) -> T | None:
        """
        プライマリキーでアイテムを取得

        Args:
            pk: パーティションキー
            sk: ソートキー

        Returns:
            モデルオブジェクト（見つからない場合はNone）

        Raises:
            DataAccessError: データアクセスエラー
        """
        try:
            response = self.table.get_item(Key={"PK": pk, "SK": sk})

            if "Item" not in response:
                logger.debug(f"アイテムが見つかりません: PK={pk}, SK={sk}")
                return None

            logger.debug(f"アイテム取得成功: PK={pk}, SK={sk}")
            return self._to_model(response["Item"])

        except Exception as e:
            logger.error(f"get_by_key エラー: PK={pk}, SK={sk}, error={e}")
            self._handle_dynamodb_error(e, "get_by_key")
            return None

    async def put_item(self, model: T) -> T:
        """
        アイテムを保存

        Args:
            model: 保存するモデルオブジェクト

        Returns:
            保存されたモデルオブジェクト

        Raises:
            DataAccessError: データアクセスエラー
            ValidationError: バリデーションエラー
        """
        try:
            item = self._from_model(model)
            self.table.put_item(Item=item)

            logger.debug(f"アイテム保存成功: PK={item.get('PK')}, SK={item.get('SK')}")
            return model

        except Exception as e:
            logger.error(f"put_item エラー: model={type(model).__name__}, error={e}")
            self._handle_dynamodb_error(e, "put_item")
            return model

    async def update_item(
        self,
        pk: str,
        sk: str,
        update_expression: str,
        expression_attribute_values: dict[str, Any],
        expression_attribute_names: dict[str, str] | None = None,
    ) -> bool:
        """
        アイテムを更新

        Args:
            pk: パーティションキー
            sk: ソートキー
            update_expression: 更新式
            expression_attribute_values: 属性値
            expression_attribute_names: 属性名（予約語対応）

        Returns:
            更新成功の場合True

        Raises:
            DataAccessError: データアクセスエラー
            ItemNotFoundError: アイテムが見つからない
        """
        try:
            update_params = {
                "Key": {"PK": pk, "SK": sk},
                "UpdateExpression": update_expression,
                "ExpressionAttributeValues": expression_attribute_values,
                "ReturnValues": "UPDATED_NEW",
            }

            if expression_attribute_names:
                update_params["ExpressionAttributeNames"] = expression_attribute_names

            self.table.update_item(**update_params)

            logger.debug(f"アイテム更新成功: PK={pk}, SK={sk}")
            return True

        except Exception as e:
            logger.error(f"update_item エラー: PK={pk}, SK={sk}, error={e}")
            self._handle_dynamodb_error(e, "update_item")
            return False

    async def delete_item(self, pk: str, sk: str) -> bool:
        """
        アイテムを削除

        Args:
            pk: パーティションキー
            sk: ソートキー

        Returns:
            削除成功の場合True

        Raises:
            DataAccessError: データアクセスエラー
        """
        try:
            self.table.delete_item(Key={"PK": pk, "SK": sk})

            logger.debug(f"アイテム削除成功: PK={pk}, SK={sk}")
            return True

        except Exception as e:
            logger.error(f"delete_item エラー: PK={pk}, SK={sk}, error={e}")
            self._handle_dynamodb_error(e, "delete_item")
            return False

    async def query_by_pk(
        self,
        pk: str,
        sk_condition: str | None = None,
        limit: int | None = None,
        scan_index_forward: bool = True,
    ) -> list[T]:
        """
        パーティションキーでクエリ

        Args:
            pk: パーティションキー
            sk_condition: ソートキー条件（例: "begins_with(SK, :sk_prefix)"）
            limit: 取得件数制限
            scan_index_forward: ソート順（True: 昇順, False: 降順）

        Returns:
            モデルオブジェクトのリスト

        Raises:
            DataAccessError: データアクセスエラー
        """
        try:
            query_params = {
                "KeyConditionExpression": "PK = :pk",
                "ExpressionAttributeValues": {":pk": pk},
                "ScanIndexForward": scan_index_forward,
            }

            if sk_condition:
                current_expression = query_params["KeyConditionExpression"]
                query_params["KeyConditionExpression"] = (
                    f"{current_expression} AND {sk_condition}"
                )

            if limit:
                query_params["Limit"] = limit

            response = self.table.query(**query_params)

            items = response.get("Items", [])
            logger.debug(f"クエリ成功: PK={pk}, 件数={len(items)}")

            return [self._to_model(item) for item in items]

        except Exception as e:
            logger.error(f"query_by_pk エラー: PK={pk}, error={e}")
            self._handle_dynamodb_error(e, "query_by_pk")
            return []

    async def query_by_gsi(
        self,
        index_name: str,
        gsi_pk: str,
        gsi_sk_condition: str | None = None,
        expression_attribute_values: dict[str, Any] | None = None,
        limit: int | None = None,
        scan_index_forward: bool = True,
    ) -> list[T]:
        """
        GSI（Global Secondary Index）でクエリ

        Args:
            index_name: インデックス名（GSI1, GSI2等）
            gsi_pk: GSIパーティションキー
            gsi_sk_condition: GSIソートキー条件
            limit: 取得件数制限
            scan_index_forward: ソート順（True: 昇順, False: 降順）

        Returns:
            モデルオブジェクトのリスト

        Raises:
            DataAccessError: データアクセスエラー
        """
        try:
            query_params = {
                "IndexName": index_name,
                "KeyConditionExpression": f"{index_name}PK = :gsi_pk",
                "ExpressionAttributeValues": {":gsi_pk": gsi_pk},
                "ScanIndexForward": scan_index_forward,
            }

            if gsi_sk_condition:
                current_expression = query_params["KeyConditionExpression"]
                query_params["KeyConditionExpression"] = (
                    f"{current_expression} AND {gsi_sk_condition}"
                )

            if expression_attribute_values:
                current_values = query_params.get("ExpressionAttributeValues", {})
                if isinstance(current_values, dict):
                    current_values.update(expression_attribute_values)
                    query_params["ExpressionAttributeValues"] = current_values

            if limit:
                query_params["Limit"] = limit

            response = self.table.query(**query_params)

            items = response.get("Items", [])
            logger.debug(
                f"GSIクエリ成功: {index_name}, GSI_PK={gsi_pk}, 件数={len(items)}"
            )

            return [self._to_model(item) for item in items]

        except Exception as e:
            logger.error(
                f"query_by_gsi エラー: {index_name}, GSI_PK={gsi_pk}, error={e}"
            )
            self._handle_dynamodb_error(e, "query_by_gsi")
            return []

    async def batch_get_items(self, keys: list[dict[str, str]]) -> list[T]:
        """
        複数アイテムを一括取得

        Args:
            keys: キーのリスト（例: [{"PK": "QUESTION#q1", "SK": "METADATA"}]）

        Returns:
            モデルオブジェクトのリスト

        Raises:
            DataAccessError: データアクセスエラー
        """
        try:
            if not keys:
                return []

            # DynamoDBのbatch_get_itemは最大100件まで
            if len(keys) > 100:
                raise ValidationError("一括取得は最大100件までです")

            response = self.dynamodb.batch_get_item(
                RequestItems={self.table_name: {"Keys": keys}}
            )

            items = response.get("Responses", {}).get(self.table_name, [])
            logger.debug(f"一括取得成功: 要求={len(keys)}件, 取得={len(items)}件")

            return [self._to_model(item) for item in items]

        except Exception as e:
            logger.error(f"batch_get_items エラー: keys={len(keys)}件, error={e}")
            self._handle_dynamodb_error(e, "batch_get_items")
            return []

    async def batch_write_items(self, models: list[T]) -> bool:
        """
        複数アイテムを一括保存

        Args:
            models: 保存するモデルオブジェクトのリスト

        Returns:
            保存成功の場合True

        Raises:
            DataAccessError: データアクセスエラー
        """
        try:
            if not models:
                return True

            # DynamoDBのbatch_write_itemは最大25件まで
            if len(models) > 25:
                raise ValidationError("一括保存は最大25件までです")

            put_requests = [
                {"PutRequest": {"Item": self._from_model(model)}} for model in models
            ]

            response = self.dynamodb.batch_write_item(
                RequestItems={self.table_name: put_requests}
            )

            # 未処理アイテムがある場合は警告
            unprocessed = response.get("UnprocessedItems", {})
            if unprocessed:
                logger.warning(f"未処理アイテムあり: {len(unprocessed)}件")

            logger.debug(f"一括保存成功: {len(models)}件")
            return True

        except Exception as e:
            logger.error(f"batch_write_items エラー: models={len(models)}件, error={e}")
            self._handle_dynamodb_error(e, "batch_write_items")
            return False

    def get_table_info(self) -> dict[str, Any]:
        """
        テーブル情報を取得

        Returns:
            テーブル情報の辞書
        """
        try:
            table_description = self.table.meta.client.describe_table(
                TableName=self.table_name
            )
            return {
                "table_name": self.table_name,
                "table_status": table_description["Table"]["TableStatus"],
                "item_count": table_description["Table"]["ItemCount"],
                "table_size_bytes": table_description["Table"]["TableSizeBytes"],
                "creation_date_time": str(
                    table_description["Table"]["CreationDateTime"]
                ),
            }
        except Exception as e:
            logger.error(f"テーブル情報取得エラー: {e}")
            return {"table_name": self.table_name, "error": str(e)}
