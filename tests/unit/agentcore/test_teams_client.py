"""
Teams クライアントの単体テスト - 契約による設計（例外ベースアプローチ）

AgentOutputをPower Automate Webhookに送信するTeamsClientの
例外ベースアプローチに基づく契約検証テスト実装。
"""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from dotenv import load_dotenv

from app.agentcore.agent_main import AgentOutput, Question
from app.agentcore.teams_client import TeamsClient

# .envファイルを読み込み
load_dotenv()


class TestTeamsClient:
    """TeamsClient の契約検証（例外ベースアプローチ）"""

    @patch.dict(
        "os.environ",
        {
            "POWER_AUTOMATE_WEBHOOK_URL": "https://test.webhook.url",
            "POWER_AUTOMATE_SECURITY_TOKEN": "test-security-token",
        },
    )
    def test_initialization_contract(self) -> None:
        """
        契約による設計: TeamsClientの環境変数初期化検証

        Given: 環境変数が設定された状態
        When: TeamsClientインスタンスを作成する
        Then: 環境変数の値が正しく設定される

        事前条件: 環境変数での初期化
        事後条件: 環境変数の値が正しく設定される
        不変条件: 設定値が正しく保持される
        """
        # Given - 環境変数が設定された状態（patch.dictで設定済み）
        timeout = 60

        # When - TeamsClientインスタンスを作成
        client = TeamsClient(timeout=timeout)

        # Then - 事後条件検証: 環境変数の値が正しく設定される
        assert client.webhook_url == "https://test.webhook.url"
        assert client.security_token == "test-security-token"
        assert client.timeout == timeout

        # 不変条件検証: 型制約と値の整合性
        assert isinstance(client.webhook_url, str)
        assert isinstance(client.security_token, str)
        assert isinstance(client.timeout, int)

    @patch.dict(
        "os.environ",
        {
            "POWER_AUTOMATE_WEBHOOK_URL": "https://test.webhook.url",
            "POWER_AUTOMATE_SECURITY_TOKEN": "test-security-token",
        },
    )
    @pytest.mark.asyncio
    async def test_successful_send_contract(self) -> None:
        """
        契約による設計: 正常送信の事後条件検証

        Given: 有効なAgentOutputと正常なHTTPレスポンス環境
        When: send()メソッドを実行する
        Then: 例外が発生せず正常に完了する

        事前条件: 有効なWebhookURL、セキュリティトークン、AgentOutput
        事後条件: 例外が発生せず正常に完了する
        不変条件: HTTPリクエストが正しく送信される
        """
        # Given - 事前条件設定
        client = TeamsClient()
        test_question = Question(
            question="テスト問題",
            options=["A. 選択肢1", "B. 選択肢2", "C. 選択肢3", "D. 選択肢4"],
            correct_answer="A",
            explanation="解説",
            source=["https://docs.aws.amazon.com/test/"],
            # 新機能: 試験ガイド活用による問題分類表示
            learning_domain="テスト分野",
            primary_technologies=["テスト技術"],
            learning_insights="テストガイド参照",
        )
        agent_output = AgentOutput(questions=[test_question])

        # HTTPクライアントをモック
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_response.raise_for_status.return_value = None

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )

            # When - 例外が発生しないことを確認
            await client.send(agent_output)

            # Then - 不変条件検証: HTTPリクエストが送信された
            mock_client.return_value.__aenter__.return_value.post.assert_called_once()

    @patch.dict(
        "os.environ",
        {
            "POWER_AUTOMATE_WEBHOOK_URL": "https://test.webhook.url",
            "POWER_AUTOMATE_SECURITY_TOKEN": "test-security-token",
        },
    )
    @pytest.mark.asyncio
    async def test_http_error_handling_contract(self) -> None:
        """
        契約による設計: HTTPエラー時の例外処理検証

        Given: HTTPエラーレスポンス環境
        When: send()メソッドを実行する
        Then: HTTPStatusError例外が発生する

        事前条件: HTTPエラーレスポンス
        事後条件: HTTPStatusError例外が発生する
        不変条件: 元の例外が再発生される
        """
        # Given - 事前条件設定
        client = TeamsClient()
        test_question = Question(
            question="エラーテスト問題",
            options=["A. 選択肢1", "B. 選択肢2"],
            correct_answer="A",
            explanation="解説",
            source=[],
            # 新機能: 試験ガイド活用による問題分類表示
            learning_domain="エラーテスト分野",
            primary_technologies=["エラーテスト技術"],
            learning_insights="エラーテストガイド参照",
        )
        agent_output = AgentOutput(questions=[test_question])

        # HTTPエラーをモック
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        http_error = httpx.HTTPStatusError(
            "HTTP Error", request=MagicMock(), response=mock_response
        )

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=http_error
            )

            # When & Then - 事後条件検証: HTTPStatusError例外が発生
            with pytest.raises(httpx.HTTPStatusError):
                await client.send(agent_output)

    @patch.dict(
        "os.environ",
        {
            "POWER_AUTOMATE_WEBHOOK_URL": "https://test.webhook.url",
            "POWER_AUTOMATE_SECURITY_TOKEN": "test-security-token",
        },
    )
    @pytest.mark.asyncio
    async def test_timeout_handling_contract(self) -> None:
        """
        契約による設計: タイムアウト時の例外処理検証

        Given: タイムアウト発生環境
        When: send()メソッドを実行する
        Then: TimeoutException例外が発生する

        事前条件: タイムアウト発生
        事後条件: TimeoutException例外が発生する
        不変条件: 元の例外が再発生される
        """
        # Given - 事前条件設定
        client = TeamsClient(timeout=1)
        test_question = Question(
            question="タイムアウトテスト問題",
            options=["A. 選択肢1", "B. 選択肢2"],
            correct_answer="A",
            explanation="解説",
            source=[],
            # 新機能: 試験ガイド活用による問題分類表示
            learning_domain="タイムアウトテスト分野",
            primary_technologies=["タイムアウトテスト技術"],
            learning_insights="タイムアウトテストガイド参照",
        )
        agent_output = AgentOutput(questions=[test_question])

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=httpx.TimeoutException("Timeout")
            )

            # When & Then - 事後条件検証: TimeoutException例外が発生
            with pytest.raises(httpx.TimeoutException):
                await client.send(agent_output)

    def test_missing_webhook_url_precondition(self) -> None:
        """
        契約による設計: 初期化時の事前条件検証

        Given: Webhook URLが設定されていない環境
        When: TeamsClientを初期化する
        Then: ValueError例外が発生する

        事前条件違反: POWER_AUTOMATE_WEBHOOK_URL が未設定
        事後条件: ValueError例外が発生し、適切なエラーメッセージが表示される
        不変条件: 初期化が失敗し、インスタンスが作成されない
        """
        # Given - 事前条件違反の環境設定
        with patch.dict("os.environ", {}, clear=True):
            # When & Then - 初期化時の事前条件検証
            with pytest.raises(
                ValueError, match="POWER_AUTOMATE_WEBHOOK_URL の設定が必須です"
            ):
                TeamsClient()

    def test_missing_security_token_precondition(self) -> None:
        """
        契約による設計: セキュリティトークン事前条件検証

        Given: WebhookURLは設定されているがセキュリティトークンが未設定の環境
        When: TeamsClientを初期化する
        Then: ValueError例外が発生する

        事前条件違反: POWER_AUTOMATE_SECURITY_TOKEN が未設定
        事後条件: ValueError例外が発生し、適切なエラーメッセージが表示される
        不変条件: 初期化が失敗し、インスタンスが作成されない
        """
        # Given - セキュリティトークンのみ未設定の環境
        with patch.dict(
            "os.environ",
            {"POWER_AUTOMATE_WEBHOOK_URL": "https://test.webhook.url"},
            clear=True,
        ):
            # When & Then - 初期化時の事前条件検証
            with pytest.raises(
                ValueError, match="POWER_AUTOMATE_SECURITY_TOKEN の設定が必須です"
            ):
                TeamsClient()

    def test_missing_both_configurations_precondition(self) -> None:
        """
        契約による設計: 両方の設定が未設定時の事前条件検証

        Given: WebhookURLとセキュリティトークンの両方が未設定の環境
        When: TeamsClientを初期化する
        Then: WebhookURLのエラーが優先して発生する

        事前条件違反: 両方の必須設定が未設定
        事後条件: WebhookURLのValueError例外が発生する（優先順位による）
        不変条件: 初期化が失敗し、インスタンスが作成されない
        """
        # Given - 両方とも未設定の環境
        with patch.dict("os.environ", {}, clear=True):
            # When & Then - WebhookURLが先にチェックされることを確認
            with pytest.raises(
                ValueError, match="POWER_AUTOMATE_WEBHOOK_URL の設定が必須です"
            ):
                TeamsClient()

    @patch.dict(
        "os.environ",
        {
            "POWER_AUTOMATE_WEBHOOK_URL": "https://test.webhook.url",
            "POWER_AUTOMATE_SECURITY_TOKEN": "test-security-token",
        },
    )
    @pytest.mark.asyncio
    async def test_unexpected_exception_handling_contract(self) -> None:
        """
        契約による設計: 予期しない例外時の処理検証

        Given: 予期しない例外発生環境
        When: send()メソッドを実行する
        Then: 元の例外が再発生される

        事前条件: 予期しない例外発生
        事後条件: 元の例外が再発生される
        不変条件: 例外情報が適切にログ出力される
        """
        # Given - 事前条件設定
        client = TeamsClient()
        test_question = Question(
            question="予期しないエラーテスト問題",
            options=["A. 選択肢1", "B. 選択肢2"],
            correct_answer="A",
            explanation="解説",
            source=[],
            # 新機能: 試験ガイド活用による問題分類表示
            learning_domain="予期しないエラーテスト分野",
            primary_technologies=["予期しないエラーテスト技術"],
            learning_insights="予期しないエラーテストガイド参照",
        )
        agent_output = AgentOutput(questions=[test_question])

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=RuntimeError("予期しないエラー")
            )

            # When & Then - 事後条件検証: RuntimeError例外が発生
            with pytest.raises(RuntimeError, match="予期しないエラー"):
                await client.send(agent_output)

    @patch.dict(
        "os.environ",
        {
            "POWER_AUTOMATE_WEBHOOK_URL": "https://test.webhook.url",
            "POWER_AUTOMATE_SECURITY_TOKEN": "test-security-token",
        },
    )
    @pytest.mark.asyncio
    async def test_payload_structure_contract(self) -> None:
        """
        契約による設計: ペイロード構造の包括的検証

        Given: 複数問題を含むAgentOutput
        When: send()メソッドを実行する
        Then: セキュリティトークン付きの正しいJSON形式で送信される

        事前条件: 複数問題を含むAgentOutput
        事後条件: セキュリティトークンが含まれたJSONペイロードが送信される
        不変条件: AgentOutputの構造が保持され、セキュリティトークンが追加される
        """
        # Given - 事前条件設定: 複数問題を含むAgentOutput
        client = TeamsClient()
        test_questions = [
            Question(
                question=f"テスト問題{i + 1}",
                options=["A. 選択肢1", "B. 選択肢2", "C. 選択肢3", "D. 選択肢4"],
                correct_answer="A",
                explanation=f"解説{i + 1}",
                source=[f"https://docs.aws.amazon.com/test{i + 1}/"],
                # 新機能: 試験ガイド活用による問題分類表示
                learning_domain=f"テスト分野{i + 1}",
                primary_technologies=[f"テスト技術{i + 1}"],
                learning_insights=f"テストガイド参照{i + 1}",
            )
            for i in range(2)
        ]
        agent_output = AgentOutput(questions=test_questions)

        # HTTPクライアントをモック
        mock_response = MagicMock()
        mock_response.status_code = 202
        captured_payload = None

        async def capture_post(*args: Any, **kwargs: Any) -> MagicMock:
            nonlocal captured_payload
            captured_payload = kwargs.get("json")
            return mock_response

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=capture_post
            )

            # When - ペイロード送信
            await client.send(agent_output)

            # Then - 事後条件検証: セキュリティトークンが含まれている
            assert captured_payload is not None
            assert "security_token" in captured_payload
            assert captured_payload["security_token"] == "test-security-token"

            # 不変条件検証: AgentOutputの構造が保持されている
            assert "questions" in captured_payload
            assert len(captured_payload["questions"]) == 2
            assert "テスト問題1" in str(captured_payload["questions"])
            assert "テスト問題2" in str(captured_payload["questions"])

            # 不変条件検証: JSONペイロードとして送信されている
            call_args = mock_client.return_value.__aenter__.return_value.post.call_args
            assert "json" in call_args.kwargs
            assert call_args.kwargs["json"] == captured_payload
