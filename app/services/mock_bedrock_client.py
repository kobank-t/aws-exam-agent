"""
テスト・開発用のMock Bedrock Client

実際のBedrock APIを呼び出さずに、高品質な問題を生成します。
単体テスト・統合テストでのコスト削減と実行速度向上を目的とします。
"""

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


class MockBedrockClient:
    """
    テスト・開発用のMock Bedrock Client

    実際のBedrock APIを呼び出さずに、サービス固有の
    高品質な問題を生成します。
    """

    def __init__(self) -> None:
        """MockBedrockClient を初期化"""
        logger.info("MockBedrockClient initialized for testing/development")

    async def generate_question(
        self,
        aws_info: dict[str, Any],
        topic: str = "EC2",
        difficulty: str = "professional",
    ) -> dict[str, Any]:
        """
        Mock問題生成（サービス固有の高品質問題）

        Args:
            aws_info: AWS情報取得エージェントからの情報
            topic: 問題のトピック
            difficulty: 難易度

        Returns:
            生成された問題の辞書
        """
        logger.info(f"Generating mock {difficulty} question for {topic}")

        # サービス固有の高品質問題テンプレート
        mock_questions = {
            "EC2": {
                "question": "グローバル企業が、地域ごとに異なる負荷パターンを持つWebアプリケーションをEC2で運用しています。アジア太平洋地域では平日の日中に高負荷、北米では夜間に高負荷となります。コスト効率と可用性を両立する最適なアーキテクチャはどれですか？",
                "options": {
                    "A": "各リージョンでリザーブドインスタンスとオンデマンドインスタンスを組み合わせ、Auto Scalingで負荷に応じてスケールする",
                    "B": "すべてのリージョンでスポットインスタンスのみを使用し、中断時は他リージョンにトラフィックを転送する",
                    "C": "最大負荷に合わせてすべてのリージョンでリザーブドインスタンスを購入する",
                    "D": "単一リージョンで大容量インスタンスを使用し、グローバルにサービスを提供する",
                },
                "correct_answer": "A",
                "explanation": "選択肢Aが最適です。各リージョンの予測可能なベースライン負荷にはリザーブドインスタンスでコストを削減し、変動する追加負荷にはオンデマンドインスタンスとAuto Scalingで柔軟に対応できます。スポットインスタンスは本番環境での中断リスクが高く、最大負荷でのリザーブドは過剰投資、単一リージョンは可用性とレイテンシの問題があります。",
                "aws_services": [
                    "EC2",
                    "Auto Scaling",
                    "CloudWatch",
                    "Elastic Load Balancing",
                ],
                "key_concepts": [
                    "グローバルアーキテクチャ",
                    "コスト最適化",
                    "Auto Scaling",
                    "リザーブドインスタンス",
                ],
            },
            "S3": {
                "question": "メディア企業が、4K動画コンテンツ（平均5GB/ファイル）を1日1000ファイル生成し、新しいコンテンツは最初の30日間は頻繁にアクセスされますが、その後は月1回程度のアクセスになります。5年間の保存が必要で、コンプライアンス要件により削除は禁止されています。最もコスト効率の良いS3戦略はどれですか？",
                "options": {
                    "A": "S3 Intelligent-Tieringを使用し、ライフサイクルポリシーで90日後にGlacier Flexible Retrieval、1年後にGlacier Deep Archiveに移行する",
                    "B": "すべてのコンテンツをS3 Standardに保存し、必要に応じて手動でアーカイブする",
                    "C": "S3 Standard-IAに保存し、アクセスログを分析して使用頻度の低いファイルを特定する",
                    "D": "S3 One Zone-IAを使用してコストを削減し、重要なファイルのみ別途バックアップする",
                },
                "correct_answer": "A",
                "explanation": "選択肢Aが最適です。S3 Intelligent-Tieringは最初の30日間の頻繁なアクセスに自動的に対応し、ライフサイクルポリシーにより段階的に安価なストレージクラスに移行してコストを最適化できます。90日後のGlacier Flexible Retrieval移行は月1回のアクセスパターンに適し、1年後のDeep Archive移行で長期保存コストを最小化します。他の選択肢は自動化されておらず運用負荷が高いか、耐久性に問題があります。",
                "aws_services": [
                    "S3",
                    "S3 Intelligent-Tiering",
                    "S3 Glacier",
                    "S3 Lifecycle",
                ],
                "key_concepts": [
                    "ストレージ最適化",
                    "ライフサイクル管理",
                    "アクセスパターン分析",
                    "長期アーカイブ",
                ],
            },
            "VPC": {
                "question": "金融機関が、PCI DSS準拠が必要なクレジットカード処理システムをAWSに構築します。Webサーバー、アプリケーションサーバー、データベースの3層構成で、最高レベルのセキュリティと監査要件を満たす必要があります。最適なVPCアーキテクチャはどれですか？",
                "options": {
                    "A": "パブリックサブネット（Web）、プライベートサブネット（App、DB）を配置し、NACLとセキュリティグループで多層防御を実装する",
                    "B": "すべてのリソースをプライベートサブネットに配置し、Application Load Balancerのみパブリックサブネットに配置する",
                    "C": "各層を異なるVPCに分離し、VPC Endpointとプライベート接続のみで通信する",
                    "D": "単一のプライベートサブネットにすべてのリソースを配置し、VPN接続のみでアクセスする",
                },
                "correct_answer": "A",
                "explanation": "選択肢Aが最適です。PCI DSS準拠には適切なネットワーク分離が必要で、Webサーバーはインターネットアクセスが必要なためパブリックサブネット、機密データを扱うアプリケーションサーバーとデータベースはプライベートサブネットに配置します。NACLとセキュリティグループの多層防御により、各層間の通信を厳密に制御できます。完全分離（C）は過度に複雑で運用負荷が高く、単一サブネット（D）は適切な分離ができません。",
                "aws_services": [
                    "VPC",
                    "Subnet",
                    "Security Groups",
                    "NACL",
                    "Application Load Balancer",
                    "VPC Flow Logs",
                ],
                "key_concepts": [
                    "PCI DSS準拠",
                    "多層防御",
                    "ネットワーク分離",
                    "セキュリティ監査",
                ],
            },
        }

        # デフォルトの汎用問題
        default_question = {
            "question": f"企業が{topic}サービスを使用してクラウドファーストな戦略を実装する際、{difficulty}レベルで最も重要な設計原則はどれですか？",
            "options": {
                "A": f"{topic}の基本機能のみを使用してシンプルに構築する",
                "B": f"{topic}のマネージドサービス機能を活用して運用負荷を削減する",
                "C": f"{topic}の最新機能をすべて採用して競争優位性を確保する",
                "D": f"{topic}のオンプレミス環境と同じ構成で移行する",
            },
            "correct_answer": "B",
            "explanation": f"{difficulty}レベルの{topic}実装では、AWSマネージドサービスの活用が重要です。これにより運用負荷を削減し、AWSの専門知識を活用できます。基本機能のみでは本番要件を満たさず、最新機能の全採用は複雑性を増し、オンプレミス同様の構成はクラウドの利点を活かせません。",
            "aws_services": [topic, "CloudWatch", "IAM"],
            "key_concepts": ["クラウドファースト", "マネージドサービス", "運用効率化"],
        }

        # サービス固有の問題があれば使用、なければデフォルト
        question_template = mock_questions.get(topic.upper(), default_question)

        # AWS情報を活用したメタデータの追加
        enhanced_question = {
            "id": f"mock_{topic.lower()}_{difficulty}_{hash(json.dumps(question_template)) % 10000:04d}",
            "topic": topic,
            "difficulty": difficulty,
            "question": question_template["question"],
            "options": question_template["options"],
            "correct_answer": question_template["correct_answer"],
            "explanation": question_template["explanation"],
            "aws_services": question_template["aws_services"],
            "key_concepts": question_template["key_concepts"],
            "generated_by": "mock_bedrock_client",
            "model_used": "mock_claude_3_5_sonnet",
            "generation_timestamp": "2025-08-11T23:35:00Z",
            "aws_info_used": bool(aws_info),
            "mock_mode": True,
        }

        logger.info(f"Successfully generated mock question: {enhanced_question['id']}")
        return enhanced_question


# グローバル Mock Bedrock Client インスタンス
mock_bedrock_client = MockBedrockClient()


async def get_mock_bedrock_client() -> MockBedrockClient:
    """
    Mock Bedrock Client インスタンスを取得

    Returns:
        MockBedrockClient インスタンス
    """
    return mock_bedrock_client
