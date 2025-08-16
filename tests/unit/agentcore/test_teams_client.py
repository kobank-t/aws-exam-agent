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

    def test_initialization_with_parameters_contract(self) -> None:
        """
        事前条件: 明示的なパラメータでの初期化
        事後条件: 指定されたパラメータが設定される
        不変条件: 設定値が正しく保持される
        """
        # Arrange - 事前条件設定
        webhook_url = "https://test.webhook.url"
        timeout = 60

        # Act
        client = TeamsClient(webhook_url=webhook_url, timeout=timeout)

        # Assert - 事後条件検証
        assert client.webhook_url == webhook_url
        assert client.timeout == timeout

        # 不変条件検証
        assert isinstance(client.webhook_url, str)
        assert isinstance(client.timeout, int)

    @patch.dict("os.environ", {"POWER_AUTOMATE_WEBHOOK_URL": "https://env.webhook.url"})
    def test_initialization_with_environment_variables_contract(self) -> None:
        """
        事前条件: 環境変数での初期化
        事後条件: 環境変数の値が設定される
        不変条件: デフォルト値が適用される
        """
        # Act
        client = TeamsClient()

        # Assert - 事後条件検証
        assert client.webhook_url == "https://env.webhook.url"
        assert client.timeout == 30  # デフォルト値

        # 不変条件検証
        assert isinstance(client.webhook_url, str)
        assert isinstance(client.timeout, int)

    @pytest.mark.asyncio
    async def test_successful_send_contract(self) -> None:
        """
        事前条件: 有効なAgentOutputと正常なHTTPレスポンス
        事後条件: 例外が発生せず正常に完了する
        不変条件: HTTPリクエストが正しく送信される
        """
        # Arrange - 事前条件設定
        client = TeamsClient(webhook_url="https://test.webhook.url")
        test_question = Question(
            question="テスト問題",
            options=["A. 選択肢1", "B. 選択肢2", "C. 選択肢3", "D. 選択肢4"],
            correct_answer="A",
            explanation="解説",
            source=["https://docs.aws.amazon.com/test/"],
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

            # Act - 例外が発生しないことを確認
            await client.send(agent_output)

            # Assert - 不変条件検証: HTTPリクエストが送信された
            mock_client.return_value.__aenter__.return_value.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_http_error_handling_contract(self) -> None:
        """
        事前条件: HTTPエラーレスポンス
        事後条件: HTTPStatusError例外が発生する
        不変条件: 元の例外が再発生される
        """
        # Arrange - 事前条件設定
        client = TeamsClient(webhook_url="https://test.webhook.url")
        test_question = Question(
            question="エラーテスト問題",
            options=["A. 選択肢1", "B. 選択肢2"],
            correct_answer="A",
            explanation="解説",
            source=[],
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

            # Act & Assert - 事後条件検証: HTTPStatusError例外が発生
            with pytest.raises(httpx.HTTPStatusError):
                await client.send(agent_output)

    @pytest.mark.asyncio
    async def test_timeout_handling_contract(self) -> None:
        """
        事前条件: タイムアウト発生
        事後条件: TimeoutException例外が発生する
        不変条件: 元の例外が再発生される
        """
        # Arrange - 事前条件設定
        client = TeamsClient(webhook_url="https://test.webhook.url", timeout=1)
        test_question = Question(
            question="タイムアウトテスト問題",
            options=["A. 選択肢1", "B. 選択肢2"],
            correct_answer="A",
            explanation="解説",
            source=[],
        )
        agent_output = AgentOutput(questions=[test_question])

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=httpx.TimeoutException("Timeout")
            )

            # Act & Assert - 事後条件検証: TimeoutException例外が発生
            with pytest.raises(httpx.TimeoutException):
                await client.send(agent_output)

    @pytest.mark.asyncio
    async def test_missing_webhook_url_precondition(self) -> None:
        """
        事前条件違反: Webhook URLが設定されていない
        事後条件: ValueError例外が発生する
        """
        # Arrange - 事前条件違反
        with patch.dict("os.environ", {}, clear=True):
            client = TeamsClient()  # webhook_url=None
            test_question = Question(
                question="設定エラーテスト問題",
                options=["A. 選択肢1", "B. 選択肢2"],
                correct_answer="A",
                explanation="解説",
                source=[],
            )
            agent_output = AgentOutput(questions=[test_question])

            # Act & Assert - 事前条件検証
            with pytest.raises(
                ValueError, match="POWER_AUTOMATE_WEBHOOK_URL が設定されていません"
            ):
                await client.send(agent_output)

    @pytest.mark.asyncio
    async def test_unexpected_exception_handling_contract(self) -> None:
        """
        事前条件: 予期しない例外発生
        事後条件: 元の例外が再発生される
        不変条件: 例外情報が適切にログ出力される
        """
        # Arrange - 事前条件設定
        client = TeamsClient(webhook_url="https://test.webhook.url")
        test_question = Question(
            question="予期しないエラーテスト問題",
            options=["A. 選択肢1", "B. 選択肢2"],
            correct_answer="A",
            explanation="解説",
            source=[],
        )
        agent_output = AgentOutput(questions=[test_question])

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=RuntimeError("予期しないエラー")
            )

            # Act & Assert - 事後条件検証: RuntimeError例外が発生
            with pytest.raises(RuntimeError, match="予期しないエラー"):
                await client.send(agent_output)

    @pytest.mark.asyncio
    async def test_agent_output_json_serialization_contract(self) -> None:
        """
        事前条件: 複数問題を含むAgentOutput
        事後条件: 正しいJSON形式で送信される
        不変条件: AgentOutputの構造が保持される
        """
        # Arrange - 事前条件設定
        client = TeamsClient(webhook_url="https://test.webhook.url")
        test_questions = [
            Question(
                question=f"テスト問題{i + 1}",
                options=["A. 選択肢1", "B. 選択肢2", "C. 選択肢3", "D. 選択肢4"],
                correct_answer="A",
                explanation=f"解説{i + 1}",
                source=[f"https://docs.aws.amazon.com/test{i + 1}/"],
            )
            for i in range(2)
        ]
        agent_output = AgentOutput(questions=test_questions)

        # HTTPクライアントをモック
        mock_response = MagicMock()
        mock_response.status_code = 202
        captured_content = None

        async def capture_post(*args: Any, **kwargs: Any) -> MagicMock:
            nonlocal captured_content
            captured_content = kwargs.get("content")
            return mock_response

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=capture_post
            )

            # Act
            await client.send(agent_output)

            # Assert - 事後条件検証
            assert captured_content is not None
            assert "questions" in captured_content
            assert "テスト問題1" in captured_content
            assert "テスト問題2" in captured_content

            # 不変条件検証: 正しいContent-Typeヘッダー
            call_args = mock_client.return_value.__aenter__.return_value.post.call_args
            headers = call_args.kwargs.get("headers", {})
            assert headers.get("Content-Type") == "application/json"
