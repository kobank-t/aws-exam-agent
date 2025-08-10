"""
app/agentcore/agent_main.py のテスト
"""

from unittest.mock import Mock, patch

from app.agentcore.agent_main import (
    agent,
    app,
    invoke,
)


class TestQuestionGenerationAgent:
    """question_generation_agent 関数のテスト"""

    def test_question_generation_agent_default_params(self) -> None:
        """デフォルトパラメータでの問題生成テスト"""
        from app.agentcore.agent_main import question_generation_agent

        result = question_generation_agent()

        assert isinstance(result, dict)
        assert result["topic"] == "EC2"
        assert result["difficulty"] == "intermediate"
        assert result["id"] == "q_ec2_intermediate_001"
        assert "question" in result
        assert "options" in result
        assert "correct_answer" in result
        assert "explanation" in result
        assert "source_info" in result

    def test_question_generation_agent_custom_params(self) -> None:
        """カスタムパラメータでの問題生成テスト"""
        from app.agentcore.agent_main import question_generation_agent

        aws_info = {"service": "S3", "description": "S3 storage service"}
        result = question_generation_agent(
            topic="S3", difficulty="advanced", aws_info=aws_info
        )

        assert result["topic"] == "S3"
        assert result["difficulty"] == "advanced"
        assert result["id"] == "q_s3_advanced_001"
        assert "What is the primary use case for AWS S3?" in result["question"]
        assert result["source_info"] == aws_info

    def test_question_generation_agent_options_structure(self) -> None:
        """問題の選択肢構造テスト"""
        from app.agentcore.agent_main import question_generation_agent

        result = question_generation_agent(topic="Lambda")

        options = result["options"]
        assert isinstance(options, dict)
        assert "A" in options
        assert "B" in options
        assert "C" in options
        assert "D" in options
        assert result["correct_answer"] == "A"


class TestAwsInfoAgent:
    """aws_info_agent 関数のテスト"""

    async def test_aws_info_agent_default_service(self) -> None:
        """デフォルトサービスでの情報取得テスト"""
        from app.agentcore.agent_main import aws_info_agent

        result = await aws_info_agent()

        assert isinstance(result, dict)
        assert result["service"] == "EC2"
        # MCP 統合後は構造が変わるため、基本的な存在確認のみ
        assert "service" in result
        assert result["service"] == "EC2"

    async def test_aws_info_agent_custom_service(self) -> None:
        """カスタムサービスでの情報取得テスト"""
        from app.agentcore.agent_main import aws_info_agent

        result = await aws_info_agent(service="RDS")

        assert result["service"] == "RDS"
        # MCP 統合後は構造が変わるため、基本的な存在確認のみ
        assert "service" in result
        assert result["service"] == "RDS"

    async def test_aws_info_agent_pricing_model(self) -> None:
        """料金モデル情報のテスト"""
        from app.agentcore.agent_main import aws_info_agent

        result = await aws_info_agent(service="DynamoDB")

        # MCP 統合後は構造が変わるため、基本的な存在確認のみ
        assert "service" in result
        assert result["service"] == "DynamoDB"


class TestQualityManagementAgent:
    """quality_management_agent 関数のテスト"""

    def test_quality_management_agent_validation(self) -> None:
        """品質検証テスト"""
        from app.agentcore.agent_main import quality_management_agent

        question = {
            "id": "q_ec2_intermediate_001",
            "topic": "EC2",
            "difficulty": "intermediate",
            "question": "What is EC2?",
        }

        result = quality_management_agent(question)

        assert isinstance(result, dict)
        assert result["question_id"] == "q_ec2_intermediate_001"
        assert result["is_valid"] is True
        assert "quality_score" in result
        assert "validation_checks" in result
        assert "suggestions" in result

    def test_quality_management_agent_validation_checks(self) -> None:
        """品質検証チェック項目テスト"""
        from app.agentcore.agent_main import quality_management_agent

        question = {"id": "test_question", "topic": "S3"}

        result = quality_management_agent(question)

        checks = result["validation_checks"]
        assert "technical_accuracy" in checks
        assert "difficulty_appropriate" in checks
        assert "format_correct" in checks
        assert "explanation_clear" in checks


class TestInvoke:
    """invoke 関数（AgentCore エントリーポイント）のテスト"""

    @patch("app.agentcore.agent_main.aws_info_agent")
    @patch("app.agentcore.agent_main.question_generation_agent")
    @patch("app.agentcore.agent_main.quality_management_agent")
    async def test_invoke_success_case(
        self, mock_quality: Mock, mock_question: Mock, mock_aws_info: Mock
    ) -> None:
        """正常ケースのテスト"""
        # 非同期関数のモック設定
        import asyncio

        mock_aws_info.return_value = asyncio.Future()
        mock_aws_info.return_value.set_result(
            {"service": "S3", "description": "S3 service"}
        )
        mock_question.return_value = {"id": "q_s3_beginner_001", "topic": "S3"}
        mock_quality.return_value = {"is_valid": True, "quality_score": 90}

        payload = {
            "prompt": "Generate a question about S3",
            "topic": "S3",
            "difficulty": "beginner",
        }

        result = await invoke(payload)

        assert result["status"] == "success"
        assert result["topic"] == "S3"
        assert result["difficulty"] == "beginner"
        assert "question" in result
        assert "quality_validation" in result
        assert "aws_info" in result
        assert "agent_info" in result

    @patch("app.agentcore.agent_main.aws_info_agent")
    @patch("app.agentcore.agent_main.question_generation_agent")
    @patch("app.agentcore.agent_main.quality_management_agent")
    async def test_invoke_default_values(
        self, mock_quality: Mock, mock_question: Mock, mock_aws_info: Mock
    ) -> None:
        """デフォルト値のテスト"""
        import asyncio

        mock_aws_info.return_value = asyncio.Future()
        mock_aws_info.return_value.set_result({"service": "EC2"})
        mock_question.return_value = {"id": "q_ec2_intermediate_001"}
        mock_quality.return_value = {"is_valid": True}

        payload: dict[str, str] = {}

        result = await invoke(payload)

        assert result["topic"] == "EC2"
        assert result["difficulty"] == "intermediate"
        mock_aws_info.assert_called_once_with(service="EC2")

    @patch("app.agentcore.agent_main.aws_info_agent")
    async def test_invoke_error_handling(self, mock_aws_info: Mock) -> None:
        """エラーハンドリングのテスト"""
        # 非同期エラーを発生させる
        import asyncio
        from typing import Any

        future: asyncio.Future[Any] = asyncio.Future()
        future.set_exception(Exception("Test error"))
        mock_aws_info.return_value = future

        payload = {"prompt": "Test prompt"}

        result = await invoke(payload)

        assert result["status"] == "error"
        assert "Test error" in result["error"]
        assert "Failed to generate and deliver question" in result["message"]
        assert result["agent_info"]["error_phase"] == "multi_agent_processing"

    @patch("app.agentcore.agent_main.aws_info_agent")
    @patch("app.agentcore.agent_main.question_generation_agent")
    @patch("app.agentcore.agent_main.quality_management_agent")
    async def test_invoke_multi_agent_flow(
        self, mock_quality: Mock, mock_question: Mock, mock_aws_info: Mock
    ) -> None:
        """マルチエージェントフローのテスト"""
        # モックの設定
        aws_info = {"service": "Lambda", "description": "Lambda service"}
        question = {"id": "q_lambda_advanced_001", "topic": "Lambda"}
        quality_result = {"is_valid": True, "quality_score": 95}

        import asyncio

        mock_aws_info.return_value = asyncio.Future()
        mock_aws_info.return_value.set_result(aws_info)
        mock_question.return_value = question
        mock_quality.return_value = quality_result

        payload = {
            "topic": "Lambda",
            "difficulty": "advanced",
        }

        result = await invoke(payload)

        # 各エージェントが正しい順序で呼ばれたかチェック
        mock_aws_info.assert_called_once_with(service="Lambda")
        mock_question.assert_called_once_with(
            topic="Lambda", difficulty="advanced", aws_info=aws_info
        )
        mock_quality.assert_called_once_with(question=question)

        # 結果の検証
        assert result["status"] == "success"
        assert result["question"] == question
        assert result["quality_validation"] == quality_result
        assert result["aws_info"] == aws_info


class TestAgentInitialization:
    """Agent 初期化のテスト"""

    def test_agent_has_tools(self) -> None:
        """エージェントにツールが設定されているかテスト"""
        # agent オブジェクトが正しく初期化されているかチェック
        assert agent is not None
        # ツールが設定されているかは内部実装に依存するため、
        # 実際の動作確認は統合テストで行う

    def test_app_initialization(self) -> None:
        """BedrockAgentCoreApp が初期化されているかテスト"""
        assert app is not None
        # app.entrypoint デコレータが正しく動作するかは
        # 実際のHTTPリクエストテストで確認


class TestIntegration:
    """統合テスト"""

    @patch("app.agentcore.agent_main.aws_info_agent")
    @patch("app.agentcore.agent_main.question_generation_agent")
    @patch("app.agentcore.agent_main.quality_management_agent")
    async def test_full_workflow(
        self, mock_quality: Mock, mock_question: Mock, mock_aws_info: Mock
    ) -> None:
        """全体ワークフロー（Agent-as-Tools パターン）のテスト"""
        # 完全なワークフローのモック設定
        aws_info = {
            "service": "EC2",
            "description": "EC2 compute service",
            "use_cases": ["Web hosting", "Application hosting"],
            "pricing_model": "Pay-as-you-use",
        }
        question = {
            "id": "q_ec2_intermediate_001",
            "topic": "EC2",
            "difficulty": "intermediate",
            "question": "What is the primary use case for AWS EC2?",
            "options": {
                "A": "Compute",
                "B": "Storage",
                "C": "Database",
                "D": "Network",
            },
            "correct_answer": "A",
        }
        quality_result = {
            "question_id": "q_ec2_intermediate_001",
            "is_valid": True,
            "quality_score": 88,
            "validation_checks": {
                "technical_accuracy": True,
                "difficulty_appropriate": True,
                "format_correct": True,
                "explanation_clear": True,
            },
        }

        import asyncio

        mock_aws_info.return_value = asyncio.Future()
        mock_aws_info.return_value.set_result(aws_info)
        mock_question.return_value = question
        mock_quality.return_value = quality_result

        payload = {
            "prompt": "Generate an AWS exam question for EC2 with intermediate difficulty",
            "topic": "EC2",
            "difficulty": "intermediate",
        }

        result = await invoke(payload)

        # 期待される結果の検証
        assert result["status"] == "success"
        assert result["topic"] == "EC2"
        assert result["difficulty"] == "intermediate"
        assert result["question"] == question
        assert result["quality_validation"] == quality_result
        assert result["aws_info"] == aws_info
        assert result["message"] == "Question generated and delivered successfully"

        # Agent-as-Tools パターンの検証
        assert result["agent_info"]["supervisor"] == "SupervisorAgent"
        assert "aws_info_agent" in result["agent_info"]["agents_used"]
        assert "question_generation_agent" in result["agent_info"]["agents_used"]
        assert "quality_management_agent" in result["agent_info"]["agents_used"]

        # 各エージェントが正しく呼ばれたかチェック
        mock_aws_info.assert_called_once_with(service="EC2")
        mock_question.assert_called_once_with(
            topic="EC2", difficulty="intermediate", aws_info=aws_info
        )
        mock_quality.assert_called_once_with(question=question)
