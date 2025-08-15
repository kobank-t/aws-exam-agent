"""
Teams クライアント - Power Automate Webhook 連携

AgentOutputをそのままPower Automate Webhookに送信してTeams投稿を実行します。
Power Automate "Anyone"モードを使用するため、APIキー認証は不要です。
"""

import logging
import os

import httpx
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# .envファイルを読み込み
load_dotenv()

logger = logging.getLogger(__name__)


class TeamsResponse(BaseModel):
    """Teams投稿レスポンスモデル（最小限）"""

    status: str = Field(description="処理ステータス")
    error: str | None = Field(default=None, description="エラーメッセージ")


class TeamsClient:
    """Teams投稿クライアント（Power Automate Webhook経由）"""

    def __init__(self, webhook_url: str | None = None, timeout: int = 30):
        """
        Webhook クライアントを初期化

        Args:
            webhook_url: Power Automate Webhook URL
            timeout: HTTPリクエストタイムアウト（秒）
        """
        self.webhook_url = webhook_url or os.getenv("POWER_AUTOMATE_WEBHOOK_URL")
        self.timeout = timeout

        if not self.webhook_url:
            logger.warning("POWER_AUTOMATE_WEBHOOK_URL が設定されていません")

    async def send_agent_output_to_teams(self, agent_output_json: str) -> TeamsResponse:
        """
        AgentOutputをPower Automate経由でTeamsに送信

        Args:
            agent_output_json: AgentOutput.model_dump_json()の結果

        Returns:
            TeamsResponse: 送信結果
        """
        if not self.webhook_url:
            return TeamsResponse(
                status="error", error="POWER_AUTOMATE_WEBHOOK_URL が設定されていません"
            )

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info("Power Automate Webhook送信開始")

                response = await client.post(
                    self.webhook_url,
                    content=agent_output_json,
                    headers={"Content-Type": "application/json"},
                )

                response.raise_for_status()  # 4xx, 5xx で HTTPStatusError を発生
                logger.info(f"Webhook送信成功 (HTTP {response.status_code})")
                return TeamsResponse(status="success")

        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
            logger.error(f"Webhook送信失敗: {error_msg}")
            return TeamsResponse(status="error", error=error_msg)

        except httpx.TimeoutException:
            error_msg = f"タイムアウト: {self.timeout}秒"
            logger.error(f"Webhook送信タイムアウト: {error_msg}")
            return TeamsResponse(status="error", error=error_msg)

        except Exception as e:
            error_msg = f"予期しないエラー: {str(e)}"
            logger.error(f"Webhook送信エラー: {error_msg}", exc_info=True)
            return TeamsResponse(status="error", error=error_msg)
