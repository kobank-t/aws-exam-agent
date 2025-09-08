#!/usr/bin/env python3
"""
Cloud CoPassAgent - シンプル化版 AgentCore Runtime メインエージェント

実証済みの問題生成機能を中心とした最小限の実装。
複雑な基盤構築を後回しにして、動く価値を最優先で提供します。
"""

import asyncio
import logging
from pathlib import Path
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
    "AWS-SAP": {
        "name": "AWS Certified Solutions Architect - Professional",
        "guide_path": "exam_guides/AWS-SAP-C02.md",
        "guide_url": "https://d1.awsstatic.com/training-and-certification/docs-sa-pro/AWS-Certified-Solutions-Architect-Professional_Exam-Guide.pdf",
        "sample_url": "https://d1.awsstatic.com/training-and-certification/docs-sa-pro/AWS-Certified-Solutions-Architect-Professional_Sample-Questions.pdf",
    },
}


def load_exam_guide(exam_type: str) -> str:
    """試験ガイドファイルを読み込む

    Args:
        exam_type: 試験タイプ（例: "AWS-SAP"）

    Returns:
        str: 試験ガイドの内容

    Raises:
        FileNotFoundError: 指定された試験ガイドファイルが存在しない場合
        RuntimeError: ファイル読み込みに失敗した場合
    """
    try:
        # 現在のファイルのディレクトリを基準にパスを解決
        current_file = Path(__file__)
        base_dir = current_file.parent

        # 試験タイプに基づいてガイドパスを決定
        if exam_type in EXAM_TYPES:
            guide_path = base_dir / EXAM_TYPES[exam_type]["guide_path"]
        else:
            # フォールバック: 試験タイプ名をそのままファイル名として使用
            guide_path = base_dir / "exam_guides" / f"{exam_type}.md"

        logger.info(f"試験ガイドファイルを読み込み中: {guide_path}")

        if not guide_path.exists():
            raise FileNotFoundError(f"試験ガイドファイルが見つかりません: {guide_path}")

        with open(guide_path, encoding="utf-8") as f:
            content = f.read()

        logger.info(f"試験ガイドファイル読み込み完了: {len(content)}文字")
        return content

    except Exception as e:
        logger.error(f"試験ガイドファイル読み込みエラー: {e}")
        raise RuntimeError(f"試験ガイドファイルの読み込みに失敗しました: {e}") from e


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
    """問題生成エージェントの入力パラメータ"""

    exam_type: str = Field(
        default="AWS-SAP",
        description="対象試験の種類（試験ガイドファイル名に対応）",
        examples=["AWS-SAP", "AWS-DVA", "AZ-104", "GCP-ACE"],
    )

    question_count: int = Field(default=1, description="生成する問題数", ge=1, le=5)


class Question(BaseModel):
    """単一問題のモデル"""

    question: str = Field(description="問題文")
    options: list[str] = Field(
        description='回答の選択肢。各選択肢は必ずMarkdown太字記法を使用して「**A.** 選択肢の内容」「**B.** 選択肢の内容」の形式で記載する。例: ["**A.** Amazon S3を使用してデータを保存する", "**B.** Amazon EBSを使用してデータを保存する"]'
    )
    correct_answer: str = Field(
        description='正解の選択肢のアルファベット（A、B、C、D等のみ）。選択肢の内容は含めず、ラベルのみを記載する。例: "B"'
    )
    explanation: str = Field(description="正解の理由と他選択肢が不適切な理由")
    source: list[str] = Field(
        description="AWS Documentation MCP Serverで、妥当性検証に用いたAWS公式ドキュメントのURL"
    )

    # 新機能: 試験ガイド活用による問題分類表示
    learning_domain: str = Field(
        description='試験ガイドで定義された学習分野分類。例: "複雑な組織に対応するソリューションの設計", "セキュリティの設計", "信頼性とビジネス継続性の設計"。複数分野にまたがる場合は最も関連の深い分野を1つ選択する。'
    )
    primary_technologies: list[str] = Field(
        description='問題で扱われる主要なサービス・技術を2-4個リスト化。例: ["AWS Organizations", "AWS Control Tower"], ["Azure Active Directory", "Azure Policy"]。サービス名は正式名称を使用（略称ではなく）。'
    )
    learning_insights: str = Field(
        description="""この問題が試験ガイドのどの分野・タスクに該当するかの解説と学習アドバイス。

【必須要件】:
- 試験ガイドから具体的に関連する部分を特定できた場合のみ、その内容を引用・参照する
- ガイドから関連する「タスク」「対象知識」「対象スキル」を引用し、問題との関連性を説明する
- ガイドとの関連性が不明確な場合は「試験ガイドとの直接的な関連付けができませんでした」と正直に記載する
- 推測や自作の学習アドバイスは避け、ガイドに基づく事実のみを記載する

【良い例】:
"この問題は試験ガイドの「タスク1.4: マルチアカウントAWS環境を設計する」に該当します。ガイドでは「組織の要件に最も適したアカウント構造を評価する」「マルチアカウントガバナンスモデルを開発する」というスキルが求められており、この問題はまさにその実践的な応用です。"

【悪い例】:
"【試験対策】出題頻度★★★、学習優先度最高。【よくある間違い】..."（形式的で根拠不明）

【ガイド活用できない場合】:
"試験ガイドとの直接的な関連付けができませんでした。"（正直な回答）"""
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

        # 試験ガイドファイルを読み込み
        try:
            exam_guide_content = load_exam_guide(input.exam_type)
        except Exception as e:
            logger.warning(
                f"試験ガイド読み込みに失敗しました。基本機能で継続します: {e}"
            )
            exam_guide_content = ""

        # 1回のプロンプトで複数問題を生成（試験ガイド統合）
        prompt = f"""
            以下の条件に沿って、{input.question_count}問の実践的な問題を作成してください。

            # 生成条件
            - **試験**: {EXAM_TYPES[input.exam_type]["name"]}
            - **問題数**: {input.question_count}問

            # 試験ガイド情報
            {exam_guide_content if exam_guide_content else "試験ガイド情報は利用できません。指定された試験レベルに適した問題を生成してください。"}

            # 注意事項
            - 各問題は重複しない内容にしてください
            - 異なるサービスや機能を扱ってください
            - 試験ガイドの内容に基づいて適切な分類情報を設定してください
        """
        logger.info("問題生成プロンプト（試験ガイド統合版）を作成しました")

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
