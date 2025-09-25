#!/usr/bin/env python3
"""
DomainMemoryClient のテスト

契約による設計（Design by Contract）に基づく単体テスト
"""

from datetime import datetime
from unittest.mock import patch

import pytest

from app.agentcore.domain_memory_client import DEFAULT_MAX_RESULTS, DomainMemoryClient


class TestDomainMemoryClient:
    """DomainMemoryClient の契約検証"""

    @pytest.fixture
    def memory_client(self) -> DomainMemoryClient:
        """テスト用のDomainMemoryClientインスタンス"""
        return DomainMemoryClient(memory_id="test-memory-id", region_name="us-east-1")

    async def test_create_event_contract(
        self, memory_client: DomainMemoryClient
    ) -> None:
        """
        事前条件: 有効なactor_id、session_id、learning_domain
        事後条件: CreateEvent APIが正しく呼び出される
        不変条件: Memory IDとリージョンが保持される
        """
        # Arrange - 事前条件設定
        actor_id = "cloud-copass-agent"
        session_id = "AWS-SAP"
        learning_domain = "コンピューティング"

        mock_response = {"eventId": "test-event-id"}

        with patch.object(memory_client.client, "create_event") as mock_create:
            mock_create.return_value = mock_response

            # Act
            result = await memory_client.create_event(
                actor_id=actor_id,
                session_id=session_id,
                learning_domain=learning_domain,
            )

        # Assert - 事後条件検証
        assert result == mock_response
        mock_create.assert_called_once()

        # 不変条件検証
        assert memory_client.memory_id == "test-memory-id"
        assert memory_client.region_name == "us-east-1"

    async def test_list_events_contract(
        self, memory_client: DomainMemoryClient
    ) -> None:
        """
        事前条件: 有効なactor_id、session_id
        事後条件: ListEvents APIが正しく呼び出される
        不変条件: Memory設定により30日以内のイベントのみ取得される
        """
        # Arrange - 事前条件設定
        actor_id = "cloud-copass-agent"
        session_id = "AWS-SAP"

        mock_events = [
            {
                "eventId": "event-1",
                "eventTimestamp": datetime.now(),
                "payload": [
                    {
                        "conversational": {
                            "content": {"text": "コンピューティング"},
                            "role": "USER",
                        }
                    }
                ],
            },
            {
                "eventId": "event-2",
                "eventTimestamp": datetime.now(),
                "payload": [
                    {
                        "conversational": {
                            "content": {"text": "ネットワーク"},
                            "role": "USER",
                        }
                    }
                ],
            },
        ]

        with patch.object(memory_client.client, "list_events") as mock_list_events:
            mock_list_events.return_value = mock_events

            # Act
            result = await memory_client.list_events(
                actor_id=actor_id, session_id=session_id
            )

        # Assert - 事後条件検証
        assert len(result) == 2  # Memory設定により30日以内のイベントのみ
        assert result[0]["eventId"] == "event-1"
        assert result[1]["eventId"] == "event-2"

        # 不変条件検証: 正しいパラメータで呼び出される
        mock_list_events.assert_called_once_with(
            memory_id="test-memory-id",
            actor_id=actor_id,
            session_id=session_id,
            max_results=DEFAULT_MAX_RESULTS,
            include_payload=True,
        )

    async def test_get_recent_domains_contract(
        self, memory_client: DomainMemoryClient
    ) -> None:
        """
        事前条件: 有効なexam_type
        事後条件: 最近使用された学習分野のリストが返される
        不変条件: 重複なしのリストが返される
        """
        # Arrange - 事前条件設定
        exam_type = "AWS-SAP"

        mock_events = [
            {
                "eventId": "event-1",
                "payload": [
                    {
                        "conversational": {
                            "content": {"text": "コンピューティング"},
                            "role": "USER",
                        }
                    }
                ],
            },
            {
                "eventId": "event-2",
                "payload": [
                    {
                        "conversational": {
                            "content": {"text": "ネットワーク"},
                            "role": "USER",
                        }
                    }
                ],
            },
            {
                "eventId": "event-3",
                "payload": [
                    {
                        "conversational": {
                            "content": {"text": "コンピューティング"},  # 重複
                            "role": "USER",
                        }
                    }
                ],
            },
        ]

        with patch.object(memory_client, "list_events") as mock_list_events:
            mock_list_events.return_value = mock_events

            # Act
            result = await memory_client.get_recent_domains(exam_type)

        # Assert - 事後条件検証
        assert isinstance(result, list)
        assert len(result) == 2  # 重複除去済み
        assert "コンピューティング" in result
        assert "ネットワーク" in result

        # 不変条件検証: 重複なしのリスト
        assert len(result) == len(set(result))

    async def test_record_domain_usage_contract(
        self, memory_client: DomainMemoryClient
    ) -> None:
        """
        事前条件: 有効なlearning_domain、exam_type
        事後条件: create_eventが正しく呼び出される
        不変条件: エラー時も処理が継続される
        """
        # Arrange - 事前条件設定
        learning_domain = "コンピューティング"
        exam_type = "AWS-SAP"

        with patch.object(memory_client, "create_event") as mock_create_event:
            mock_create_event.return_value = {"eventId": "test-event-id"}

            # Act
            await memory_client.record_domain_usage(learning_domain, exam_type)

        # Assert - 事後条件検証
        mock_create_event.assert_called_once_with(
            actor_id="cloud-copass-agent",
            session_id=exam_type,
            learning_domain=learning_domain,
        )

    async def test_error_handling_invariant(
        self, memory_client: DomainMemoryClient
    ) -> None:
        """
        不変条件: API エラー時も適切にハンドリングされる
        """
        # Arrange - エラー条件設定
        with patch.object(memory_client.client, "list_events") as mock_list_events:
            mock_list_events.side_effect = Exception("Memory API Error")

            # Act & Assert - 不変条件検証
            with pytest.raises(Exception, match="Memory API Error"):
                await memory_client.list_events(
                    actor_id="cloud-copass-agent", session_id="AWS-SAP"
                )

    async def test_get_recent_domains_error_handling_invariant(
        self, memory_client: DomainMemoryClient
    ) -> None:
        """
        不変条件: get_recent_domains エラー時は空リストを返して処理継続
        """
        # Arrange - エラー条件設定
        with patch.object(memory_client, "list_events") as mock_list_events:
            mock_list_events.side_effect = Exception("Memory API Error")

            # Act
            result = await memory_client.get_recent_domains("AWS-SAP")

        # Assert - 不変条件検証: エラー時は空リストを返す
        assert result == []

    async def test_record_domain_usage_error_handling_invariant(
        self, memory_client: DomainMemoryClient
    ) -> None:
        """
        不変条件: record_domain_usage エラー時も処理継続（例外を再発生させない）
        """
        # Arrange - エラー条件設定
        with patch.object(memory_client, "create_event") as mock_create_event:
            mock_create_event.side_effect = Exception("Memory API Error")

            # Act - 不変条件検証: 例外が発生しない
            await memory_client.record_domain_usage("コンピューティング", "AWS-SAP")

        # Assert - 事後条件検証: create_eventが呼び出された
        mock_create_event.assert_called_once()
