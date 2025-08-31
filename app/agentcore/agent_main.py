#!/usr/bin/env python3
"""
Cloud CoPassAgent - シンプル化版 AgentCore Runtime メインエージェント

実証済みの問題生成機能を中心とした最小限の実装。
複雑な基盤構築を後回しにして、動く価値を最優先で提供します。
"""

import asyncio
import logging
from typing import Any

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from botocore.config import Config
from mcp import StdioServerParameters, stdio_client
from pydantic import BaseModel, Field
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient

# 環境検出による動的インポート（AgentCore vs ローカル環境対応）
try:
    # AgentCore環境では相対インポートが必要
    from teams_client import TeamsClient
except ImportError:
    # ローカル環境（テスト・開発）では絶対インポートが必要
    from app.agentcore.teams_client import TeamsClient

# ログ設定
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# AWS認定試験の種類
EXAM_TYPES = {
    "SAP": {
        "name": "AWS Certified Solutions Architect - Professional",
        "guide_url": "https://d1.awsstatic.com/training-and-certification/docs-sa-pro/AWS-Certified-Solutions-Architect-Professional_Exam-Guide.pdf",
        "sample_url": "https://d1.awsstatic.com/training-and-certification/docs-sa-pro/AWS-Certified-Solutions-Architect-Professional_Sample-Questions.pdf",
    }
}

# Bedrock基盤モデル（SCP制限対応: ON_DEMAND対応モデルはus.プレフィックスなし）
MODEL_ID = {
    # ON_DEMAND対応モデル（SCP制限回避）
    "claude-3.5-sonnet": "anthropic.claude-3-5-sonnet-20240620-v1:0",
    "nova-pro": "amazon.nova-pro-v1:0",
    # INFERENCE_PROFILE のみ対応（SCP制限解除が必要）
    "claude-3.5-sonnet-v2": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    "claude-3.7-sonnet": "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    "claude-sonnet-4": "us.anthropic.claude-sonnet-4-20250514-v1:0",
}


class AgentInput(BaseModel):
    """インプットモデル"""

    exam_type: str = Field(default="SAP", description="AWS認定試験の種類")

    category: list[str] = Field(
        default=[],
        description="試験ガイド記載のAWSサービスの主な機能に応じたカテゴリ",
        examples=[
            "分析",
            "アプリケーション統合",
            "クラウド財務管理",
            "コンピューティング",
            "コンテナ",
            "データベース",
            "デベロッパーツール",
            "エンドユーザーコンピューティング",
            "フロントエンドのウェブとモバイル",
            "IoT機械学習",
            "マネジメントとガバナンス",
            "移行と転送",
            "ネットワークとコンテンツ配信",
            "セキュリティ、アイデンティティ、コンプライアンス",
            "ストレージ",
        ],
    )

    question_count: int = Field(default=1, description="生成する問題数", ge=1, le=5)


class Question(BaseModel):
    """単一問題のモデル"""

    question: str = Field(description="問題文")
    options: list[str] = Field(description="回答の選択肢(A. xxxx, B. xxxx, …)")
    correct_answer: str = Field(description="正解の選択肢")
    explanation: str = Field(description="正解の理由と他選択肢が不適切な理由")
    source: list[str] = Field(
        description="AWS Documentation MCP Serverで、妥当性検証に用いたAWS公式ドキュメントのURL"
    )


class AgentOutput(BaseModel):
    """エージェントのアウトプットモデル（複数問題対応）"""

    questions: list[Question] = Field(description="生成された問題のリスト")


# シンプルで安全な初期化（テスト環境対応）
agent: Agent | None = None

try:
    # 本番環境での初期化
    mcp_client = MCPClient(
        lambda: stdio_client(
            StdioServerParameters(
                command="uvx",
                args=["awslabs.aws-documentation-mcp-server@latest"],
            )
        )
    )

    with mcp_client:
        agent = Agent(
            model=BedrockModel(
                model_id=MODEL_ID["claude-3.5-sonnet"],
                region_name="us-east-1",  # バージニア北部に明示的に指定
                boto_client_config=Config(
                    read_timeout=300,  # 5分（複数問題生成対応）
                    connect_timeout=60,  # 1分
                    retries={"max_attempts": 3},
                ),
            ),
            tools=mcp_client.list_tools_sync(),
            system_prompt="""
        あなたはAWS認定試験の問題を生成する専門エージェントです。

        # 重要な要件
        - 実際の業務シナリオに基づく
        - 回答の選択肢は最低4つ以上のローマ字表記(A-Z)
        - 正解は1つ、他は技術的に妥当だが最適でない
        - 最新のAWS機能・サービスを反映

        # 問題品質チェック項目
        - **技術的正確性**: AWS公式ドキュメントを参照して検証(AWS Documentation MCP Serverを使用)
        - **問題の明確性**: 曖昧さのない問題文
        - **選択肢の妥当性**: 適切な誤答選択肢
        - **解説の充実性**: 学習に役立つ詳細な解説
        """,
        )
except Exception as e:
    # テスト環境や開発環境での初期化失敗時
    logger.warning(f"MCP初期化に失敗しました（テスト環境の可能性）: {e}")
    agent = None

# AgentCore アプリケーションの初期化
app = BedrockAgentCoreApp()


@app.entrypoint
async def invoke(payload: dict[str, Any]) -> dict[str, Any]:
    """AWS試験問題生成エージェントのエントリーポイント

    Args:
        payload (dict[str, Any]): AgentInputモデルに対応する入力データ

    Returns:
        dict[str, Any]: AgentOutputモデルまたはエラー情報
        - 成功時: AgentOutput.model_dump()
        - エラー時: {"error": str}
    """

    try:
        input = AgentInput(**payload)

        # 1回のプロンプトで複数問題を生成
        prompt = f"""
            以下の条件に沿って、{input.question_count}問の実践的な問題を作成してください。

            # 生成条件
            - **レベル**: {EXAM_TYPES[input.exam_type]["name"]}
            - **カテゴリ**: {input.category}（指定がある場合は、それを考慮してください）
            - **問題数**: {input.question_count}問

            # 注意事項
            - 各問題は重複しない内容にしてください
            - 異なるAWSサービスや機能を扱ってください
        """
        logger.info(f"問題生成プロンプト: {prompt}")

        # エージェントが利用可能かチェック
        if agent is None:
            raise RuntimeError("エージェントが初期化されていません（MCP初期化失敗）")

        # 複数問題を一度に生成
        agent_output = agent.structured_output(
            output_model=AgentOutput,
            prompt=prompt,
        )
        logger.info(f"問題生成結果: {agent_output.model_dump_json()}")

        # Teams投稿
        teams_client = TeamsClient()
        try:
            await teams_client.send(agent_output)

        except Exception as e:
            # Teams投稿失敗でも問題生成結果は返す（処理継続）
            logger.warning(f"Teams投稿に失敗しましたが、処理を継続します: {str(e)}")

        return agent_output.model_dump()

    except Exception as error:
        logger.error(f"問題生成処理でエラーが発生しました: {str(error)}", exc_info=True)
        return {"error": str(error)}


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # ローカル実行モード　 (uv run python app/agentcore/agent_main.py --test)

        async def test_run() -> None:
            input = AgentInput()
            await invoke(payload=input.model_dump())

        asyncio.run(test_run())
    else:
        # AgentCore　Runtime を起動
        app.run()
