import asyncio
import logging

from dotenv import load_dotenv

from app.agentcore.agent_main import AgentOutput
from app.agentcore.teams_client import TeamsClient

load_dotenv()

logger = logging.getLogger(__name__)


questions = [
    {
        "question": "大規模な多国籍企業が、複数のAWSアカウントを使用してグローバルなプレゼンスを管理しています。この企業は、すべてのリージョンにわたって一貫したセキュリティポリシーを実施し、コンプライアンス要件を満たすことを目指しています。また、新しいアカウントのプロビジョニングプロセスを自動化し、ベストプラクティスに基づいたガバナンスモデルを実装したいと考えています。これらの要件を満たすための最も効果的なソリューションは何ですか？",
        "options": [
            "**A.** 各AWSアカウントで個別にIAMポリシーを設定し、AWS Configルールを使用してコンプライアンスをモニタリングする",
            "**B.** AWS Organizationsを使用してマルチアカウント環境を管理し、Service Control Policies (SCPs)を適用してグローバルなポリシーを実施する",
            "**C.** AWS Control Towerを使用してランディングゾーンを設定し、ガードレールを実装してアカウントのプロビジョニングと管理を自動化する",
            "**D.** AWS Firewall Managerを使用してすべてのアカウントにセキュリティルールを適用し、AWS Trusted Advisorでベストプラクティスを監視する",
        ],
        "correct_answer": "C",
        "explanation": "AWS Control Towerは、この状況で最も包括的で効果的なソリューションを提供します。以下の理由から、Control Towerが最適な選択肢となります：\n\n1. マルチアカウント環境の管理：Control Towerは、AWS Organizationsを基盤として使用し、複数のアカウントを効率的に管理します。\n\n2. 一貫したセキュリティポリシーの実施：ガードレール（予防的および探索的）を通じて、すべてのアカウントとリージョンにわたって一貫したセキュリティポリシーを実施できます。\n\n3. コンプライアンス要件の満足：事前設定されたガードレールとカスタムガードレールを使用して、特定のコンプライアンス要件を満たすことができます。\n\n4. アカウントプロビジョニングの自動化：Account Factory機能により、新しいアカウントのプロビジョニングプロセスを自動化し、標準化することができます。\n\n5. ベストプラクティスに基づいたガバナンス：Control Towerは、AWSのベストプラクティスに基づいてセットアップされ、継続的なガバナンスを提供します。\n\n他の選択肢と比較すると：\n\nA. 個別のIAMポリシー設定は拡張性に欠け、一貫性を保つのが困難です。\n\nB. AWS Organizationsは有効ですが、Control Towerほど包括的な自動化とガバナンス機能を提供しません。\n\nD. Firewall ManagerとTrusted Advisorは有用なツールですが、この状況で必要とされる包括的なガバナンスとアカウント管理機能を提供しません。\n\nしたがって、AWS Control Towerを使用することで、企業は効率的にマルチアカウント環境を管理し、一貫したセキュリティとコンプライアンスを確保しながら、アカウントプロビジョニングを自動化できます。",
        "source": [
            "https://docs.aws.amazon.com/controltower/latest/userguide/what-is-control-tower.html",
            "https://docs.aws.amazon.com/controltower/latest/userguide/guardrails.html",
        ],
        "learning_domain": "複雑な組織に対応するソリューションの設計",
        "primary_technologies": [
            "AWS Control Tower",
            "AWS Organizations",
            "AWS IAM",
        ],
        "learning_insights": "【試験対策】出題頻度★★★★☆、学習優先度最高。【よくある間違い】AWS OrganizationsとControl Towerの違いを混同しがち。【学習戦略】Control Tower → Organizations → IAM の順で学習を推奨。【実務経験差】大規模組織でのAWS管理経験者に有利。【関連項目】セキュリティ設計、コンプライアンス管理、マルチアカウントガバナンス。【効果的な学習方法】Control Tower経験者5-8時間\n\n【よくある間違い】\n・SCPは「許可」ではなく「制限」のみ（IAMポリシーとの混同注意）\n・Control Towerは既存アカウントの「修正」ではなく「新規作成」に特化\n・Security Hubは「検知」が主機能、「修復」は別サービスが必要\n\n【実務経験による差】\n・有利: エンタープライズでのマルチアカウント運用経験者\n・不利: 単一アカウントのみの経験者（概念理解に時間要）\n・補強方法: AWS Well-Architected「組織編」とControl Tower User Guideを熟読\n\n【関連出題項目】\n・ドメイン2: マルチリージョンでのDR戦略\n・ドメイン4: 組織レベルでのRI/SP最適化\n・複合問題として出題される可能性が高い分野",
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
