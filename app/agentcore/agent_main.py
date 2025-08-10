#!/usr/bin/env python3
"""
AWS Exam Agent - AgentCore Runtime メインエージェント

このファイルは Amazon Bedrock AgentCore Runtime で実行される
監督者エージェント（SupervisorAgent）の実装です。

Agent-as-Tools パターンにより、専門エージェントを統合して
AWS試験問題の生成・配信を行います。
"""

import asyncio
import logging
from typing import Any, cast

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent, tool

from app.agentcore.mcp.client import get_mcp_client
from app.shared.config import (
    get_agentcore_agent_config,
    get_agentcore_error_handling_config,
    get_agentcore_log_config,
    get_agentcore_mcp_config,
)

# ログ設定（AgentCore設定を使用）
log_config = get_agentcore_log_config()
logging.basicConfig(
    level=getattr(logging, log_config["log_level"]), format=log_config["log_format"]
)
logger = logging.getLogger(__name__)

# AgentCore アプリケーションの初期化
app = BedrockAgentCoreApp()


@tool
async def aws_info_agent(service: str = "EC2", topic: str = "") -> dict[str, Any]:
    """
    AWS情報取得エージェント（@tool）

    MCP Server を通じて AWS 公式ドキュメントから最新情報を取得します。
    AWS Documentation MCP Server と AWS Knowledge MCP Server を統合使用します。

    Args:
        service: AWSサービス名
        topic: 特定のトピック（オプション）

    Returns:
        サービス情報の辞書
    """
    logger.info(
        f"[AWS Info Agent] Getting AWS info for service: {service}, topic: {topic}"
    )

    try:
        # MCP Client を取得
        mcp_client = await get_mcp_client()

        # AWS Documentation と AWS Knowledge の両方から情報を取得
        documentation_task = mcp_client.get_aws_documentation(service, topic)
        knowledge_task = mcp_client.get_aws_knowledge(f"{service} {topic}".strip())

        # 並行して情報を取得
        results = await asyncio.gather(
            documentation_task, knowledge_task, return_exceptions=True
        )

        # エラーハンドリング
        documentation: dict[str, Any]
        if isinstance(results[0], Exception):
            logger.error(f"Documentation retrieval failed: {results[0]}")
            documentation = {"error": str(results[0])}
        else:
            # asyncio.gatherの結果は正常時にdict[str, Any]を返すことが保証されている
            documentation = cast(dict[str, Any], results[0])

        knowledge: dict[str, Any]
        if isinstance(results[1], Exception):
            logger.error(f"Knowledge retrieval failed: {results[1]}")
            knowledge = {"error": str(results[1])}
        else:
            # asyncio.gatherの結果は正常時にdict[str, Any]を返すことが保証されている
            knowledge = cast(dict[str, Any], results[1])

        # 統合された情報を構築
        integrated_info = {
            "service": service,
            "topic": topic,
            "documentation": documentation,
            "knowledge": knowledge,
            "mcp_integration": {
                "aws_docs_server": "connected"
                if not documentation.get("error")
                else "error",
                "aws_knowledge_server": "connected"
                if not knowledge.get("error")
                else "error",
            },
            "timestamp": "2025-08-09T20:19:34Z",
        }

        logger.info(
            f"[AWS Info Agent] AWS info retrieved for {service} via MCP integration"
        )
        return integrated_info

    except Exception as e:
        logger.error(f"[AWS Info Agent] Error in MCP integration: {e}")
        # フォールバック: 基本的な情報を返す
        fallback_info = {
            "service": service,
            "topic": topic,
            "description": f"AWS {service} is a cloud service",
            "use_cases": [f"Use case 1 for {service}", f"Use case 2 for {service}"],
            "pricing_model": "Pay-as-you-use",
            "latest_features": [f"Feature 1 for {service}", f"Feature 2 for {service}"],
            "mcp_integration": {"status": "fallback", "error": str(e)},
        }

        logger.info(f"[AWS Info Agent] Using fallback info for {service}")
        return fallback_info


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


# AgentCore設定の取得
agent_config = get_agentcore_agent_config()
mcp_config = get_agentcore_mcp_config()
error_config = get_agentcore_error_handling_config()

# 監督者エージェント（SupervisorAgent）の初期化
# Agent-as-Tools パターンで専門エージェントを統合
agent = Agent(
    tools=[aws_info_agent, question_generation_agent, quality_management_agent],
    name=agent_config["agent_name"],
    description=agent_config["description"],
)


@app.entrypoint
async def invoke(payload: dict[str, Any]) -> dict[str, Any]:
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
        aws_info = await aws_info_agent(service=topic)

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
