"""
Cloud CoPassAgent - agent_main.py のテストコード

契約による設計に基づく包括的なテスト実装。
複数問題生成に対応したAgentOutputモデルの検証。
Given-When-Thenパターンによる明確なテスト構造。
"""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import ValidationError

from app.agentcore.agent_main import AgentInput, AgentOutput, Question, invoke


class TestAgentInput:
    """AgentInput モデルの契約検証"""

    def test_default_values_contract(self) -> None:
        """
        契約による設計: AgentInputのデフォルト値検証

        Given: パラメータなしでの初期化
        When: AgentInputインスタンスを作成する
        Then: デフォルト値が正しく設定される

        事前条件: パラメータなしでの初期化
        事後条件: デフォルト値が正しく設定される
        不変条件: デフォルト値の整合性と型制約
        """
        # Given - パラメータなしでの初期化条件
        # When - AgentInputインスタンスを作成
        input_model = AgentInput()

        # Then - 事後条件検証: デフォルト値が正しく設定される
        assert input_model.exam_type == "AWS-SAP"
        assert input_model.question_count == 1

        # 不変条件検証: 型制約と値の整合性
        assert isinstance(input_model.exam_type, str)
        assert isinstance(input_model.question_count, int)
        assert input_model.question_count >= 1

    def test_custom_values_contract(self) -> None:
        """
        契約による設計: AgentInputのカスタム値検証

        Given: カスタム値での初期化
        When: AgentInputインスタンスを作成する
        Then: 指定した値が正しく設定される

        事前条件: カスタム値での初期化
        事後条件: 指定した値が正しく設定される
        不変条件: 値の型と制約が保持される
        """
        # Given - カスタム値での初期化条件
        custom_data: dict[str, Any] = {
            "exam_type": "AWS-SAP",
            "question_count": 3,
        }

        # When - AgentInputインスタンスを作成
        input_model = AgentInput(**custom_data)

        # Then - 事後条件検証
        assert input_model.exam_type == "AWS-SAP"
        assert input_model.question_count == 3

        # 不変条件検証
        assert 1 <= input_model.question_count <= 5

    def test_question_count_validation_contract(self) -> None:
        """
        契約による設計: AgentInputの問題数バリデーション検証

        Given: 無効な問題数での初期化
        When: AgentInputインスタンスを作成する
        Then: ValidationErrorが発生する

        事前条件: 無効な問題数での初期化
        事後条件: ValidationError が発生する
        不変条件: 問題数の制約（1-5問）が守られる
        """
        # Given - 事前条件違反: 問題数が範囲外

        # When & Then - ValidationErrorが発生することを検証
        with pytest.raises(ValidationError):
            AgentInput(exam_type="AWS-SAP", question_count=0)

        # 上限テスト
        with pytest.raises(ValidationError):
            AgentInput(exam_type="AWS-SAP", question_count=6)


class TestQuestion:
    """Question モデルの契約検証"""

    def test_valid_question_contract(self) -> None:
        """
        契約による設計: Questionモデルの有効性検証

        Given: 有効な問題データ
        When: Questionインスタンスを作成する
        Then: Questionモデルが正常に作成される

        事前条件: 有効な問題データ
        事後条件: Question モデルが正常に作成される
        不変条件: 問題の構造と制約が保持される
        """
        # Given - 事前条件設定
        question_data: dict[str, Any] = {
            "question": "EC2インスタンスに関する問題",
            "options": ["A. t2.micro", "B. m5.large", "C. c5.xlarge", "D. r5.2xlarge"],
            "correct_answer": "B",
            "explanation": "m5.largeが最適です。",
            "source": ["https://docs.aws.amazon.com/ec2/"],
            # 新機能: 試験ガイド活用による問題分類表示
            "learning_domain": "コンピューティング",
            "primary_technologies": ["EC2", "インスタンスタイプ"],
            "learning_insights": "EC2インスタンスタイプ選択では、ワークロードの特性（CPU集約型、メモリ集約型等）を理解することが重要。実務では、コスト最適化とパフォーマンスのバランスを考慮した選択が求められる。",
        }

        # When - Questionインスタンスを作成
        question = Question(**question_data)

        # Then - 事後条件検証
        assert question.question == "EC2インスタンスに関する問題"
        assert len(question.options) == 4
        assert question.correct_answer == "B"
        assert question.explanation == "m5.largeが最適です。"
        assert len(question.source) == 1
        # 新機能フィールドの検証
        assert question.learning_domain == "コンピューティング"
        assert question.primary_technologies == ["EC2", "インスタンスタイプ"]
        assert "EC2インスタンスタイプ選択では" in question.learning_insights

        # 不変条件検証
        assert isinstance(question.question, str)
        assert isinstance(question.options, list)
        assert isinstance(question.correct_answer, str)
        assert isinstance(question.explanation, str)
        assert isinstance(question.source, list)
        # 新機能フィールドの型検証
        assert isinstance(question.learning_domain, str)
        assert isinstance(question.primary_technologies, list)
        assert isinstance(question.learning_insights, str)
        assert isinstance(question.source, list)
        assert len(question.question) > 0
        assert len(question.options) >= 4  # 最低4つの選択肢


class TestAgentOutput:
    """AgentOutput モデルの契約検証"""

    def test_single_question_output_contract(self) -> None:
        """
        契約による設計: AgentOutput単一問題出力検証

        Given: 単一問題のデータ
        When: AgentOutputインスタンスを作成する
        Then: AgentOutputモデルが正常に作成される

        事前条件: 単一問題のデータ
        事後条件: AgentOutput モデルが正常に作成される
        不変条件: 問題リストの構造が保持される
        """
        # Given - 事前条件設定
        question = Question(
            question="単一問題テスト",
            options=["A. 選択肢1", "B. 選択肢2", "C. 選択肢3", "D. 選択肢4"],
            correct_answer="A",
            explanation="解説",
            source=["https://docs.aws.amazon.com/test/"],
            # 新機能: 試験ガイド活用による問題分類表示
            learning_domain="テスト分野",
            primary_technologies=["テスト技術"],
            learning_insights="テスト分野の重要ポイントは基本概念の理解。実務では継続的な学習が重要。",
        )

        # When - AgentOutputインスタンスを作成
        agent_output = AgentOutput(questions=[question])

        # Then - 事後条件検証
        assert len(agent_output.questions) == 1
        assert agent_output.questions[0].question == "単一問題テスト"

        # 不変条件検証
        assert isinstance(agent_output.questions, list)
        assert all(isinstance(q, Question) for q in agent_output.questions)

    def test_multiple_questions_output_contract(self) -> None:
        """
        契約による設計: AgentOutput複数問題出力検証

        Given: 複数問題のデータ
        When: AgentOutputインスタンスを作成する
        Then: AgentOutputモデルが正常に作成される

        事前条件: 複数問題のデータ
        事後条件: AgentOutput モデルが正常に作成される
        不変条件: 複数問題の構造が保持される
        """
        # Given - 事前条件設定
        questions = [
            Question(
                question=f"問題{i + 1}",
                options=[f"{chr(65 + j)}. 選択肢{j + 1}" for j in range(4)],
                correct_answer="A",
                explanation=f"解説{i + 1}",
                source=[f"https://docs.aws.amazon.com/test{i + 1}/"],
                # 新機能: 試験ガイド活用による問題分類表示
                learning_domain=f"テスト分野{i + 1}",
                primary_technologies=[f"技術{i + 1}"],
                learning_insights=f"学習ポイント{i + 1}",
            )
            for i in range(3)
        ]

        # When - AgentOutputインスタンスを作成
        agent_output = AgentOutput(questions=questions)

        # Then - 事後条件検証
        assert len(agent_output.questions) == 3
        assert agent_output.questions[0].question == "問題1"
        assert agent_output.questions[2].question == "問題3"

        # 不変条件検証
        assert isinstance(agent_output.questions, list)
        assert all(isinstance(q, Question) for q in agent_output.questions)
        assert len(agent_output.questions) > 1


class TestInvokeFunction:
    """invoke 関数の契約検証"""

    def _create_mock_question(self, index: int = 1) -> Question:
        """テスト用のQuestionモックを作成"""
        return Question(
            question=f"EC2インスタンスに関する問題{index}",
            options=["A. t2.micro", "B. m5.large", "C. c5.xlarge", "D. r5.2xlarge"],
            correct_answer="B",
            explanation=f"m5.largeが最適です。解説{index}",
            source=["https://docs.aws.amazon.com/ec2/"],
            # 新機能: 試験ガイド活用による問題分類表示
            learning_domain="コンピューティング",
            primary_technologies=["EC2", "インスタンスタイプ"],
            learning_insights="EC2インスタンスタイプ選択では、ワークロードの特性を理解することが重要。実務では、コスト最適化とパフォーマンスのバランスを考慮。",
        )

    @patch.dict(
        "os.environ",
        {
            "POWER_AUTOMATE_WEBHOOK_URL": "https://test.webhook.url",
            "POWER_AUTOMATE_SECURITY_TOKEN": "test-security-token",
        },
    )
    @patch("app.agentcore.agent_main.memory_client")
    @patch("app.agentcore.agent_main.TeamsClient")
    @patch("app.agentcore.agent_main.agent")
    async def test_single_question_generation_contract(
        self,
        mock_agent: MagicMock,
        mock_teams_client_class: MagicMock,
        mock_memory_client: MagicMock,
    ) -> None:
        """
        契約による設計: 単一問題生成の包括的検証

        Given: 単一問題生成の有効なペイロードと正常なモック環境
        When: invoke関数を実行する
        Then: AgentOutputが返され、Teams投稿が実行される

        事前条件: 単一問題生成の有効なペイロード
        事後条件: AgentOutputが返される
        不変条件: 問題数が1問、Teams投稿が実行される
        """
        # Given - 事前条件設定: 有効なペイロードとモック環境
        valid_payload: dict[str, Any] = {
            "exam_type": "AWS-SAP",
            "question_count": 1,
        }

        # エージェントモックの設定
        mock_result = AgentOutput(questions=[self._create_mock_question()])
        mock_agent.structured_output.return_value = mock_result

        # Memory クライアントモックの設定
        mock_memory_client.get_recent_domains = AsyncMock(return_value=[])
        mock_memory_client.record_domain_usage = AsyncMock(return_value=None)

        # Teamsクライアントモックの設定
        mock_teams_client = MagicMock()
        mock_teams_client.send = AsyncMock(return_value=None)
        mock_teams_client_class.return_value = mock_teams_client

        # When - invoke関数を実行
        result = await invoke(valid_payload)

        # Then - 事後条件検証: AgentOutputが返される
        assert "questions" in result
        assert len(result["questions"]) == 1

        question = result["questions"][0]
        assert "question" in question
        assert "options" in question
        assert "correct_answer" in question
        assert "explanation" in question
        assert "source" in question

        # 不変条件検証
        assert isinstance(result["questions"], list)
        assert len(result["questions"]) == 1
        assert isinstance(question["options"], list)
        assert len(question["options"]) >= 4

        # エージェント、Memory、Teamsクライアントが正しく呼び出されたことを確認
        mock_agent.structured_output.assert_called_once()
        mock_memory_client.get_recent_domains.assert_called_once_with(
            exam_type="AWS-SAP"
        )
        mock_memory_client.record_domain_usage.assert_called_once_with(
            learning_domain="コンピューティング", exam_type="AWS-SAP"
        )
        mock_teams_client.send.assert_called_once()

    @patch.dict(
        "os.environ",
        {
            "POWER_AUTOMATE_WEBHOOK_URL": "https://test.webhook.url",
            "POWER_AUTOMATE_SECURITY_TOKEN": "test-security-token",
        },
    )
    @patch("app.agentcore.agent_main.memory_client")
    @patch("app.agentcore.agent_main.TeamsClient")
    @patch("app.agentcore.agent_main.agent")
    async def test_multiple_questions_generation_contract(
        self,
        mock_agent: MagicMock,
        mock_teams_client_class: MagicMock,
        mock_memory_client: MagicMock,
    ) -> None:
        """
        契約による設計: 複数問題生成の包括的検証

        Given: 複数問題生成の有効なペイロードと正常なモック環境
        When: invoke関数を実行する
        Then: 複数問題のAgentOutputが返され、Teams投稿が実行される

        事前条件: 複数問題生成の有効なペイロード
        事後条件: 複数問題のAgentOutputが返される
        不変条件: 指定した問題数、Teams投稿が実行される
        """
        # Given - 事前条件設定
        valid_payload: dict[str, Any] = {
            "exam_type": "AWS-SAP",
            "question_count": 3,
        }

        # エージェントモックの設定（3問）
        mock_questions = [self._create_mock_question(i) for i in range(1, 4)]
        mock_result = AgentOutput(questions=mock_questions)
        mock_agent.structured_output.return_value = mock_result

        # Memory クライアントモックの設定
        mock_memory_client.get_recent_domains = AsyncMock(return_value=[])
        mock_memory_client.record_domain_usage = AsyncMock(return_value=None)

        # Teamsクライアントモックの設定
        mock_teams_client = MagicMock()
        # mock_teams_response削除
        # status設定削除
        mock_teams_client.send = AsyncMock(
            return_value=None
        )  # 例外ベース: 成功時は何も返さない
        mock_teams_client_class.return_value = mock_teams_client

        # When - invoke関数を実行
        result = await invoke(valid_payload)

        # Then - 事後条件検証
        assert "questions" in result
        assert len(result["questions"]) == 3

        # 各問題の構造確認
        for i, question in enumerate(result["questions"]):
            assert "question" in question
            assert f"問題{i + 1}" in question["question"]
            assert "options" in question
            assert "correct_answer" in question
            assert "explanation" in question
            assert "source" in question

        # 不変条件検証
        assert isinstance(result["questions"], list)
        assert len(result["questions"]) == 3
        assert all(isinstance(q["options"], list) for q in result["questions"])

        # エージェント、Memory、Teamsクライアントが正しく呼び出されたことを確認
        mock_agent.structured_output.assert_called_once()
        mock_memory_client.get_recent_domains.assert_called_once_with(
            exam_type="AWS-SAP"
        )
        assert mock_memory_client.record_domain_usage.call_count == 3  # 3問分
        mock_teams_client.send.assert_called_once()

    @patch.dict(
        "os.environ",
        {
            "POWER_AUTOMATE_WEBHOOK_URL": "https://test.webhook.url",
            "POWER_AUTOMATE_SECURITY_TOKEN": "test-security-token",
        },
    )
    @patch("app.agentcore.agent_main.TeamsClient")
    @patch("app.agentcore.agent_main.agent")
    async def test_teams_posting_failure_contract(
        self, mock_agent: MagicMock, mock_teams_client_class: MagicMock
    ) -> None:
        """
        契約による設計: Teams投稿失敗時の処理検証

        Given: 有効なペイロードとTeams投稿失敗環境
        When: invoke関数を実行する
        Then: 問題生成は成功し、Teams投稿失敗がログに記録される

        事前条件: 有効なペイロード、Teams投稿失敗
        事後条件: 問題生成は成功、Teams投稿失敗はログに記録
        不変条件: 問題データは正常に生成される
        """
        # Given - 事前条件設定
        valid_payload: dict[str, Any] = {
            "exam_type": "AWS-SAP",
            "question_count": 1,
        }

        # エージェントモックの設定
        mock_result = AgentOutput(questions=[self._create_mock_question()])
        mock_agent.structured_output.return_value = mock_result

        # Teamsクライアントモック（失敗）の設定
        mock_teams_client = MagicMock()
        mock_teams_client.send = AsyncMock(
            side_effect=ValueError("Webhook URL not configured")
        )
        mock_teams_client_class.return_value = mock_teams_client

        # When - invoke関数を実行
        result = await invoke(valid_payload)

        # Then - 事後条件検証
        assert "questions" in result

        # 不変条件検証: 問題生成は成功している
        assert "error" not in result
        assert isinstance(result["questions"], list)
        assert len(result["questions"]) == 1
        assert len(result["questions"][0]["question"]) > 0

    @patch("app.agentcore.agent_main.agent")
    async def test_invalid_payload_precondition(self, mock_agent: MagicMock) -> None:
        """
        契約による設計: 無効ペイロード時の事前条件検証

        Given: 無効なペイロード
        When: invoke関数を実行する
        Then: ValidationErrorによりエラーレスポンスが返される

        事前条件: 無効なペイロード
        事後条件: ValidationError によりエラーレスポンスが返される
        不変条件: エラー時は error フィールドが存在する
        """
        # Given - 事前条件違反: 無効な問題数
        invalid_payload: dict[str, Any] = {
            "question_count": 0  # 無効な値
        }

        # When - invoke関数を実行
        result = await invoke(invalid_payload)

        # Then - 事後条件検証
        assert "error" in result

        # 不変条件検証
        assert isinstance(result, dict)

    @patch.dict(
        "os.environ",
        {
            "POWER_AUTOMATE_WEBHOOK_URL": "https://test.webhook.url",
            "POWER_AUTOMATE_SECURITY_TOKEN": "test-security-token",
        },
    )
    @patch("app.agentcore.agent_main.TeamsClient")
    @patch("app.agentcore.agent_main.agent")
    async def test_empty_payload_contract(
        self, mock_agent: MagicMock, mock_teams_client_class: MagicMock
    ) -> None:
        """
        契約による設計: 空ペイロード時のデフォルト値処理検証

        Given: 空のペイロード
        When: invoke関数を実行する
        Then: デフォルト値で処理される

        事前条件: 空のペイロード
        事後条件: デフォルト値で処理される
        不変条件: デフォルト値での正常処理
        """
        # Given - 事前条件設定
        empty_payload: dict[str, Any] = {}

        # エージェントモックの設定
        mock_result = AgentOutput(questions=[self._create_mock_question()])
        mock_agent.structured_output.return_value = mock_result

        # Teamsクライアントモックの設定
        mock_teams_client = MagicMock()
        # mock_teams_response削除
        # status設定削除
        mock_teams_client.send = AsyncMock(
            return_value=None
        )  # 例外ベース: 成功時は何も返さない
        mock_teams_client_class.return_value = mock_teams_client

        # When - invoke関数を実行
        result = await invoke(empty_payload)

        # Then - 事後条件検証
        assert "questions" in result
        assert len(result["questions"]) == 1  # デフォルトは1問

        # 不変条件検証: デフォルト値での処理が成功
        mock_agent.structured_output.assert_called_once()


class TestConstants:
    """定数の契約検証"""

    def test_exam_types_invariant(self) -> None:
        """
        不変条件: EXAM_TYPES の構造と内容が正しい
        """
        from app.agentcore.agent_main import EXAM_TYPES

        # 不変条件検証
        assert isinstance(EXAM_TYPES, dict)
        assert "AWS-SAP" in EXAM_TYPES
        assert "name" in EXAM_TYPES["AWS-SAP"]

        # 簡素化後の構造: nameフィールドのみ保持
        assert isinstance(EXAM_TYPES["AWS-SAP"]["name"], str)
        assert len(EXAM_TYPES["AWS-SAP"]["name"]) > 0

    def test_model_id_invariant(self) -> None:
        """
        不変条件: MODEL_ID の構造と内容が正しい
        """
        from app.agentcore.agent_main import MODEL_ID

        # 不変条件検証
        assert isinstance(MODEL_ID, dict)
        assert "claude-3.7-sonnet" in MODEL_ID
        assert isinstance(MODEL_ID["claude-3.7-sonnet"], str)
        assert MODEL_ID["claude-3.7-sonnet"].startswith("us.anthropic.claude")


class TestBusinessLogicContracts:
    """ビジネスロジックの契約検証"""

    @patch.dict(
        "os.environ",
        {
            "POWER_AUTOMATE_WEBHOOK_URL": "https://test.webhook.url",
            "POWER_AUTOMATE_SECURITY_TOKEN": "test-security-token",
        },
    )
    @patch("app.agentcore.agent_main.TeamsClient")
    @patch("app.agentcore.agent_main.agent")
    async def test_exam_type_specific_generation_contract(
        self, mock_agent: MagicMock, mock_teams_client_class: MagicMock
    ) -> None:
        """
        契約による設計: 試験タイプ指定時の問題生成検証

        Given: 特定試験タイプが指定されたペイロード
        When: invoke関数を実行する
        Then: プロンプトに試験タイプが含まれる

        事前条件: 特定試験タイプが指定される
        事後条件: プロンプトに試験タイプが含まれる
        不変条件: 指定された試験タイプが処理に反映される
        """
        # Given - 事前条件設定
        payload: dict[str, Any] = {
            "exam_type": "AWS-SAP",
            "question_count": 1,
        }

        # エージェントモックの設定
        mock_result = AgentOutput(
            questions=[
                Question(
                    question="Solutions Architectに関する問題",
                    options=["A", "B", "C", "D"],
                    correct_answer="A",
                    explanation="解説",
                    source=[],
                    # 新機能: 試験ガイド活用による問題分類表示
                    learning_domain="複雑な組織に対応するソリューションの設計",
                    primary_technologies=["AWS Organizations", "AWS Control Tower"],
                    learning_insights="マルチアカウント戦略では、組織単位(OU)による階層管理とSCPによる権限制御が重要。実務では開発・本番環境の分離やコスト管理の観点から設計する。",
                )
            ]
        )
        mock_agent.structured_output.return_value = mock_result

        # Teamsクライアントモックの設定
        mock_teams_client = MagicMock()
        mock_teams_client.send = AsyncMock(return_value=None)
        mock_teams_client_class.return_value = mock_teams_client

        # When - invoke関数を実行
        result = await invoke(payload)

        # Then - 事後条件検証
        assert "error" not in result
        assert "questions" in result

        # 不変条件検証: プロンプトに試験タイプが含まれることを確認
        call_args = mock_agent.structured_output.call_args
        prompt_arg = call_args.kwargs["prompt"]
        assert "AWS Certified Solutions Architect - Professional" in prompt_arg

    @patch.dict(
        "os.environ",
        {
            "POWER_AUTOMATE_WEBHOOK_URL": "https://test.webhook.url",
            "POWER_AUTOMATE_SECURITY_TOKEN": "test-security-token",
        },
    )
    @patch("app.agentcore.agent_main.TeamsClient")
    @patch("app.agentcore.agent_main.agent")
    async def test_exam_type_contract(
        self, mock_agent: MagicMock, mock_teams_client_class: MagicMock
    ) -> None:
        """
        契約による設計: 試験タイプ指定時の処理検証

        Given: 有効な試験タイプが指定されたペイロード
        When: invoke関数を実行する
        Then: プロンプトに試験タイプが含まれる

        事前条件: 有効な試験タイプが指定される
        事後条件: プロンプトに試験タイプが含まれる
        不変条件: 試験タイプが処理に反映される
        """
        # Given - 事前条件設定
        payload: dict[str, Any] = {"exam_type": "AWS-SAP", "question_count": 1}

        # エージェントモックの設定
        mock_result = AgentOutput(
            questions=[
                Question(
                    question="SAP レベルの問題",
                    options=["A", "B", "C", "D"],
                    correct_answer="A",
                    explanation="解説",
                    source=[],
                    # 新機能: 試験ガイド活用による問題分類表示
                    learning_domain="セキュリティ、アイデンティティ、コンプライアンス",
                    primary_technologies=["IAM", "CloudTrail"],
                    learning_insights="IAMセキュリティでは最小権限の原則が基本。CloudTrailによる監査ログ記録で、セキュリティインシデントの早期発見と原因究明が可能。実務では定期的な権限レビューが重要。",
                )
            ]
        )
        mock_agent.structured_output.return_value = mock_result

        # Teamsクライアントモックの設定
        mock_teams_client = MagicMock()
        # mock_teams_response削除
        # status設定削除
        mock_teams_client.send = AsyncMock(
            return_value=None
        )  # 例外ベース: 成功時は何も返さない
        mock_teams_client_class.return_value = mock_teams_client

        # When - invoke関数を実行
        result = await invoke(payload)

        # Then - 事後条件検証
        assert "error" not in result
        assert "questions" in result

        # 不変条件検証: プロンプトに試験タイプが含まれることを確認
        call_args = mock_agent.structured_output.call_args
        prompt_arg = call_args.kwargs["prompt"]
        assert "AWS Certified Solutions Architect - Professional" in prompt_arg


class TestDataIntegrityContracts:
    """データ整合性の契約検証"""

    @patch.dict(
        "os.environ",
        {
            "POWER_AUTOMATE_WEBHOOK_URL": "https://test.webhook.url",
            "POWER_AUTOMATE_SECURITY_TOKEN": "test-security-token",
        },
    )
    @patch("app.agentcore.agent_main.TeamsClient")
    @patch("app.agentcore.agent_main.agent")
    async def test_question_structure_integrity_contract(
        self, mock_agent: MagicMock, mock_teams_client_class: MagicMock
    ) -> None:
        """
        契約による設計: 問題構造整合性検証

        Given: 有効なペイロード
        When: invoke関数を実行する
        Then: 問題構造の整合性が保たれる

        事前条件: 有効なペイロード
        事後条件: 問題構造の整合性が保たれる
        不変条件: 各問題が必要なフィールドを持つ
        """
        # Given - 事前条件設定
        payload: dict[str, Any] = {"question_count": 2}

        # エージェントモックの設定
        mock_questions = [
            Question(
                question=f"問題{i + 1}",
                options=[f"{chr(65 + j)}. 選択肢{j + 1}" for j in range(4)],
                correct_answer="A",
                explanation=f"解説{i + 1}",
                source=[f"https://docs.aws.amazon.com/test{i + 1}/"],
                # 新機能: 試験ガイド活用による問題分類表示
                learning_domain=f"テスト分野{i + 1}",
                primary_technologies=[f"技術{i + 1}"],
                learning_insights=f"学習ポイント{i + 1}",
            )
            for i in range(2)
        ]
        mock_result = AgentOutput(questions=mock_questions)
        mock_agent.structured_output.return_value = mock_result

        # Teamsクライアントモックの設定
        mock_teams_client = MagicMock()
        # mock_teams_response削除
        # status設定削除
        mock_teams_client.send = AsyncMock(
            return_value=None
        )  # 例外ベース: 成功時は何も返さない
        mock_teams_client_class.return_value = mock_teams_client

        # When - invoke関数を実行
        result = await invoke(payload)

        # Then - 事後条件検証
        assert "questions" in result
        assert len(result["questions"]) == 2

        # 不変条件検証: 各問題の構造整合性
        for question in result["questions"]:
            assert "question" in question
            assert "options" in question
            assert "correct_answer" in question
            assert "explanation" in question
            assert "source" in question
            assert isinstance(question["options"], list)
            assert len(question["options"]) >= 4


class TestSystemInvariants:
    """システム全体の不変条件検証"""

    @patch.dict(
        "os.environ",
        {
            "POWER_AUTOMATE_WEBHOOK_URL": "https://test.webhook.url",
            "POWER_AUTOMATE_SECURITY_TOKEN": "test-security-token",
        },
    )
    @patch("app.agentcore.agent_main.TeamsClient")
    @patch("app.agentcore.agent_main.agent")
    async def test_logging_invariant(
        self, mock_agent: MagicMock, mock_teams_client_class: MagicMock
    ) -> None:
        """
        不変条件: 適切なログが出力される
        """
        # Given - 事前条件設定
        payload: dict[str, Any] = {"question_count": 1}

        mock_result = AgentOutput(
            questions=[
                Question(
                    question="ログテスト問題",
                    options=["A", "B", "C", "D"],
                    correct_answer="A",
                    explanation="解説",
                    source=[],
                    # 新機能: 試験ガイド活用による問題分類表示
                    learning_domain="ログテスト分野",
                    primary_technologies=["ログテスト技術"],
                    learning_insights="ログテスト分野の学習ポイント。実務での応用と注意点を含む。",
                )
            ]
        )
        mock_agent.structured_output.return_value = mock_result

        mock_teams_client = MagicMock()
        # mock_teams_response削除
        # status設定削除
        mock_teams_client.send = AsyncMock(
            return_value=None
        )  # 例外ベース: 成功時は何も返さない
        mock_teams_client_class.return_value = mock_teams_client

        # When - ログ出力をモックしてinvoke関数を実行
        with patch("app.agentcore.agent_main.logger") as mock_logger:
            await invoke(payload)

            # Then - 不変条件検証: ログが適切に出力される
            mock_logger.info.assert_called()
            log_calls = [call.args[0] for call in mock_logger.info.call_args_list]

            # 期待されるログメッセージの確認
            assert any("問題生成プロンプト" in msg for msg in log_calls)
            assert any("問題生成結果:" in msg for msg in log_calls)

    def test_model_validation_invariant(self) -> None:
        """
        不変条件: モデルのバリデーションが正しく動作する
        """
        # 不変条件検証: 型が間違っているデータでValidationErrorが発生
        with pytest.raises(ValidationError):
            Question(
                question=123,  # type: ignore  # 意図的な型エラーのテスト
                options=["A", "B"],
                correct_answer="A",
                explanation="説明",
                source=["https://example.com"],
                # 新機能: 試験ガイド活用による問題分類表示
                learning_domain="テスト分野",
                primary_technologies=["テスト技術"],
                learning_insights="テスト分野の学習ポイント。実務での応用と注意点を含む。",
            )

    @patch.dict(
        "os.environ",
        {
            "POWER_AUTOMATE_WEBHOOK_URL": "https://test.webhook.url",
            "POWER_AUTOMATE_SECURITY_TOKEN": "test-security-token",
        },
    )
    @patch("app.agentcore.agent_main.TeamsClient")
    @patch("app.agentcore.agent_main.agent")
    async def test_error_handling_invariant(
        self, mock_agent: MagicMock, mock_teams_client_class: MagicMock
    ) -> None:
        """
        不変条件: エラー時は適切なエラーレスポンスが返される
        """
        # Given - エラーを発生させる設定
        payload: dict[str, Any] = {"question_count": 1}
        mock_agent.structured_output.side_effect = Exception("テストエラー")

        # When - invoke関数を実行
        result = await invoke(payload)

        # Then - 不変条件検証: エラー時の適切な処理
        assert "error" in result
        assert "テストエラー" in result["error"]
        assert isinstance(result, dict)


class TestIntegrationContracts:
    """統合レベルの契約検証"""

    @patch("app.agentcore.agent_main.agent", None)
    async def test_agent_not_initialized_error_contract(self) -> None:
        """
        契約による設計: エージェント未初期化時のエラーハンドリング検証

        Given: エージェントが初期化されていない状態
        When: invoke関数を呼び出す
        Then: エラー辞書が返される

        事前条件: エージェントがNoneに設定されている
        事後条件: エラー辞書が返される
        不変条件: エラーメッセージが適切に設定される
        """
        # Given - 有効なペイロード（正しい形式）

        # When - invoke関数を呼び出す
        payload = {
            "exam_type": "AWS-SAP",
            "question_count": 1,
        }

        # When - invoke関数を呼び出す
        result = await invoke(payload)

        # Then - 事後条件検証: エラー辞書が返される
        assert "error" in result
        assert "エージェントが初期化されていません" in result["error"]

    @patch.dict(
        "os.environ",
        {
            "POWER_AUTOMATE_WEBHOOK_URL": "https://test.webhook.url",
            "POWER_AUTOMATE_SECURITY_TOKEN": "test-security-token",
        },
    )
    @patch("app.agentcore.agent_main.TeamsClient")
    @patch("app.agentcore.agent_main.agent")
    async def test_end_to_end_flow_contract(
        self, mock_agent: MagicMock, mock_teams_client_class: MagicMock
    ) -> None:
        """
        契約による設計: エンドツーエンドフロー検証

        Given: 完全な処理フロー環境
        When: invoke関数を実行する
        Then: 問題生成からTeams投稿まで完了する

        事前条件: 完全な処理フロー
        事後条件: 問題生成からTeams投稿まで完了
        不変条件: 全体フローの整合性
        """
        # Given - 事前条件設定
        payload: dict[str, Any] = {
            "exam_type": "AWS-SAP",
            "question_count": 2,
        }

        # エージェントモックの設定
        mock_questions = [
            Question(
                question=f"統合テスト問題{i + 1}",
                options=[f"{chr(65 + j)}. 選択肢{j + 1}" for j in range(4)],
                correct_answer="A",
                explanation=f"統合テスト解説{i + 1}",
                source=[f"https://docs.aws.amazon.com/integration{i + 1}/"],
                # 新機能: 試験ガイド活用による問題分類表示
                learning_domain=f"統合テスト分野{i + 1}",
                primary_technologies=[f"統合テスト技術{i + 1}"],
                learning_insights=f"統合テストガイド参照{i + 1}",
            )
            for i in range(2)
        ]
        mock_result = AgentOutput(questions=mock_questions)
        mock_agent.structured_output.return_value = mock_result

        # Teamsクライアントモックの設定
        mock_teams_client = MagicMock()
        # mock_teams_response削除
        # status設定削除
        mock_teams_client.send = AsyncMock(
            return_value=None
        )  # 例外ベース: 成功時は何も返さない
        mock_teams_client_class.return_value = mock_teams_client

        # When - invoke関数を実行
        result = await invoke(payload)

        # Then - 事後条件検証
        assert "questions" in result
        assert len(result["questions"]) == 2
        assert "error" not in result

        # 不変条件検証: 全体フローの整合性
        mock_agent.structured_output.assert_called_once()
        mock_teams_client.send.assert_called_once()

        # Teams投稿に渡されたデータの確認
        teams_call_args = mock_teams_client.send.call_args[0][0]
        assert hasattr(teams_call_args, "questions")
        assert len(teams_call_args.questions) == 2


class TestLoadExamGuide:
    """load_exam_guide 関数の契約検証"""

    def test_valid_exam_type_sap_contract(self) -> None:
        """
        契約による設計: 有効な試験タイプ"AWS-SAP"での試験ガイド読み込み検証

        事前条件: 試験タイプ"AWS-SAP"が指定される
        事後条件: AWS-SAP-C02.mdファイルの内容が返される
        不変条件: 返される内容は文字列で、空でない
        """
        from app.agentcore.agent_main import load_exam_guide

        # Arrange - 事前条件設定
        exam_type = "AWS-SAP"

        # Act - 実行
        result = load_exam_guide(exam_type)

        # Assert - 事後条件検証
        assert isinstance(result, str)
        assert len(result) > 0
        assert "AWS Certified Solutions Architect - Professional" in result

        # 不変条件検証: ファイル内容の基本構造
        assert "試験ガイド" in result or "Exam Guide" in result

    def test_fallback_exam_type_contract(self) -> None:
        """
        契約による設計: フォールバック機能での試験ガイド読み込み検証

        事前条件: EXAM_TYPESに存在しない試験タイプが指定される
        事後条件: 統一命名ルールに基づくファイルパスで読み込みが試行される
        不変条件: 適切なエラーハンドリングが行われる
        """
        from app.agentcore.agent_main import load_exam_guide

        # Arrange - 事前条件設定: 存在しない試験タイプ
        exam_type = "NONEXISTENT-EXAM"

        # Act & Assert - フォールバック機能の検証
        with pytest.raises(
            RuntimeError, match="試験ガイドファイルの読み込みに失敗しました"
        ):
            load_exam_guide(exam_type)

    def test_file_content_structure_invariant(self) -> None:
        """
        不変条件: 読み込まれるファイル内容の構造検証

        不変条件: ファイル内容が期待される構造を持つ
        """
        from app.agentcore.agent_main import load_exam_guide

        # Arrange - 事前条件設定
        exam_type = "AWS-SAP"

        # Act - 実行
        result = load_exam_guide(exam_type)

        # Assert - 不変条件検証: ファイル内容の構造
        assert isinstance(result, str)
        assert len(result) > 1000  # 十分な内容があることを確認

        # 試験ガイドの基本的な構造要素の確認
        expected_sections = ["試験ガイド", "受験対象者", "試験内容"]

        # 少なくとも一つの期待されるセクションが含まれていることを確認
        assert any(section in result for section in expected_sections)

    @patch("pathlib.Path.exists")
    def test_file_not_found_precondition(self, mock_exists: MagicMock) -> None:
        """
        事前条件違反: ファイルが存在しない場合のエラーハンドリング検証

        事前条件違反: 試験ガイドファイルが存在しない
        事後条件: RuntimeErrorが発生する
        """
        from app.agentcore.agent_main import load_exam_guide

        # Arrange - 事前条件違反: ファイルが存在しない
        mock_exists.return_value = False
        exam_type = "AWS-SAP"

        # Act & Assert - 事前条件検証
        with pytest.raises(
            RuntimeError, match="試験ガイドファイルの読み込みに失敗しました"
        ):
            load_exam_guide(exam_type)

    @patch("builtins.open")
    @patch("pathlib.Path.exists")
    def test_file_read_error_precondition(
        self, mock_exists: MagicMock, mock_open: MagicMock
    ) -> None:
        """
        事前条件違反: ファイル読み込みエラー時のエラーハンドリング検証

        事前条件違反: ファイル読み込み時にIOErrorが発生
        事後条件: RuntimeErrorが発生する
        """
        from app.agentcore.agent_main import load_exam_guide

        # Arrange - 事前条件違反: ファイル読み込みエラー
        mock_exists.return_value = True
        mock_open.side_effect = OSError("ファイル読み込みエラー")
        exam_type = "AWS-SAP"

        # Act & Assert - 事前条件検証
        with pytest.raises(
            RuntimeError, match="試験ガイドファイルの読み込みに失敗しました"
        ):
            load_exam_guide(exam_type)


class TestLoadSampleQuestions:
    """load_sample_questions 関数の契約検証"""

    def test_valid_exam_type_sap_contract(self) -> None:
        """
        契約による設計: 有効な試験タイプ"AWS-SAP"でのサンプル問題読み込み検証

        事前条件: 試験タイプ"AWS-SAP"が指定される
        事後条件: AWS-SAP-samples.mdファイルの内容が返される
        不変条件: 返される内容は文字列で、空でない
        """
        from app.agentcore.agent_main import load_sample_questions

        # Arrange - 事前条件設定
        exam_type = "AWS-SAP"

        # Act - 実行
        result = load_sample_questions(exam_type)

        # Assert - 事後条件検証
        assert isinstance(result, str)
        assert len(result) > 0

        # 不変条件検証: ファイル内容の基本構造
        assert "AWS Certified Solutions Architect - Professional" in result
        assert "サンプル問題" in result

    def test_nonexistent_exam_type_precondition(self) -> None:
        """
        事前条件違反: 存在しない試験タイプでのサンプル問題読み込み

        事前条件違反: 存在しない試験タイプが指定される
        事後条件: RuntimeErrorが発生する
        """
        from app.agentcore.agent_main import load_sample_questions

        # Arrange - 事前条件違反: 存在しないファイル
        exam_type = "NONEXISTENT-EXAM"

        # Act & Assert - 事前条件検証
        with pytest.raises(
            RuntimeError, match="サンプル問題ファイルの読み込みに失敗しました"
        ):
            load_sample_questions(exam_type)

    def test_file_content_structure_invariant(self) -> None:
        """
        不変条件: サンプル問題ファイル内容の構造検証

        事前条件: 有効な試験タイプが指定される
        不変条件: ファイル内容が期待される構造を持つ
        """
        from app.agentcore.agent_main import load_sample_questions

        # Arrange - 事前条件設定
        exam_type = "AWS-SAP"

        # Act - 実行
        result = load_sample_questions(exam_type)

        # Assert - 不変条件検証: ファイル内容の構造
        assert isinstance(result, str)
        assert len(result) > 100  # 最小限の内容があることを確認

        # 基本的な構造要素の存在確認
        assert "# AWS Certified Solutions Architect - Professional" in result
        assert "サンプル問題" in result

        # ファイル形式の確認（Markdown形式）
        assert result.startswith("#")  # Markdownヘッダーで開始

    @patch("builtins.open")
    def test_file_read_error_precondition(self, mock_open: MagicMock) -> None:
        """
        事前条件違反: ファイル読み込みエラー時の例外処理検証

        事前条件違反: ファイル読み込み時にIOErrorが発生
        事後条件: RuntimeErrorが発生する
        """
        from app.agentcore.agent_main import load_sample_questions

        # Arrange - 事前条件違反: ファイル読み込みエラー
        mock_open.side_effect = OSError("ファイル読み込みエラー")
        exam_type = "AWS-SAP"

        # Act & Assert - 事前条件検証
        with pytest.raises(
            RuntimeError, match="サンプル問題ファイルの読み込みに失敗しました"
        ):
            load_sample_questions(exam_type)


class TestDomainMemoryIntegration:
    """分野履歴記録機能の契約検証"""

    @patch.dict(
        "os.environ",
        {
            "POWER_AUTOMATE_WEBHOOK_URL": "https://test.webhook.url",
            "POWER_AUTOMATE_SECURITY_TOKEN": "test-security-token",
        },
    )
    @patch("app.agentcore.agent_main.memory_client")
    @patch("app.agentcore.agent_main.TeamsClient")
    @patch("app.agentcore.agent_main.agent")
    async def test_domain_memory_recording_contract(
        self,
        mock_agent: MagicMock,
        mock_teams_client_class: MagicMock,
        mock_memory_client: MagicMock,
    ) -> None:
        """
        契約による設計: 分野履歴記録機能の検証

        Given: 有効なペイロードと正常なMemoryクライアント
        When: invoke関数を実行する
        Then: 学習分野がMemoryに記録される

        事前条件: 有効なペイロード、正常なMemoryクライアント
        事後条件: 学習分野がMemoryに記録される
        不変条件: 各問題の学習分野が個別に記録される
        """
        # Given - 事前条件設定
        valid_payload: dict[str, Any] = {
            "exam_type": "AWS-SAP",
            "question_count": 2,
        }

        # エージェントモックの設定（異なる学習分野の2問）
        mock_questions = [
            Question(
                question="EC2に関する問題",
                options=["A. t2.micro", "B. m5.large", "C. c5.xlarge", "D. r5.2xlarge"],
                correct_answer="B",
                explanation="m5.largeが最適です。",
                source=["https://docs.aws.amazon.com/ec2/"],
                learning_domain="コンピューティング",
                primary_technologies=["EC2", "インスタンスタイプ"],
                learning_insights="EC2インスタンスタイプ選択の重要ポイント",
            ),
            Question(
                question="S3に関する問題",
                options=["A. Standard", "B. IA", "C. Glacier", "D. Deep Archive"],
                correct_answer="A",
                explanation="Standardが最適です。",
                source=["https://docs.aws.amazon.com/s3/"],
                learning_domain="ストレージ",
                primary_technologies=["S3", "ストレージクラス"],
                learning_insights="S3ストレージクラス選択の重要ポイント",
            ),
        ]
        mock_result = AgentOutput(questions=mock_questions)
        mock_agent.structured_output.return_value = mock_result

        # Memory クライアントモックの設定
        mock_memory_client.record_domain_usage = AsyncMock(return_value=None)

        # Teamsクライアントモックの設定
        mock_teams_client = MagicMock()
        mock_teams_client.send = AsyncMock(return_value=None)
        mock_teams_client_class.return_value = mock_teams_client

        # When - invoke関数を実行
        result = await invoke(valid_payload)

        # Then - 事後条件検証: 問題生成が成功
        assert "questions" in result
        assert len(result["questions"]) == 2
        assert "error" not in result

        # 不変条件検証: 各問題の学習分野が個別に記録される
        assert mock_memory_client.record_domain_usage.call_count == 2

        # 1問目の記録確認
        first_call = mock_memory_client.record_domain_usage.call_args_list[0]
        assert first_call.kwargs["learning_domain"] == "コンピューティング"
        assert first_call.kwargs["exam_type"] == "AWS-SAP"

        # 2問目の記録確認
        second_call = mock_memory_client.record_domain_usage.call_args_list[1]
        assert second_call.kwargs["learning_domain"] == "ストレージ"
        assert second_call.kwargs["exam_type"] == "AWS-SAP"

    @patch.dict(
        "os.environ",
        {
            "POWER_AUTOMATE_WEBHOOK_URL": "https://test.webhook.url",
            "POWER_AUTOMATE_SECURITY_TOKEN": "test-security-token",
        },
    )
    @patch("app.agentcore.agent_main.memory_client")
    @patch("app.agentcore.agent_main.TeamsClient")
    @patch("app.agentcore.agent_main.agent")
    async def test_memory_recording_failure_contract(
        self,
        mock_agent: MagicMock,
        mock_teams_client_class: MagicMock,
        mock_memory_client: MagicMock,
    ) -> None:
        """
        契約による設計: Memory記録失敗時の処理検証

        Given: 有効なペイロードとMemory記録失敗環境
        When: invoke関数を実行する
        Then: 問題生成は成功し、Memory記録失敗がログに記録される

        事前条件: 有効なペイロード、Memory記録失敗
        事後条件: 問題生成は成功、Memory記録失敗はログに記録
        不変条件: Memory記録失敗でも処理は継続される
        """
        # Given - 事前条件設定
        valid_payload: dict[str, Any] = {
            "exam_type": "AWS-SAP",
            "question_count": 1,
        }

        # エージェントモックの設定
        mock_result = AgentOutput(
            questions=[
                Question(
                    question="Memory失敗テスト問題",
                    options=["A", "B", "C", "D"],
                    correct_answer="A",
                    explanation="解説",
                    source=["https://docs.aws.amazon.com/test/"],
                    learning_domain="テスト分野",
                    primary_technologies=["テスト技術"],
                    learning_insights="テスト学習ポイント",
                )
            ]
        )
        mock_agent.structured_output.return_value = mock_result

        # Memory クライアントモック（失敗）の設定
        mock_memory_client.record_domain_usage = AsyncMock(
            side_effect=Exception("Memory記録失敗")
        )

        # Teamsクライアントモックの設定
        mock_teams_client = MagicMock()
        mock_teams_client.send = AsyncMock(return_value=None)
        mock_teams_client_class.return_value = mock_teams_client

        # When - invoke関数を実行
        result = await invoke(valid_payload)

        # Then - 事後条件検証: 問題生成は成功
        assert "questions" in result
        assert "error" not in result

        # 不変条件検証: Memory記録失敗でも処理継続
        assert isinstance(result["questions"], list)
        assert len(result["questions"]) == 1
        mock_memory_client.record_domain_usage.assert_called_once()

    @patch("app.agentcore.agent_main.memory_client", None)
    @patch.dict(
        "os.environ",
        {
            "POWER_AUTOMATE_WEBHOOK_URL": "https://test.webhook.url",
            "POWER_AUTOMATE_SECURITY_TOKEN": "test-security-token",
        },
    )
    @patch("app.agentcore.agent_main.TeamsClient")
    @patch("app.agentcore.agent_main.agent")
    async def test_memory_client_disabled_contract(
        self,
        mock_agent: MagicMock,
        mock_teams_client_class: MagicMock,
    ) -> None:
        """
        契約による設計: Memoryクライアント無効時の処理検証

        Given: 有効なペイロードとMemoryクライアント無効環境
        When: invoke関数を実行する
        Then: 問題生成は成功し、Memory記録はスキップされる

        事前条件: 有効なペイロード、Memoryクライアント無効
        事後条件: 問題生成は成功、Memory記録はスキップ
        不変条件: Memoryクライアント無効でも処理は正常に動作
        """
        # Given - 事前条件設定
        valid_payload: dict[str, Any] = {
            "exam_type": "AWS-SAP",
            "question_count": 1,
        }

        # エージェントモックの設定
        mock_result = AgentOutput(
            questions=[
                Question(
                    question="Memory無効テスト問題",
                    options=["A", "B", "C", "D"],
                    correct_answer="A",
                    explanation="解説",
                    source=["https://docs.aws.amazon.com/test/"],
                    learning_domain="テスト分野",
                    primary_technologies=["テスト技術"],
                    learning_insights="テスト学習ポイント",
                )
            ]
        )
        mock_agent.structured_output.return_value = mock_result

        # Teamsクライアントモックの設定
        mock_teams_client = MagicMock()
        mock_teams_client.send = AsyncMock(return_value=None)
        mock_teams_client_class.return_value = mock_teams_client

        # When - invoke関数を実行
        result = await invoke(valid_payload)

        # Then - 事後条件検証: 問題生成は成功
        assert "questions" in result
        assert "error" not in result

        # 不変条件検証: Memoryクライアント無効でも正常動作
        assert isinstance(result["questions"], list)
        assert len(result["questions"]) == 1

    @patch.dict(
        "os.environ",
        {
            "POWER_AUTOMATE_WEBHOOK_URL": "https://test.webhook.url",
            "POWER_AUTOMATE_SECURITY_TOKEN": "test-security-token",
        },
    )
    @patch("app.agentcore.agent_main.memory_client")
    @patch("app.agentcore.agent_main.TeamsClient")
    @patch("app.agentcore.agent_main.agent")
    async def test_recent_domains_retrieval_contract(
        self,
        mock_agent: MagicMock,
        mock_teams_client_class: MagicMock,
        mock_memory_client: MagicMock,
    ) -> None:
        """
        契約による設計: 最近の分野取得機能の検証

        Given: 有効なペイロードと最近の分野履歴があるMemoryクライアント
        When: invoke関数を実行する
        Then: 最近の分野が取得され、ジャンル分散指示がプロンプトに含まれる

        事前条件: 有効なペイロード、最近の分野履歴がある
        事後条件: 最近の分野が取得され、ジャンル分散指示がプロンプトに含まれる
        不変条件: 分野取得失敗でも処理は継続される
        """
        # Given - 事前条件設定
        valid_payload: dict[str, Any] = {
            "exam_type": "AWS-SAP",
            "question_count": 1,
        }

        # Memory クライアントモックの設定（最近の分野あり）
        mock_memory_client.get_recent_domains = AsyncMock(
            return_value=["コンピューティング", "ストレージ"]
        )
        mock_memory_client.record_domain_usage = AsyncMock(return_value=None)

        # エージェントモックの設定
        mock_result = AgentOutput(
            questions=[
                Question(
                    question="ネットワーキングに関する問題",
                    options=["A", "B", "C", "D"],
                    correct_answer="A",
                    explanation="解説",
                    source=["https://docs.aws.amazon.com/test/"],
                    learning_domain="ネットワーキング",  # 異なる分野
                    primary_technologies=["VPC", "Route53"],
                    learning_insights="ネットワーキング学習ポイント",
                )
            ]
        )
        mock_agent.structured_output.return_value = mock_result

        # Teamsクライアントモックの設定
        mock_teams_client = MagicMock()
        mock_teams_client.send = AsyncMock(return_value=None)
        mock_teams_client_class.return_value = mock_teams_client

        # When - invoke関数を実行
        result = await invoke(valid_payload)

        # Then - 事後条件検証: 問題生成が成功
        assert "questions" in result
        assert "error" not in result

        # 不変条件検証: 最近の分野取得が呼び出される
        mock_memory_client.get_recent_domains.assert_called_once_with(
            exam_type="AWS-SAP"
        )

        # プロンプトにジャンル分散指示が含まれることを確認
        call_args = mock_agent.structured_output.call_args
        prompt_arg = call_args.kwargs["prompt"]
        assert "ジャンル分散指示" in prompt_arg
        assert "コンピューティング" in prompt_arg
        assert "ストレージ" in prompt_arg
        assert "使用頻度の低い分野を優先して問題を生成してください" in prompt_arg

    @patch.dict(
        "os.environ",
        {
            "POWER_AUTOMATE_WEBHOOK_URL": "https://test.webhook.url",
            "POWER_AUTOMATE_SECURITY_TOKEN": "test-security-token",
        },
    )
    @patch("app.agentcore.agent_main.memory_client")
    @patch("app.agentcore.agent_main.TeamsClient")
    @patch("app.agentcore.agent_main.agent")
    async def test_recent_domains_retrieval_failure_contract(
        self,
        mock_agent: MagicMock,
        mock_teams_client_class: MagicMock,
        mock_memory_client: MagicMock,
    ) -> None:
        """
        契約による設計: 最近の分野取得失敗時の処理検証

        Given: 有効なペイロードと分野取得失敗環境
        When: invoke関数を実行する
        Then: 問題生成は成功し、分野取得失敗がログに記録される

        事前条件: 有効なペイロード、分野取得失敗
        事後条件: 問題生成は成功、分野取得失敗はログに記録
        不変条件: 分野取得失敗でも処理は継続される
        """
        # Given - 事前条件設定
        valid_payload: dict[str, Any] = {
            "exam_type": "AWS-SAP",
            "question_count": 1,
        }

        # Memory クライアントモック（分野取得失敗）の設定
        mock_memory_client.get_recent_domains = AsyncMock(
            side_effect=Exception("分野取得失敗")
        )
        mock_memory_client.record_domain_usage = AsyncMock(return_value=None)

        # エージェントモックの設定
        mock_result = AgentOutput(
            questions=[
                Question(
                    question="分野取得失敗テスト問題",
                    options=["A", "B", "C", "D"],
                    correct_answer="A",
                    explanation="解説",
                    source=["https://docs.aws.amazon.com/test/"],
                    learning_domain="テスト分野",
                    primary_technologies=["テスト技術"],
                    learning_insights="テスト学習ポイント",
                )
            ]
        )
        mock_agent.structured_output.return_value = mock_result

        # Teamsクライアントモックの設定
        mock_teams_client = MagicMock()
        mock_teams_client.send = AsyncMock(return_value=None)
        mock_teams_client_class.return_value = mock_teams_client

        # When - invoke関数を実行
        result = await invoke(valid_payload)

        # Then - 事後条件検証: 問題生成は成功
        assert "questions" in result
        assert "error" not in result

        # 不変条件検証: 分野取得失敗でも処理継続
        mock_memory_client.get_recent_domains.assert_called_once()
        assert isinstance(result["questions"], list)
        assert len(result["questions"]) == 1

        # プロンプトにジャンル分散指示が含まれないことを確認
        call_args = mock_agent.structured_output.call_args
        prompt_arg = call_args.kwargs["prompt"]
        assert "ジャンル分散指示" not in prompt_arg

    @patch.dict(
        "os.environ",
        {
            "POWER_AUTOMATE_WEBHOOK_URL": "https://test.webhook.url",
            "POWER_AUTOMATE_SECURITY_TOKEN": "test-security-token",
        },
    )
    @patch("app.agentcore.agent_main.memory_client")
    @patch("app.agentcore.agent_main.TeamsClient")
    @patch("app.agentcore.agent_main.agent")
    async def test_no_recent_domains_contract(
        self,
        mock_agent: MagicMock,
        mock_teams_client_class: MagicMock,
        mock_memory_client: MagicMock,
    ) -> None:
        """
        契約による設計: 最近の分野履歴なしの処理検証

        Given: 有効なペイロードと最近の分野履歴なし
        When: invoke関数を実行する
        Then: 問題生成は成功し、ジャンル分散指示は含まれない

        事前条件: 有効なペイロード、最近の分野履歴なし
        事後条件: 問題生成は成功、ジャンル分散指示は含まれない
        不変条件: 分野履歴なしでも正常に処理される
        """
        # Given - 事前条件設定
        valid_payload: dict[str, Any] = {
            "exam_type": "AWS-SAP",
            "question_count": 1,
        }

        # Memory クライアントモックの設定（最近の分野なし）
        mock_memory_client.get_recent_domains = AsyncMock(return_value=[])
        mock_memory_client.record_domain_usage = AsyncMock(return_value=None)

        # エージェントモックの設定
        mock_result = AgentOutput(
            questions=[
                Question(
                    question="分野履歴なしテスト問題",
                    options=["A", "B", "C", "D"],
                    correct_answer="A",
                    explanation="解説",
                    source=["https://docs.aws.amazon.com/test/"],
                    learning_domain="テスト分野",
                    primary_technologies=["テスト技術"],
                    learning_insights="テスト学習ポイント",
                )
            ]
        )
        mock_agent.structured_output.return_value = mock_result

        # Teamsクライアントモックの設定
        mock_teams_client = MagicMock()
        mock_teams_client.send = AsyncMock(return_value=None)
        mock_teams_client_class.return_value = mock_teams_client

        # When - invoke関数を実行
        result = await invoke(valid_payload)

        # Then - 事後条件検証: 問題生成は成功
        assert "questions" in result
        assert "error" not in result

        # 不変条件検証: 分野履歴なしでも正常処理
        mock_memory_client.get_recent_domains.assert_called_once()
        assert isinstance(result["questions"], list)
        assert len(result["questions"]) == 1

        # プロンプトにジャンル分散指示が含まれないことを確認
        call_args = mock_agent.structured_output.call_args
        prompt_arg = call_args.kwargs["prompt"]
        assert "ジャンル分散指示" not in prompt_arg
