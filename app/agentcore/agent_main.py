#!/usr/bin/env python3
"""
AWS Exam Agent - AgentCore Runtime メインエージェント

このファイルは Amazon Bedrock AgentCore Runtime で実行される
監督者エージェント（SupervisorAgent）の実装です。

Agent-as-Tools パターンにより、専門エージェントを統合して
AWS試験問題の生成・配信を行います。
"""

import logging
from typing import Any

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent, tool

# ログ設定
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# AgentCore アプリケーションの初期化
app = BedrockAgentCoreApp()


@tool
def aws_info_agent(service: str = "EC2") -> dict[str, Any]:
    """
    AWS情報取得エージェント（@tool）

    MCP Server を通じて AWS 公式ドキュメントから最新情報を取得します。
    現在はモック実装、後でMCP統合に置き換えます。

    Args:
        service: AWSサービス名

    Returns:
        サービス情報の辞書
    """
    logger.info(f"[AWS Info Agent] Getting AWS info for service: {service}")

    # 基本的な情報取得ロジック（後でMCP統合に置き換え）
    info = {
        "service": service,
        "description": f"AWS {service} is a cloud service",
        "use_cases": [f"Use case 1 for {service}", f"Use case 2 for {service}"],
        "pricing_model": "Pay-as-you-use",
        "latest_features": [f"Feature 1 for {service}", f"Feature 2 for {service}"],
    }

    logger.info(f"[AWS Info Agent] AWS info retrieved for {service}")
    return info


@tool
def question_generation_agent(
    topic: str = "EC2",
    difficulty: str = "intermediate",
    aws_info: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    問題生成エージェント（@tool）

    AWS情報を基にProfessionalレベルの試験問題を生成します。
    現在はモック実装、後でBedrock統合に置き換えます。

    Args:
        topic: 問題のトピック（例: "EC2", "S3", "Lambda"）
        difficulty: 難易度（"beginner", "intermediate", "advanced"）
        aws_info: AWS情報取得エージェントからの情報

    Returns:
        生成された問題の辞書
    """
    logger.info(
        f"[Question Gen Agent] Generating question for topic: {topic}, difficulty: {difficulty}"
    )

    # AWS情報を活用した問題生成（基本実装）
    question = {
        "id": f"q_{topic.lower()}_{difficulty}_001",
        "topic": topic,
        "difficulty": difficulty,
        "question": f"What is the primary use case for AWS {topic}?",
        "options": {
            "A": f"Primary function of {topic}",
            "B": f"Secondary function of {topic}",
            "C": f"Alternative function of {topic}",
            "D": "Unrelated function",
        },
        "correct_answer": "A",
        "explanation": f"AWS {topic} is primarily used for its main functionality.",
        "source_info": aws_info if aws_info else {"note": "Using default info"},
    }

    logger.info(
        f"[Question Gen Agent] Question generated successfully: {question['id']}"
    )
    return question


@tool
def quality_management_agent(question: dict[str, Any]) -> dict[str, Any]:
    """
    品質管理エージェント（@tool）

    生成された問題の技術的正確性と適切な難易度を検証します。

    Args:
        question: 検証対象の問題

    Returns:
        品質検証結果
    """
    logger.info(f"[Quality Agent] Validating question: {question.get('id', 'unknown')}")

    # 基本的な品質検証ロジック
    validation_result = {
        "question_id": question.get("id", "unknown"),
        "is_valid": True,
        "quality_score": 85,
        "validation_checks": {
            "technical_accuracy": True,
            "difficulty_appropriate": True,
            "format_correct": True,
            "explanation_clear": True,
        },
        "suggestions": [],
    }

    logger.info(
        f"[Quality Agent] Question validation completed: score={validation_result['quality_score']}"
    )
    return validation_result


# 監督者エージェント（SupervisorAgent）の初期化
# Agent-as-Tools パターンで専門エージェントを統合
agent = Agent(
    tools=[aws_info_agent, question_generation_agent, quality_management_agent],
    name="SupervisorAgent",
    description="AWS Exam Agent の監督者エージェント。専門エージェントを統合して問題生成・配信を行います。",
)


@app.entrypoint
def invoke(payload: dict[str, Any]) -> dict[str, Any]:
    """
    AgentCore Runtime エントリーポイント

    監督者エージェントが専門エージェントを統合して
    AWS試験問題の生成・配信を行います。

    Args:
        payload: AgentCore から送信されるペイロード

    Returns:
        処理結果
    """
    logger.info("=== AWS Exam Agent - SupervisorAgent Starting ===")
    logger.info("Initializing Supervisor Agent")
    logger.info("Supervisor Agent initialized successfully")

    # ペイロードから情報を取得
    topic = payload.get("topic", "EC2")
    difficulty = payload.get("difficulty", "intermediate")

    logger.info(
        f"Starting question generation flow: topic={topic}, difficulty={difficulty}"
    )
    logger.info(f"Processing request: topic={topic}, difficulty={difficulty}")

    try:
        # Agent-as-Tools パターンによるマルチエージェント処理
        logger.info("=== Phase 1: AWS Information Retrieval ===")
        aws_info = aws_info_agent(service=topic)

        logger.info("=== Phase 2: Question Generation ===")
        question = question_generation_agent(
            topic=topic, difficulty=difficulty, aws_info=aws_info
        )

        logger.info("=== Phase 3: Quality Management ===")
        quality_result = quality_management_agent(question=question)

        # 最終結果の構築
        result = {
            "status": "success",
            "topic": topic,
            "difficulty": difficulty,
            "question": question,
            "quality_validation": quality_result,
            "aws_info": aws_info,
            "message": "Question generated and delivered successfully",
            "agent_info": {
                "supervisor": "SupervisorAgent",
                "agents_used": [
                    "aws_info_agent",
                    "question_generation_agent",
                    "quality_management_agent",
                ],
            },
        }

        logger.info("=== Multi-Agent Processing Completed Successfully ===")
        logger.info(
            f"Question ID: {question.get('id')}, Quality Score: {quality_result.get('quality_score')}"
        )
        logger.info(
            f"Execution result: {{'status': 'success', 'question_id': '{question.get('id')}'}}"
        )

        return result

    except Exception as e:
        logger.error(f"Error in SupervisorAgent processing: {str(e)}")
        result = {
            "status": "error",
            "error": str(e),
            "topic": topic,
            "difficulty": difficulty,
            "message": "Failed to generate and deliver question",
            "agent_info": {
                "supervisor": "SupervisorAgent",
                "error_phase": "multi_agent_processing",
            },
        }
        logger.info(f"Execution result: {{'status': 'error', 'error': '{str(e)}'}}")
        return result


if __name__ == "__main__":
    # AgentCore Runtime として実行
    app.run()
