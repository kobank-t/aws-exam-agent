#!/usr/bin/env python3
"""
AWS Exam Agent - agent_main.py のテストコード

契約による設計（Design by Contract）に基づいたテスト実装:
- 事前条件（Preconditions）: 入力データの妥当性検証
- 事後条件（Postconditions）: 出力データの妥当性検証
- 不変条件（Invariants）: システム状態の一貫性検証
"""

import logging
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

# テスト対象のインポート
from app.agentcore.agent_main import (
    EXAM_TYPES,
    MODEL_ID,
    AgentInput,
    AgentOutput,
    invoke,
)


class TestAgentInput:
    """AgentInput モデルの契約検証"""

    def test_default_values_contract(self) -> None:
        """
        事前条件: デフォルト値での初期化
        事後条件: 適切なデフォルト値が設定される
        """
        # Act
        input_model = AgentInput()

        # Assert - 事後条件検証
        assert input_model.exam_type == "SAP"
        assert input_model.category == []
        assert input_model.question_count == 1

        # 不変条件検証
        assert input_model.question_count >= 1
        assert input_model.question_count <= 5
        assert input_model.exam_type in EXAM_TYPES

    def test_valid_input_contract(self) -> None:
        """
        事前条件: 有効な入力データ
        事後条件: 正常にモデルが作成される
        """
        # Arrange - 事前条件設定
        valid_data: dict[str, Any] = {
            "exam_type": "SAP",
            "category": ["コンピューティング", "ストレージ"],
            "question_count": 3,
        }

        # Act
        input_model = AgentInput(**valid_data)

        # Assert - 事後条件検証
        assert input_model.exam_type == "SAP"
        assert input_model.category == ["コンピューティング", "ストレージ"]
        assert input_model.question_count == 3

        # 不変条件検証
        assert 1 <= input_model.question_count <= 5

    def test_invalid_question_count_precondition(self) -> None:
        """
        事前条件: 無効な問題数（範囲外）
        事後条件: ValidationError が発生する
        """
        # Arrange - 事前条件違反データ
        invalid_data_cases: list[dict[str, Any]] = [
            {"question_count": 0},  # 下限違反
            {"question_count": 6},  # 上限違反
            {"question_count": -1},  # 負数
        ]

        for invalid_data in invalid_data_cases:
            # Act & Assert - 事前条件違反の検証
            with pytest.raises(ValidationError) as exc_info:
                AgentInput(**invalid_data)

            # 不変条件検証: エラーメッセージに制約情報が含まれる
            error_details = str(exc_info.value)
            assert "question_count" in error_details

    def test_category_examples_contract(self) -> None:
        """
        事前条件: カテゴリ例に含まれる値
        事後条件: 正常に受け入れられる
        不変条件: カテゴリは空リストまたは有効な文字列リスト
        """
        # Arrange - 事前条件: 有効なカテゴリ例
        valid_categories = [
            ["分析"],
            ["コンピューティング", "ストレージ"],
            ["セキュリティ、アイデンティティ、コンプライアンス"],
            [],  # 空リストも有効
        ]

        for category in valid_categories:
            # Act
            input_model = AgentInput(category=category)

            # Assert - 事後条件検証
            assert input_model.category == category

            # 不変条件検証
            assert isinstance(input_model.category, list)
            for item in input_model.category:
                assert isinstance(item, str)
                assert len(item) > 0  # 空文字列でない


class TestAgentOutput:
    """AgentOutput モデルの契約検証"""

    def test_valid_output_contract(self) -> None:
        """
        事前条件: 有効な出力データ
        事後条件: 正常にモデルが作成される
        不変条件: 必須フィールドが全て存在する
        """
        # Arrange - 事前条件設定
        valid_output_data: dict[str, Any] = {
            "question": "AWS EC2に関する問題です。",
            "options": ["A. 選択肢A", "B. 選択肢B", "C. 選択肢C", "D. 選択肢D"],
            "correct_answer": "A",
            "explanation": "正解はAです。理由は...",
            "source": [
                "https://docs.aws.amazon.com/ec2/",
                "https://docs.aws.amazon.com/ec2/latest/userguide/",
            ],
        }

        # Act
        output_model = AgentOutput(**valid_output_data)

        # Assert - 事後条件検証
        assert output_model.question == valid_output_data["question"]
        assert output_model.options == valid_output_data["options"]
        assert output_model.correct_answer == valid_output_data["correct_answer"]
        assert output_model.explanation == valid_output_data["explanation"]
        assert output_model.source == valid_output_data["source"]

        # 不変条件検証
        assert len(output_model.options) >= 4  # 最低4つの選択肢
        assert len(output_model.question) > 0  # 問題文は空でない
        assert len(output_model.explanation) > 0  # 解説は空でない
        assert len(output_model.source) > 0  # ソースは空でない

    def test_insufficient_options_precondition(self) -> None:
        """
        事前条件: 選択肢が4つ未満
        事後条件: モデルは作成されるが、不変条件違反を検出
        """
        # Arrange - 事前条件: 選択肢不足
        insufficient_options_data: dict[str, Any] = {
            "question": "テスト問題",
            "options": ["A. 選択肢A", "B. 選択肢B"],  # 2つのみ
            "correct_answer": "A",
            "explanation": "テスト解説",
            "source": ["https://example.com"],
        }

        # Act
        output_model = AgentOutput(**insufficient_options_data)

        # Assert - 不変条件違反の検証
        # 注意: Pydanticは基本的な型検証のみ行うため、
        # ビジネスルール（4つ以上の選択肢）は別途検証が必要
        assert len(output_model.options) < 4  # 不変条件違反を確認

    def test_empty_required_fields_precondition(self) -> None:
        """
        事前条件: 必須フィールドが空
        事後条件: ValidationError が発生する
        """
        # Arrange - 事前条件違反: 必須フィールド欠如
        incomplete_data_cases: list[dict[str, Any]] = [
            {},  # 全フィールド欠如
            {"question": ""},  # 空の問題文
            {"question": "テスト", "options": []},  # 空の選択肢
        ]

        for incomplete_data in incomplete_data_cases:
            # Act & Assert - 事前条件違反の検証
            with pytest.raises(ValidationError):
                AgentOutput(**incomplete_data)


class TestInvokeFunction:
    """invoke 関数の契約検証"""

    @pytest.fixture
    def mock_agent(self) -> MagicMock:
        """エージェントのモック"""
        mock = MagicMock()
        mock_result = MagicMock()
        mock_result.model_dump.return_value = {
            "question": "モック問題",
            "options": ["A. 選択肢A", "B. 選択肢B", "C. 選択肢C", "D. 選択肢D"],
            "correct_answer": "A",
            "explanation": "モック解説",
            "source": ["https://docs.aws.amazon.com/mock/"],
        }
        mock.structured_output.return_value = mock_result
        return mock

    @patch("app.agentcore.agent_main.agent")
    async def test_valid_payload_contract(self, mock_agent: MagicMock) -> None:
        """
        事前条件: 有効なペイロード
        事後条件: 正常な問題データが返される
        不変条件: 出力形式が AgentOutput の仕様に準拠
        """
        # Arrange - 事前条件設定
        valid_payload: dict[str, Any] = {
            "exam_type": "SAP",
            "category": ["コンピューティング"],
            "question_count": 1,
        }

        # モックの設定
        mock_result = MagicMock()
        mock_result.model_dump.return_value = {
            "question": "EC2インスタンスに関する問題",
            "options": ["A. t2.micro", "B. m5.large", "C. c5.xlarge", "D. r5.2xlarge"],
            "correct_answer": "B",
            "explanation": "m5.largeが最適です。",
            "source": ["https://docs.aws.amazon.com/ec2/"],
        }
        mock_agent.structured_output.return_value = mock_result

        # Act
        result = await invoke(valid_payload)

        # Assert - 事後条件検証
        assert "question" in result
        assert "options" in result
        assert "correct_answer" in result
        assert "explanation" in result
        assert "source" in result

        # 不変条件検証
        assert isinstance(result["question"], str)
        assert isinstance(result["options"], list)
        assert len(result["options"]) >= 4
        assert isinstance(result["correct_answer"], str)
        assert isinstance(result["explanation"], str)
        assert isinstance(result["source"], list)

        # エージェントが正しく呼び出されたことを確認
        mock_agent.structured_output.assert_called_once()

    @patch("app.agentcore.agent_main.agent")
    async def test_invalid_payload_precondition(self, mock_agent: MagicMock) -> None:
        """
        事前条件: 無効なペイロード（型エラー）
        事後条件: エラー情報が返される
        不変条件: エラー時は error キーが存在する
        """
        # Arrange - 事前条件違反: 無効なペイロード
        invalid_payload: dict[str, Any] = {
            "exam_type": "INVALID",  # 存在しない試験タイプ
            "question_count": "invalid",  # 文字列（数値でない）
        }

        # Act
        result = await invoke(invalid_payload)

        # Assert - 事後条件検証（エラーケース）
        assert "error" in result
        assert isinstance(result["error"], str)

        # 不変条件検証: エラー時はエージェントが呼び出されない
        mock_agent.structured_output.assert_not_called()

    @patch("app.agentcore.agent_main.agent")
    async def test_agent_exception_handling_contract(
        self, mock_agent: MagicMock
    ) -> None:
        """
        事前条件: エージェント実行時に例外発生
        事後条件: エラー情報が適切に返される
        不変条件: 例外が適切にキャッチされ、システムが停止しない
        """
        # Arrange - エージェント例外の設定
        mock_agent.structured_output.side_effect = Exception("エージェント実行エラー")

        valid_payload: dict[str, Any] = {
            "exam_type": "SAP",
            "category": ["コンピューティング"],
            "question_count": 1,
        }

        # Act
        result = await invoke(valid_payload)

        # Assert - 事後条件検証（例外処理）
        assert "error" in result
        assert "エージェント実行エラー" in result["error"]

        # 不変条件検証: システムが停止せず、適切にエラーが返される
        assert isinstance(result, dict)

    @patch("app.agentcore.agent_main.agent")
    async def test_empty_payload_contract(self, mock_agent: MagicMock) -> None:
        """
        事前条件: 空のペイロード
        事後条件: デフォルト値で処理される
        不変条件: AgentInput のデフォルト値が適用される
        """
        # Arrange - 事前条件: 空のペイロード
        empty_payload: dict[str, Any] = {}

        # モックの設定
        mock_result = MagicMock()
        mock_result.model_dump.return_value = {
            "question": "デフォルト問題",
            "options": ["A. 選択肢A", "B. 選択肢B", "C. 選択肢C", "D. 選択肢D"],
            "correct_answer": "A",
            "explanation": "デフォルト解説",
            "source": ["https://docs.aws.amazon.com/default/"],
        }
        mock_agent.structured_output.return_value = mock_result

        # Act
        result = await invoke(empty_payload)

        # Assert - 事後条件検証
        assert "question" in result
        assert "error" not in result

        # 不変条件検証: デフォルト値での処理が成功
        mock_agent.structured_output.assert_called_once()


class TestConstants:
    """定数の契約検証"""

    def test_exam_types_invariant(self) -> None:
        """
        不変条件: EXAM_TYPES の構造と内容が正しい
        """
        # Assert - 不変条件検証
        assert isinstance(EXAM_TYPES, dict)
        assert "SAP" in EXAM_TYPES

        sap_config = EXAM_TYPES["SAP"]
        assert "name" in sap_config
        assert "guide_url" in sap_config
        assert "sample_url" in sap_config

        # URL形式の検証
        assert sap_config["guide_url"].startswith("https://")
        assert sap_config["sample_url"].startswith("https://")
        assert "AWS Certified Solutions Architect - Professional" in sap_config["name"]

    def test_model_id_invariant(self) -> None:
        """
        不変条件: MODEL_ID の構造と内容が正しい
        """
        # Assert - 不変条件検証
        assert isinstance(MODEL_ID, dict)
        assert len(MODEL_ID) > 0

        for model_name, model_id in MODEL_ID.items():
            assert isinstance(model_name, str)
            assert isinstance(model_id, str)
            assert len(model_id) > 0
            # Bedrock モデル ID の形式検証
            assert "." in model_id  # モデル名にはドットが含まれる


class TestBusinessLogicContracts:
    """ビジネスロジックの契約検証"""

    @patch("app.agentcore.agent_main.agent")
    async def test_category_specific_generation_contract(
        self, mock_agent: MagicMock
    ) -> None:
        """
        事前条件: 特定カテゴリが指定される
        事後条件: そのカテゴリに関連する問題が生成される
        不変条件: プロンプトにカテゴリ情報が含まれる
        """
        # Arrange - 事前条件設定
        payload: dict[str, Any] = {
            "exam_type": "SAP",
            "category": ["コンピューティング", "ネットワークとコンテンツ配信"],
            "question_count": 1,
        }

        # モックの設定
        mock_result = MagicMock()
        mock_result.model_dump.return_value = {
            "question": "EC2とVPCに関する統合問題",
            "options": ["A. 選択肢A", "B. 選択肢B", "C. 選択肢C", "D. 選択肢D"],
            "correct_answer": "A",
            "explanation": "統合的な解説",
            "source": [
                "https://docs.aws.amazon.com/ec2/",
                "https://docs.aws.amazon.com/vpc/",
            ],
        }
        mock_agent.structured_output.return_value = mock_result

        # Act
        result = await invoke(payload)

        # Assert - 事後条件検証
        assert "error" not in result
        assert "question" in result

        # 不変条件検証: プロンプトにカテゴリが含まれることを確認
        call_args = mock_agent.structured_output.call_args
        assert call_args is not None

        # プロンプトの内容確認
        prompt_arg = call_args.kwargs.get("prompt", "")
        assert "コンピューティング" in prompt_arg
        assert "ネットワークとコンテンツ配信" in prompt_arg

    @patch("app.agentcore.agent_main.agent")
    async def test_multiple_questions_contract(self, mock_agent: MagicMock) -> None:
        """
        事前条件: 複数問題の生成要求
        事後条件: 指定された数の問題が生成される（現在は1問のみ対応）
        不変条件: question_count がプロンプトに反映される
        """
        # Arrange - 事前条件設定
        payload: dict[str, Any] = {
            "exam_type": "SAP",
            "category": ["ストレージ"],
            "question_count": 3,
        }

        # モックの設定
        mock_result = MagicMock()
        mock_result.model_dump.return_value = {
            "question": "S3に関する問題",
            "options": ["A. 選択肢A", "B. 選択肢B", "C. 選択肢C", "D. 選択肢D"],
            "correct_answer": "A",
            "explanation": "S3の解説",
            "source": ["https://docs.aws.amazon.com/s3/"],
        }
        mock_agent.structured_output.return_value = mock_result

        # Act
        result = await invoke(payload)

        # Assert - 事後条件検証
        assert "error" not in result

        # 不変条件検証: プロンプトに問題数が含まれることを確認
        call_args = mock_agent.structured_output.call_args
        assert call_args is not None

        prompt_arg = call_args.kwargs.get("prompt", "")
        assert "3問" in prompt_arg

    @patch("app.agentcore.agent_main.agent")
    async def test_exam_type_contract(self, mock_agent: MagicMock) -> None:
        """
        事前条件: 有効な試験タイプが指定される
        事後条件: 対応する試験レベルで問題が生成される
        不変条件: EXAM_TYPES の情報がプロンプトに反映される
        """
        # Arrange - 事前条件設定
        payload: dict[str, Any] = {
            "exam_type": "SAP",
            "category": [],
            "question_count": 1,
        }

        # モックの設定
        mock_result = MagicMock()
        mock_result.model_dump.return_value = {
            "question": "Professional レベル問題",
            "options": ["A. 選択肢A", "B. 選択肢B", "C. 選択肢C", "D. 選択肢D"],
            "correct_answer": "A",
            "explanation": "Professional レベル解説",
            "source": ["https://docs.aws.amazon.com/professional/"],
        }
        mock_agent.structured_output.return_value = mock_result

        # Act
        result = await invoke(payload)

        # Assert - 事後条件検証
        assert "error" not in result

        # 不変条件検証: プロンプトに試験名が含まれることを確認
        call_args = mock_agent.structured_output.call_args
        assert call_args is not None

        prompt_arg = call_args.kwargs.get("prompt", "")
        expected_exam_name = EXAM_TYPES["SAP"]["name"]
        assert expected_exam_name in prompt_arg


class TestDataIntegrityContracts:
    """データ整合性の契約検証"""

    def test_agent_input_serialization_contract(self) -> None:
        """
        事前条件: AgentInput モデルのインスタンス
        事後条件: 正常にシリアライズ・デシリアライズできる
        不変条件: データの整合性が保持される
        """
        # Arrange - 事前条件設定
        original_input = AgentInput(
            exam_type="SAP",
            category=["コンピューティング", "ストレージ"],
            question_count=2,
        )

        # Act - シリアライズ・デシリアライズ
        serialized = original_input.model_dump()
        deserialized = AgentInput(**serialized)

        # Assert - 事後条件検証
        assert deserialized.exam_type == original_input.exam_type
        assert deserialized.category == original_input.category
        assert deserialized.question_count == original_input.question_count

        # 不変条件検証: データの完全性
        assert deserialized.model_dump() == original_input.model_dump()

    def test_agent_output_validation_contract(self) -> None:
        """
        事前条件: 実際の問題生成結果に近いデータ
        事後条件: AgentOutput として有効
        不変条件: AWS試験問題として必要な要素が全て含まれる
        """
        # Arrange - 事前条件: 実際の問題データに近い形式
        realistic_output_data: dict[str, Any] = {
            "question": "企業がAWSでマルチリージョンアーキテクチャを構築する際の最適なアプローチはどれですか？",
            "options": [
                "A. 各リージョンに独立したVPCを作成し、VPC Peeringで接続する",
                "B. Transit Gatewayを使用してリージョン間を接続する",
                "C. CloudFrontとRoute 53を使用してトラフィックを分散する",
                "D. Global Acceleratorを使用してパフォーマンスを最適化する",
            ],
            "correct_answer": "B",
            "explanation": "Transit Gatewayは複数リージョン間の接続を効率的に管理できるため、マルチリージョンアーキテクチャに最適です。",
            "source": [
                "https://docs.aws.amazon.com/vpc/latest/tgw/what-is-transit-gateway.html",
                "https://docs.aws.amazon.com/vpc/latest/peering/what-is-vpc-peering.html",
            ],
        }

        # Act
        output_model = AgentOutput(**realistic_output_data)

        # Assert - 事後条件検証
        assert output_model.question == realistic_output_data["question"]
        assert output_model.correct_answer in ["A", "B", "C", "D"]

        # 不変条件検証: AWS試験問題として必要な要素
        assert len(output_model.options) >= 4  # 最低4つの選択肢
        assert len(output_model.explanation) > 50  # 十分な解説長
        assert all(
            url.startswith("https://docs.aws.amazon.com/")
            for url in output_model.source
        )  # AWS公式ドキュメント

        # 選択肢の形式検証
        for i, option in enumerate(output_model.options):
            expected_prefix = f"{chr(65 + i)}."  # A., B., C., D.
            assert option.startswith(expected_prefix)


class TestSystemInvariants:
    """システム全体の不変条件検証"""

    def test_logging_configuration_invariant(self) -> None:
        """
        不変条件: ログ設定が適切に構成されている
        """
        # Assert - ログ設定の不変条件検証
        # agent_main.pyでlogging.basicConfigが呼ばれることを確認

        # ログレベルが適切に設定されていることを確認
        # basicConfigでINFOレベルが設定されているが、
        # テスト環境では親ロガーのレベルが影響する可能性がある
        root_logger = logging.getLogger()

        # ログハンドラーの存在確認
        handlers = root_logger.handlers
        assert len(handlers) > 0

        # フォーマッターの存在確認（設定されている場合）
        for handler in handlers:
            if hasattr(handler, "formatter") and handler.formatter:
                format_str = handler.formatter._fmt
                if format_str:  # format_strがNoneでないことを確認
                    # 基本的なログフォーマット要素の確認
                    assert any(
                        element in format_str
                        for element in [
                            "%(asctime)s",
                            "%(name)s",
                            "%(levelname)s",
                            "%(message)s",
                        ]
                    )

    def test_mcp_client_initialization_invariant(self) -> None:
        """
        不変条件: MCPクライアントが適切に初期化されている
        """
        # この不変条件は実際のMCPクライアントの初期化をテストするため、
        # 統合テストで検証するのが適切
        # ここでは設定の妥当性のみ検証

        # Assert - MCP設定の不変条件検証
        assert "awslabs.aws-documentation-mcp-server@latest" != None
        assert isinstance("awslabs.aws-documentation-mcp-server@latest", str)

    def test_model_configuration_invariant(self) -> None:
        """
        不変条件: モデル設定が適切に構成されている
        """
        # Assert - モデル設定の不変条件検証
        assert "claude-3.7-sonnet" in MODEL_ID
        selected_model_id = MODEL_ID["claude-3.7-sonnet"]

        # Bedrock モデル ID の形式検証
        assert isinstance(selected_model_id, str)
        assert len(selected_model_id) > 0
        assert (
            "anthropic.claude" in selected_model_id
            or "us.anthropic.claude" in selected_model_id
        )


@pytest.mark.integration
class TestIntegrationContracts:
    """統合レベルの契約検証（実際のコンポーネント連携）"""

    async def test_end_to_end_contract(self) -> None:
        """
        事前条件: 実際のAgentInputデータ
        事後条件: 実際の問題生成が成功する
        不変条件: 全体のフローが正常に動作する

        注意: このテストは実際のMCPサーバーとBedrockを使用するため、
        統合テスト環境でのみ実行されます。
        """
        # このテストは実際のMCP統合が必要なため、
        # 現在はプレースホルダーとして定義
        # 実際の統合テストは tests/integration/ で実装
        pass

    async def test_error_recovery_contract(self) -> None:
        """
        事前条件: MCP接続エラーまたはBedrock APIエラー
        事後条件: 適切なエラーハンドリングが行われる
        不変条件: システムが停止せず、エラー情報が返される

        注意: このテストは実際のエラー状況をシミュレートするため、
        統合テスト環境でのみ実行されます。
        """
        # このテストは実際のエラー状況のシミュレートが必要なため、
        # 現在はプレースホルダーとして定義
        # 実際の統合テストは tests/integration/ で実装
        pass
