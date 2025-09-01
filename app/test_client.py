import asyncio
import logging

from dotenv import load_dotenv

from app.agentcore.agent_main import AgentOutput
from app.agentcore.teams_client import TeamsClient

load_dotenv()

logger = logging.getLogger(__name__)


questions = [
    {
        "question": "大規模な金融サービス企業が、複数のAWSアカウントにまたがる数千のAmazon EC2インスタンスを管理しています。セキュリティチームは、すべてのEC2インスタンスが最新のセキュリティパッチで更新されていることを確認する必要があります。また、パッチ適用プロセスはコンプライアンス要件を満たすために完全に監査可能である必要があります。この要件を満たすための最も効率的で拡張性の高いソリューションは何ですか？",
        "options": [
            "**A.** 各AWSアカウントでAWS Systems Manager Patch Managerを設定し、AWS Organizationsを使用してすべてのアカウントにパッチベースラインを展開する。AWS Security HubとAWS Config統合を使用してパッチコンプライアンスを監視する。",
            "**B.** カスタムスクリプトを作成し、AWS Lambda関数を使用して各EC2インスタンスにパッチを適用する。AWS Step Functionsを使用してパッチ適用プロセスを調整し、Amazon CloudWatchを使用して結果を記録する。",
            "**C.** 各AWSアカウントでAmazon Inspector評価を設定し、EC2インスタンスの脆弱性をスキャンする。AWS Systems Manager Automationを使用して、検出された脆弱性に基づいてパッチを適用する。",
            "**D.** 中央管理AWSアカウントにAWS Systems Manager Patch Managerを設定し、クロスアカウントのIAMロールを使用して他のアカウントのEC2インスタンスにパッチを適用する。Amazon EventBridgeを使用してパッチ適用ジョブをスケジュールし、AWS CloudTrailでアクティビティを監査する。",
            "**E.** 各EC2インスタンスにカスタムエージェントをインストールし、中央の管理サーバーからパッチをプルして適用する。Amazon S3を使用してパッチファイルを保存し、Amazon DynamoDBを使用してパッチステータスを追跡する。",
        ],
        "correct_answer": "A",
        "explanation": "この問題では、大規模で複雑な環境におけるEC2インスタンスのパッチ管理とコンプライアンス監視が求められています。最も効率的で拡張性の高いソリューションは、オプションAです。\n\n正解の理由：\n1. AWS Systems Manager Patch Managerは、大規模な環境でのパッチ管理に最適化されたサービスです。\n2. AWS Organizationsとの統合により、複数のAWSアカウントにわたってパッチベースラインを一元管理できます。\n3. AWS Security HubとAWS Config統合により、パッチコンプライアンスの包括的な可視性と監査機能が提供されます。\n\n他のオプションが最適でない理由：\nB: カスタムスクリプトとLambda関数の使用は、数千のインスタンスに対して拡張性が低く、管理が複雑になります。\n\nC: Amazon Inspectorは脆弱性スキャンに有用ですが、パッチ管理には最適化されていません。また、複数アカウントでの一元管理が難しくなります。\n\nD: 中央管理アカウントからのクロスアカウントパッチ適用は、セキュリティ上のリスクがあり、大規模環境では管理が複雑になる可能性があります。\n\nE: カスタムエージェントの使用は、管理オーバーヘッドが大きく、AWSのマネージドサービスを活用できていません。\n\nAWS Systems Manager Patch Managerを使用することで、パッチ管理プロセスを自動化し、大規模な環境でも効率的に運用できます。また、AWS Security HubとAWS Configの統合により、コンプライアンス要件を満たす監査可能なソリューションを実現できます。",
        "source": [
            "https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-patch.html",
            "https://docs.aws.amazon.com/organizations/latest/userguide/orgs_integrate_services_list.html",
            "https://docs.aws.amazon.com/securityhub/latest/userguide/securityhub-standards-fsbp-controls.html#fsbp-ec2-8",
        ],
    }
]


async def main() -> None:
    teams_client = TeamsClient()
    try:
        await teams_client.send(
            agent_output=AgentOutput.model_construct(questions=questions)
        )

    except Exception as e:
        # Teams投稿失敗でも問題生成結果は返す（処理継続）
        logger.warning(f"Teams投稿に失敗しましたが、処理を継続します: {str(e)}")


if __name__ == "__main__":
    # uv run python app/test_client.py
    asyncio.run(main())
