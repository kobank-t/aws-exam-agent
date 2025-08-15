"""
Teams クライアントの単体テスト - シンプル化版

AgentOutputをそのままPower Automate Webhookに送信する
シンプル化されたTeamsClientのテスト実装。
"""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from dotenv import load_dotenv

from app.agentcore.teams_client import TeamsClient, TeamsResponse

# .envファイルを読み込み
load_dotenv()


class TestTeamsResponse:
    """TeamsResponse モデルの契約検証"""

    def test_success_response_contract(self) -> None:
        """
        事前条件: 成功レスポンスデータ
        事後条件: TeamsResponse モデルが正常に作成される
        不変条件: 成功時は status="success" かつ error は None
        """
        # Arrange - 事前条件設定
        success_data = {"status": "success"}

        # Act
        response = TeamsResponse(**success_data)

        # Assert - 事後条件検証
        assert response.status == "success"
        assert response.error is None

        # 不変条件検証: 成功時の制約
        assert response.status == "success"

    def test_error_response_contract(self) -> None:
        """
        事前条件: エラーレスポンスデータ
        事後条件: TeamsResponse モデルが正常に作成される
        不変条件: エラー時は status="error" かつ error メッセージが存在する
        """
        # Arrange - 事前条件設定
        error_data = {
            "status": "error",
            "error": "POWER_AUTOMATE_WEBHOOK_URL が設定されていません",
        }

        # Act
        response = TeamsResponse(**error_data)

        # Assert - 事後条件検証
        assert response.status == "error"
        assert response.error == "POWER_AUTOMATE_WEBHOOK_URL が設定されていません"

        # 不変条件検証: エラー時の制約
        assert response.status == "error"
        assert response.error is not None
        assert len(response.error) > 0


class TestTeamsClient:
    """TeamsClient の契約検証"""

    def test_initialization_with_parameters_contract(self) -> None:
        """
        事前条件: 有効な初期化パラメータ
        事後条件: TeamsClient インスタンスが正常に作成される
        不変条件: 設定値が適切に保存される
        """
        # Arrange - 事前条件設定
        webhook_url = "https://prod-123.westus.logic.azure.com/workflows/abc123/triggers/manual/paths/invoke"
        timeout = 60

        # Act
        client = TeamsClient(webhook_url=webhook_url, timeout=timeout)

        # Assert - 事後条件検証
        assert client.webhook_url == webhook_url
        assert client.timeout == timeout

        # 不変条件検証
        assert isinstance(client.webhook_url, str)
        assert isinstance(client.timeout, int)
        assert client.timeout > 0

    def test_initialization_with_environment_variables_contract(self) -> None:
        """
        事前条件: 環境変数が設定されている
        事後条件: 環境変数から設定値が読み込まれる
        不変条件: 環境変数の値が適切に反映される
        """
        # Arrange - 事前条件設定
        with patch.dict(
            "os.environ",
            {"POWER_AUTOMATE_WEBHOOK_URL": "https://env.logic.azure.com/webhook"},
        ):
            # Act
            client = TeamsClient()

            # Assert - 事後条件検証
            assert client.webhook_url == "https://env.logic.azure.com/webhook"

            # 不変条件検証
            assert client.webhook_url is not None

    @pytest.mark.asyncio
    async def test_successful_webhook_send_contract(self) -> None:
        """
        事前条件: 有効な設定とAgentOutput JSON
        事後条件: 成功レスポンスが返される
        不変条件: HTTP 200 レスポンス時は成功ステータス
        """
        # Arrange - 事前条件設定
        client = TeamsClient(webhook_url="https://example.logic.azure.com/webhook")

        # HTTPクライアントをモック
        mock_response = MagicMock()
        mock_response.status_code = 200

        agent_output_json = '{"question": "テスト問題", "options": ["A", "B"], "correct_answer": "A", "explanation": "解説", "source": []}'

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )

            # Act
            result = await client.send_agent_output_to_teams(agent_output_json)

            # Assert - 事後条件検証
            assert result.status == "success"
            assert result.error is None

            # 不変条件検証: 成功時の制約
            assert isinstance(result, TeamsResponse)
            assert result.status == "success"

    @pytest.mark.asyncio
    async def test_http_error_handling_contract(self) -> None:
        """
        事前条件: HTTP エラーレスポンス
        事後条件: エラーレスポンスが返される
        不変条件: HTTP エラー時はエラーステータス
        """
        # Arrange - 事前条件設定
        client = TeamsClient(webhook_url="https://example.logic.azure.com/webhook")

        agent_output_json = '{"question": "エラーテスト問題"}'

        with patch("httpx.AsyncClient") as mock_client:
            # HTTPStatusError を発生させる
            mock_response = MagicMock()
            mock_response.status_code = 400
            mock_response.text = "Bad Request"

            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=httpx.HTTPStatusError(
                    "Bad Request", request=MagicMock(), response=mock_response
                )
            )

            # Act
            result = await client.send_agent_output_to_teams(agent_output_json)

            # Assert - 事後条件検証
            assert result.status == "error"
            assert result.error is not None and "HTTP 400" in result.error

            # 不変条件検証: エラー時の制約
            assert isinstance(result, TeamsResponse)
            assert result.status == "error"
            assert result.error is not None

    @pytest.mark.asyncio
    async def test_timeout_handling_contract(self) -> None:
        """
        事前条件: タイムアウト発生
        事後条件: タイムアウトエラーレスポンスが返される
        不変条件: タイムアウト時はエラーステータス
        """
        # Arrange - 事前条件設定
        client = TeamsClient(
            webhook_url="https://example.logic.azure.com/webhook", timeout=1
        )

        agent_output_json = '{"question": "タイムアウトテスト問題"}'

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=httpx.TimeoutException("Timeout")
            )

            # Act
            result = await client.send_agent_output_to_teams(agent_output_json)

            # Assert - 事後条件検証
            assert result.status == "error"
            assert result.error is not None and "タイムアウト" in result.error

            # 不変条件検証: タイムアウト時の制約
            assert isinstance(result, TeamsResponse)
            assert result.status == "error"

    @pytest.mark.asyncio
    async def test_missing_webhook_url_precondition(self) -> None:
        """
        事前条件: Webhook URL が未設定
        事後条件: 設定エラーレスポンスが返される
        不変条件: 必須設定欠如時はエラーステータス
        """
        # Arrange - 事前条件違反: 環境変数とパラメータ両方なし
        with patch.dict("os.environ", {}, clear=True):
            client = TeamsClient()  # webhook_url なし、環境変数もなし

            agent_output_json = '{"question": "設定エラーテスト問題"}'

            # Act
            result = await client.send_agent_output_to_teams(agent_output_json)

            # Assert - 事後条件検証
            assert result.status == "error"
            assert (
                result.error is not None
                and "POWER_AUTOMATE_WEBHOOK_URL が設定されていません" in result.error
            )

            # 不変条件検証: 設定エラー時の制約
            assert isinstance(result, TeamsResponse)
            assert result.status == "error"

    @pytest.mark.asyncio
    async def test_unexpected_exception_handling_contract(self) -> None:
        """
        事前条件: 予期しない例外が発生
        事後条件: 予期しないエラーレスポンスが返される
        不変条件: 予期しない例外時はエラーステータス
        """
        # Arrange - 事前条件設定
        client = TeamsClient(webhook_url="https://example.logic.azure.com/webhook")

        agent_output_json = '{"question": "予期しないエラーテスト問題"}'

        # 予期しない例外を発生させる
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=ValueError("予期しないエラーが発生しました")
            )

            # Act
            result = await client.send_agent_output_to_teams(agent_output_json)

            # Assert - 事後条件検証
            assert result.status == "error"
            assert result.error is not None and "予期しないエラー" in result.error
            assert (
                "ValueError" in result.error
                or "予期しないエラーが発生しました" in result.error
            )

            # 不変条件検証: 予期しない例外時の制約
            assert isinstance(result, TeamsResponse)
            assert result.status == "error"
            assert result.error is not None
