"""
配信履歴リポジトリ

Delivery エンティティのDynamoDB操作を提供
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from app.models.delivery import Delivery, DeliveryStatus
from app.shared.exceptions import ValidationError

from .base import BaseRepository

logger = logging.getLogger(__name__)


class DeliveryRepository(BaseRepository[Delivery]):
    """配信履歴データのリポジトリクラス"""

    def _to_model(self, item: dict[str, Any]) -> Delivery:
        """DynamoDBアイテムをDeliveryモデルに変換"""
        return Delivery.from_dynamodb_item(item)

    def _from_model(self, model: Delivery) -> dict[str, Any]:
        """DeliveryモデルをDynamoDBアイテムに変換"""
        return model.to_dynamodb_item()

    async def get_by_delivery_id(self, delivery_id: str) -> Delivery | None:
        """
        配信IDで配信履歴を取得

        Args:
            delivery_id: 配信ID（例: d_20250729_001）

        Returns:
            配信履歴オブジェクト（見つからない場合はNone）
        """
        pk = f"DELIVERY#{delivery_id}"
        sk = "METADATA"
        return await self.get_by_key(pk, sk)

    async def create_delivery(self, delivery: Delivery) -> Delivery:
        """
        新しい配信履歴を作成

        Args:
            delivery: 作成する配信履歴オブジェクト

        Returns:
            作成された配信履歴オブジェクト

        Raises:
            ValidationError: 同じIDの配信履歴が既に存在する場合
        """
        # 既存チェック
        existing = await self.get_by_delivery_id(delivery.delivery_id)
        if existing:
            raise ValidationError(f"配信ID '{delivery.delivery_id}' は既に存在します")

        # 作成日時を設定
        delivery.created_at = datetime.now()
        delivery.updated_at = datetime.now()

        return await self.put_item(delivery)

    async def update_delivery(self, delivery: Delivery) -> Delivery:
        """
        配信履歴を更新

        Args:
            delivery: 更新する配信履歴オブジェクト

        Returns:
            更新された配信履歴オブジェクト

        Raises:
            ValidationError: 配信履歴が存在しない場合
        """
        # 存在チェック
        existing = await self.get_by_delivery_id(delivery.delivery_id)
        if not existing:
            raise ValidationError(f"配信ID '{delivery.delivery_id}' が見つかりません")

        # 更新日時を設定
        delivery.updated_at = datetime.now()

        return await self.put_item(delivery)

    async def get_deliveries_by_question(self, question_id: str) -> list[Delivery]:
        """
        問題IDで配信履歴を取得

        Args:
            question_id: 問題ID

        Returns:
            配信履歴のリスト（配信日時の降順）
        """
        gsi_pk = f"QUESTION#{question_id}"
        return await self.query_by_gsi(
            index_name="GSI1",
            gsi_pk=gsi_pk,
            scan_index_forward=False,  # 新しい順
        )

    async def get_deliveries_by_status(
        self, status: DeliveryStatus, limit: int | None = None
    ) -> list[Delivery]:
        """
        ステータス別に配信履歴を取得

        Args:
            status: 配信ステータス
            limit: 取得件数制限

        Returns:
            配信履歴のリスト（配信日時の降順）
        """
        gsi_pk = f"STATUS#{status.value}"
        return await self.query_by_gsi(
            index_name="GSI2",
            gsi_pk=gsi_pk,
            limit=limit,
            scan_index_forward=False,  # 新しい順
        )

    async def get_active_deliveries(self) -> list[Delivery]:
        """
        アクティブな配信履歴を取得

        Returns:
            アクティブな配信履歴のリスト
        """
        active_deliveries = []

        # PENDINGとPOSTEDの配信を取得
        for status in [DeliveryStatus.PENDING, DeliveryStatus.POSTED]:
            deliveries = await self.get_deliveries_by_status(status)
            active_deliveries.extend(deliveries)

        # 配信日時降順でソート
        active_deliveries.sort(key=lambda d: d.posted_at or d.created_at, reverse=True)

        return active_deliveries

    async def get_recent_deliveries(
        self, days: int = 7, limit: int | None = None
    ) -> list[Delivery]:
        """
        最近の配信履歴を取得

        Args:
            days: 過去何日間の配信を取得するか
            limit: 取得件数制限

        Returns:
            最近の配信履歴のリスト
        """
        cutoff_date = datetime.now() - timedelta(days=days)

        # 全ステータスから最近の配信を取得
        all_deliveries = []

        for status in DeliveryStatus:
            gsi_pk = f"STATUS#{status.value}"
            deliveries = await self.query_by_gsi(
                index_name="GSI2",
                gsi_pk=gsi_pk,
                gsi_sk_condition="GSI2SK >= :cutoff_date",
                expression_attribute_values={":cutoff_date": cutoff_date.isoformat()},
                limit=limit,
                scan_index_forward=False,  # 新しい順
            )

            # 追加のフィルタリング
            recent_deliveries = [
                d for d in deliveries if (d.posted_at or d.created_at) >= cutoff_date
            ]
            all_deliveries.extend(recent_deliveries)

        # 配信日時降順でソート
        all_deliveries.sort(key=lambda d: d.posted_at or d.created_at, reverse=True)

        return all_deliveries[:limit] if limit else all_deliveries

    async def update_delivery_status(
        self,
        delivery_id: str,
        status: DeliveryStatus,
        teams_message_id: str | None = None,
        error_message: str | None = None,
    ) -> bool:
        """
        配信ステータスを更新

        Args:
            delivery_id: 配信ID
            status: 新しいステータス
            teams_message_id: TeamsメッセージID（配信完了時）
            error_message: エラーメッセージ（失敗時）

        Returns:
            更新成功の場合True
        """
        pk = f"DELIVERY#{delivery_id}"
        sk = "METADATA"

        # 更新する属性を準備
        update_expression_parts = ["#status = :status", "updated_at = :updated_at"]
        expression_attribute_values = {
            ":status": status.value,
            ":updated_at": datetime.now().isoformat(),
        }
        expression_attribute_names = {"#status": "status"}

        # ステータスに応じて追加の属性を更新
        if status == DeliveryStatus.POSTED and teams_message_id:
            update_expression_parts.extend(
                ["teams_message_id = :teams_message_id", "posted_at = :posted_at"]
            )
            expression_attribute_values.update(
                {
                    ":teams_message_id": teams_message_id,
                    ":posted_at": datetime.now().isoformat(),
                }
            )

        elif status == DeliveryStatus.ANSWERED:
            update_expression_parts.append("answered_at = :answered_at")
            expression_attribute_values[":answered_at"] = datetime.now().isoformat()

        elif status == DeliveryStatus.FAILED and error_message:
            update_expression_parts.append("error_message = :error_message")
            expression_attribute_values[":error_message"] = error_message

        # GSI2キーも更新
        gsi2_pk = f"STATUS#{status.value}"
        posted_time = datetime.now().isoformat()
        gsi2_sk = f"POSTED#{posted_time}"

        update_expression_parts.extend(["GSI2PK = :gsi2_pk", "GSI2SK = :gsi2_sk"])
        expression_attribute_values.update(
            {
                ":gsi2_pk": gsi2_pk,
                ":gsi2_sk": gsi2_sk,
            }
        )

        update_expression = "SET " + ", ".join(update_expression_parts)

        return await self.update_item(
            pk=pk,
            sk=sk,
            update_expression=update_expression,
            expression_attribute_values=expression_attribute_values,
            expression_attribute_names=expression_attribute_names,
        )

    async def update_response_stats(
        self, delivery_id: str, total_responses: int, correct_responses: int
    ) -> bool:
        """
        回答統計を更新

        Args:
            delivery_id: 配信ID
            total_responses: 総回答数
            correct_responses: 正解数

        Returns:
            更新成功の場合True

        Raises:
            ValidationError: 正解数が総回答数を超える場合
        """
        if correct_responses > total_responses:
            raise ValidationError(
                f"正解数 {correct_responses} が総回答数 {total_responses} を超えています"
            )

        pk = f"DELIVERY#{delivery_id}"
        sk = "METADATA"

        # 正解率を計算（Decimal型で）
        from decimal import Decimal

        correct_rate = (
            Decimal(str(correct_responses)) / Decimal(str(total_responses))
            if total_responses > 0
            else None
        )

        update_expression = "SET total_responses = :total, correct_responses = :correct, correct_rate = :rate, updated_at = :updated_at"
        expression_attribute_values = {
            ":total": total_responses,
            ":correct": correct_responses,
            ":rate": correct_rate,
            ":updated_at": datetime.now().isoformat(),
        }

        return await self.update_item(
            pk=pk,
            sk=sk,
            update_expression=update_expression,
            expression_attribute_values=expression_attribute_values,
        )

    async def get_delivery_statistics(self, days: int = 30) -> dict[str, Any]:
        """
        配信統計を取得

        Args:
            days: 統計期間（日数）

        Returns:
            配信統計の辞書
        """
        recent_deliveries = await self.get_recent_deliveries(days)

        # ステータス別集計
        status_counts = {}
        for status in DeliveryStatus:
            status_counts[status.value] = len(
                [d for d in recent_deliveries if d.status == status]
            )

        # 回答統計
        total_responses = sum(d.total_responses for d in recent_deliveries)
        total_correct = sum(d.correct_responses for d in recent_deliveries)
        overall_correct_rate = (
            total_correct / total_responses if total_responses > 0 else 0.0
        )

        # 配信成功率
        total_deliveries = len(recent_deliveries)
        successful_deliveries = len(
            [
                d
                for d in recent_deliveries
                if d.status in [DeliveryStatus.POSTED, DeliveryStatus.ANSWERED]
            ]
        )
        success_rate = (
            successful_deliveries / total_deliveries if total_deliveries > 0 else 0.0
        )

        return {
            "period_days": days,
            "total_deliveries": total_deliveries,
            "status_counts": status_counts,
            "success_rate": success_rate,
            "total_responses": total_responses,
            "total_correct_responses": total_correct,
            "overall_correct_rate": overall_correct_rate,
        }

    async def cleanup_old_deliveries(self, days: int = 90) -> int:
        """
        古い配信履歴をクリーンアップ

        Args:
            days: 保持期間（日数）

        Returns:
            削除した配信履歴の数
        """
        cutoff_date = datetime.now() - timedelta(days=days)

        # 完了した古い配信を取得
        old_deliveries = []
        for status in [
            DeliveryStatus.ANSWERED,
            DeliveryStatus.FAILED,
            DeliveryStatus.CANCELLED,
        ]:
            deliveries = await self.get_deliveries_by_status(status)
            old_deliveries.extend(
                [d for d in deliveries if (d.posted_at or d.created_at) < cutoff_date]
            )

        # 削除実行
        deleted_count = 0
        for delivery in old_deliveries:
            pk = f"DELIVERY#{delivery.delivery_id}"
            sk = "METADATA"
            if await self.delete_item(pk, sk):
                deleted_count += 1

        logger.info(f"古い配信履歴をクリーンアップ: {deleted_count}件削除")
        return deleted_count
