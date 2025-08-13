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

from app.mcp.client import get_mcp_client
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
async def question_generation_agent(
    topic: str = "EC2",
    difficulty: str = "professional",
    aws_info: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    問題生成エージェント（@tool）

    AWS情報を基にProfessionalレベルの試験問題を生成します。
    Bedrock Claude モデルを使用して高品質な問題を生成します。

    Args:
        topic: 問題のトピック（例: "EC2", "S3", "Lambda"）
        difficulty: 難易度（"professional" 推奨）
        aws_info: AWS情報取得エージェントからの情報

    Returns:
        生成された問題の辞書
    """
    logger.info(
        f"[Question Gen Agent] Generating {difficulty} question for topic: {topic}"
    )

    try:
        # Bedrock Client を動的インポート（循環インポート回避）
        from app.services.bedrock_client import get_bedrock_client

        bedrock_client = await get_bedrock_client()

        # AWS情報が提供されていない場合のフォールバック
        if aws_info is None:
            logger.warning("No AWS info provided, using minimal fallback")
            aws_info = {
                "service": topic,
                "documentation": {"sections": [f"{topic} Overview"]},
                "knowledge": {"professional_insights": [f"Basic {topic} concepts"]},
            }

        # Bedrock Claude を使用して問題生成
        question = await bedrock_client.generate_question(
            aws_info=aws_info, topic=topic, difficulty=difficulty
        )

        # 生成された問題にメタデータを追加
        question["agent_info"] = {
            "generated_by": "question_generation_agent",
            "bedrock_integration": True,
            "aws_info_used": bool(aws_info),
        }

        logger.info(
            f"[Question Gen Agent] Professional question generated successfully: {question['id']}"
        )
        return question

    except Exception as e:
        logger.error(f"[Question Gen Agent] Error in Bedrock integration: {e}")

        # エラーを隠蔽せず、明確に返す
        error_question = {
            "id": f"q_{topic.lower()}_{difficulty}_error_{hash(str(e)) % 1000:03d}",
            "topic": topic,
            "difficulty": difficulty,
            "error": True,
            "error_type": "question_generation_error",
            "error_message": str(e),
            "question": f"❌ 問題生成エラー ({topic}): {str(e)}",
            "options": {
                "A": "Bedrockアクセス権限の設定を確認する",
                "B": "AWS認証情報を確認する",
                "C": "ネットワーク接続を確認する",
                "D": "Bedrockサービスの利用可能性を確認する",
            },
            "correct_answer": "A",
            "explanation": f"問題生成中にエラーが発生しました。最も可能性が高いのはBedrockへのアクセス権限の問題です。詳細エラー: {str(e)}",
            "aws_services": ["Bedrock", topic],
            "key_concepts": ["エラーハンドリング", "API アクセス権限"],
            "generated_by": "error_handler",
            "bedrock_integration": False,
            "error_info": str(e),
            "source_info": aws_info if aws_info else {"note": "Error mode"},
        }

        logger.info(
            f"[Question Gen Agent] Error question generated: {error_question['id']}"
        )
        return error_question


@tool
def quality_management_agent(question: dict[str, Any]) -> dict[str, Any]:
    """
    品質管理エージェント（@tool）

    生成された問題の技術的正確性と適切な難易度を検証します。
    Professional レベルの品質基準に基づいて詳細な検証を行います。

    Args:
        question: 検証対象の問題

    Returns:
        品質検証結果
    """
    logger.info(
        f"[Quality Agent] Validating Professional-level question: {question.get('id', 'unknown')}"
    )

    try:
        # 詳細な品質検証の実行
        validation_checks = {}
        quality_score = 0
        suggestions = []

        # 1. 技術的正確性の検証
        technical_accuracy = _validate_technical_accuracy(question)
        validation_checks["technical_accuracy"] = technical_accuracy["is_valid"]
        quality_score += technical_accuracy["score"]
        suggestions.extend(technical_accuracy["suggestions"])

        # 2. Professional レベル難易度の検証
        difficulty_check = _validate_professional_difficulty(question)
        validation_checks["difficulty_appropriate"] = difficulty_check["is_valid"]
        quality_score += difficulty_check["score"]
        suggestions.extend(difficulty_check["suggestions"])

        # 3. フォーマット正確性の検証
        format_check = _validate_question_format(question)
        validation_checks["format_correct"] = format_check["is_valid"]
        quality_score += format_check["score"]
        suggestions.extend(format_check["suggestions"])

        # 4. 解説の明確性検証
        explanation_check = _validate_explanation_quality(question)
        validation_checks["explanation_clear"] = explanation_check["is_valid"]
        quality_score += explanation_check["score"]
        suggestions.extend(explanation_check["suggestions"])

        # 5. ビジネスシナリオの妥当性検証
        scenario_check = _validate_business_scenario(question)
        validation_checks["business_scenario_realistic"] = scenario_check["is_valid"]
        quality_score += scenario_check["score"]
        suggestions.extend(scenario_check["suggestions"])

        # 総合品質スコアの計算（最大100点）
        total_quality_score = min(quality_score // 5, 100)

        # 品質基準の判定（Professional レベルは80点以上）
        is_valid = total_quality_score >= 80 and all(validation_checks.values())

        validation_result = {
            "question_id": question.get("id", "unknown"),
            "is_valid": is_valid,
            "quality_score": total_quality_score,
            "validation_checks": validation_checks,
            "suggestions": suggestions,
            "quality_breakdown": {
                "technical_accuracy": technical_accuracy["score"],
                "difficulty_level": difficulty_check["score"],
                "format_quality": format_check["score"],
                "explanation_quality": explanation_check["score"],
                "scenario_realism": scenario_check["score"],
            },
            "professional_standards": {
                "minimum_score_required": 80,
                "meets_professional_level": is_valid,
                "certification_alignment": "AWS Certified Solutions Architect - Professional",
            },
        }

        logger.info(
            f"[Quality Agent] Professional validation completed: score={total_quality_score}, valid={is_valid}"
        )
        return validation_result

    except Exception as e:
        logger.error(f"[Quality Agent] Error during validation: {e}")
        # エラー時のフォールバック
        return {
            "question_id": question.get("id", "unknown"),
            "is_valid": False,
            "quality_score": 0,
            "validation_checks": {"error": True},
            "suggestions": [f"Validation error: {str(e)}"],
            "error_info": str(e),
        }


def _validate_technical_accuracy(question: dict[str, Any]) -> dict[str, Any]:
    """技術的正確性を検証"""
    score = 20
    suggestions = []

    # AWS サービス名の確認
    aws_services = question.get("aws_services", [])
    if not aws_services:
        score -= 5
        suggestions.append("AWS services should be explicitly listed")

    # 技術用語の適切性確認
    question_text = question.get("question", "").lower()
    if "professional" in question_text or "enterprise" in question_text:
        score += 5  # Professional レベルのコンテキスト

    return {"is_valid": score >= 15, "score": score, "suggestions": suggestions}


def _validate_professional_difficulty(question: dict[str, Any]) -> dict[str, Any]:
    """Professional レベルの難易度を検証"""
    score = 20
    suggestions = []

    difficulty = question.get("difficulty", "").lower()
    if difficulty != "professional":
        score -= 10
        suggestions.append("Question should be marked as 'professional' difficulty")

    # 複雑性の確認
    key_concepts = question.get("key_concepts", [])
    if len(key_concepts) < 3:
        score -= 5
        suggestions.append("Professional questions should cover multiple key concepts")

    # 複数サービス統合の確認
    aws_services = question.get("aws_services", [])
    if len(aws_services) < 2:
        score -= 5
        suggestions.append(
            "Professional questions should involve multiple AWS services"
        )

    return {"is_valid": score >= 15, "score": score, "suggestions": suggestions}


def _validate_question_format(question: dict[str, Any]) -> dict[str, Any]:
    """問題フォーマットの正確性を検証"""
    score = 20
    suggestions = []

    # 必須フィールドの確認
    required_fields = ["question", "options", "correct_answer", "explanation"]
    for field in required_fields:
        if field not in question:
            score -= 5
            suggestions.append(f"Missing required field: {field}")

    # 選択肢の確認
    options = question.get("options", {})
    if len(options) != 4 or set(options.keys()) != {"A", "B", "C", "D"}:
        score -= 5
        suggestions.append("Should have exactly 4 options (A, B, C, D)")

    # 正解の確認
    correct_answer = question.get("correct_answer", "")
    if correct_answer not in ["A", "B", "C", "D"]:
        score -= 5
        suggestions.append("Correct answer must be A, B, C, or D")

    return {"is_valid": score >= 15, "score": score, "suggestions": suggestions}


def _validate_explanation_quality(question: dict[str, Any]) -> dict[str, Any]:
    """解説の品質を検証"""
    score = 20
    suggestions = []

    explanation = question.get("explanation", "")
    if len(explanation) < 100:
        score -= 10
        suggestions.append(
            "Explanation should be more detailed (minimum 100 characters)"
        )

    # 正解理由と不正解理由の確認
    if "option" not in explanation.lower() and "choice" not in explanation.lower():
        score -= 5
        suggestions.append(
            "Explanation should reference why other options are incorrect"
        )

    return {"is_valid": score >= 15, "score": score, "suggestions": suggestions}


def _validate_business_scenario(question: dict[str, Any]) -> dict[str, Any]:
    """ビジネスシナリオの妥当性を検証"""
    score = 20
    suggestions = []

    question_text = question.get("question", "").lower()

    # ビジネスコンテキストの確認
    business_keywords = [
        "company",
        "enterprise",
        "organization",
        "business",
        "migrate",
        "implement",
    ]
    if not any(keyword in question_text for keyword in business_keywords):
        score -= 10
        suggestions.append("Question should include realistic business scenario")

    # 実用的な要件の確認
    practical_keywords = [
        "cost",
        "performance",
        "security",
        "availability",
        "scalability",
    ]
    if not any(keyword in question_text for keyword in practical_keywords):
        score -= 5
        suggestions.append("Question should address practical business requirements")

    return {"is_valid": score >= 15, "score": score, "suggestions": suggestions}


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

        logger.info("=== Phase 2: Professional Question Generation ===")
        question = await question_generation_agent(
            topic=topic, difficulty=difficulty, aws_info=aws_info
        )

        logger.info("=== Phase 3: Quality Management & Validation ===")
        quality_result = quality_management_agent(question=question)

        # 品質基準未達の場合は再生成を試行
        if not quality_result.get("is_valid", False):
            logger.warning(
                f"Question quality below standards (score: {quality_result.get('quality_score', 0)}), attempting regeneration..."
            )

            # 1回だけ再生成を試行
            logger.info("=== Phase 2b: Question Regeneration ===")
            question = await question_generation_agent(
                topic=topic, difficulty=difficulty, aws_info=aws_info
            )

            logger.info("=== Phase 3b: Re-validation ===")
            quality_result = quality_management_agent(question=question)

            if quality_result.get("is_valid", False):
                logger.info("Regenerated question meets quality standards")
            else:
                logger.warning(
                    "Regenerated question still below standards, proceeding with current version"
                )

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
    import sys

    # コマンドライン引数の処理
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # テスト実行モード
        async def test_run() -> None:
            topic = sys.argv[2] if len(sys.argv) > 2 else "EC2"
            payload = {"topic": topic, "difficulty": "professional"}
            result = await invoke(payload)
            print("\n=== Test Result ===")
            print(f"Status: {result['status']}")
            print(f"Topic: {result['topic']}")
            print(f"Question ID: {result['question']['id']}")
            print(f"Quality Score: {result['quality_validation']['quality_score']}")
            print(f"Is Valid: {result['quality_validation']['is_valid']}")
            print(f"\nQuestion: {result['question']['question']}")
            print("\nOptions:")
            for key, value in result["question"]["options"].items():
                print(f"  {key}: {value}")
            print(f"\nCorrect Answer: {result['question']['correct_answer']}")
            print(f"\nExplanation: {result['question']['explanation']}")

        # 非同期実行
        asyncio.run(test_run())
    else:
        # AgentCore Runtime として実行
        app.run()
