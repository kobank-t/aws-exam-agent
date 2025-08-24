# 環境変数設定ガイド

AWS Exam Agent の環境変数設定について説明します。

## 🔧 必須環境変数

| 変数名 | 説明 | 例 | 環境 |
|--------|------|----|-----|
| `AWS_ACCESS_KEY_ID` | AWS アクセスキー ID | `<your-access-key-id>` | ローカル |
| `AWS_SECRET_ACCESS_KEY` | AWS シークレットアクセスキー | `<your-secret-access-key>` | ローカル |
| `AWS_DEFAULT_REGION` | AWS デフォルトリージョン | `us-east-1` | ローカル |
| `POWER_AUTOMATE_WEBHOOK_URL` | Teams 連携用 Webhook URL | `<your-webhook-url>` | 全環境 |

## 🎛️ オプション環境変数

| 変数名 | 説明 | デフォルト値 | 環境 |
|--------|------|-------------|------|
| `BEDROCK_MODEL_ID` | 使用する Bedrock モデル ID | `anthropic.claude-3-haiku-20240307-v1:0` | 全環境 |
| `MAX_TOKENS` | 最大トークン数 | `4000` | 全環境 |
| `TEMPERATURE` | モデルの温度パラメータ | `0.7` | 全環境 |
| `LOG_LEVEL` | ログレベル | `INFO` | 全環境 |

## 💻 ローカル開発環境

### .env ファイルの設定

プロジェクトルートに `.env` ファイルを作成：

```bash
# AWS 認証情報
AWS_ACCESS_KEY_ID=<your-access-key-id>
AWS_SECRET_ACCESS_KEY=<your-secret-access-key>
AWS_DEFAULT_REGION=us-east-1

# Teams 連携
POWER_AUTOMATE_WEBHOOK_URL=<your-webhook-url>

# Bedrock 設定（オプション）
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
MAX_TOKENS=4000
TEMPERATURE=0.7

# ログ設定
LOG_LEVEL=INFO
```

### AWS 認証情報の取得方法

1. **AWS CLI での設定**:
   ```bash
   aws configure
   ```

2. **IAM ユーザーでの設定**:
   - AWS Console → IAM → Users → Create User
   - 必要な権限を付与（Bedrock, DynamoDB, Lambda など）
   - Access Key を生成

3. **必要な権限**:
   - `bedrock:InvokeModel`
   - `dynamodb:GetItem`, `dynamodb:PutItem`, `dynamodb:UpdateItem`
   - `lambda:InvokeFunction`

## 🚀 本番環境

### AgentCore Runtime

AgentCore では環境変数は自動的に設定されます：

```yaml
# .bedrock_agentcore.yaml での設定例
environment_variables:
  BEDROCK_MODEL_ID: "anthropic.claude-3-haiku-20240307-v1:0"
  MAX_TOKENS: "4000"
  TEMPERATURE: "0.7"
  LOG_LEVEL: "INFO"
```

### Lambda 環境

Lambda 関数では CloudFormation テンプレートで設定：

```yaml
Environment:
  Variables:
    POWER_AUTOMATE_WEBHOOK_URL: !Ref PowerAutomateWebhookUrl
    LOG_LEVEL: INFO
```

## 🔒 セキュリティ考慮事項

- **機密情報の管理**: AWS Secrets Manager または Parameter Store を使用
- **環境分離**: 開発・ステージング・本番で異なる値を使用
- **アクセス制御**: 最小権限の原則に従った IAM ポリシー設定
- **ログ出力**: 機密情報がログに出力されないよう注意

## 🔍 トラブルシューティング

### よくある問題

1. **認証エラー**:
   ```
   NoCredentialsError: Unable to locate credentials
   ```
   → AWS 認証情報が正しく設定されているか確認

2. **権限エラー**:
   ```
   AccessDenied: User is not authorized to perform
   ```
   → IAM ポリシーで必要な権限が付与されているか確認

3. **リージョンエラー**:
   ```
   InvalidRegion: The region 'xxx' is not supported
   ```
   → AWS_DEFAULT_REGION が正しく設定されているか確認

### デバッグ方法

```bash
# 環境変数の確認
env | grep AWS

# AWS CLI での認証確認
aws sts get-caller-identity

# Bedrock の利用可能性確認
aws bedrock list-foundation-models --region us-east-1
```
