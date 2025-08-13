import asyncio
from typing import Any

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from pydantic import BaseModel, Field
from strands import Agent
from strands.tools.mcp import MCPClient

from mcp import StdioServerParameters, stdio_client


class ExamQuestion(BaseModel):
    """AWS試験問題の構造化モデル"""

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
    # model_id = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
    model_id = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
    # model_id = "us.anthropic.claude-sonnet-4-20250514-v1:0"

    agent = Agent(
        model=model_id,
        tools=mcp_client.list_tools_sync(),
        system_prompt="""
        あなたはAWS認定試験の問題を生成する専門エージェントです。

        # 重要な要件
        - AWS Certified Solutions Architect Professional レベルの実践的な問題
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
    result = agent.structured_output(
        output_model=ExamQuestion,
        prompt="問題を1つ作って",
    )
    return result.model_dump()


# uv run python app/agentcore/agent_sample.py
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # テスト実行モード
        async def test_run() -> None:
            result = await invoke(payload={})
            print(result)

        asyncio.run(test_run())
    else:
        # AgentCore　Runtime を起動
        app.run()
