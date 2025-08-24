import asyncio
import logging
import os

import httpx
from dotenv import load_dotenv

from app.agentcore.agent_main import AgentOutput, Question

load_dotenv()

logger = logging.getLogger(__name__)

output = AgentOutput(
    questions=[
        Question(
            question="ある企業は複数のリージョンにまたがるマルチリージョンアーキテクチャを運用しています。この企業は、プライマリリージョンで障害が発生した場合にビジネスクリティカルなアプリケーションを別のリージョンにフェイルオーバーする能力を確保したいと考えています。このアプリケーションはAmazon RDSのMySQL互換データベースに依存しており、リージョン間で一貫したデータを維持する必要があります。また、フェイルオーバー時のRPO（Recovery Point Objective）は1分未満、RTO（Recovery Time Objective）は数分以内という要件があります。コスト効率も考慮する必要があります。この要件を満たすソリューションとして最も適切なのはどれですか？",
            options=[
                "A. プライマリリージョンとセカンダリリージョンの両方でAmazon RDS for MySQLのマルチAZデプロイメントを設定し、AWS Database Migration Service (DMS) を使用して継続的レプリケーションを行う",
                "B. Amazon RDS for MySQL Global Database を使用し、プライマリリージョンとセカンダリリージョン間でレプリケーションを設定する",
                "C. Amazon Aurora Global Database を使用して、プライマリリージョンからセカンダリリージョンへの非同期レプリケーションを構成する",
                "D. プライマリリージョンで Amazon RDS for MySQL を使用し、Amazon S3 クロスリージョンレプリケーションを使用してデータバックアップを複製し、障害時にセカンダリリージョンで新しいインスタンスを起動する",
                "E. Amazon DynamoDB グローバルテーブルを使用して、すべてのリージョン間でデータを自動的に複製する",
            ],
            correct_answer="C",
            explanation="この問題では、マルチリージョン環境での高可用性データベースソリューションが求められており、RPO 1分未満、RTO 数分以内という厳しい要件があります。\n\nC: Amazon Aurora Global Database は、プライマリリージョンからセカンダリリージョンへの非同期レプリケーションを提供し、典型的なレプリケーション遅延は1秒未満です。また、災害発生時には、セカンダリリージョンを数分以内にプライマリにプロモートすることができるため、RTO要件も満たします。Aurora Global Databaseは専用のインフラストラクチャを使用してレプリケーションを行い、プライマリDBインスタンスへの影響を最小限に抑えます。これは高性能でコスト効率の良いソリューションです。\n\nA: AWS DMSを使用したレプリケーションは可能ですが、Aurora Global Databaseほど効率的ではなく、設定と管理が複雑になります。また、RPO 1分未満の要件を一貫して満たすことが難しい場合があります。\n\nB: RDS for MySQL Global Database は存在しません。RDSの標準機能ではグローバルデータベースをサポートしていません。グローバルデータベース機能はAurora固有の機能です。\n\nD: S3クロスリージョンレプリケーションを使用したバックアップ戦略では、RPO 1分未満の要件を満たすことができません。また、障害発生時に新しいインスタンスを起動してバックアップから復元する必要があるため、RTOも数分以内という要件を満たすことができません。\n\nE: DynamoDB グローバルテーブルはNoSQLソリューションであり、MySQL互換のリレーショナルデータベースが必要とされている要件を満たしません。\n\nしたがって、要件を最もよく満たすのはC（Amazon Aurora Global Database）です。",
            source=[
                "https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-global-database.html",
                "https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-global-database-disaster-recovery.html",
            ],
        )
    ],
)


async def main() -> None:
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            url=os.getenv("POWER_AUTOMATE_WEBHOOK_URL", "dummy"),
            content=output.model_dump_json(),
            headers={"Content-Type": "application/json"},
        )

        logger.info(f"Teams投稿完了 (HTTP {response.status_code})")


if __name__ == "__main__":
    # uv run python app/test_client.py
    asyncio.run(main())
