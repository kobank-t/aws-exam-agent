"""
AWS Exam Agent - EventBridge Scheduler Trigger Function

EventBridge SchedulerからAgentCore Runtimeを呼び出すLambda関数
"""

import json
import logging
from typing import Any

import boto3

# ログ設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """
    EventBridge SchedulerからのトリガーでAgentCore Runtimeを呼び出す

    Args:
        event: EventBridge Schedulerからのイベント
        context: Lambda実行コンテキスト

    Returns:
        実行結果のレスポンス
    """
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        logger.info(f"boto3 version: {boto3.__version__}")

        # 必須パラメータの確認
        required_params = ["agentRuntimeArn", "exam_type", "question_count"]
        for param in required_params:
            if param not in event:
                raise ValueError(f"Missing required parameter: {param}")

        # AgentCore Runtime呼び出し
        client = boto3.client("bedrock-agentcore")

        agent_runtime_arn = event["agentRuntimeArn"]
        payload = {
            "exam_type": event["exam_type"],
            "question_count": event["question_count"],
        }

        logger.info(f"Invoking AgentCore Runtime: {agent_runtime_arn}")
        logger.info(f"Payload: {json.dumps(payload)}")

        response = client.invoke_agent_runtime(
            agentRuntimeArn=agent_runtime_arn,
            payload=json.dumps(payload).encode("utf-8"),
            contentType="application/json",
            accept="application/json",
        )

        logger.info("AgentCore invocation successful")
        logger.info(f"Response content type: {response.get('contentType', 'unknown')}")

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "message": "Question generation triggered successfully",
                    "agentRuntimeArn": agent_runtime_arn,
                    "payload": payload,
                    "responseContentType": response.get("contentType", "unknown"),
                }
            ),
        }

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Validation error", "message": str(e)}),
        }

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error", "message": str(e)}),
        }
