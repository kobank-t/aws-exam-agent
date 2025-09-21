#!/usr/bin/env python3
"""
AgentCore Memory クライアント

bedrock_agentcore.memory.MemoryClient を活用したシンプルな実装。
"""

import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from bedrock_agentcore.memory import MemoryClient

logger = logging.getLogger(__name__)


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
        self, actor_id: str, session_id: str, max_results: int = 10, days_back: int = 7
    ) -> list[dict[str, Any]]:
        """Memory からイベントを一覧取得

        Args:
            actor_id: アクター識別子
            session_id: セッション識別子
            max_results: 最大取得件数（デフォルト: 10）
            days_back: 何日前まで取得するか（デフォルト: 7日）

        Returns:
            イベントのリスト

        Raises:
            Exception: API 呼び出しに失敗した場合
        """
        try:
            # bedrock_agentcore.memory.MemoryClient の list_events を使用
            events = self.client.list_events(
                memory_id=self.memory_id,
                actor_id=actor_id,
                session_id=session_id,
                max_results=max_results,
                include_payload=True,
            )

            # 指定日数以内のイベントのみフィルタリング
            cutoff_date = datetime.now() - timedelta(days=days_back)
            recent_events = []

            for event in events:
                # eventTimestamp の形式を確認して適切に処理
                event_time = event.get("eventTimestamp")
                if isinstance(event_time, datetime):
                    # タイムゾーン付きの場合はUTCに変換してからnaiveに変換
                    if event_time.tzinfo is not None:
                        event_time_naive = event_time.astimezone(UTC).replace(
                            tzinfo=None
                        )
                    else:
                        event_time_naive = event_time
                    if event_time_naive > cutoff_date:
                        recent_events.append(event)
                elif isinstance(event_time, str):
                    # ISO 8601 文字列の場合（例: "2025-09-22 09:12:24+09:00"）
                    try:
                        event_datetime = datetime.fromisoformat(event_time)
                        # UTCに変換してからタイムゾーン情報を除去
                        event_datetime_utc = event_datetime.astimezone(UTC).replace(
                            tzinfo=None
                        )
                        if event_datetime_utc > cutoff_date:
                            recent_events.append(event)
                    except ValueError:
                        # パース失敗時はスキップ
                        continue
                elif isinstance(event_time, int | float):
                    # Unix timestamp の場合
                    event_datetime = datetime.fromtimestamp(event_time)
                    if event_datetime > cutoff_date:
                        recent_events.append(event)

            logger.info(
                f"Memory イベント取得成功: session_id={session_id}, 件数={len(recent_events)}"
            )
            return recent_events

        except Exception as e:
            logger.error(f"Memory イベント取得失敗: {e}")
            raise

    async def get_recent_domains(self, exam_type: str, days_back: int = 7) -> list[str]:
        """最近使用された学習分野を取得

        Args:
            exam_type: 試験タイプ
            days_back: 何日前まで取得するか（デフォルト: 7日）

        Returns:
            最近使用された学習分野のリスト（重複なし）
        """
        try:
            actor_id = "cloud-copass-agent"
            session_id = (
                exam_type  # AWS-SAP → 実際のnamespace: learning-domains/AWS-SAP
            )

            events = await self.list_events(
                actor_id=actor_id,
                session_id=session_id,
                max_results=10,
                days_back=days_back,
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
            session_id = (
                exam_type  # AWS-SAP → 実際のnamespace: learning-domains/AWS-SAP
            )

            await self.create_event(
                actor_id=actor_id,
                session_id=session_id,
                learning_domain=learning_domain,
            )

            logger.info(
                f"Memory イベント作成成功: session_id={session_id}, domain={learning_domain}"
            )

        except Exception as e:
            logger.warning(f"学習分野使用記録に失敗（処理継続）: {e}")
            # エラーが発生しても問題生成処理は継続する
