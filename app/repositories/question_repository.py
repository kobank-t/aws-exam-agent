"""
問題リポジトリ

Question エンティティのDynamoDB操作を提供
"""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Any

from app.models.question import AWSService, DifficultyLevel, Question
from app.shared.exceptions import ValidationError

from .base import BaseRepository

logger = logging.getLogger(__name__)


class QuestionRepository(BaseRepository[Question]):
    """問題データのリポジトリクラス"""

    def _to_model(self, item: dict[str, Any]) -> Question:
        """DynamoDBアイテムをQuestionモデルに変換"""
        return Question.from_dynamodb_item(item)

    def _from_model(self, model: Question) -> dict[str, Any]:
        """QuestionモデルをDynamoDBアイテムに変換"""
        return model.to_dynamodb_item()

    async def get_by_question_id(self, question_id: str) -> Question | None:
        """
        問題IDで問題を取得

        Args:
            question_id: 問題ID（例: q_20250729_001）

        Returns:
            問題オブジェクト（見つからない場合はNone）
        """
        pk = f"QUESTION#{question_id}"
        sk = "METADATA"
        return await self.get_by_key(pk, sk)

    async def create_question(self, question: Question) -> Question:
        """
        新しい問題を作成

        Args:
            question: 作成する問題オブジェクト

        Returns:
            作成された問題オブジェクト

        Raises:
            ValidationError: 同じIDの問題が既に存在する場合
        """
        # 既存チェック
        existing = await self.get_by_question_id(question.question_id)
        if existing:
            raise ValidationError(f"問題ID '{question.question_id}' は既に存在します")

        # 作成日時を設定
        question.created_at = datetime.now()
        question.updated_at = datetime.now()

        return await self.put_item(question)

    async def update_question(self, question: Question) -> Question:
        """
        問題を更新

        Args:
            question: 更新する問題オブジェクト

        Returns:
            更新された問題オブジェクト

        Raises:
            ValidationError: 問題が存在しない場合
        """
        # 存在チェック
        existing = await self.get_by_question_id(question.question_id)
        if not existing:
            raise ValidationError(f"問題ID '{question.question_id}' が見つかりません")

        # 更新日時を設定
        question.updated_at = datetime.now()

        return await self.put_item(question)

    async def delete_question(self, question_id: str) -> bool:
        """
        問題を削除

        Args:
            question_id: 削除する問題ID

        Returns:
            削除成功の場合True

        Raises:
            ValidationError: 問題が存在しない場合
        """
        # 存在チェック
        existing = await self.get_by_question_id(question_id)
        if not existing:
            raise ValidationError(f"問題ID '{question_id}' が見つかりません")

        pk = f"QUESTION#{question_id}"
        sk = "METADATA"
        return await self.delete_item(pk, sk)

    async def get_questions_by_service(
        self, service: AWSService, limit: int | None = None
    ) -> list[Question]:
        """
        AWSサービス別に問題を取得

        Args:
            service: AWSサービス
            limit: 取得件数制限

        Returns:
            問題のリスト（作成日時の降順）
        """
        gsi_pk = f"SERVICE#{service.value}"
        return await self.query_by_gsi(
            index_name="GSI1",
            gsi_pk=gsi_pk,
            limit=limit,
            scan_index_forward=False,  # 新しい順
        )

    async def get_questions_by_difficulty(
        self, difficulty: DifficultyLevel, limit: int | None = None
    ) -> list[Question]:
        """
        難易度別に問題を取得

        Args:
            difficulty: 難易度
            limit: 取得件数制限

        Returns:
            問題のリスト（品質スコアの降順）
        """
        gsi_pk = f"DIFFICULTY#{difficulty.value}"
        return await self.query_by_gsi(
            index_name="GSI2",
            gsi_pk=gsi_pk,
            limit=limit,
            scan_index_forward=False,  # 高品質順
        )

    async def get_high_quality_questions(
        self, quality_threshold: Decimal = Decimal("0.8"), limit: int | None = None
    ) -> list[Question]:
        """
        高品質問題を取得

        Args:
            quality_threshold: 品質スコア閾値
            limit: 取得件数制限

        Returns:
            高品質問題のリスト
        """
        # 全難易度から高品質問題を取得
        all_questions = []

        for difficulty in DifficultyLevel:
            questions = await self.get_questions_by_difficulty(difficulty, limit)
            # 品質スコア閾値でフィルタ
            high_quality = [
                q for q in questions if q.quality_score >= quality_threshold
            ]
            all_questions.extend(high_quality)

        # 品質スコア降順でソート
        all_questions.sort(key=lambda q: q.quality_score, reverse=True)

        return all_questions[:limit] if limit else all_questions

    async def get_questions_by_service_and_topic(
        self, service: AWSService, topic: str, limit: int | None = None
    ) -> list[Question]:
        """
        サービスとトピックで問題を取得（類似度チェック用）

        Args:
            service: AWSサービス
            topic: トピック
            limit: 取得件数制限

        Returns:
            問題のリスト
        """
        # サービス別に取得してからトピックでフィルタ
        questions = await self.get_questions_by_service(service, limit)

        # トピックが一致する問題をフィルタ
        filtered_questions = [q for q in questions if q.topic.lower() == topic.lower()]

        return filtered_questions

    async def update_quality_score(
        self, question_id: str, quality_score: Decimal
    ) -> bool:
        """
        問題の品質スコアを更新

        Args:
            question_id: 問題ID
            quality_score: 新しい品質スコア

        Returns:
            更新成功の場合True

        Raises:
            ValidationError: 品質スコアが範囲外の場合
        """
        if not Decimal("0.0") <= quality_score <= Decimal("1.0"):
            raise ValidationError("品質スコアは0.0-1.0の範囲で指定してください")

        pk = f"QUESTION#{question_id}"
        sk = "METADATA"

        # GSI2SKも更新する必要がある
        gsi2_sk = f"QUALITY#{quality_score:.3f}"

        return await self.update_item(
            pk=pk,
            sk=sk,
            update_expression="SET quality_score = :score, updated_at = :updated_at, GSI2SK = :gsi2_sk",
            expression_attribute_values={
                ":score": quality_score,
                ":updated_at": datetime.now().isoformat(),
                ":gsi2_sk": gsi2_sk,
            },
        )

    async def get_recent_questions(
        self, days: int = 7, limit: int | None = None
    ) -> list[Question]:
        """
        最近作成された問題を取得

        Args:
            days: 過去何日間の問題を取得するか
            limit: 取得件数制限

        Returns:
            最近の問題のリスト
        """
        # 指定日数前の日時を計算
        from datetime import timedelta

        cutoff_date = datetime.now() - timedelta(days=days)

        # 全サービスから最近の問題を取得
        all_questions = []

        for service in AWSService:
            gsi_pk = f"SERVICE#{service.value}"
            questions = await self.query_by_gsi(
                index_name="GSI1",
                gsi_pk=gsi_pk,
                gsi_sk_condition="GSI1SK >= :cutoff_date",
                expression_attribute_values={":cutoff_date": cutoff_date.isoformat()},
                limit=limit,
                scan_index_forward=False,  # 新しい順
            )

            # 追加のフィルタリング（DynamoDBクエリで完全にフィルタできない場合）
            recent_questions = [q for q in questions if q.created_at >= cutoff_date]
            all_questions.extend(recent_questions)

        # 作成日時降順でソート
        all_questions.sort(key=lambda q: q.created_at, reverse=True)

        return all_questions[:limit] if limit else all_questions

    async def get_questions_count_by_service(self) -> dict[str, int]:
        """
        サービス別の問題数を取得

        Returns:
            サービス名をキー、問題数を値とする辞書
        """
        service_counts = {}

        for service in AWSService:
            questions = await self.get_questions_by_service(service)
            service_counts[service.value] = len(questions)

        return service_counts

    async def search_questions_by_keyword(
        self, keyword: str, limit: int | None = None
    ) -> list[Question]:
        """
        キーワードで問題を検索（簡易実装）

        Args:
            keyword: 検索キーワード
            limit: 取得件数制限

        Returns:
            キーワードにマッチする問題のリスト

        Note:
            DynamoDBはフルテキスト検索をサポートしていないため、
            全問題を取得してからフィルタリングする簡易実装
        """
        # 全サービスから問題を取得
        all_questions = []

        for service in AWSService:
            questions = await self.get_questions_by_service(service)
            all_questions.extend(questions)

        # キーワードでフィルタリング
        keyword_lower = keyword.lower()
        matching_questions = []

        for question in all_questions:
            # 問題文、選択肢、解説からキーワードを検索
            text_to_search = [
                question.question_text.lower(),
                question.explanation.lower(),
                question.topic.lower(),
            ]
            text_to_search.extend([choice.lower() for choice in question.choices])

            if any(keyword_lower in text for text in text_to_search):
                matching_questions.append(question)

        # 品質スコア降順でソート
        matching_questions.sort(key=lambda q: q.quality_score, reverse=True)

        return matching_questions[:limit] if limit else matching_questions
