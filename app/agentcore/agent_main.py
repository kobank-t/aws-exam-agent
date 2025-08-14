#!/usr/bin/env python3
"""
AWS Exam Agent - シンプル化版 AgentCore Runtime メインエージェント

実証済みの問題生成機能を中心とした最小限の実装。
複雑な基盤構築を後回しにして、動く価値を最優先で提供します。
"""

import asyncio
import logging
from typing import Any

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from mcp import StdioServerParameters, stdio_client
from pydantic import BaseModel, Field
from strands import Agent
from strands.tools.mcp import MCPClient

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

# Bedrock基盤モデル
MODEL_ID = {
    "claude-3.5-sonnet": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
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


class AgentOutput(BaseModel):
    """アウトプットモデル"""

    question: str = Field(description="問題文")
    options: list[str] = Field(description="回答の選択肢(A-Z)")
    correct_answer: str = Field(description="正解の選択肢")
    explanation: str = Field(description="正解の理由と他選択肢が不適切な理由")
    source: list[str] = Field(
        description="AWS Documentation MCP Serverで、妥当性検証に用いたAWS公式ドキュメントのURL"
    )


# MCPクライアントを初期化する
mcp_client = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(
            command="uvx",
            args=["awslabs.aws-documentation-mcp-server@latest"],
        )
    )
)


# エージェントを初期化する
with mcp_client:
    agent = Agent(
        model=MODEL_ID["claude-3.7-sonnet"],
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

# AgentCore アプリケーションの初期化
app = BedrockAgentCoreApp()


@app.entrypoint
async def invoke(payload: dict[str, Any]) -> dict[str, Any]:
    """AWS試験問題生成エージェントのエントリーポイント

    Args:
        payload (dict[str, Any]): AgentInputモデルに対応する入力データ

    Returns:
        dict[str, Any]: AgentOutputモデルに対応する問題データまたはエラー情報
    """

    try:
        input = AgentInput(**payload)

        prompt = f"""
            以下の条件に沿って、{input.question_count}問の実践的な問題を作成してください。

            # 生成条件
            - **レベル**: {EXAM_TYPES[input.exam_type]["name"]}
            - **カテゴリ**: {input.category}（指定がある場合は、それを考慮してください）
        """
        logger.info(f"prompt: {prompt}")

        result = agent.structured_output(
            output_model=AgentOutput,
            prompt=prompt,
        )
        logger.info(f"result: {result.model_dump_json()}")

        return result.model_dump()

    except Exception as error:
        logger.error(f"Failed to generate question: {str(error)}", exc_info=True)

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
