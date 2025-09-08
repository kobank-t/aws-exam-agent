import asyncio
import logging

from dotenv import load_dotenv

from app.agentcore.agent_main import AgentOutput
from app.agentcore.teams_client import TeamsClient

load_dotenv()

logger = logging.getLogger(__name__)


questions = [
    {
        "question": "大規模な国際企業が、複数のAWSアカウントを使用して、さまざまな部門や地域の要件に対応しています。セキュリティチームは、すべてのアカウントにわたって一貫したセキュリティポリシーを実施し、コンプライアンスを確保したいと考えています。この要件を満たすための最も効果的なソリューションは何ですか？",
        "options": [
            "**A.** 各AWSアカウントで個別にIAMポリシーを設定し、定期的に手動で同期する",
            "**B.** AWS Organizationsを使用してマルチアカウント環境を管理し、サービスコントロールポリシー(SCP)を適用する",
            "**C.** すべてのリソースを単一のAWSアカウントに統合し、IAMロールとポリシーを使用してアクセスを制御する",
            "**D.** 各部門や地域ごとに個別のAWS Organizationsを作成し、それぞれで独立したポリシーを管理する",
        ],
        "correct_answer": "B",
        "explanation": "AWS Organizationsを使用してマルチアカウント環境を管理し、サービスコントロールポリシー(SCP)を適用することが、この要件を満たすための最も効果的なソリューションです。\n\nAWS Organizationsは、複数のAWSアカウントを中央で管理するためのサービスです。SCPを使用することで、組織全体または特定の組織単位(OU)に対して、一貫したセキュリティポリシーを適用できます。これにより、すべてのアカウントにわたって統一されたセキュリティ基準を確保し、コンプライアンス要件を満たすことができます。\n\n他の選択肢が適切でない理由:\n\nA: 各アカウントで個別にポリシーを管理し手動で同期する方法は、エラーが発生しやすく、スケーラブルではありません。\n\nC: すべてのリソースを単一のアカウントに統合することは、セキュリティの境界を減らし、リスクを増大させる可能性があります。また、部門や地域ごとの要件に対応することが困難になります。\n\nD: 複数のAWS Organizationsを作成することは、中央管理の利点を失い、一貫したポリシーの適用を困難にします。",
        "source": [
            "https://docs.aws.amazon.com/organizations/latest/userguide/orgs_introduction.html",
            "https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps.html",
        ],
        "learning_domain": "複雑な組織に対応するソリューションの設計",
        "primary_technologies": [
            "AWS Organizations",
            "AWS Identity and Access Management (IAM)",
        ],
        "learning_insights": "この問題は、試験ガイドの「コンテンツ分野1: 複雑な組織に対応するソリューションの設計」に関連しています。特に、以下のタスクと対象知識、対象スキルに直接対応しています：\n\nタスク1.4: マルチアカウントAWS環境を設計する\n\n対象知識:\n- AWS OrganizationsとAWS Control Tower\n- マルチアカウントイベント通知\n- 環境間のAWSリソース共有\n\n対象スキル:\n- 組織の要件に最も適したアカウント構造を評価する。\n- マルチアカウントガバナンスモデルを開発する。\n\nこの問題は、複数のAWSアカウントを持つ大規模な組織が、一貫したセキュリティポリシーを実施し、コンプライアンスを確保するためのソリューションを求めています。AWS Organizationsとサービスコントロールポリシー(SCP)の使用は、まさにこのタスクと対象スキルに合致する解決策です。",
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
