"""
MCP Client 統合

AWS Documentation MCP Server と AWS Knowledge MCP Server との連携を行います。
"""

import asyncio
import logging
import subprocess
from typing import Any, cast

logger = logging.getLogger(__name__)


class MCPClient:
    """
    MCP Server との連携を行うクライアント

    設計書に基づき、以下の2つのMCP Serverと連携します：
    - AWS Documentation MCP Server (uvx awslabs.aws-documentation-mcp-server)
    - AWS Knowledge MCP Server (uvx awslabs.aws-knowledge-mcp-server)
    """

    def __init__(self) -> None:
        self.aws_docs_server_process: Any = None
        self.aws_knowledge_server_process: Any = None
        self.is_connected = False

    async def connect_aws_docs_server(self) -> bool:
        """
        AWS Documentation MCP Server に接続

        Returns:
            接続成功の場合 True
        """
        try:
            logger.info("Connecting to AWS Documentation MCP Server...")

            # uvx コマンドで AWS Documentation MCP Server を起動
            # 注意: 実際の統合では stdio 通信を使用しますが、
            # テスト環境では接続確認のみ行います

            # MCP Server の存在確認
            result = subprocess.run(
                ["uvx", "--help"], capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                logger.info(
                    "uvx command available - AWS Documentation MCP Server can be launched"
                )
                return True
            else:
                logger.error("uvx command not available")
                return False

        except Exception as e:
            logger.error(f"Failed to connect to AWS Documentation MCP Server: {e}")
            return False

    async def connect_aws_knowledge_server(self) -> bool:
        """
        AWS Knowledge MCP Server に接続

        Returns:
            接続成功の場合 True
        """
        try:
            logger.info("Connecting to AWS Knowledge MCP Server...")

            # uvx コマンドで AWS Knowledge MCP Server を起動
            # 注意: 実際の統合では stdio 通信を使用しますが、
            # テスト環境では接続確認のみ行います

            # MCP Server の存在確認
            result = subprocess.run(
                ["uvx", "--help"], capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                logger.info(
                    "uvx command available - AWS Knowledge MCP Server can be launched"
                )
                return True
            else:
                logger.error("uvx command not available")
                return False

        except Exception as e:
            logger.error(f"Failed to connect to AWS Knowledge MCP Server: {e}")
            return False

    async def connect_all_servers(self) -> bool:
        """
        全ての MCP Server に接続

        Returns:
            全ての接続が成功した場合 True
        """
        try:
            logger.info("Connecting to all MCP Servers...")

            # 並行して両方のサーバーに接続
            results = await asyncio.gather(
                self.connect_aws_docs_server(),
                self.connect_aws_knowledge_server(),
                return_exceptions=True,
            )

            # 結果の確認
            docs_connected: bool
            if isinstance(results[0], Exception):
                logger.error(f"AWS Docs Server connection failed: {results[0]}")
                docs_connected = False
            else:
                # asyncio.gatherの結果は正常時にboolを返すことが保証されている
                docs_connected = cast(bool, results[0])

            knowledge_connected: bool
            if isinstance(results[1], Exception):
                logger.error(f"AWS Knowledge Server connection failed: {results[1]}")
                knowledge_connected = False
            else:
                # asyncio.gatherの結果は正常時にboolを返すことが保証されている
                knowledge_connected = cast(bool, results[1])

            self.is_connected = docs_connected and knowledge_connected

            if self.is_connected:
                logger.info("Successfully connected to all MCP Servers")
            else:
                logger.warning("Failed to connect to some MCP Servers")

            return self.is_connected

        except Exception as e:
            logger.error(f"Failed to connect to MCP Servers: {e}")
            self.is_connected = False
            return False

    async def get_aws_documentation(
        self, service: str, topic: str = ""
    ) -> dict[str, Any]:
        """
        AWS Documentation MCP Server から情報を取得

        Args:
            service: AWSサービス名 (例: "EC2", "S3", "Lambda")
            topic: 特定のトピック (オプション)

        Returns:
            取得した情報の辞書
        """
        try:
            logger.info(
                f"Getting AWS documentation for service: {service}, topic: {topic}"
            )

            # 現在はモック実装
            # 実際の実装では MCP Server との stdio 通信を行います
            mock_documentation = {
                "service": service,
                "topic": topic,
                "documentation": f"AWS {service} documentation content",
                "source": "AWS Documentation MCP Server",
                "last_updated": "2024-01-01",
                "sections": [
                    f"{service} Overview",
                    f"{service} Getting Started",
                    f"{service} Best Practices",
                    f"{service} Troubleshooting",
                ],
            }

            logger.info(f"Successfully retrieved AWS documentation for {service}")
            return mock_documentation

        except Exception as e:
            logger.error(f"Failed to get AWS documentation: {e}")
            return {"error": str(e), "service": service, "topic": topic}

    async def get_aws_knowledge(self, query: str) -> dict[str, Any]:
        """
        AWS Knowledge MCP Server から情報を取得

        Args:
            query: 検索クエリ

        Returns:
            取得した情報の辞書
        """
        try:
            logger.info(f"Getting AWS knowledge for query: {query}")

            # 現在はモック実装
            # 実際の実装では MCP Server との stdio 通信を行います
            mock_knowledge = {
                "query": query,
                "knowledge": f"AWS knowledge content for: {query}",
                "source": "AWS Knowledge MCP Server",
                "confidence": 0.95,
                "related_topics": [
                    f"Related topic 1 for {query}",
                    f"Related topic 2 for {query}",
                    f"Related topic 3 for {query}",
                ],
                "references": [
                    "AWS Documentation",
                    "AWS Blog",
                    "AWS What's New",
                    "AWS Well-Architected Framework",
                ],
            }

            logger.info(f"Successfully retrieved AWS knowledge for query: {query}")
            return mock_knowledge

        except Exception as e:
            logger.error(f"Failed to get AWS knowledge: {e}")
            return {"error": str(e), "query": query}

    async def disconnect(self) -> None:
        """
        MCP Server との接続を切断
        """
        try:
            logger.info("Disconnecting from MCP Servers...")

            # プロセスが起動している場合は終了
            if self.aws_docs_server_process:
                self.aws_docs_server_process.terminate()
                self.aws_docs_server_process = None

            if self.aws_knowledge_server_process:
                self.aws_knowledge_server_process.terminate()
                self.aws_knowledge_server_process = None

            self.is_connected = False
            logger.info("Successfully disconnected from MCP Servers")

        except Exception as e:
            logger.error(f"Error during MCP Server disconnection: {e}")


# グローバル MCP Client インスタンス
mcp_client = MCPClient()


async def get_mcp_client() -> MCPClient:
    """
    MCP Client インスタンスを取得

    Returns:
        MCPClient インスタンス
    """
    if not mcp_client.is_connected:
        await mcp_client.connect_all_servers()

    return mcp_client
