"""
Teams クライアント - Power Automate Webhook 連携

AgentOutputをそのままPower Automate Webhookに送信してTeams投稿を実行します。
Power Automate "Anyone"モードを使用するため、APIキー認証は不要です。

設計判断:
- AgentOutput型の直接インポートは循環インポートを引き起こすため、Any型を使用
- agent_main.py ⇄ teams_client.py の相互依存を回避
- model_dump_json()メソッドの存在で実行時の型安全性を保証
- 使用箇所が限定的（agent_main.pyのみ）なため、実用上問題なし
"""

import logging
import os
from typing import Any

import httpx
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

logger = logging.getLogger(__name__)


class TeamsClient:
    """Teams投稿クライアント（Power Automate Webhook経由）"""

    def __init__(self, timeout: int = 30):
        """
        Webhook クライアントを初期化

        Args:
            timeout: HTTPリクエストタイムアウト（秒）

        Raises:
            ValueError: WebhookURLまたはセキュリティトークンが未設定の場合
        """
        webhook_url = os.getenv("POWER_AUTOMATE_WEBHOOK_URL")
        security_token = os.getenv("POWER_AUTOMATE_SECURITY_TOKEN")

        if not webhook_url:
            raise ValueError("POWER_AUTOMATE_WEBHOOK_URL の設定が必須です")

        if not security_token:
            raise ValueError("POWER_AUTOMATE_SECURITY_TOKEN の設定が必須です")

        # 型安全性を保証: 初期化時にチェック済みのため、Noneではない
        self.webhook_url: str = webhook_url
        self.security_token: str = security_token
        self.timeout = timeout

    async def send(self, agent_output: Any) -> None:
        """
        AgentOutputをPower Automate経由でTeamsに送信

        Args:
            agent_output: AgentOutputモデルインスタンス
                         注意: 循環インポート回避のためAny型を使用。
                         実際はapp.agentcore.agent_main.AgentOutputを期待。
                         model_dump_json()メソッドの存在で型安全性を保証。

        Raises:
            httpx.HTTPStatusError: HTTP エラー時
            httpx.TimeoutException: タイムアウト時
            Exception: その他のエラー時
        """
        try:
            # AgentOutputをJSONオブジェクトに変換
            agent_output_data = agent_output.model_dump()

            # セキュリティトークンを追加
            secure_payload = {
                "security_token": self.security_token,  # Power Automateで検証
                **agent_output_data,  # 既存のAgentOutputデータを展開
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info("Power Automate への送信を開始します")

                response = await client.post(
                    self.webhook_url,
                    json=secure_payload,
                )

                response.raise_for_status()  # 4xx, 5xx で HTTPStatusError を発生
                logger.info(f"Teams投稿完了 (HTTP {response.status_code})")

        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
            logger.error(f"Teams投稿失敗: {error_msg}")
            raise  # 例外を再発生

        except httpx.TimeoutException:
            error_msg = f"タイムアウト: {self.timeout}秒"
            logger.error(f"Teams投稿タイムアウト: {error_msg}")
            raise  # 例外を再発生

        except Exception as e:
            error_msg = f"予期しないエラー: {str(e)}"
            logger.error(f"Teams投稿でエラーが発生: {error_msg}", exc_info=True)
            raise  # 例外を再発生
