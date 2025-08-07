"""
AWS Exam Agent - メインエージェント（監督者エージェント）

AgentCore Runtime で実行されるメインエージェントです。
Agent-as-Tools パターンで専門エージェントを統合し、
問題生成から配信までの全体フローを管理します。
"""

import asyncio
import logging
from typing import Any

from strands_agents import Agent, tool
from strands_agents.core import AgentContext

# 専門エージェントのインポート（後で実装）
# from agents.aws_info_agent import AWSInfoAgent
# from agents.question_gen_agent import QuestionGenerationAgent
# from agents.quality_agent import QualityAgent

# 共通モジュールのインポート（後で実装）
# from app.shared.config import Config
# from app.shared.exceptions import AgentError

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SupervisorAgent(Agent):
    """
    監督者エージェント

    Agent-as-Tools パターンで専門エージェントを統合し、
    問題生成から配信までの全体フローを管理します。
    """

    def __init__(self, name: str = "supervisor_agent"):
        super().__init__(name=name)
        self.aws_info_agent = None  # 後で初期化
        self.question_gen_agent = None  # 後で初期化
        self.quality_agent = None  # 後で初期化

    async def initialize(self) -> None:
        """エージェントの初期化"""
        logger.info("Initializing Supervisor Agent")

        # 専門エージェントの初期化（後で実装）
        # self.aws_info_agent = AWSInfoAgent()
        # self.question_gen_agent = QuestionGenerationAgent()
        # self.quality_agent = QualityAgent()

        logger.info("Supervisor Agent initialized successfully")

    @tool
    async def generate_and_deliver_question(
        self,
        context: AgentContext,
        topic: str | None = None,
        difficulty: str = "intermediate",
    ) -> dict[str, Any]:
        """
        問題生成・配信のメインフロー

        Args:
            context: エージェントコンテキスト
            topic: 問題のトピック（指定なしの場合はランダム）
            difficulty: 問題の難易度

        Returns:
            Dict[str, Any]: 処理結果
        """
        try:
            logger.info(
                f"Starting question generation flow: topic={topic}, difficulty={difficulty}"
            )

            # Phase 1: AWS 情報取得
            logger.info("Phase 1: Gathering AWS information")
            aws_info = await self._gather_aws_information(context, topic)

            # Phase 2: 問題生成
            logger.info("Phase 2: Generating question")
            question_data = await self._generate_question(context, aws_info, difficulty)

            # Phase 3: 品質検証
            logger.info("Phase 3: Quality validation")
            validated_question = await self._validate_quality(context, question_data)

            # Phase 4: 配信
            logger.info("Phase 4: Delivering question")
            delivery_result = await self._deliver_question(context, validated_question)

            result = {
                "status": "success",
                "question_id": validated_question.get("id"),
                "topic": validated_question.get("topic"),
                "delivery_status": delivery_result.get("status"),
                "message": "Question generated and delivered successfully",
            }

            logger.info(f"Question generation flow completed: {result}")
            return result

        except Exception as e:
            logger.error(f"Error in question generation flow: {e}")
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to generate and deliver question",
            }

    async def _gather_aws_information(
        self, context: AgentContext, topic: str | None
    ) -> dict[str, Any]:
        """AWS 情報取得フェーズ"""
        # TODO: AWS 情報取得エージェントの呼び出し
        # return await self.aws_info_agent.gather_information(context, topic)

        # 仮実装
        return {
            "topic": topic or "EC2",
            "service_info": "Amazon EC2 provides scalable computing capacity...",
            "best_practices": ["Use appropriate instance types", "Enable monitoring"],
            "common_scenarios": ["Web application hosting", "Batch processing"],
        }

    async def _generate_question(
        self, context: AgentContext, aws_info: dict[str, Any], difficulty: str
    ) -> dict[str, Any]:
        """問題生成フェーズ"""
        # TODO: 問題生成エージェントの呼び出し
        # return await self.question_gen_agent.generate_question(context, aws_info, difficulty)

        # 仮実装
        return {
            "id": "q_001",
            "topic": aws_info["topic"],
            "question_text": "Which EC2 instance type is most suitable for CPU-intensive workloads?",
            "options": ["A. t3.micro", "B. c5.large", "C. r5.large", "D. i3.large"],
            "correct_answer": "B",
            "explanation": "C5 instances are optimized for compute-intensive workloads...",
            "difficulty": difficulty,
        }

    async def _validate_quality(
        self, context: AgentContext, question_data: dict[str, Any]
    ) -> dict[str, Any]:
        """品質検証フェーズ"""
        # TODO: 品質管理エージェントの呼び出し
        # return await self.quality_agent.validate_question(context, question_data)

        # 仮実装
        question_data["quality_score"] = 0.85
        question_data["validation_status"] = "passed"
        return question_data

    async def _deliver_question(
        self, context: AgentContext, question_data: dict[str, Any]
    ) -> dict[str, Any]:
        """問題配信フェーズ"""
        # TODO: Teams 配信サービスの呼び出し
        # return await self.teams_service.deliver_question(context, question_data)

        # 仮実装
        return {
            "status": "delivered",
            "delivery_id": "d_001",
            "teams_message_id": "msg_001",
        }


# AgentCore Runtime エントリーポイント
async def main() -> None:
    """メイン実行関数"""
    try:
        # 監督者エージェントの初期化
        supervisor = SupervisorAgent()
        await supervisor.initialize()

        # テスト実行（実際の運用では外部からのトリガーで実行）
        context = AgentContext()  # 仮のコンテキスト
        result = await supervisor.generate_and_deliver_question(
            context=context, topic="EC2", difficulty="intermediate"
        )

        logger.info(f"Execution result: {result}")

    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        raise


if __name__ == "__main__":
    # ローカルテスト用
    asyncio.run(main())
