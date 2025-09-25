#!/usr/bin/env python3
"""
AgentCore Memory クライアント

bedrock_agentcore.memory.MemoryClient を活用したシンプルな実装。
"""

import logging
from datetime import datetime
from typing import Any

from bedrock_agentcore.memory import MemoryClient

logger = logging.getLogger(__name__)

# Memory設定定数
# 30日間の履歴を十分カバーする件数設定
# - Memory自動削除: 30日経過後（eventExpiryDuration=30）
# - 想定使用頻度: 毎日1回実行 = 最大30件
# - 将来拡張対応: 1日複数回実行や複数問題生成にも対応
# - API制限考慮: AgentCore Memory API最大100件まで取得可能
DEFAULT_MAX_RESULTS = 50


class DomainMemoryClient:
    """AgentCore Memory API クライアント

    bedrock_agentcore.memory.MemoryClient を活用したシンプルな実装。
    """

    def __init__(self, memory_id: str, region_name: str = "us-east-1") -> None:
        """Memory クライアントを初期化

        Args:
            memory_id: AgentCore Memory リソースID
            region_name: AWS リージョン（デフォルト: us-east-1）
        """
        self.memory_id = memory_id
        self.region_name = region_name

        # bedrock_agentcore の MemoryClient を使用
        self.client = MemoryClient(region_name=region_name)

        logger.info(
            f"AgentCore Memory クライアント初期化完了: memory_id={memory_id}, region={region_name}"
        )

    async def create_event(
        self, actor_id: str, session_id: str, learning_domain: str
    ) -> dict[str, Any]:
        """Memory にイベントを作成

        Args:
            actor_id: アクター識別子（例: "cloud-copass-agent"）
            session_id: セッション識別子（例: "AWS-SAP"）
            learning_domain: 学習分野名

        Returns:
            CreateEvent API のレスポンス

        Raises:
            Exception: API 呼び出しに失敗した場合
        """
        try:
            # bedrock_agentcore.memory.MemoryClient の create_event を使用
            # シンプルに学習分野名のみを記録
            messages = [(learning_domain, "USER")]

            response = self.client.create_event(
                memory_id=self.memory_id,
                actor_id=actor_id,
                session_id=session_id,
                messages=messages,
                event_timestamp=datetime.now(),
            )

            logger.info(
                f"Memory イベント作成成功: session_id={session_id}, domain={learning_domain}"
            )
            return response

        except Exception as e:
            logger.error(f"Memory イベント作成失敗: {e}")
            raise

    async def list_events(
        self, actor_id: str, session_id: str, max_results: int = DEFAULT_MAX_RESULTS
    ) -> list[dict[str, Any]]:
        """Memory からイベントを一覧取得

        Args:
            actor_id: アクター識別子
            session_id: セッション識別子
            max_results: 最大取得件数（デフォルト: DEFAULT_MAX_RESULTS、30日間の履歴を十分カバー）

        Returns:
            イベントのリスト（Memory設定により30日以内のイベントのみ）

        Raises:
            Exception: API 呼び出しに失敗した場合

        Note:
            Memory作成時にeventExpiryDuration=30を設定しているため、
            30日経過後のイベントはAWS側で自動削除される。
            クライアント側でのフィルタリング処理は不要。
        """
        try:
            # bedrock_agentcore.memory.MemoryClient の list_events を使用
            # Memory設定により30日以内のイベントのみ取得される
            events = self.client.list_events(
                memory_id=self.memory_id,
                actor_id=actor_id,
                session_id=session_id,
                max_results=max_results,
                include_payload=True,
            )

            logger.info(
                f"Memory イベント取得成功: session_id={session_id}, 件数={len(events)}"
            )
            return events

        except Exception as e:
            logger.error(f"Memory イベント取得失敗: {e}")
            raise

    async def get_recent_domains(self, exam_type: str) -> list[str]:
        """最近使用された学習分野を取得

        Args:
            exam_type: 試験タイプ

        Returns:
            最近使用された学習分野のリスト（重複なし、30日以内）

        Note:
            Memory設定により30日経過後のイベントは自動削除されるため、
            取得されるイベントは全て30日以内のものとなる。
        """
        try:
            actor_id = "cloud-copass-agent"
            session_id = exam_type

            events = await self.list_events(
                actor_id=actor_id,
                session_id=session_id,
                max_results=DEFAULT_MAX_RESULTS,
            )

            # 学習分野を抽出（重複除去）
            recent_domains = []
            for event in events:
                # payload から学習分野を取得
                payload = event.get("payload", [])
                for item in payload:
                    if "conversational" in item:
                        content = item["conversational"].get("content", {})
                        text = content.get("text", "")
                        role = item["conversational"].get("role", "")
                        if role == "USER" and text and text not in recent_domains:
                            recent_domains.append(text)
                            break

            logger.info(
                f"最近の学習分野取得: exam_type={exam_type}, domains={recent_domains}"
            )
            return recent_domains

        except Exception as e:
            logger.warning(f"最近の学習分野取得に失敗（処理継続）: {e}")
            return []  # エラー時は空リストを返して処理継続

    async def record_domain_usage(self, learning_domain: str, exam_type: str) -> None:
        """学習分野の使用を記録

        Args:
            learning_domain: 使用した学習分野
            exam_type: 試験タイプ
        """
        try:
            actor_id = "cloud-copass-agent"
            session_id = exam_type

            await self.create_event(
                actor_id=actor_id,
                session_id=session_id,
                learning_domain=learning_domain,
            )
            # ログは create_event メソッド内で出力されるため、ここでは不要

        except Exception as e:
            logger.warning(f"学習分野使用記録に失敗（処理継続）: {e}")
            # エラーが発生しても問題生成処理は継続する
