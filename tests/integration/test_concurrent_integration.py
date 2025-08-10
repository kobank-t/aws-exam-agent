"""
並行処理統合テスト

複数のコンポーネントが並行実行される際の統合動作をテストします。
"""

import asyncio
from typing import Any
from unittest.mock import patch

import pytest

from app.agentcore.agent_main import aws_info_agent
from app.agentcore.mcp.client import MCPClient, get_mcp_client


@pytest.mark.integration
class TestConcurrentIntegration:
    """並行処理統合テストクラス"""

    async def test_concurrent_aws_info_agent_requests(self) -> None:
        """並行AWS情報取得エージェントリクエスト統合テスト"""
        # 複数のサービスに対する並行リクエスト
        services = ["EC2", "S3", "Lambda", "DynamoDB", "RDS"]
        topics = ["overview", "best-practices", "pricing", "security", "monitoring"]

        tasks = []
        for i, service in enumerate(services):
            topic = topics[i % len(topics)]
            tasks.append(aws_info_agent(service=service, topic=topic))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        assert len(results) == len(services)

        success_count = 0
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                pytest.fail(f"Concurrent request for {services[i]} failed: {result}")

            assert isinstance(result, dict)
            assert "service" in result
            assert result["service"] == services[i]
            success_count += 1

        assert success_count == len(services)

    async def test_concurrent_mcp_client_operations(self) -> None:
        """並行MCP Clientオペレーション統合テスト"""
        mcp_client = MCPClient()
        await mcp_client.connect_all_servers()

        # 複数のMCP操作を並行実行
        tasks = [
            mcp_client.get_aws_documentation("EC2", "instances"),
            mcp_client.get_aws_documentation("S3", "buckets"),
            mcp_client.get_aws_knowledge("Lambda best practices"),
            mcp_client.get_aws_knowledge("DynamoDB performance"),
            mcp_client.get_aws_documentation("RDS", "security"),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        assert len(results) == 5

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                pytest.fail(f"Concurrent MCP operation {i} failed: {result}")

            assert isinstance(result, dict)

        await mcp_client.disconnect()

    async def test_concurrent_supervisor_agent_flows(self) -> None:
        """並行SupervisorAgentフロー統合テスト"""
        # 複数の問題生成フローを並行実行
        topics = ["EC2", "S3", "Lambda"]
        difficulties = ["beginner", "intermediate", "advanced"]

        tasks = []
        for topic in topics:
            for difficulty in difficulties:
                tasks.append(aws_info_agent(service=topic, topic=difficulty))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        assert len(results) == len(topics) * len(difficulties)

        success_count = 0
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                pytest.fail(f"Concurrent supervisor flow {i} failed: {result}")

            assert isinstance(result, dict)
            assert "status" in result
            success_count += 1

        assert success_count == len(results)

    async def test_concurrent_mixed_operations(self) -> None:
        """並行混合オペレーション統合テスト"""
        # 異なる種類のオペレーションを並行実行
        mcp_client = await get_mcp_client()

        tasks = [
            # AWS情報取得エージェント操作
            aws_info_agent(service="EC2", topic="intermediate"),
            aws_info_agent(service="S3", topic="beginner"),
            # AWS情報取得エージェント操作
            aws_info_agent(service="Lambda", topic="functions"),
            aws_info_agent(service="DynamoDB", topic="tables"),
            # MCP Client操作
            mcp_client.get_aws_documentation("RDS", "overview"),
            mcp_client.get_aws_knowledge("VPC best practices"),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        assert len(results) == 6

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                pytest.fail(f"Concurrent mixed operation {i} failed: {result}")

            assert isinstance(result, dict)

    async def test_concurrent_error_handling(self) -> None:
        """並行処理エラーハンドリング統合テスト"""
        # 一部のリクエストでエラーを発生させる
        with patch("app.agentcore.agent_main.aws_info_agent") as mock_agent:
            # 成功、エラー、成功、エラー、成功のパターン
            mock_agent.side_effect = [
                {"service": "EC2", "status": "success"},
                Exception("Simulated error 1"),
                {"service": "Lambda", "status": "success"},
                Exception("Simulated error 2"),
                {"service": "RDS", "status": "success"},
            ]

            tasks = [
                aws_info_agent(service="EC2", topic="instances"),
                aws_info_agent(service="S3", topic="buckets"),
                aws_info_agent(service="Lambda", topic="functions"),
                aws_info_agent(service="DynamoDB", topic="tables"),
                aws_info_agent(service="RDS", topic="databases"),
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            assert len(results) == 5

            success_count = 0
            error_count = 0

            for result in results:
                if isinstance(result, Exception):
                    error_count += 1
                else:
                    success_count += 1
                    assert isinstance(result, dict)

            # 成功とエラーの両方が発生していることを確認
            assert success_count > 0
            assert error_count > 0

    async def test_concurrent_performance_baseline(self) -> None:
        """並行処理パフォーマンスベースライン統合テスト"""
        import time

        # シーケンシャル実行の測定
        start_time = time.time()
        sequential_results = []
        for i in range(3):
            result = await aws_info_agent(service=f"Service{i}", topic=f"topic{i}")
            sequential_results.append(result)
        sequential_time = time.time() - start_time

        # 並行実行の測定
        start_time = time.time()
        tasks = [
            aws_info_agent(service=f"Service{i}", topic=f"topic{i}") for i in range(3)
        ]
        concurrent_results_raw = await asyncio.gather(*tasks, return_exceptions=True)
        concurrent_results: list[dict[str, Any]] = []
        for r in concurrent_results_raw:
            if isinstance(r, Exception):
                pytest.fail(f"Performance test failed: {r}")
            elif isinstance(r, dict):
                concurrent_results.append(r)
        concurrent_time = time.time() - start_time

        # 結果の確認
        assert len(sequential_results) == 3
        assert len(concurrent_results) == 3

        # 結果の確認（Exceptionを除外）
        all_results = sequential_results + concurrent_results
        for result in all_results:
            assert isinstance(result, dict)

        # 並行実行が効率的であることを確認（厳密な性能要件は設けない）
        assert concurrent_time <= sequential_time * 1.5  # 50%のマージンを許容

    async def test_concurrent_timeout_handling(self) -> None:
        """並行処理タイムアウトハンドリング統合テスト"""

        # タイムアウト付きの並行実行
        async def timeout_wrapper(coro: Any, timeout: float) -> dict[str, Any]:
            try:
                return await asyncio.wait_for(coro, timeout=timeout)
            except TimeoutError:
                return {"status": "timeout", "error": "Operation timed out"}

        tasks = [
            timeout_wrapper(
                aws_info_agent(service=f"Service{i}", topic=f"topic{i}"),
                timeout=5.0,  # 5秒のタイムアウト
            )
            for i in range(3)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        assert len(results) == 3

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                pytest.fail(f"Timeout wrapper task {i} failed: {result}")

            assert isinstance(result, dict)

            # タイムアウトまたは正常完了のいずれか
            if result.get("status") == "timeout":
                assert "error" in result
            else:
                # 正常完了の場合の基本構造確認
                assert "service" in result or "status" in result
