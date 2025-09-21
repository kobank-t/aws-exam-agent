#!/usr/bin/env python3
"""
DomainMemoryClient の契約検証テスト

シンプル化されたMemory機能のテスト
"""

from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from app.agentcore.domain_memory_client import DomainMemoryClient


class TestDomainMemoryClient:
    """DomainMemoryClient の契約検証"""

    @pytest.fixture
    def memory_client(self) -> DomainMemoryClient:
        """テスト用メモリクライアント"""
        return DomainMemoryClient(memory_id="mem-test-12345", region_name="us-east-1")

    @pytest.fixture
    def sample_learning_domain(self) -> str:
        """テスト用学習分野データ"""
        return "セキュリティの設計"

    def test_client_initialization_contract(self) -> None:
        """
        事前条件: 有効なmemory_idとregion_name
        事後条件: 正しく初期化されたクライアント
        不変条件: bedrock_agentcore.memory.MemoryClientが適切に設定される
        """
        # Arrange - 事前条件設定
        memory_id = "mem-test-12345"
        region_name = "us-east-1"

        # Act
        client = DomainMemoryClient(memory_id=memory_id, region_name=region_name)

        # Assert - 事後条件検証
        assert client.memory_id == memory_id
        assert client.region_name == region_name

        # 不変条件検証
        assert client.client is not None

    async def test_record_domain_usage_success_contract(
        self, memory_client: DomainMemoryClient, sample_learning_domain: str
    ) -> None:
        """
        事前条件: 有効なlearning_domain、exam_type
        事後条件: create_eventが適切な引数で呼ばれる
        不変条件: 現在時刻でイベントが作成される
        """
        # Arrange - 事前条件設定
        exam_type = "AWS-SAP"

        # create_eventをモック
        with patch.object(memory_client.client, "create_event") as mock_create_event:
            mock_create_event.return_value = {"eventId": "event-12345"}

            # Act
            with patch("app.agentcore.domain_memory_client.datetime") as mock_datetime:
                mock_now = datetime(2025, 9, 21, 10, 0, 0)
                mock_datetime.now.return_value = mock_now

                await memory_client.record_domain_usage(
                    sample_learning_domain, exam_type
                )

        # Assert - 事後条件検証
        mock_create_event.assert_called_once()
        call_args = mock_create_event.call_args

        assert call_args[1]["memory_id"] == "mem-test-12345"
        assert call_args[1]["actor_id"] == "cloud-copass-agent"
        assert call_args[1]["session_id"] == "AWS-SAP"
        assert call_args[1]["messages"] == [(sample_learning_domain, "USER")]
        assert call_args[1]["event_timestamp"] == mock_now

    async def test_get_recent_domains_success_contract(
        self, memory_client: DomainMemoryClient
    ) -> None:
        """
        事前条件: 有効なexam_type
        事後条件: 最近の学習分野リストが返される
        不変条件: 重複なしのリストが返される
        """
        # Arrange - 事前条件設定
        exam_type = "AWS-SAP"

        # 現在時刻と過去のイベントを設定
        now = datetime.now()
        recent_time = now - timedelta(days=3)  # 3日前（範囲内）
        old_time = now - timedelta(days=10)  # 10日前（範囲外）

        mock_events = [
            {
                "eventId": "event-1",
                "eventTimestamp": recent_time.isoformat() + "+09:00",
                "payload": [
                    {
                        "conversational": {
                            "content": {"text": "セキュリティの設計"},
                            "role": "USER",
                        }
                    }
                ],
            },
            {
                "eventId": "event-2",
                "eventTimestamp": old_time.isoformat() + "+09:00",
                "payload": [
                    {
                        "conversational": {
                            "content": {"text": "古い分野"},
                            "role": "USER",
                        }
                    }
                ],
            },
        ]

        with patch.object(memory_client, "list_events") as mock_list_events:
            mock_list_events.return_value = mock_events

            # Act
            result = await memory_client.get_recent_domains(exam_type, days_back=7)

        # Assert - 事後条件検証
        assert isinstance(result, list)
        assert "セキュリティの設計" in result

        # 不変条件検証: 重複なし
        assert len(result) == len(set(result))

    async def test_get_recent_domains_deduplication_invariant(
        self, memory_client: DomainMemoryClient
    ) -> None:
        """
        不変条件: 重複する学習分野は除去される
        """
        # Arrange - 重複データを含むイベント
        now = datetime.now()
        recent_time = now - timedelta(days=1)  # 1日前（範囲内）

        mock_events = [
            {
                "eventId": "event-1",
                "eventTimestamp": recent_time.isoformat() + "+09:00",
                "payload": [
                    {
                        "conversational": {
                            "content": {"text": "セキュリティの設計"},
                            "role": "USER",
                        }
                    }
                ],
            },
            {
                "eventId": "event-2",
                "eventTimestamp": recent_time.isoformat() + "+09:00",
                "payload": [
                    {
                        "conversational": {
                            "content": {"text": "信頼性の設計"},
                            "role": "USER",
                        }
                    }
                ],
            },
            {
                "eventId": "event-3",
                "eventTimestamp": recent_time.isoformat() + "+09:00",
                "payload": [
                    {
                        "conversational": {
                            "content": {"text": "セキュリティの設計"},
                            "role": "USER",
                        }
                    }
                ],
            },  # 重複
        ]

        with patch.object(memory_client, "list_events") as mock_list_events:
            mock_list_events.return_value = mock_events

            # Act
            result = await memory_client.get_recent_domains("AWS-SAP")

        # Assert - 不変条件検証
        assert len(result) == 2  # 重複除去されて2つ
        assert "セキュリティの設計" in result
        assert "信頼性の設計" in result

    async def test_record_domain_usage_error_invariant(
        self, memory_client: DomainMemoryClient, sample_learning_domain: str
    ) -> None:
        """
        不変条件: エラー発生時も処理が継続される
        """
        # Arrange - create_eventでエラーが発生する設定
        with patch.object(memory_client.client, "create_event") as mock_create_event:
            mock_create_event.side_effect = Exception("Memory API Error")

            # Act & Assert - 不変条件検証（例外が発生しない）
            try:
                await memory_client.record_domain_usage(
                    sample_learning_domain, "AWS-SAP"
                )
                # エラーが発生しても例外は発生しない（ログ出力のみ）
            except Exception:
                pytest.fail("record_domain_usage should not raise exceptions")

    async def test_get_recent_domains_error_invariant(
        self, memory_client: DomainMemoryClient
    ) -> None:
        """
        不変条件: エラー発生時は空リストが返される
        """
        # Arrange - list_eventsでエラーが発生する設定
        with patch.object(memory_client, "list_events") as mock_list_events:
            mock_list_events.side_effect = Exception("Memory API Error")

            # Act
            result = await memory_client.get_recent_domains("AWS-SAP")

        # Assert - 不変条件検証
        assert result == []  # エラー時は空リスト

    async def test_list_events_unix_timestamp_contract(
        self, memory_client: DomainMemoryClient
    ) -> None:
        """
        事前条件: Unix timestamp形式のイベント
        事後条件: 適切に日時変換されてフィルタリングされる
        不変条件: 指定日数以内のイベントのみが返される
        """
        # Arrange - Unix timestamp形式のイベント
        now = datetime.now()
        recent_timestamp = (now - timedelta(days=3)).timestamp()  # 3日前（範囲内）
        old_timestamp = (now - timedelta(days=10)).timestamp()  # 10日前（範囲外）

        mock_events = [
            {
                "eventId": "event-1",
                "eventTimestamp": recent_timestamp,  # Unix timestamp
                "payload": [
                    {
                        "conversational": {
                            "content": {"text": "セキュリティの設計"},
                            "role": "USER",
                        }
                    }
                ],
            },
            {
                "eventId": "event-2",
                "eventTimestamp": old_timestamp,  # Unix timestamp
                "payload": [
                    {
                        "conversational": {
                            "content": {"text": "古い分野"},
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
                actor_id="cloud-copass-agent", session_id="AWS-SAP", days_back=7
            )

        # Assert - 事後条件検証
        assert len(result) == 1  # 範囲内のイベントのみ
        assert result[0]["eventId"] == "event-1"

    async def test_list_events_naive_datetime_contract(
        self, memory_client: DomainMemoryClient
    ) -> None:
        """
        事前条件: タイムゾーンなしのdatetimeオブジェクト
        事後条件: 適切にフィルタリングされる
        不変条件: 指定日数以内のイベントのみが返される
        """
        # Arrange - タイムゾーンなしのdatetimeイベント
        now = datetime.now()
        recent_time = now - timedelta(days=3)  # 3日前（範囲内）
        old_time = now - timedelta(days=10)  # 10日前（範囲外）

        mock_events = [
            {
                "eventId": "event-1",
                "eventTimestamp": recent_time,  # naive datetime
                "payload": [
                    {
                        "conversational": {
                            "content": {"text": "セキュリティの設計"},
                            "role": "USER",
                        }
                    }
                ],
            },
            {
                "eventId": "event-2",
                "eventTimestamp": old_time,  # naive datetime
                "payload": [
                    {
                        "conversational": {
                            "content": {"text": "古い分野"},
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
                actor_id="cloud-copass-agent", session_id="AWS-SAP", days_back=7
            )

        # Assert - 事後条件検証
        assert len(result) == 1  # 範囲内のイベントのみ
        assert result[0]["eventId"] == "event-1"

    async def test_list_events_invalid_iso_string_contract(
        self, memory_client: DomainMemoryClient
    ) -> None:
        """
        事前条件: 無効なISO 8601文字列
        事後条件: ValueErrorが発生してもスキップされる
        不変条件: 有効なイベントのみが返される
        """
        # Arrange - 無効なISO文字列を含むイベント
        now = datetime.now()
        valid_time = now - timedelta(days=1)

        mock_events = [
            {
                "eventId": "event-1",
                "eventTimestamp": "invalid-datetime-string",  # 無効な文字列
                "payload": [
                    {
                        "conversational": {
                            "content": {"text": "無効な分野"},
                            "role": "USER",
                        }
                    }
                ],
            },
            {
                "eventId": "event-2",
                "eventTimestamp": valid_time.isoformat() + "+09:00",  # 有効な文字列
                "payload": [
                    {
                        "conversational": {
                            "content": {"text": "有効な分野"},
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
                actor_id="cloud-copass-agent", session_id="AWS-SAP", days_back=7
            )

        # Assert - 事後条件検証
        assert len(result) == 1  # 有効なイベントのみ
        assert result[0]["eventId"] == "event-2"

    async def test_get_recent_domains_empty_payload_contract(
        self, memory_client: DomainMemoryClient
    ) -> None:
        """
        事前条件: payloadが空のイベント
        事後条件: 空のリストが返される
        不変条件: エラーが発生しない
        """
        # Arrange - payloadが空のイベント
        now = datetime.now()
        recent_time = now - timedelta(days=1)

        mock_events = [
            {
                "eventId": "event-1",
                "eventTimestamp": recent_time.isoformat() + "+09:00",
                "payload": [],  # 空のpayload
            },
            {
                "eventId": "event-2",
                "eventTimestamp": recent_time.isoformat() + "+09:00",
                # payloadキーなし
            },
        ]

        with patch.object(memory_client, "list_events") as mock_list_events:
            mock_list_events.return_value = mock_events

            # Act
            result = await memory_client.get_recent_domains("AWS-SAP")

        # Assert - 事後条件検証
        assert result == []  # 空のリスト

    async def test_get_recent_domains_malformed_payload_contract(
        self, memory_client: DomainMemoryClient
    ) -> None:
        """
        事前条件: 不正な形式のpayload
        事後条件: エラーが発生せず処理が継続される
        不変条件: 有効なデータのみが抽出される
        """
        # Arrange - 不正な形式のpayloadを含むイベント
        now = datetime.now()
        recent_time = now - timedelta(days=1)

        mock_events = [
            {
                "eventId": "event-1",
                "eventTimestamp": recent_time.isoformat() + "+09:00",
                "payload": [
                    {
                        "conversational": {
                            # contentキーなし
                            "role": "USER"
                        }
                    }
                ],
            },
            {
                "eventId": "event-2",
                "eventTimestamp": recent_time.isoformat() + "+09:00",
                "payload": [
                    {
                        "conversational": {
                            "content": {"text": "有効な分野"},
                            "role": "USER",
                        }
                    }
                ],
            },
            {
                "eventId": "event-3",
                "eventTimestamp": recent_time.isoformat() + "+09:00",
                "payload": [
                    {
                        # conversationalキーなし
                        "other": "data"
                    }
                ],
            },
        ]

        with patch.object(memory_client, "list_events") as mock_list_events:
            mock_list_events.return_value = mock_events

            # Act
            result = await memory_client.get_recent_domains("AWS-SAP")

        # Assert - 事後条件検証
        assert len(result) == 1  # 有効なデータのみ
        assert result[0] == "有効な分野"

    async def test_get_recent_domains_missing_text_field_contract(
        self, memory_client: DomainMemoryClient
    ) -> None:
        """
        事前条件: textフィールドが空文字列のpayload
        事後条件: 空文字列は除外される
        不変条件: 有効なテキストのみが返される
        """
        # Arrange - textが空文字列のイベント
        now = datetime.now()
        recent_time = now - timedelta(days=1)

        mock_events = [
            {
                "eventId": "event-1",
                "eventTimestamp": recent_time.isoformat() + "+09:00",
                "payload": [
                    {
                        "conversational": {
                            "content": {"text": ""},  # 空文字列
                            "role": "USER",
                        }
                    }
                ],
            },
            {
                "eventId": "event-2",
                "eventTimestamp": recent_time.isoformat() + "+09:00",
                "payload": [
                    {
                        "conversational": {
                            "content": {"text": "有効な分野"},
                            "role": "USER",
                        }
                    }
                ],
            },
        ]

        with patch.object(memory_client, "list_events") as mock_list_events:
            mock_list_events.return_value = mock_events

            # Act
            result = await memory_client.get_recent_domains("AWS-SAP")

        # Assert - 事後条件検証
        assert len(result) == 1  # 空文字列は除外
        assert result[0] == "有効な分野"

    async def test_get_recent_domains_non_user_role_contract(
        self, memory_client: DomainMemoryClient
    ) -> None:
        """
        事前条件: roleがUSER以外のpayload
        事後条件: USER以外のroleは除外される
        不変条件: USERロールのみが返される
        """
        # Arrange - 異なるroleのイベント
        now = datetime.now()
        recent_time = now - timedelta(days=1)

        mock_events = [
            {
                "eventId": "event-1",
                "eventTimestamp": recent_time.isoformat() + "+09:00",
                "payload": [
                    {
                        "conversational": {
                            "content": {"text": "システム分野"},
                            "role": "SYSTEM",  # USER以外
                        }
                    }
                ],
            },
            {
                "eventId": "event-2",
                "eventTimestamp": recent_time.isoformat() + "+09:00",
                "payload": [
                    {
                        "conversational": {
                            "content": {"text": "ユーザー分野"},
                            "role": "USER",
                        }
                    }
                ],
            },
        ]

        with patch.object(memory_client, "list_events") as mock_list_events:
            mock_list_events.return_value = mock_events

            # Act
            result = await memory_client.get_recent_domains("AWS-SAP")

        # Assert - 事後条件検証
        assert len(result) == 1  # USERロールのみ
        assert result[0] == "ユーザー分野"

    async def test_list_events_timezone_aware_datetime_contract(
        self, memory_client: DomainMemoryClient
    ) -> None:
        """
        事前条件: タイムゾーン付きのdatetimeオブジェクト
        事後条件: 適切にUTC変換されてフィルタリングされる
        不変条件: 指定日数以内のイベントのみが返される
        """
        # Arrange - タイムゾーン付きのdatetimeイベント
        from datetime import timezone

        now = datetime.now()
        jst = timezone(timedelta(hours=9))  # JST
        recent_time_jst = (now - timedelta(days=3)).replace(
            tzinfo=jst
        )  # 3日前（範囲内）
        old_time_jst = (now - timedelta(days=10)).replace(
            tzinfo=jst
        )  # 10日前（範囲外）

        mock_events = [
            {
                "eventId": "event-1",
                "eventTimestamp": recent_time_jst,  # timezone-aware datetime
                "payload": [
                    {
                        "conversational": {
                            "content": {"text": "セキュリティの設計"},
                            "role": "USER",
                        }
                    }
                ],
            },
            {
                "eventId": "event-2",
                "eventTimestamp": old_time_jst,  # timezone-aware datetime
                "payload": [
                    {
                        "conversational": {
                            "content": {"text": "古い分野"},
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
                actor_id="cloud-copass-agent", session_id="AWS-SAP", days_back=7
            )

        # Assert - 事後条件検証
        assert len(result) == 1  # 範囲内のイベントのみ
        assert result[0]["eventId"] == "event-1"

    async def test_list_events_exception_handling_contract(
        self, memory_client: DomainMemoryClient
    ) -> None:
        """
        事前条件: list_eventsでAPIエラーが発生
        事後条件: 例外が再発生される
        不変条件: エラーログが出力される
        """
        # Arrange - APIエラーを発生させる
        with patch.object(memory_client.client, "list_events") as mock_list_events:
            mock_list_events.side_effect = Exception("Memory API Error")

            # Act & Assert - 例外処理検証
            with pytest.raises(Exception, match="Memory API Error"):
                await memory_client.list_events(
                    actor_id="cloud-copass-agent", session_id="AWS-SAP", days_back=7
                )
