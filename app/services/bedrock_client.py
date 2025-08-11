"""
Amazon Bedrock Claude モデル統合クライアント

AWS Certified Solutions Architect - Professional レベルの
試験問題生成のためのBedrock Claude モデル統合を提供します。
"""

import json
import logging
from typing import Any

import boto3
from botocore.exceptions import ClientError

from app.shared.config import get_aws_config

logger = logging.getLogger(__name__)


class BedrockClient:
    """
    Amazon Bedrock Claude モデルとの統合クライアント

    Professional レベルの AWS 試験問題生成に特化した
    Claude モデルとの連携を提供します。
    """

    def __init__(self) -> None:
        """BedrockClient を初期化"""
        self.aws_config = get_aws_config()
        self.bedrock_client = boto3.client(
            "bedrock-runtime",
            region_name=self.aws_config["region"],
            aws_access_key_id=self.aws_config.get("access_key_id"),
            aws_secret_access_key=self.aws_config.get("secret_access_key"),
        )

        # Claude モデル設定
        self.model_configs = {
            "claude-3-5-sonnet": {
                "model_id": "anthropic.claude-3-5-sonnet-20241022-v2:0",
                "max_tokens": 4000,
                "temperature": 0.7,
            },
            "claude-3-haiku": {
                "model_id": "anthropic.claude-3-haiku-20240307-v1:0",
                "max_tokens": 2000,
                "temperature": 0.5,
            },
        }

        # デフォルトモデル（利用可能なモデル）
        self.default_model = "claude-3-haiku"

    async def generate_question(
        self,
        aws_info: dict[str, Any],
        topic: str = "EC2",
        difficulty: str = "professional",
    ) -> dict[str, Any]:
        """
        AWS 情報を基に Professional レベルの試験問題を生成

        Args:
            aws_info: AWS情報取得エージェントからの情報
            topic: 問題のトピック
            difficulty: 難易度

        Returns:
            生成された問題の辞書
        """
        try:
            logger.info(
                f"Generating {difficulty} question for {topic} using Bedrock Claude"
            )

            # プロンプトの構築
            prompt = self._build_question_prompt(aws_info, topic, difficulty)

            # Claude モデルで問題生成
            response = await self._invoke_claude_model(prompt)

            # レスポンスの解析
            question_data = self._parse_question_response(response, topic, difficulty)

            logger.info(f"Successfully generated question: {question_data.get('id')}")
            return question_data

        except Exception as e:
            logger.error(f"Failed to generate question with Bedrock: {e}")
            # エラーを隠蔽せず、明確に返す
            return {
                "id": f"error_{topic.lower()}_{difficulty}_{hash(str(e)) % 1000:03d}",
                "topic": topic,
                "difficulty": difficulty,
                "error": True,
                "error_type": "bedrock_api_error",
                "error_message": str(e),
                "question": f"❌ Bedrock API エラー: {str(e)}",
                "options": {
                    "A": "エラーのため選択肢を生成できません",
                    "B": "Bedrockアクセス権限を確認してください",
                    "C": "AWS認証情報を確認してください",
                    "D": "ネットワーク接続を確認してください",
                },
                "correct_answer": "B",
                "explanation": f"Bedrock APIへのアクセスでエラーが発生しました。詳細: {str(e)}",
                "aws_services": ["Bedrock"],
                "key_concepts": ["API エラー", "アクセス権限"],
                "generated_by": "error_handler",
                "generation_timestamp": "2025-08-11T23:30:00Z",
            }

    def _build_question_prompt(
        self, aws_info: dict[str, Any], topic: str, difficulty: str
    ) -> str:
        """
        問題生成用のプロンプトを構築

        Args:
            aws_info: AWS情報
            topic: トピック
            difficulty: 難易度

        Returns:
            構築されたプロンプト
        """
        # AWS情報の抽出
        documentation = aws_info.get("documentation", {})
        knowledge = aws_info.get("knowledge", {})

        prompt = f"""
あなたは AWS Certified Solutions Architect - Professional 試験の問題作成専門家です。

以下の AWS {topic} に関する最新情報を基に、Professional レベルの試験問題を1問、**日本語で**作成してください。

## AWS情報
### ドキュメント情報:
{json.dumps(documentation, indent=2, ensure_ascii=False)}

### 知識情報:
{json.dumps(knowledge, indent=2, ensure_ascii=False)}

## 要件
- 難易度: {difficulty.upper()}
- 対象: AWS Certified Solutions Architect - Professional
- **言語: 日本語**（問題文、選択肢、解説すべて日本語で作成）
- 実際のビジネスシナリオを想定した複雑な問題
- 4つの選択肢（A、B、C、D）で1つの正解と3つの説得力のある不正解
- 詳細な解説（なぜ正解なのか、なぜ他の選択肢が不正解なのか）

## 出力形式（JSON）
{{
    "question": "問題文（日本語、実際のビジネスシナリオを含む）",
    "options": {{
        "A": "選択肢A（日本語）",
        "B": "選択肢B（日本語）",
        "C": "選択肢C（日本語）",
        "D": "選択肢D（日本語）"
    }},
    "correct_answer": "正解の記号（A、B、C、Dのいずれか）",
    "explanation": "詳細な解説（日本語、正解の理由と不正解の理由を含む）",
    "topic": "{topic}",
    "difficulty": "{difficulty}",
    "aws_services": ["関連するAWSサービスのリスト"],
    "key_concepts": ["重要な概念のリスト"]
}}

Professional レベルの問題として、複数のAWSサービスの統合、アーキテクチャの最適化、
コスト効率、セキュリティ、可用性などの観点を含めてください。

**重要**: 問題文、選択肢、解説はすべて自然な日本語で作成してください。
"""
        return prompt

    async def _invoke_claude_model(
        self, prompt: str, model_name: str | None = None
    ) -> str:
        """
        Claude モデルを呼び出して応答を取得

        Args:
            prompt: 入力プロンプト
            model_name: 使用するモデル名

        Returns:
            モデルからの応答
        """
        if model_name is None:
            model_name = self.default_model

        model_config = self.model_configs[model_name]

        try:
            # Bedrock Runtime API を使用してモデルを呼び出し
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": model_config["max_tokens"],
                "temperature": model_config["temperature"],
                "messages": [{"role": "user", "content": prompt}],
            }

            response = self.bedrock_client.invoke_model(
                modelId=model_config["model_id"],
                body=json.dumps(body),
                contentType="application/json",
                accept="application/json",
            )

            # レスポンスの解析
            response_body = json.loads(response["body"].read())
            content: str = response_body["content"][0]["text"]

            logger.info(f"Successfully invoked Claude model: {model_name}")
            return content

        except ClientError as e:
            logger.error(f"Bedrock API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error invoking Claude model: {e}")
            raise

    def _parse_question_response(
        self, response: str, topic: str, difficulty: str
    ) -> dict[str, Any]:
        """
        Claude からの応答を解析して問題データを構築

        Args:
            response: Claude からの応答
            topic: トピック
            difficulty: 難易度

        Returns:
            解析された問題データ
        """
        try:
            # JSON部分を抽出（Claude の応答にはテキストが含まれる場合がある）
            json_start = response.find("{")
            json_end = response.rfind("}") + 1

            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")

            json_str = response[json_start:json_end]
            question_data: dict[str, Any] = json.loads(json_str)

            # IDの生成
            question_data["id"] = (
                f"q_{topic.lower()}_{difficulty}_{hash(question_data['question']) % 10000:04d}"
            )

            # メタデータの追加
            question_data["generated_by"] = "bedrock_claude"
            question_data["model_used"] = self.default_model
            question_data["generation_timestamp"] = "2025-08-11T20:30:00Z"

            return question_data

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.error(f"Failed to parse Claude response: {e}")
            # フォールバック処理
            return self._generate_fallback_question(
                topic, difficulty, f"Parse error: {e}"
            )

    def _generate_fallback_question(
        self, topic: str, difficulty: str, error_msg: str
    ) -> dict[str, Any]:
        """
        エラー時のサービス固有フォールバック問題を生成

        Args:
            topic: トピック
            difficulty: 難易度
            error_msg: エラーメッセージ

        Returns:
            フォールバック問題データ
        """
        # サービス固有の問題テンプレート
        service_questions = {
            "EC2": {
                "question": "大規模なWebアプリケーションを運用する企業が、EC2インスタンスのコスト最適化と高可用性を両立させる必要があります。平日は高負荷、週末は低負荷という予測可能なパターンがあります。最適なアプローチはどれですか？",
                "options": {
                    "A": "リザーブドインスタンスとオンデマンドインスタンスの組み合わせを使用する",
                    "B": "すべてスポットインスタンスで運用してコストを最小化する",
                    "C": "Auto Scalingでオンデマンドインスタンスのみを使用する",
                    "D": "最大容量でリザーブドインスタンスを購入する",
                },
                "correct_answer": "A",
                "explanation": "選択肢Aが最適です。予測可能なベースライン負荷にはリザーブドインスタンスでコストを削減し、変動する追加負荷にはオンデマンドインスタンスで柔軟に対応できます。スポットインスタンスは中断リスクがあり本番環境には不適切、オンデマンドのみでは高コスト、最大容量のリザーブドは過剰投資になります。",
                "aws_services": ["EC2", "Auto Scaling", "CloudWatch"],
                "key_concepts": [
                    "コスト最適化",
                    "高可用性",
                    "リザーブドインスタンス",
                    "Auto Scaling",
                ],
            },
            "S3": {
                "question": "メディア企業が500TBの動画コンテンツを保存し、新しいコンテンツは頻繁にアクセスされるが、古いコンテンツは稀にしかアクセスされません。ストレージコストを最適化する最良の戦略はどれですか？",
                "options": {
                    "A": "すべてのコンテンツをS3 Standardに保存する",
                    "B": "S3 Intelligent-Tieringを使用してライフサイクルポリシーを設定する",
                    "C": "すべてのコンテンツをS3 Glacier Deep Archiveに保存する",
                    "D": "S3 One Zone-IAですべてのコンテンツを保存する",
                },
                "correct_answer": "B",
                "explanation": "選択肢Bが最適です。S3 Intelligent-Tieringは自動的にアクセスパターンに基づいてオブジェクトを適切なストレージクラスに移動し、ライフサイクルポリシーで古いコンテンツをより安価なアーカイブストレージに移動できます。Standardのみでは高コスト、Glacier Deep Archiveのみでは頻繁なアクセスに不適切、One Zone-IAは耐久性が劣ります。",
                "aws_services": ["S3", "S3 Intelligent-Tiering", "S3 Glacier"],
                "key_concepts": [
                    "ストレージ最適化",
                    "ライフサイクルポリシー",
                    "アクセスパターン",
                    "コスト効率",
                ],
            },
            "VPC": {
                "question": "多層アーキテクチャのWebアプリケーションをVPCに構築する際、セキュリティを最大化しながら適切なネットワーク分離を実現する設計はどれですか？",
                "options": {
                    "A": "すべてのリソースをパブリックサブネットに配置してInternet Gatewayで接続する",
                    "B": "Webサーバーをパブリック、アプリケーションとDBをプライベートサブネットに分離する",
                    "C": "すべてのリソースをプライベートサブネットに配置してVPN接続のみを使用する",
                    "D": "各層を異なるVPCに配置してVPC Peeringで接続する",
                },
                "correct_answer": "B",
                "explanation": "選択肢Bが最適です。Webサーバーはインターネットからのアクセスが必要なのでパブリックサブネット、アプリケーションサーバーとデータベースは外部からの直接アクセスを防ぐためプライベートサブネットに配置します。これにより適切な層分離とセキュリティを実現できます。すべてパブリックは危険、すべてプライベートはWeb公開不可、複数VPCは過度に複雑です。",
                "aws_services": [
                    "VPC",
                    "Subnet",
                    "Internet Gateway",
                    "NAT Gateway",
                    "Security Groups",
                ],
                "key_concepts": [
                    "ネットワークセキュリティ",
                    "多層アーキテクチャ",
                    "サブネット分離",
                    "セキュリティグループ",
                ],
            },
        }

        # デフォルトの汎用問題
        default_question = {
            "question": f"企業が{topic}サービスを使用してクラウド移行を行う際の最適なアプローチを検討しています。{difficulty}レベルの実装において重要な考慮事項はどれですか？",
            "options": {
                "A": f"{topic}の基本設定でシンプルに実装する",
                "B": f"{topic}の高可用性とセキュリティを重視した設計を行う",
                "C": f"{topic}の最小コストのみを優先して設計する",
                "D": f"{topic}の最新機能をすべて使用して実装する",
            },
            "correct_answer": "B",
            "explanation": f"{difficulty}レベルの{topic}実装では、高可用性とセキュリティが最重要です。基本設定のみでは本番要件を満たさず、コストのみの優先は可用性を犠牲にし、最新機能の全使用は複雑性を増加させます。",
            "aws_services": [topic],
            "key_concepts": ["高可用性", "セキュリティ", "ベストプラクティス"],
        }

        # サービス固有の問題があれば使用、なければデフォルト
        question_data = service_questions.get(topic.upper(), default_question)

        fallback_question = {
            "id": f"fallback_{topic.lower()}_{difficulty}_001",
            "question": question_data["question"],
            "options": question_data["options"],
            "correct_answer": question_data["correct_answer"],
            "explanation": question_data["explanation"],
            "topic": topic,
            "difficulty": difficulty,
            "aws_services": question_data["aws_services"],
            "key_concepts": question_data["key_concepts"],
            "generated_by": "service_specific_fallback_generator",
            "error_info": error_msg,
            "generation_timestamp": "2025-08-11T23:15:00Z",
        }

        logger.info(f"Generated fallback question: {fallback_question['id']}")
        return fallback_question


# グローバル Bedrock Client インスタンス
bedrock_client = BedrockClient()


async def get_bedrock_client() -> BedrockClient:
    """
    Bedrock Client インスタンスを取得

    Returns:
        BedrockClient インスタンス
    """
    return bedrock_client
