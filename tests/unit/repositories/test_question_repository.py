"""
問題リポジトリの単体テスト

外部依存のない純粋なロジックのテスト
"""

from datetime import UTC, datetime
from decimal import Decimal

from app.models.question import AWSService, DifficultyLevel, Question
from app.repositories.question_repository import QuestionRepository


class TestQuestionRepository:
    """問題リポジトリの純粋ロジックテスト"""

    def test_to_model_conversion(self) -> None:
        """DynamoDBアイテム → Questionモデル変換ロジック"""
        repository = QuestionRepository("dummy-table")

        item = {
            "PK": "QUESTION#q001",
            "SK": "METADATA",
            "question_id": "q001",
            "question_text": "これは10文字以上の有効な問題文です",
            "choices": ["A: 選択肢A", "B: 選択肢B", "C: 選択肢C", "D: 選択肢D"],
            "correct_answer": "A",
            "explanation": "これは10文字以上の有効な解説文です",
            "service": "EC2",
            "topic": "テストトピック",
            "difficulty": "Associate",
            "quality_score": "0.85",
            "created_at": "2025-08-11T15:30:00+00:00",
            "updated_at": "2025-08-11T15:30:00+00:00",
            "GSI1PK": "SERVICE#EC2",
            "GSI1SK": "DIFFICULTY#Associate",
        }

        result = repository._to_model(item)

        assert isinstance(result, Question)
        assert result.question_id == "q001"
        assert result.question_text == "これは10文字以上の有効な問題文です"
        assert result.choices == [
            "A: 選択肢A",
            "B: 選択肢B",
            "C: 選択肢C",
            "D: 選択肢D",
        ]
        assert result.correct_answer == "A"
        assert result.explanation == "これは10文字以上の有効な解説文です"
        assert result.service == AWSService.EC2
        assert result.topic == "テストトピック"
        assert result.difficulty == DifficultyLevel.ASSOCIATE
        assert result.quality_score == Decimal("0.85")

    def test_from_model_conversion(self) -> None:
        """Questionモデル → DynamoDBアイテム変換ロジック"""
        repository = QuestionRepository("dummy-table")

        question = Question(
            question_id="q001",
            question_text="これは10文字以上の有効な問題文です",
            choices=["A: 選択肢A", "B: 選択肢B", "C: 選択肢C", "D: 選択肢D"],
            correct_answer="A",
            explanation="これは10文字以上の有効な解説文です",
            service=AWSService.EC2,
            topic="テストトピック",
            difficulty=DifficultyLevel.ASSOCIATE,
            quality_score=Decimal("0.85"),
            created_at=datetime(2025, 8, 11, 15, 30, 0, tzinfo=UTC),
            updated_at=datetime(2025, 8, 11, 15, 30, 0, tzinfo=UTC),
        )

        result = repository._from_model(question)

        assert result["PK"] == "QUESTION#q001"
        assert result["SK"] == "METADATA"
        assert result["question_id"] == "q001"
        assert result["question_text"] == "これは10文字以上の有効な問題文です"
        assert result["choices"] == [
            "A: 選択肢A",
            "B: 選択肢B",
            "C: 選択肢C",
            "D: 選択肢D",
        ]
        assert result["correct_answer"] == "A"
        assert result["explanation"] == "これは10文字以上の有効な解説文です"
        assert result["service"] == "EC2"
        assert result["topic"] == "テストトピック"
        assert result["difficulty"] == "Associate"
        assert result["quality_score"] == Decimal("0.85")
        assert result["GSI1PK"] == "SERVICE#EC2"
        assert result["GSI1SK"] == "CREATED#2025-08-11T15:30:00+00:00"

    def test_service_enum_conversion(self) -> None:
        """AWSService列挙型変換テスト"""
        repository = QuestionRepository("dummy-table")

        test_cases = [
            ("EC2", AWSService.EC2),
            ("S3", AWSService.S3),
            ("RDS", AWSService.RDS),
            ("Lambda", AWSService.LAMBDA),
        ]

        for service_str, expected_enum in test_cases:
            item = {
                "PK": "QUESTION#q001",
                "SK": "METADATA",
                "question_id": "q001",
                "question_text": "これは10文字以上の有効な問題文です",
                "choices": ["A: 選択肢A", "B: 選択肢B", "C: 選択肢C", "D: 選択肢D"],
                "correct_answer": "A",
                "explanation": "これは10文字以上の有効な解説文です",
                "service": service_str,
                "topic": "テストトピック",
                "difficulty": "Associate",
                "quality_score": "0.85",
                "created_at": "2025-08-11T15:30:00+00:00",
                "updated_at": "2025-08-11T15:30:00+00:00",
                "GSI1PK": f"SERVICE#{service_str}",
                "GSI1SK": "DIFFICULTY#Associate",
            }

            result = repository._to_model(item)
            assert result.service == expected_enum

    def test_difficulty_enum_conversion(self) -> None:
        """DifficultyLevel列挙型変換テスト"""
        repository = QuestionRepository("dummy-table")

        test_cases = [
            ("Practitioner", DifficultyLevel.PRACTITIONER),
            ("Associate", DifficultyLevel.ASSOCIATE),
            ("Professional", DifficultyLevel.PROFESSIONAL),
            ("Specialty", DifficultyLevel.SPECIALTY),
        ]

        for difficulty_str, expected_enum in test_cases:
            item = {
                "PK": "QUESTION#q001",
                "SK": "METADATA",
                "question_id": "q001",
                "question_text": "これは10文字以上の有効な問題文です",
                "choices": ["A: 選択肢A", "B: 選択肢B", "C: 選択肢C", "D: 選択肢D"],
                "correct_answer": "A",
                "explanation": "これは10文字以上の有効な解説文です",
                "service": "EC2",
                "topic": "テストトピック",
                "difficulty": difficulty_str,
                "quality_score": "0.85",
                "created_at": "2025-08-11T15:30:00+00:00",
                "updated_at": "2025-08-11T15:30:00+00:00",
                "GSI1PK": "SERVICE#EC2",
                "GSI1SK": f"DIFFICULTY#{difficulty_str}",
            }

            result = repository._to_model(item)
            assert result.difficulty == expected_enum

    def test_decimal_conversion(self) -> None:
        """Decimal型変換テスト"""
        repository = QuestionRepository("dummy-table")

        test_cases = [
            "0.0",
            "0.5",
            "0.85",
            "1.0",
            "0.123456789",  # 高精度
        ]

        for quality_score_str in test_cases:
            item = {
                "PK": "QUESTION#q001",
                "SK": "METADATA",
                "question_id": "q001",
                "question_text": "これは10文字以上の有効な問題文です",
                "choices": ["A: 選択肢A", "B: 選択肢B", "C: 選択肢C", "D: 選択肢D"],
                "correct_answer": "A",
                "explanation": "これは10文字以上の有効な解説文です",
                "service": "EC2",
                "topic": "テストトピック",
                "difficulty": "Associate",
                "quality_score": quality_score_str,
                "created_at": "2025-08-11T15:30:00+00:00",
                "updated_at": "2025-08-11T15:30:00+00:00",
                "GSI1PK": "SERVICE#EC2",
                "GSI1SK": "DIFFICULTY#Associate",
            }

            result = repository._to_model(item)
            assert result.quality_score == Decimal(quality_score_str)
            assert isinstance(result.quality_score, Decimal)
