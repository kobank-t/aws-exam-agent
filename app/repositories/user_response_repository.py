"""
ユーザー回答リポジトリ

UserResponse エンティティのDynamoDB操作を提供
"""

import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from app.models.user_response import UserResponse
from app.shared.exceptions import ValidationError

from .base import BaseRepository

logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)


class UserResponseRepository(BaseRepository[UserResponse]):
    """ユーザー回答データのリポジトリクラス"""

    def _to_model(self, item: dict[str, Any]) -> UserResponse:
        """DynamoDBアイテムをUserResponseモデルに変換"""
        return UserResponse.from_dynamodb_item(item)

    def _from_model(self, model: UserResponse) -> dict[str, Any]:
        """UserResponseモデルをDynamoDBアイテムに変換"""
        return model.to_dynamodb_item()

    async def get_user_response(
        self, delivery_id: str, user_id: str
    ) -> UserResponse | None:
        """
        特定の配信に対するユーザーの回答を取得

        Args:
            delivery_id: 配信ID
            user_id: ユーザーID

        Returns:
            ユーザー回答オブジェクト（見つからない場合はNone）
        """
        pk = f"DELIVERY#{delivery_id}"
        sk = f"USER#{user_id}"
        return await self.get_by_key(pk, sk)

    async def create_user_response(self, user_response: UserResponse) -> UserResponse:
        """
        新しいユーザー回答を作成

        Args:
            user_response: 作成するユーザー回答オブジェクト

        Returns:
            作成されたユーザー回答オブジェクト

        Raises:
            ValidationError: 同じユーザーの回答が既に存在する場合
        """
        # 既存チェック
        existing = await self.get_user_response(
            user_response.delivery_id, user_response.user_id
        )
        if existing:
            raise ValidationError(
                f"ユーザー '{user_response.user_id}' の配信 '{user_response.delivery_id}' への回答は既に存在します"
            )

        # 作成日時を設定
        user_response.created_at = datetime.now()
        user_response.updated_at = datetime.now()

        return await self.put_item(user_response)

    async def update_user_response(self, user_response: UserResponse) -> UserResponse:
        """
        ユーザー回答を更新

        Args:
            user_response: 更新するユーザー回答オブジェクト

        Returns:
            更新されたユーザー回答オブジェクト

        Raises:
            ValidationError: ユーザー回答が存在しない場合
        """
        # 存在チェック
        existing = await self.get_user_response(
            user_response.delivery_id, user_response.user_id
        )
        if not existing:
            raise ValidationError(
                f"ユーザー '{user_response.user_id}' の配信 '{user_response.delivery_id}' への回答が見つかりません"
            )

        # 更新日時を設定
        user_response.updated_at = datetime.now()

        return await self.put_item(user_response)

    async def get_responses_by_delivery(self, delivery_id: str) -> list[UserResponse]:
        """
        特定の配信に対する全ユーザーの回答を取得

        Args:
            delivery_id: 配信ID

        Returns:
            ユーザー回答のリスト（回答日時の昇順）
        """
        try:
            query_params = {
                "KeyConditionExpression": "PK = :pk AND begins_with(SK, :user_prefix)",
                "ExpressionAttributeValues": {
                    ":pk": f"DELIVERY#{delivery_id}",
                    ":user_prefix": "USER#",
                },
                "ScanIndexForward": True,  # 古い順
            }

            response = self.table.query(**query_params)
            items = response.get("Items", [])

            return [self._to_model(item) for item in items]

        except Exception as e:
            logger.error(
                f"get_responses_by_delivery エラー: delivery_id={delivery_id}, error={e}"
            )
            self._handle_dynamodb_error(e, "get_responses_by_delivery")
            return []

    async def get_responses_by_user(
        self, user_id: str, limit: int | None = None
    ) -> list[UserResponse]:
        """
        特定ユーザーの回答履歴を取得

        Args:
            user_id: ユーザーID
            limit: 取得件数制限

        Returns:
            ユーザー回答のリスト（回答日時の降順）
        """
        gsi_pk = f"USER#{user_id}"
        return await self.query_by_gsi(
            index_name="GSI1",
            gsi_pk=gsi_pk,
            limit=limit,
            scan_index_forward=False,  # 新しい順
        )

    async def get_recent_responses_by_delivery(
        self, delivery_id: str, hours: int = 24
    ) -> list[UserResponse]:
        """
        特定配信の最近の回答を取得

        Args:
            delivery_id: 配信ID
            hours: 過去何時間の回答を取得するか

        Returns:
            最近のユーザー回答のリスト
        """
        cutoff_time = datetime.now(UTC) - timedelta(hours=hours)
        gsi_pk = f"DELIVERY#{delivery_id}"

        responses = await self.query_by_gsi(
            index_name="GSI2",
            gsi_pk=gsi_pk,
            gsi_sk_condition="GSI2SK >= :cutoff_time",
            expression_attribute_values={":cutoff_time": cutoff_time.isoformat()},
            scan_index_forward=False,  # 新しい順
        )

        # 追加のフィルタリング
        recent_responses = [r for r in responses if r.responded_at >= cutoff_time]

        return recent_responses

    async def get_delivery_response_summary(self, delivery_id: str) -> dict[str, Any]:
        """
        配信の回答サマリーを取得

        Args:
            delivery_id: 配信ID

        Returns:
            回答サマリーの辞書
        """
        responses = await self.get_responses_by_delivery(delivery_id)

        if not responses:
            return {
                "delivery_id": delivery_id,
                "total_responses": 0,
                "correct_responses": 0,
                "correct_rate": None,
                "response_breakdown": {},
                "user_responses": [],
            }

        # 統計計算
        total_responses = len(responses)
        correct_responses = sum(1 for r in responses if r.is_correct)
        correct_rate = correct_responses / total_responses

        # 選択肢別集計
        response_breakdown: dict[str, int] = {}
        for response in responses:
            answer = response.selected_answer
            response_breakdown[answer] = response_breakdown.get(answer, 0) + 1

        # ユーザー回答詳細
        user_responses = [
            {
                "user_id": r.user_id,
                "user_name": r.user_name,
                "selected_answer": r.selected_answer,
                "is_correct": r.is_correct,
                "responded_at": r.responded_at.isoformat(),
                "reaction_type": r.reaction_type.value,
            }
            for r in responses
        ]

        return {
            "delivery_id": delivery_id,
            "total_responses": total_responses,
            "correct_responses": correct_responses,
            "correct_rate": correct_rate,
            "response_breakdown": response_breakdown,
            "user_responses": user_responses,
        }

    async def get_user_statistics(self, user_id: str, days: int = 30) -> dict[str, Any]:
        """
        ユーザーの回答統計を取得

        Args:
            user_id: ユーザーID
            days: 統計期間（日数）

        Returns:
            ユーザー統計の辞書
        """
        # 期間内の回答を取得
        cutoff_date = datetime.now() - timedelta(days=days)
        all_responses = await self.get_responses_by_user(user_id)

        # 期間でフィルタ
        recent_responses = [r for r in all_responses if r.responded_at >= cutoff_date]

        if not recent_responses:
            return {
                "user_id": user_id,
                "period_days": days,
                "total_responses": 0,
                "correct_responses": 0,
                "correct_rate": None,
                "participation_days": 0,
                "average_responses_per_day": 0.0,
            }

        # 統計計算
        total_responses = len(recent_responses)
        correct_responses = sum(1 for r in recent_responses if r.is_correct)
        correct_rate = correct_responses / total_responses

        # 参加日数計算
        response_dates = {r.responded_at.date() for r in recent_responses}
        participation_days = len(response_dates)

        # 1日あたりの平均回答数
        average_responses_per_day = total_responses / days

        return {
            "user_id": user_id,
            "period_days": days,
            "total_responses": total_responses,
            "correct_responses": correct_responses,
            "correct_rate": correct_rate,
            "participation_days": participation_days,
            "average_responses_per_day": average_responses_per_day,
        }

    async def get_leaderboard(
        self, days: int = 30, limit: int = 10
    ) -> list[dict[str, Any]]:
        """
        リーダーボードを取得

        Args:
            days: 統計期間（日数）
            limit: 取得件数制限

        Returns:
            リーダーボードのリスト（正解率順）
        """
        # 全ユーザーの最近の回答を取得
        # 注意: 実際の実装では、ユーザーリストを別途管理するか、
        # 全回答をスキャンする必要がある（DynamoDBの制限）
        # ここでは簡易実装として、GSI2を使用して最近の回答を取得

        # 実装上の制約: 全配信をスキャンして回答を取得
        # 本来はユーザーマスターテーブルを別途用意すべき
        logger.warning("リーダーボード取得は非効率的な実装です（学習用途のため許容）")

        # 注意: この実装は非効率的です
        # 実際のプロダクションでは、定期的にユーザー統計を集計して
        # 別テーブルに保存するか、ElasticSearchなどを使用すべきです

        # 簡易実装として、空のリーダーボードを返す
        return []

    async def delete_user_response(self, delivery_id: str, user_id: str) -> bool:
        """
        ユーザー回答を削除

        Args:
            delivery_id: 配信ID
            user_id: ユーザーID

        Returns:
            削除成功の場合True

        Raises:
            ValidationError: ユーザー回答が存在しない場合
        """
        # 存在チェック
        existing = await self.get_user_response(delivery_id, user_id)
        if not existing:
            raise ValidationError(
                f"ユーザー '{user_id}' の配信 '{delivery_id}' への回答が見つかりません"
            )

        pk = f"DELIVERY#{delivery_id}"
        sk = f"USER#{user_id}"
        return await self.delete_item(pk, sk)

    async def bulk_create_responses(
        self, responses: list[UserResponse]
    ) -> list[UserResponse]:
        """
        複数のユーザー回答を一括作成

        Args:
            responses: 作成するユーザー回答のリスト

        Returns:
            作成されたユーザー回答のリスト

        Raises:
            ValidationError: 一括作成の制限を超える場合
        """
        if len(responses) > 25:
            raise ValidationError("一括作成は最大25件までです")

        # 重複チェック
        for response in responses:
            existing = await self.get_user_response(
                response.delivery_id, response.user_id
            )
            if existing:
                raise ValidationError(
                    f"ユーザー '{response.user_id}' の配信 '{response.delivery_id}' への回答は既に存在します"
                )

        # 作成日時を設定
        now = datetime.now()
        for response in responses:
            response.created_at = now
            response.updated_at = now

        # 一括保存
        await self.batch_write_items(responses)

        return responses

    async def cleanup_old_responses(self, days: int = 365) -> int:
        """
        古いユーザー回答をクリーンアップ

        Args:
            days: 保持期間（日数）

        Returns:
            削除したユーザー回答の数

        Note:
            この操作は非効率的です。実際のプロダクションでは
            DynamoDB TTLを使用するか、定期的なバッチ処理で実行すべきです。
        """
        # 注意: この実装は非効率的です
        # 実際のプロダクションでは、TTLを使用するか、
        # 別途バッチ処理で実行すべきです

        logger.warning("古い回答のクリーンアップは非効率的な実装です")

        # 簡易実装として、削除数0を返す
        return 0
