"""
Lambda Trigger Function の単体テスト - 契約による設計（例外ベースアプローチ）

EventBridge SchedulerからAgentCore Runtimeを呼び出すLambda関数の
例外ベースアプローチに基づく契約検証テスト実装。

このテストモジュールは以下の契約を検証します：
- 事前条件: 必須パラメータ（agentRuntimeArn, exam_type, question_count）の存在
- 事後条件: 適切なHTTPステータスコードとレスポンス構造の返却
- 不変条件: エラー時も含めた一貫したレスポンス形式の維持
"""

import importlib
import json
from typing import Any
from unittest.mock import Mock, patch

import pytest

# テスト対象のインポート - pyproject.tomlの設定に従った統一的なアプローチ
# lambdaが予約語のため、importlibを使用してモジュールを動的にインポート
lambda_module = importlib.import_module("app.lambda.trigger.lambda_function")
lambda_handler = lambda_module.lambda_handler


class TestLambdaHandler:
    """
    Lambda関数の契約検証（例外ベースアプローチ）

    EventBridge SchedulerからのトリガーでAgentCore Runtimeを呼び出す
    Lambda関数の動作を契約による設計の観点から検証する。
    """

    def test_successful_invocation_contract(self) -> None:
        """
        契約による設計: 正常実行時の事後条件検証

        Given: 全ての必須パラメータを含む有効なイベント
        When: lambda_handler()を実行する
        Then: 成功レスポンス（200）と適切な構造のボディが返される

        事前条件:
        - agentRuntimeArn が有効なARN形式である
        - exam_type が文字列である
        - question_count が存在する

        事後条件:
        - statusCode が 200 である
        - body が有効なJSON文字列である
        - レスポンスに必要な情報が含まれる

        不変条件:
        - AgentCore Runtime が正確に1回呼び出される
        - レスポンス構造が一貫している
        """
        # Given - 事前条件設定: 全ての必須パラメータを含む有効なイベント
        valid_event: dict[str, Any] = {
            "agentRuntimeArn": "arn:aws:bedrock-agentcore:us-east-1:123456789012:runtime/test-agent-xyz",
            "exam_type": "SAP",
            "question_count": 1,
        }
        mock_context = Mock()
        mock_context.function_name = "test-lambda-function"
        mock_context.request_id = "test-request-id-12345"

        # When - lambda_handler()を実行（Bedrockクライアントをモック）
        with patch("boto3.client") as mock_boto_client:
            # Bedrockクライアントの正常レスポンスをモック
            mock_bedrock_client = Mock()
            mock_bedrock_client.invoke_agent_runtime.return_value = {
                "contentType": "application/json",
                "payload": b'{"status": "success"}',
            }
            mock_boto_client.return_value = mock_bedrock_client

            result = lambda_handler(valid_event, mock_context)

        # Then - 事後条件検証: 成功レスポンスと適切な構造
        assert result["statusCode"] == 200, "正常実行時は200ステータスコードを返すべき"

        # レスポンスボディの詳細検証
        body = json.loads(result["body"])
        assert body["message"] == "Question generation triggered successfully", (
            "成功メッセージが含まれるべき"
        )
        assert body["agentRuntimeArn"] == valid_event["agentRuntimeArn"], (
            "リクエストされたARNが含まれるべき"
        )

        # ペイロード情報の検証
        assert body["payload"]["exam_type"] == valid_event["exam_type"], (
            "exam_typeが正しく含まれるべき"
        )
        assert body["payload"]["question_count"] == valid_event["question_count"], (
            "question_countが正しく含まれるべき"
        )
        assert "responseContentType" in body, "レスポンスコンテンツタイプが含まれるべき"

        # 不変条件検証: AgentCore Runtime の正確な呼び出し
        mock_bedrock_client.invoke_agent_runtime.assert_called_once()
        call_args = mock_bedrock_client.invoke_agent_runtime.call_args

        # 呼び出しパラメータの詳細検証
        assert call_args.kwargs["agentRuntimeArn"] == valid_event["agentRuntimeArn"]
        assert call_args.kwargs["contentType"] == "application/json"
        assert call_args.kwargs["accept"] == "application/json"

        # ペイロードの検証
        payload = json.loads(call_args.kwargs["payload"].decode("utf-8"))
        assert payload["exam_type"] == valid_event["exam_type"]
        assert payload["question_count"] == valid_event["question_count"]

    def test_missing_agent_runtime_arn_precondition_violation(self) -> None:
        """
        契約による設計: agentRuntimeArn不足時の事前条件違反検証

        Given: agentRuntimeArnが不足したイベント
        When: lambda_handler()を実行する
        Then: バリデーションエラー（400）が返される

        事前条件違反: agentRuntimeArn が存在しない
        事後条件: 400ステータスコードとエラーメッセージが返される
        不変条件: AgentCore Runtime は呼び出されない
        """
        # Given - 事前条件違反: agentRuntimeArn が不足
        invalid_event: dict[str, Any] = {
            "exam_type": "SAP",
            "question_count": 1,
            # agentRuntimeArn が意図的に不足
        }
        mock_context = Mock()

        # When - lambda_handler()を実行
        result = lambda_handler(invalid_event, mock_context)

        # Then - 事後条件検証: バリデーションエラーレスポンス
        assert result["statusCode"] == 400, (
            "必須パラメータ不足時は400ステータスコードを返すべき"
        )

        body = json.loads(result["body"])
        assert body["error"] == "Validation error", "バリデーションエラーが示されるべき"
        assert "Missing required parameter: agentRuntimeArn" in body["message"], (
            "具体的な不足パラメータが示されるべき"
        )

        # 不変条件検証: エラー時のレスポンス構造一貫性
        assert "statusCode" in result, "レスポンスにはstatusCodeが含まれるべき"
        assert "body" in result, "レスポンスにはbodyが含まれるべき"
        assert isinstance(body, dict), "bodyは辞書形式であるべき"

    def test_missing_exam_type_precondition_violation(self) -> None:
        """
        契約による設計: exam_type不足時の事前条件違反検証

        Given: exam_typeが不足したイベント
        When: lambda_handler()を実行する
        Then: バリデーションエラー（400）が返される

        事前条件違反: exam_type が存在しない
        事後条件: 400ステータスコードとエラーメッセージが返される
        不変条件: AgentCore Runtime は呼び出されない
        """
        # Given - 事前条件違反: exam_type が不足
        invalid_event: dict[str, Any] = {
            "agentRuntimeArn": "arn:aws:bedrock-agentcore:us-east-1:123456789012:runtime/test-agent",
            "question_count": 1,
            # exam_type が意図的に不足
        }
        mock_context = Mock()

        # When - lambda_handler()を実行
        result = lambda_handler(invalid_event, mock_context)

        # Then - 事後条件検証: バリデーションエラーレスポンス
        assert result["statusCode"] == 400, (
            "必須パラメータ不足時は400ステータスコードを返すべき"
        )

        body = json.loads(result["body"])
        assert body["error"] == "Validation error", "バリデーションエラーが示されるべき"
        assert "Missing required parameter: exam_type" in body["message"], (
            "具体的な不足パラメータが示されるべき"
        )

    def test_missing_question_count_precondition_violation(self) -> None:
        """
        契約による設計: question_count不足時の事前条件違反検証

        Given: question_countが不足したイベント
        When: lambda_handler()を実行する
        Then: バリデーションエラー（400）が返される

        事前条件違反: question_count が存在しない
        事後条件: 400ステータスコードとエラーメッセージが返される
        不変条件: AgentCore Runtime は呼び出されない
        """
        # Given - 事前条件違反: question_count が不足
        invalid_event: dict[str, Any] = {
            "agentRuntimeArn": "arn:aws:bedrock-agentcore:us-east-1:123456789012:runtime/test-agent",
            "exam_type": "SAP",
            # question_count が意図的に不足
        }
        mock_context = Mock()

        # When - lambda_handler()を実行
        result = lambda_handler(invalid_event, mock_context)

        # Then - 事後条件検証: バリデーションエラーレスポンス
        assert result["statusCode"] == 400, (
            "必須パラメータ不足時は400ステータスコードを返すべき"
        )

        body = json.loads(result["body"])
        assert body["error"] == "Validation error", "バリデーションエラーが示されるべき"
        assert "Missing required parameter: question_count" in body["message"], (
            "具体的な不足パラメータが示されるべき"
        )

    def test_bedrock_service_error_exception_handling(self) -> None:
        """
        契約による設計: Bedrockサービスエラー時の例外処理検証

        Given: 有効なイベントとBedrockサービスエラー環境
        When: lambda_handler()を実行する
        Then: 内部サーバーエラー（500）が返される

        事前条件: 有効なイベントパラメータ
        例外条件: Bedrockサービスでエラーが発生
        事後条件: 500ステータスコードとエラーメッセージが返される
        不変条件: エラー時も一貫したレスポンス構造を維持
        """
        # Given - 事前条件設定: 有効なイベント
        valid_event: dict[str, Any] = {
            "agentRuntimeArn": "arn:aws:bedrock-agentcore:us-east-1:123456789012:runtime/test-agent",
            "exam_type": "SAP",
            "question_count": 1,
        }
        mock_context = Mock()

        # When - Bedrockサービスエラーが発生する環境でlambda_handler()を実行
        with patch("boto3.client") as mock_boto_client:
            mock_bedrock_client = Mock()
            # Bedrockサービスエラーをシミュレート
            mock_bedrock_client.invoke_agent_runtime.side_effect = Exception(
                "Bedrock service unavailable"
            )
            mock_boto_client.return_value = mock_bedrock_client

            result = lambda_handler(valid_event, mock_context)

        # Then - 事後条件検証: 内部サーバーエラーレスポンス
        assert result["statusCode"] == 500, (
            "サービスエラー時は500ステータスコードを返すべき"
        )

        body = json.loads(result["body"])
        assert body["error"] == "Internal server error", (
            "内部サーバーエラーが示されるべき"
        )
        assert "Bedrock service unavailable" in body["message"], (
            "具体的なエラーメッセージが含まれるべき"
        )

        # 不変条件検証: エラー時のレスポンス構造一貫性
        assert "statusCode" in result, "エラー時もstatusCodeが含まれるべき"
        assert "body" in result, "エラー時もbodyが含まれるべき"
        assert isinstance(body, dict), "エラー時もbodyは辞書形式であるべき"

    def test_payload_construction_contract(self) -> None:
        """
        契約による設計: ペイロード構築の正確性検証

        Given: 特定の値を持つイベントパラメータ
        When: lambda_handler()を実行する
        Then: AgentCoreに正確なペイロードが送信される

        事前条件: 有効なイベントパラメータ
        事後条件: 正確なペイロードでAgentCoreが呼び出される
        不変条件: ペイロード構造とエンコーディングの一貫性
        """
        # Given - 事前条件設定: 特定の値を持つイベント
        event_with_specific_values: dict[str, Any] = {
            "agentRuntimeArn": "arn:aws:bedrock-agentcore:us-east-1:987654321098:runtime/production-agent",
            "exam_type": "SAA",  # Solutions Architect Associate
            "question_count": 3,
        }
        mock_context = Mock()

        # When - lambda_handler()を実行
        with patch("boto3.client") as mock_boto_client:
            mock_bedrock_client = Mock()
            mock_bedrock_client.invoke_agent_runtime.return_value = {
                "contentType": "application/json"
            }
            mock_boto_client.return_value = mock_bedrock_client

            lambda_handler(event_with_specific_values, mock_context)

        # Then - 事後条件検証: 正確なペイロード構築
        call_args = mock_bedrock_client.invoke_agent_runtime.call_args

        # ARNの正確性検証
        assert (
            call_args.kwargs["agentRuntimeArn"]
            == event_with_specific_values["agentRuntimeArn"]
        ), "AgentCore ARNが正確に渡されるべき"

        # ペイロードの詳細検証
        payload_bytes = call_args.kwargs["payload"]
        assert isinstance(payload_bytes, bytes), "ペイロードはbytes形式であるべき"

        payload = json.loads(payload_bytes.decode("utf-8"))
        assert payload["exam_type"] == event_with_specific_values["exam_type"], (
            "exam_typeが正確にペイロードに含まれるべき"
        )
        assert (
            payload["question_count"] == event_with_specific_values["question_count"]
        ), "question_countが正確にペイロードに含まれるべき"

        # コンテンツタイプの検証
        assert call_args.kwargs["contentType"] == "application/json", (
            "コンテンツタイプはapplication/jsonであるべき"
        )
        assert call_args.kwargs["accept"] == "application/json", (
            "Acceptヘッダーはapplication/jsonであるべき"
        )

        # 不変条件検証: ペイロード構造の一貫性
        assert len(payload) == 2, "ペイロードには正確に2つのフィールドが含まれるべき"
        assert all(key in payload for key in ["exam_type", "question_count"]), (
            "ペイロードには必要なフィールドが全て含まれるべき"
        )

    def test_logging_behavior_contract(self) -> None:
        """
        契約による設計: ログ出力動作の検証

        Given: 有効なイベントとモックされたロガー
        When: lambda_handler()を実行する
        Then: 適切なログメッセージが出力される

        事前条件: 有効なイベントパラメータ
        事後条件: 実行フローに応じた適切なログが出力される
        不変条件: ログレベルと内容の一貫性
        """
        # Given - 事前条件設定: 有効なイベント
        event: dict[str, Any] = {
            "agentRuntimeArn": "arn:aws:bedrock-agentcore:us-east-1:123456789012:runtime/test-agent",
            "exam_type": "SAP",
            "question_count": 1,
        }
        mock_context = Mock()

        # When - ログをキャプチャしながらlambda_handler()を実行
        with (
            patch("boto3.client") as mock_boto_client,
            patch("app.lambda.trigger.lambda_function.logger") as mock_logger,
        ):
            mock_bedrock_client = Mock()
            mock_bedrock_client.invoke_agent_runtime.return_value = {
                "contentType": "application/json"
            }
            mock_boto_client.return_value = mock_bedrock_client

            lambda_handler(event, mock_context)

        # Then - 事後条件検証: 適切なログ出力
        # イベント受信ログの検証
        mock_logger.info.assert_any_call(f"Received event: {json.dumps(event)}")

        # boto3バージョンログの検証
        version_log_calls = [
            call
            for call in mock_logger.info.call_args_list
            if "boto3 version:" in str(call)
        ]
        assert len(version_log_calls) > 0, "boto3バージョンがログ出力されるべき"

        # AgentCore呼び出しログの検証
        mock_logger.info.assert_any_call(
            f"Invoking AgentCore Runtime: {event['agentRuntimeArn']}"
        )

        # ペイロードログの検証
        expected_payload = {
            "exam_type": event["exam_type"],
            "question_count": event["question_count"],
        }
        mock_logger.info.assert_any_call(f"Payload: {json.dumps(expected_payload)}")

        # 成功ログの検証
        mock_logger.info.assert_any_call("AgentCore invocation successful")

    def test_response_structure_invariant(self) -> None:
        """
        契約による設計: レスポンス構造の不変条件検証

        Given: 様々なシナリオ（成功・失敗）のイベント
        When: 各シナリオでlambda_handler()を実行する
        Then: 全てのケースで一貫したレスポンス構造が返される

        不変条件:
        - レスポンスには必ずstatusCodeとbodyが含まれる
        - bodyは有効なJSON文字列である
        - エラー時も成功時も構造が一貫している
        """
        # Given - 様々なシナリオの定義
        test_scenarios = [
            {
                "name": "成功ケース",
                "event": {
                    "agentRuntimeArn": "arn:aws:bedrock-agentcore:us-east-1:123456789012:runtime/test",
                    "exam_type": "SAP",
                    "question_count": 1,
                },
                "expected_status": 200,
                "mock_bedrock": True,
            },
            {
                "name": "agentRuntimeArn不足ケース",
                "event": {"exam_type": "SAP", "question_count": 1},
                "expected_status": 400,
                "mock_bedrock": False,
            },
            {
                "name": "exam_type不足ケース",
                "event": {
                    "agentRuntimeArn": "arn:aws:bedrock-agentcore:us-east-1:123456789012:runtime/test",
                    "question_count": 1,
                },
                "expected_status": 400,
                "mock_bedrock": False,
            },
            {
                "name": "空のイベントケース",
                "event": {},
                "expected_status": 400,
                "mock_bedrock": False,
            },
        ]

        # When & Then - 各シナリオでレスポンス構造を検証
        for scenario in test_scenarios:
            with patch("boto3.client") as mock_boto_client:
                if scenario["mock_bedrock"]:
                    mock_bedrock_client = Mock()
                    mock_bedrock_client.invoke_agent_runtime.return_value = {
                        "contentType": "application/json"
                    }
                    mock_boto_client.return_value = mock_bedrock_client

                result = lambda_handler(scenario["event"], Mock())

                # 不変条件検証: レスポンス構造の一貫性
                assert "statusCode" in result, (
                    f"{scenario['name']}: statusCodeが含まれるべき"
                )
                assert "body" in result, f"{scenario['name']}: bodyが含まれるべき"
                assert result["statusCode"] == scenario["expected_status"], (
                    f"{scenario['name']}: 期待されるステータスコードが返されるべき"
                )

                # bodyの有効性検証
                try:
                    body = json.loads(result["body"])
                    assert isinstance(body, dict), (
                        f"{scenario['name']}: bodyは辞書形式であるべき"
                    )
                except json.JSONDecodeError:
                    pytest.fail(f"{scenario['name']}: bodyは有効なJSON文字列であるべき")

    def test_empty_event_edge_case(self) -> None:
        """
        契約による設計: 空イベント処理のエッジケース検証

        Given: 完全に空のイベント
        When: lambda_handler()を実行する
        Then: 最初の必須パラメータ不足エラーが返される

        エッジケース: 全パラメータが不足した状況
        事後条件: 適切なエラーハンドリングが行われる
        不変条件: エラー時も一貫したレスポンス構造
        """
        # Given - エッジケース: 完全に空のイベント
        empty_event: dict[str, Any] = {}
        mock_context = Mock()

        # When - lambda_handler()を実行
        result = lambda_handler(empty_event, mock_context)

        # Then - 事後条件検証: 適切なエラーハンドリング
        assert result["statusCode"] == 400, (
            "空イベント時は400ステータスコードを返すべき"
        )

        body = json.loads(result["body"])
        assert body["error"] == "Validation error", "バリデーションエラーが示されるべき"
        # 最初にチェックされる必須パラメータのエラーが返される
        assert "Missing required parameter: agentRuntimeArn" in body["message"], (
            "最初の必須パラメータ不足エラーが返されるべき"
        )

        # 不変条件検証: エラー時のレスポンス構造一貫性
        assert isinstance(body, dict), "エラー時もbodyは辞書形式であるべき"
        assert "error" in body, "エラー時はerrorフィールドが含まれるべき"
        assert "message" in body, "エラー時はmessageフィールドが含まれるべき"

    def test_parameter_type_flexibility_contract(self) -> None:
        """
        契約による設計: パラメータ型の柔軟性検証

        Given: 異なる型のパラメータを含むイベント
        When: lambda_handler()を実行する
        Then: 型変換やシリアライゼーションが適切に処理される

        事前条件: 必須パラメータが存在する（型は問わない）
        事後条件: JSON シリアライゼーション可能な形で処理される
        不変条件: 元の値が保持される
        """
        # Given - 事前条件設定: 異なる型のパラメータを含むイベント
        mixed_type_event: dict[str, Any] = {
            "agentRuntimeArn": "arn:aws:bedrock-agentcore:us-east-1:123456789012:runtime/test",
            "exam_type": "SAP",
            "question_count": "2",  # 文字列として渡される数値
        }
        mock_context = Mock()

        # When - lambda_handler()を実行
        with patch("boto3.client") as mock_boto_client:
            mock_bedrock_client = Mock()
            mock_bedrock_client.invoke_agent_runtime.return_value = {
                "contentType": "application/json"
            }
            mock_boto_client.return_value = mock_bedrock_client

            result = lambda_handler(mixed_type_event, mock_context)

        # Then - 事後条件検証: 型の柔軟な処理
        assert result["statusCode"] == 200, (
            "型が異なっても必須パラメータがあれば成功すべき"
        )

        body = json.loads(result["body"])
        # 元の値が保持されることを確認
        assert body["payload"]["question_count"] == "2", "元の文字列値が保持されるべき"

        # AgentCoreへのペイロードでも元の値が保持されることを確認
        call_args = mock_bedrock_client.invoke_agent_runtime.call_args
        payload = json.loads(call_args.kwargs["payload"].decode("utf-8"))
        assert payload["question_count"] == "2", (
            "AgentCoreペイロードでも元の値が保持されるべき"
        )

        # 不変条件検証: JSON シリアライゼーション可能性
        assert isinstance(result["body"], str), "レスポンスbodyは文字列であるべき"
        # 再度パースして確認
        reparsed_body = json.loads(result["body"])
        assert reparsed_body == body, "レスポンスは再パース可能であるべき"
