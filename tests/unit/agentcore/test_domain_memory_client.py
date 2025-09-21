#!/usr/bin/env python3
"""
AgentCore Memory クライアントのテスト

契約による設計に基づく包括的なテスト。
bedrock_agentcore.memory.DomainMemoryClient を使用した新しい実装に対応。
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from app.agentcore.domain_memory_client import DomainMemoryClient, MemoryEvent


class TestMemoryEvent:
    """MemoryEvent モデルの契約検証"""

    def test_valid_memory_event_contract(self) -> None:
        """
        事前条件: 有効なMemoryEventデータ
        事後条件: 正しいMemoryEventモデルが作成される
        不変条件: 必須フィールドが全て設定される
        """
        # Arrange - 事前条件設定
        event_data = {
            "learning_domain": "複雑な組織に対応するソリューションの設計",
            "exam_type": "AWS-SAP",
            "generated_at": "2025-09-21T10:00:00Z",
        }

        # Act
        event = MemoryEvent(**event_data)

        # Assert - 事後条件検証
        assert event.learning_domain == "複雑な組織に対応するソリューションの設計"
        assert event.exam_type == "AWS-SAP"
        assert event.generated_at == "2025-09-21T10:00:00Z"

        # 不変条件検証
        assert isinstance(event.learning_domain, str)
        assert len(event.learning_domain) > 0
        assert isinstance(event.exam_type, str)
        assert len(event.exam_type) > 0


class TestDomainMemoryClient:
    """DomainMemoryClient の契約検証"""

    @pytest.fixture
    def memory_client(self) -> DomainMemoryClient:
        """テスト用Memory クライアント"""
        with patch("app.agentcore.domain_memory_client.MemoryClient") as mock_memory_client:
            mock_client = MagicMock()
            mock_memory_client.return_value = mock_client

            client = DomainMemoryClient(
                memory_id="mem-test-12345", region_name="us-east-1"
            )
            client.client = mock_client
            return client

    @pytest.fixture
    def sample_event_data(self) -> MemoryEvent:
        """テスト用イベントデータ"""
        return MemoryEvent(
            learning_domain="セキュリティの設計",
            exam_type="AWS-SAP",
            generated_at="2025-09-21T10:00:00Z",
        )

    def test_client_initialization_contract(self) -> None:
        """
        事前条件: 有効なmemory_idとregion_name
        事後条件: 正しく初期化されたクライアント
        不変条件: bedrock_agentcore.memory.DomainMemoryClientが適切に設定される
        """
        # Arrange - 事前条件設定
        memory_id = "mem-test-12345"
        region_name = "us-east-1"

        # Act & Assert - DomainMemoryClientの呼び出しを検証
        with patch("app.agentcore.domain_memory_client.MemoryClient") as mock_memory_client:
            mock_client = MagicMock()
            mock_memory_client.return_value = mock_client

            client = DomainMemoryClient(memory_id, region_name)

            # 事後条件検証
            assert client.memory_id == memory_id
            assert client.region_name == region_name
            assert client.client == mock_client

            # 不変条件検証: DomainMemoryClientが適切な引数で呼ばれる
            mock_memory_client.assert_called_once_with(region_name=region_name)
            mock_memory_client.assert_called_once_with(region_name=region_name)

    async def test_create_event_success_contract(
        self, memory_client: DomainMemoryClient, sample_event_data: MemoryEvent
    ) -> None:
        """
        事前条件: 有効なactor_id、session_id、event_data
        事後条件: CreateEvent APIが正しく呼ばれ、レスポンスが返される
        不変条件: messagesが適切な形式で作成される
        """
        # Arrange - 事前条件設定
        actor_id = "cloud-copass-agent"
        session_id = "AWS-SAP-generation"
        expected_response = {"eventId": "event-12345"}

        memory_client.client.create_event.return_value = expected_response  # type: ignore[attr-defined]

        # Act
        with patch("app.agentcore.domain_memory_client.datetime") as mock_datetime:
            mock_now = datetime(2025, 9, 21, 10, 0, 0)
            mock_datetime.now.return_value = mock_now

            result = await memory_client.create_event(
                actor_id=actor_id, session_id=session_id, event_data=sample_event_data
            )

        # Assert - 事後条件検証
        assert result == expected_response

        # 不変条件検証: create_eventが正しい引数で呼ばれる
        expected_messages = [
            ("user", f"学習分野: {sample_event_data.learning_domain}"),
            (
                "assistant",
                f"試験タイプ: {sample_event_data.exam_type}, 生成日時: {sample_event_data.generated_at}",
            ),
        ]
        memory_client.client.create_event.assert_called_once_with(  # type: ignore[attr-defined]
            memory_id="mem-test-12345",
            actor_id=actor_id,
            session_id=session_id,
            messages=expected_messages,
            event_timestamp=mock_now,
        )

    async def test_create_event_api_error_precondition(
        self, memory_client: DomainMemoryClient, sample_event_data: MemoryEvent
    ) -> None:
        """
        事前条件違反: CreateEvent API呼び出しが失敗
        事後条件: 適切な例外が発生する
        """
        # Arrange - 事前条件違反: API エラー
        memory_client.client.create_event.side_effect = Exception("API Error")  # type: ignore[attr-defined]

        # Act & Assert - 事前条件検証
        with pytest.raises(Exception, match="API Error"):
            await memory_client.create_event(
                actor_id="cloud-copass-agent",
                session_id="AWS-SAP-generation",
                event_data=sample_event_data,
            )

    async def test_list_events_success_contract(
        self, memory_client: DomainMemoryClient
    ) -> None:
        """
        事前条件: 有効なactor_id、session_id
        事後条件: ListEvents APIが正しく呼ばれ、フィルタリングされたイベントが返される
        不変条件: 指定日数以内のイベントのみが返される
        """
        # Arrange - 事前条件設定
        actor_id = "cloud-copass-agent"
        session_id = "AWS-SAP-generation"

        # 現在時刻と過去のイベントを設定
        now = datetime.now()
        recent_time = now - timedelta(days=3)  # 3日前（範囲内）
        old_time = now - timedelta(days=10)  # 10日前（範囲外）

        mock_events = [
            {
                "eventId": "event-1",
                "event_timestamp": recent_time,  # datetime オブジェクト
                "messages": [("user", "学習分野: セキュリティの設計")],
            },
            {
                "eventId": "event-2",
                "event_timestamp": old_time,  # datetime オブジェクト
                "messages": [("user", "学習分野: 古い分野")],
            },
        ]

        memory_client.client.list_events.return_value = mock_events  # type: ignore[attr-defined]

        # Act
        result = await memory_client.list_events(
            actor_id=actor_id, session_id=session_id, max_results=10, days_back=7
        )

        # Assert - 事後条件検証
        assert len(result) == 1  # 7日以内のイベントのみ
        assert result[0]["eventId"] == "event-1"

        # 不変条件検証: list_eventsが正しい引数で呼ばれる
        memory_client.client.list_events.assert_called_once_with(  # type: ignore[attr-defined]
            memory_id="mem-test-12345",
            actor_id=actor_id,
            session_id=session_id,
            max_results=10,
            include_payload=True,
        )

    async def test_get_recent_domains_success_contract(
        self, memory_client: DomainMemoryClient
    ) -> None:
        """
        事前条件: 有効なexam_type
        事後条件: 最近の学習分野リストが重複なしで返される
        不変条件: 学習分野の順序が保持される
        """
        # Arrange - 事前条件設定
        exam_type = "AWS-SAP"

        # list_eventsをモック
        mock_events = [
            {
                "eventId": "event-1",
                "messages": [("user", "学習分野: セキュリティの設計")],
            },
            {"eventId": "event-2", "messages": [("user", "学習分野: 信頼性の設計")]},
            {
                "eventId": "event-3",
                "messages": [("user", "学習分野: セキュリティの設計")],  # 重複
            },
        ]

        with patch.object(memory_client, "list_events", return_value=mock_events):
            # Act
            result = await memory_client.get_recent_domains(exam_type)

        # Assert - 事後条件検証
        assert len(result) == 2  # 重複除去
        assert result == ["セキュリティの設計", "信頼性の設計"]

        # 不変条件検証: 順序が保持される
        assert result[0] == "セキュリティの設計"  # 最初に出現した分野が最初

    async def test_get_recent_domains_api_error_invariant(
        self, memory_client: DomainMemoryClient
    ) -> None:
        """
        不変条件: API エラー時は空リストを返して処理継続
        """
        # Arrange - API エラーを設定
        with patch.object(
            memory_client, "list_events", side_effect=Exception("API Error")
        ):
            # Act
            result = await memory_client.get_recent_domains("AWS-SAP")

        # Assert - 不変条件検証
        assert result == []  # エラー時は空リスト

    async def test_record_domain_usage_success_contract(
        self, memory_client: DomainMemoryClient
    ) -> None:
        """
        事前条件: 有効なlearning_domain、exam_type
        事後条件: create_eventが適切な引数で呼ばれる
        不変条件: 現在時刻でイベントが作成される
        """
        # Arrange - 事前条件設定
        learning_domain = "複雑な組織に対応するソリューションの設計"
        exam_type = "AWS-SAP"

        # create_eventをモック
        with patch.object(memory_client, "create_event") as mock_create_event:
            mock_create_event.return_value = {"eventId": "event-12345"}

            # Act
            with patch("app.agentcore.domain_memory_client.datetime") as mock_datetime:
                mock_now = datetime(2025, 9, 21, 10, 0, 0)
                mock_datetime.now.return_value = mock_now

                await memory_client.record_domain_usage(learning_domain, exam_type)

        # Assert - 事後条件検証
        mock_create_event.assert_called_once()
        call_args = mock_create_event.call_args

        assert call_args[1]["actor_id"] == "cloud-copass-agent"
        assert call_args[1]["session_id"] == "AWS-SAP-generation"

        # 不変条件検証: イベントデータが正しく設定される
        event_data = call_args[1]["event_data"]
        assert event_data.learning_domain == learning_domain
        assert event_data.exam_type == exam_type
        assert event_data.generated_at == mock_now.isoformat()

    async def test_record_domain_usage_error_invariant(
        self, memory_client: DomainMemoryClient
    ) -> None:
        """
        不変条件: create_event エラー時も例外を発生させず処理継続
        """
        # Arrange - create_event エラーを設定
        with patch.object(
            memory_client, "create_event", side_effect=Exception("API Error")
        ):
            # Act & Assert - 例外が発生しないことを確認
            try:
                await memory_client.record_domain_usage("テスト分野", "AWS-SAP")
                # 例外が発生しなければ成功
            except Exception:
                pytest.fail("record_domain_usage should not raise exceptions")
