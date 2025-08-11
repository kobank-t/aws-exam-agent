"""
問題データモデルの単体テスト

Questionモデルの機能とバリデーションをテスト
"""

from decimal import Decimal

import pytest

from app.models.question import AWSService, DifficultyLevel, Question


class TestQuestion:
    """Questionモデルのテストクラス"""

    def test_question_creation_valid(self) -> None:
        """有効なデータでの問題作成をテスト"""
        question = Question(
            question_id="q_test_001",
            question_text="これはテスト問題です。正しい答えはどれですか？",
            choices=["選択肢A", "選択肢B", "選択肢C", "選択肢D"],
            correct_answer="B",
            explanation="正解はBです。これはテスト用の詳細な説明文です。",
            service=AWSService.EC2,
            topic="テストトピック",
            difficulty=DifficultyLevel.ASSOCIATE,
            quality_score=Decimal("0.85"),
        )

        # 基本フィールドの確認
        assert question.question_id == "q_test_001"
        assert question.correct_answer == "B"
        assert question.service == AWSService.EC2
        assert question.difficulty == DifficultyLevel.ASSOCIATE
        assert question.quality_score == Decimal("0.85")

        # DynamoDBキーの自動生成確認
        assert question.pk == "QUESTION#q_test_001"
        assert question.sk == "METADATA"
        assert question.entity_type == "Question"
        assert question.gsi1_pk == "SERVICE#EC2"
        assert question.gsi2_pk == "DIFFICULTY#Associate"
        assert "QUALITY#0.850" in question.gsi2_sk

    def test_question_validation_correct_answer_invalid_choice(self) -> None:
        """正解が選択肢範囲外の場合のバリデーションエラーをテスト"""
        with pytest.raises(ValueError, match="正解 'E' が選択肢数 4 を超えています"):
            Question(
                question_id="q_test_002",
                question_text="これはテスト問題です。",
                choices=["選択肢A", "選択肢B", "選択肢C", "選択肢D"],
                correct_answer="E",  # 選択肢数を超えている
                explanation="これはテスト用の説明文です。",
                service=AWSService.EC2,
                topic="テスト",
                difficulty=DifficultyLevel.ASSOCIATE,
            )

    def test_question_validation_correct_answer_numeric(self) -> None:
        """数値形式の正解のバリデーションをテスト"""
        question = Question(
            question_id="q_test_003",
            question_text="これはテスト問題です。",
            choices=["選択肢A", "選択肢B", "選択肢C"],
            correct_answer="2",  # 数値形式
            explanation="これはテスト用の説明文です。",
            service=AWSService.S3,
            topic="テスト",
            difficulty=DifficultyLevel.PROFESSIONAL,
        )

        assert question.correct_answer == "2"

    def test_question_validation_correct_answer_numeric_invalid(self) -> None:
        """数値形式の正解が範囲外の場合のエラーをテスト"""
        with pytest.raises(
            ValueError, match="正解 '5' が選択肢範囲 1-3 を超えています"
        ):
            Question(
                question_id="q_test_004",
                question_text="これはテスト問題です。",
                choices=["選択肢A", "選択肢B", "選択肢C"],
                correct_answer="5",  # 範囲外
                explanation="これはテスト用の説明文です。",
                service=AWSService.S3,
                topic="テスト",
                difficulty=DifficultyLevel.PROFESSIONAL,
            )

    def test_question_validation_choices_too_few(self) -> None:
        """選択肢が少なすぎる場合のエラーをテスト"""
        with pytest.raises(ValueError, match="List should have at least 2 items"):
            Question(
                question_id="q_test_005",
                question_text="これはテスト問題です。",
                choices=["選択肢A"],  # 1つだけ
                correct_answer="A",
                explanation="これはテスト用の説明文です。",
                service=AWSService.EC2,
                topic="テスト",
                difficulty=DifficultyLevel.ASSOCIATE,
            )

    def test_question_validation_choices_too_many(self) -> None:
        """選択肢が多すぎる場合のエラーをテスト"""
        with pytest.raises(ValueError, match="List should have at most 6 items"):
            Question(
                question_id="q_test_006",
                question_text="これはテスト問題です。",
                choices=["A", "B", "C", "D", "E", "F", "G"],  # 7つ
                correct_answer="A",
                explanation="これはテスト用の説明文です。",
                service=AWSService.EC2,
                topic="テスト",
                difficulty=DifficultyLevel.ASSOCIATE,
            )

    def test_question_validation_empty_choice(self) -> None:
        """空の選択肢がある場合のエラーをテスト"""
        with pytest.raises(ValueError, match="選択肢 2 が空です"):
            Question(
                question_id="q_test_007",
                question_text="これはテスト問題です。",
                choices=["選択肢A", "", "選択肢C"],  # 2番目が空
                correct_answer="A",
                explanation="これはテスト用の説明文です。",
                service=AWSService.EC2,
                topic="テスト",
                difficulty=DifficultyLevel.ASSOCIATE,
            )

    def test_get_choice_by_answer(self) -> None:
        """正解に対応する選択肢テキストの取得をテスト"""
        question = Question(
            question_id="q_test_008",
            question_text="これはテスト問題です。",
            choices=["選択肢A", "選択肢B", "選択肢C", "選択肢D"],
            correct_answer="C",
            explanation="これはテスト用の説明文です。",
            service=AWSService.EC2,
            topic="テスト",
            difficulty=DifficultyLevel.ASSOCIATE,
        )

        assert question.get_choice_by_answer() == "選択肢C"

    def test_get_choice_by_answer_numeric(self) -> None:
        """数値形式の正解での選択肢テキスト取得をテスト"""
        question = Question(
            question_id="q_test_009",
            question_text="これはテスト問題です。",
            choices=["選択肢A", "選択肢B", "選択肢C"],
            correct_answer="2",
            explanation="これはテスト用の説明文です。",
            service=AWSService.EC2,
            topic="テスト",
            difficulty=DifficultyLevel.ASSOCIATE,
        )

        assert question.get_choice_by_answer() == "選択肢B"

    def test_is_high_quality(self) -> None:
        """高品質問題の判定をテスト"""
        high_quality = Question(
            question_id="q_test_010",
            question_text="これはテスト問題です。",
            choices=["A", "B", "C", "D"],
            correct_answer="A",
            explanation="これはテスト用の説明文です。",
            service=AWSService.EC2,
            topic="テスト",
            difficulty=DifficultyLevel.ASSOCIATE,
            quality_score=Decimal("0.9"),
        )

        low_quality = Question(
            question_id="q_test_011",
            question_text="これはテスト問題です。",
            choices=["A", "B", "C", "D"],
            correct_answer="A",
            explanation="これはテスト用の説明文です。",
            service=AWSService.EC2,
            topic="テスト",
            difficulty=DifficultyLevel.ASSOCIATE,
            quality_score=Decimal("0.7"),
        )

        assert high_quality.is_high_quality() is True
        assert low_quality.is_high_quality() is False
        assert low_quality.is_high_quality(threshold=Decimal("0.6")) is True

    def test_update_quality_score(self) -> None:
        """品質スコア更新をテスト"""
        question = Question(
            question_id="q_test_012",
            question_text="これはテスト問題です。",
            choices=["A", "B", "C", "D"],
            correct_answer="A",
            explanation="これはテスト用の説明文です。",
            service=AWSService.EC2,
            topic="テスト",
            difficulty=DifficultyLevel.ASSOCIATE,
            quality_score=Decimal("0.5"),
        )

        original_updated_at = question.updated_at
        original_gsi2_sk = question.gsi2_sk

        # 品質スコアを更新
        import time

        time.sleep(0.01)
        question.update_quality_score(Decimal("0.9"))

        assert question.quality_score == Decimal("0.9")
        assert question.updated_at > original_updated_at
        assert question.gsi2_sk != original_gsi2_sk
        assert "QUALITY#0.900" in question.gsi2_sk

    def test_update_quality_score_invalid(self) -> None:
        """無効な品質スコア更新のエラーをテスト"""
        question = Question(
            question_id="q_test_013",
            question_text="これはテスト問題です。",
            choices=["A", "B", "C", "D"],
            correct_answer="A",
            explanation="これはテスト用の説明文です。",
            service=AWSService.EC2,
            topic="テスト",
            difficulty=DifficultyLevel.ASSOCIATE,
        )

        with pytest.raises(
            ValueError, match="品質スコアは0.0-1.0の範囲で指定してください"
        ):
            question.update_quality_score(Decimal("1.5"))

        with pytest.raises(
            ValueError, match="品質スコアは0.0-1.0の範囲で指定してください"
        ):
            question.update_quality_score(Decimal("-0.1"))

    def test_alias_functionality(self) -> None:
        """Pydantic aliasの動作をテスト"""
        question = Question(
            question_id="q_test_014",
            question_text="これはテスト問題です。",
            choices=["A", "B", "C", "D"],
            correct_answer="A",
            explanation="これはテスト用の説明文です。",
            service=AWSService.EC2,
            topic="テスト",
            difficulty=DifficultyLevel.ASSOCIATE,
        )

        # Python変数名でアクセス
        assert question.pk.startswith("QUESTION#")
        assert question.sk == "METADATA"
        assert question.entity_type == "Question"

        # DynamoDB形式での出力
        dynamodb_data = question.model_dump(by_alias=True, exclude_none=True)
        assert "PK" in dynamodb_data
        assert "SK" in dynamodb_data
        assert "EntityType" in dynamodb_data

        # DynamoDBデータからの復元
        restored = Question.model_validate(dynamodb_data)
        assert restored.question_id == question.question_id
        assert restored.pk == question.pk
