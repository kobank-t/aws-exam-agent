"""
基底リポジトリクラスの単体テスト
"""

from collections.abc import Generator
from decimal import Decimal
from typing import Any
from unittest.mock import patch

import pytest
from moto import mock_aws

from app.models.question import AWSService, DifficultyLevel, Question
from app.repositories.base import BaseRepository
from app.shared.exceptions import ItemNotFoundError, ValidationError


class MockRepository(BaseRepository[Question]):
    """テスト用リポジトリクラス"""

    def _to_model(self, item: dict[str, Any]) -> Question:
        return Question.from_dynamodb_item(item)

    def _from_model(self, model: Question) -> dict[str, Any]:
        return model.to_dynamodb_item()


@pytest.fixture
def test_repository() -> Generator[MockRepository, None, None]:
    with mock_aws():
        # テーブル作成
        import boto3

        dynamodb = boto3.resource("dynamodb", region_name="ap-northeast-1")

        table = dynamodb.create_table(
            TableName="test-table",
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

        # テーブルがアクティブになるまで待機
        table.wait_until_exists()

        yield MockRepository("test-table")


@pytest.fixture
def sample_question() -> Question:
    return Question(
        question_id="q_test_001",
        question_text="これはテスト用の問題文です。最低10文字以上必要です。",
        choices=["選択肢A", "選択肢B", "選択肢C", "選択肢D"],
        correct_answer="A",
        explanation="正解はAです。この解説は最低10文字以上必要です。",
        service=AWSService.EC2,
        topic="テストトピック",
        difficulty=DifficultyLevel.ASSOCIATE,
        quality_score=Decimal("0.8"),
    )


class TestBaseRepository:
    """基底リポジトリクラスのテスト"""

    @pytest.mark.asyncio
    async def test_put_item_and_get_by_key(
        self, test_repository: MockRepository, sample_question: Question
    ) -> None:
        """アイテムの保存と取得のテスト"""
        # 保存
        saved_question = await test_repository.put_item(sample_question)
        assert saved_question.question_id == sample_question.question_id

        # 取得
        pk = f"QUESTION#{sample_question.question_id}"
        sk = "METADATA"
        retrieved_question = await test_repository.get_by_key(pk, sk)

        assert retrieved_question is not None
        assert retrieved_question.question_id == sample_question.question_id
        assert retrieved_question.question_text == sample_question.question_text

    @pytest.mark.asyncio
    async def test_get_by_key_not_found(self, test_repository: MockRepository) -> None:
        """存在しないアイテムの取得テスト"""
        result = await test_repository.get_by_key("NONEXISTENT", "METADATA")
        assert result is None

    @pytest.mark.asyncio
    async def test_update_item(
        self, test_repository: MockRepository, sample_question: Question
    ) -> None:
        """アイテム更新のテスト"""
        # まず保存
        await test_repository.put_item(sample_question)

        # 更新
        pk = f"QUESTION#{sample_question.question_id}"
        sk = "METADATA"

        success = await test_repository.update_item(
            pk=pk,
            sk=sk,
            update_expression="SET quality_score = :score",
            expression_attribute_values={":score": Decimal("0.9")},
        )

        assert success is True

        # 更新確認
        updated_question = await test_repository.get_by_key(pk, sk)
        assert updated_question is not None
        assert updated_question.quality_score == Decimal("0.9")

    @pytest.mark.asyncio
    async def test_delete_item(
        self, test_repository: MockRepository, sample_question: Question
    ) -> None:
        """アイテム削除のテスト"""
        # まず保存
        await test_repository.put_item(sample_question)

        pk = f"QUESTION#{sample_question.question_id}"
        sk = "METADATA"

        # 削除前の確認
        question_before = await test_repository.get_by_key(pk, sk)
        assert question_before is not None

        # 削除
        success = await test_repository.delete_item(pk, sk)
        assert success is True

        # 削除後の確認
        question_after = await test_repository.get_by_key(pk, sk)
        assert question_after is None

    @pytest.mark.asyncio
    async def test_query_by_pk(
        self, test_repository: MockRepository, sample_question: Question
    ) -> None:
        """パーティションキーでのクエリテスト"""
        # 複数のアイテムを保存
        questions = []
        for i in range(3):
            question = Question(
                question_id=f"q_test_{i:03d}",
                question_text=f"これはテスト問題{i}の詳細な説明文です",
                choices=["A", "B", "C", "D"],
                correct_answer="A",
                explanation="これは詳細な説明文です",
                service=AWSService.EC2,
                topic="テスト",
                difficulty=DifficultyLevel.ASSOCIATE,
            )
            questions.append(question)
            await test_repository.put_item(question)

        # 特定のパーティションキーでクエリ
        pk = f"QUESTION#{questions[0].question_id}"
        results = await test_repository.query_by_pk(pk)

        assert len(results) == 1
        assert results[0].question_id == questions[0].question_id

    @pytest.mark.asyncio
    async def test_query_by_gsi(
        self, test_repository: MockRepository, sample_question: Question
    ) -> None:
        """GSIでのクエリテスト"""
        # 保存
        await test_repository.put_item(sample_question)

        # GSI1でクエリ
        gsi_pk = f"SERVICE#{sample_question.service.value}"
        results = await test_repository.query_by_gsi("GSI1", gsi_pk)

        assert len(results) >= 1
        assert any(r.question_id == sample_question.question_id for r in results)

    @pytest.mark.asyncio
    async def test_batch_get_items(
        self, test_repository: MockRepository, sample_question: Question
    ) -> None:
        """一括取得のテスト"""
        # 複数のアイテムを保存
        questions = []
        keys = []

        for i in range(3):
            question = Question(
                question_id=f"q_batch_{i:03d}",
                question_text=f"これはバッチテスト問題{i}の詳細な説明文です",
                choices=["A", "B", "C", "D"],
                correct_answer="A",
                explanation="これは詳細な説明文です",
                service=AWSService.EC2,
                topic="バッチテスト",
                difficulty=DifficultyLevel.ASSOCIATE,
            )
            questions.append(question)
            await test_repository.put_item(question)

            keys.append({"PK": f"QUESTION#{question.question_id}", "SK": "METADATA"})

        # 一括取得
        results = await test_repository.batch_get_items(keys)

        assert len(results) == 3
        result_ids = {r.question_id for r in results}
        expected_ids = {q.question_id for q in questions}
        assert result_ids == expected_ids

    @pytest.mark.asyncio
    async def test_batch_write_items(self, test_repository: MockRepository) -> None:
        """一括保存のテスト"""
        # 複数のアイテムを準備
        questions = []
        for i in range(3):
            question = Question(
                question_id=f"q_batch_write_{i:03d}",
                question_text=f"これは一括保存テスト問題{i}の詳細な説明文です",
                choices=["A", "B", "C", "D"],
                correct_answer="A",
                explanation="これは詳細な説明文です",
                service=AWSService.EC2,
                topic="一括保存テスト",
                difficulty=DifficultyLevel.ASSOCIATE,
            )
            questions.append(question)

        # 一括保存
        success = await test_repository.batch_write_items(questions)
        assert success is True

        # 保存確認
        for question in questions:
            pk = f"QUESTION#{question.question_id}"
            sk = "METADATA"
            retrieved = await test_repository.get_by_key(pk, sk)
            assert retrieved is not None
            assert retrieved.question_id == question.question_id

    @pytest.mark.asyncio
    async def test_batch_operations_validation(
        self, test_repository: MockRepository
    ) -> None:
        """一括操作のバリデーションテスト"""
        # 空のリストでの一括取得
        results = await test_repository.batch_get_items([])
        assert results == []

        # 空のリストでの一括保存
        success = await test_repository.batch_write_items([])
        assert success is True

        # 制限を超える一括取得
        large_keys = [{"PK": f"KEY_{i}", "SK": "METADATA"} for i in range(101)]
        with pytest.raises(ValidationError, match="一括取得は最大100件まで"):
            await test_repository.batch_get_items(large_keys)

        # 制限を超える一括保存
        large_questions = []
        for i in range(26):
            question = Question(
                question_id=f"q_large_{i:03d}",
                question_text="これは大量テスト用の問題文です",
                choices=["A", "B"],
                correct_answer="A",
                explanation="これは詳細な説明文です",
                service=AWSService.EC2,
                topic="大量テスト",
                difficulty=DifficultyLevel.ASSOCIATE,
            )
            large_questions.append(question)

        with pytest.raises(ValidationError, match="一括保存は最大25件まで"):
            await test_repository.batch_write_items(large_questions)

    def test_get_table_info(self, test_repository: MockRepository) -> None:
        """テーブル情報取得のテスト"""
        table_info = test_repository.get_table_info()

        assert "table_name" in table_info
        assert table_info["table_name"] == "test-table"
        assert "table_status" in table_info

    @pytest.mark.asyncio
    async def test_error_handling(
        self, test_repository: MockRepository, sample_question: Question
    ) -> None:
        """エラーハンドリングのテスト"""
        # 存在しないテーブルでの操作をシミュレート
        with patch.object(test_repository.table, "get_item") as mock_get:
            from botocore.exceptions import ClientError

            mock_get.side_effect = ClientError(
                {
                    "Error": {
                        "Code": "ResourceNotFoundException",
                        "Message": "Table not found",
                    }
                },
                "GetItem",
            )

            with pytest.raises(ItemNotFoundError):
                await test_repository.get_by_key("TEST", "METADATA")

        # バリデーションエラーのシミュレート
        with patch.object(test_repository.table, "put_item") as mock_put:
            mock_put.side_effect = ClientError(
                {"Error": {"Code": "ValidationException", "Message": "Invalid input"}},
                "PutItem",
            )

            with pytest.raises(ValidationError):
                await test_repository.put_item(sample_question)

    @pytest.mark.asyncio
    async def test_query_with_conditions(self, test_repository: MockRepository) -> None:
        """条件付きクエリのテスト"""
        # テストデータを準備
        questions = []
        for i in range(5):
            question = Question(
                question_id=f"q_condition_{i:03d}",
                question_text=f"これは条件テスト問題{i}の詳細な説明文です",
                choices=["A", "B", "C", "D"],
                correct_answer="A",
                explanation="これは詳細な説明文です",
                service=AWSService.EC2,
                topic="条件テスト",
                difficulty=DifficultyLevel.ASSOCIATE,
                quality_score=Decimal(str(0.5 + (i * 0.1))),  # 0.5, 0.6, 0.7, 0.8, 0.9
            )
            questions.append(question)
            await test_repository.put_item(question)

        # 制限付きクエリ
        gsi_pk = f"SERVICE#{AWSService.EC2.value}"
        limited_results = await test_repository.query_by_gsi("GSI1", gsi_pk, limit=3)

        assert len(limited_results) <= 3

        # 降順クエリ
        desc_results = await test_repository.query_by_gsi(
            "GSI1", gsi_pk, scan_index_forward=False
        )

        # 結果が降順になっていることを確認（作成日時順）
        if len(desc_results) > 1:
            for i in range(len(desc_results) - 1):
                assert desc_results[i].created_at >= desc_results[i + 1].created_at
