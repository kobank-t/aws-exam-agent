# Cloud CoPassAgent デプロイガイド

Cloud CoPassAgent を新しい AWS アカウント（AWS SSO 環境）にデプロイする包括的なガイドです。

## 📋 概要

このガイドでは、以下のコンポーネントを統合的にデプロイします：

- **AgentCore Runtime**: AWS Bedrock AgentCore で動作する AI エージェント
- **Lambda 関数**: EventBridge Scheduler からの呼び出し用
- **EventBridge Scheduler**: 定期実行スケジュール
- **関連リソース**: ECR、IAM、S3、CodeBuild

## 🏗️ システム構成

```
EventBridge Scheduler → Lambda Function → AgentCore Runtime → Bedrock Models
     (定期実行)         (トリガー関数)      (問題生成AI)        (Claude等)
```

## 🔧 事前準備：環境変数設定

### 必須環境変数

| 変数名                          | 説明                                       | 例                                                                 |
| ------------------------------- | ------------------------------------------ | ------------------------------------------------------------------ |
| `BEDROCK_MODEL_ID`              | 使用する Bedrock モデル ID                 | `jp.anthropic.claude-sonnet-4-5-20250929-v1:0`                     |
| `BEDROCK_REGION`                | Bedrock モデル呼び出しのリージョン         | `ap-northeast-1`                                                   |
| `POWER_AUTOMATE_WEBHOOK_URL`    | Teams 連携用 Webhook URL                   | `https://prod-XX.japaneast.logic.azure.com/workflows/...`          |
| `POWER_AUTOMATE_SECURITY_TOKEN` | Webhook URL 漏洩対策用セキュリティトークン | `cef26f0de574983a475345f2e3518abbd6472d102b5254384ef6912931f8a68f` |
| `AGENTCORE_MEMORY_ID`           | ジャンル分散機能用 AgentCore Memory ID     | `CloudCoPassAgentMemory_1758470667-YvBRIT3DdL`                     |

### 環境変数の設定

プロジェクトルートに `.env` ファイルを作成：

```bash
# セキュリティトークンの生成（64文字のランダム文字列）
SECURITY_TOKEN=$(openssl rand -hex 32)
echo $SECURITY_TOKEN
# 例: a1b2c3d4e5f6789... （実際の値は毎回異なります）

# .envファイルの作成
cat > .env << EOF
# Bedrock モデル設定
BEDROCK_MODEL_ID=jp.anthropic.claude-sonnet-4-5-20250929-v1:0
BEDROCK_REGION=ap-northeast-1

# Teams 連携（必須）
POWER_AUTOMATE_WEBHOOK_URL=https://prod-XX.japaneast.logic.azure.com/workflows/YOUR-WORKFLOW-ID/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=YOUR-SIGNATURE

# セキュリティトークン（必須）
POWER_AUTOMATE_SECURITY_TOKEN=$SECURITY_TOKEN

# AgentCore Memory ID（ジャンル分散機能用）
AGENTCORE_MEMORY_ID=CloudCoPassAgentMemory_XXXXXXXXX-XXXXXXXXXX
EOF
```

**Bedrock モデル設定の選択肢**:

- `jp.anthropic.claude-sonnet-4-5-20250929-v1:0`: Claude Sonnet 4.5（JP Cross-Region、日本国内限定）
- `us.anthropic.claude-sonnet-4-5-20250929-v1:0`: Claude Sonnet 4.5（US Cross-Region）
- `global.anthropic.claude-sonnet-4-5-20250929-v1:0`: Claude Sonnet 4.5（Global、最高スループット）
- `anthropic.claude-3-5-sonnet-20240620-v1:0`: Claude 3.5 Sonnet（ON_DEMAND）

**重要**: 上記の例の値は実際には使用しないでください。必ず `openssl rand -hex 32` で生成した値を使用してください。

### Power Automate Webhook URL の取得

1. **Power Automate** にアクセス
2. **新しいフロー** を作成
3. **HTTP 要求の受信時** トリガーを選択
4. **JSON スキーマ** を設定：

```json
{
  "type": "object",
  "properties": {
    "question": {
      "type": "string"
    },
    "options": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "correct_answer": {
      "type": "string"
    },
    "explanation": {
      "type": "string"
    },
    "security_token": {
      "type": "string"
    }
  }
}
```

5. **Teams にメッセージを投稿** アクションを追加
6. **保存** して **HTTP POST URL** をコピー

## 🚀 前提条件

### 必要なツール

- **Python 3.12+**
- **bedrock-agentcore-starter-toolkit** (最新版)
- **AWS CLI v2** (SSO 対応)
- **jq** (JSON 処理用)

### AWS SSO 情報

デプロイ先アカウントの SSO 情報を事前に確認：

- **SSO Start URL**: 組織の SSO URL
- **SSO Region**: SSO が設定されているリージョン
- **デプロイ先アカウント ID**: 移行先アカウント
- **使用ロール**: `AdministratorAccess` 等
- **デプロイリージョン**: `us-east-1` (推奨)

### 必要な権限

デプロイ先アカウントで以下の権限が必要：

- `AmazonBedrockFullAccess` (推奨) または個別権限：
  - `bedrock:InvokeModel*`
  - `bedrock:CreateInferenceProfile`
  - ECR、IAM、CodeBuild、S3、Lambda、EventBridge の必要権限

## 📝 デプロイ手順

### ステップ 1: AWS SSO の設定

#### 1.1 AWS CLI プロファイル設定

```bash
# SSO プロファイル設定
aws configure sso --profile YOUR_PROFILE_NAME
```

**設定時の入力例:**

| 項目                      | 入力値例                                  | 説明                           |
| ------------------------- | ----------------------------------------- | ------------------------------ |
| SSO session name          | `deployment-session`                      | 任意のセッション名             |
| SSO start URL             | `https://d-xxxxxxxxx.awsapps.com/start/#` | 組織の SSO URL                 |
| SSO region                | `ap-northeast-1`                          | SSO が設定されているリージョン |
| Account                   | `123456789012`                            | デプロイ先アカウント ID        |
| Role                      | `AdministratorAccess`                     | 使用するロール                 |
| CLI default client Region | `us-east-1`                               | デプロイ先リージョン           |
| CLI default output format | `json`                                    | 出力形式                       |

#### 1.2 SSO ログインと接続確認

```bash
# 環境変数設定
export AWS_PROFILE=YOUR_PROFILE_NAME

# SSO ログイン
aws sso login --profile $AWS_PROFILE

# 接続確認
aws sts get-caller-identity
```

### ステップ 2: 依存ツールの準備

#### 2.1 bedrock-agentcore-starter-toolkit の更新

```bash
# 現在のバージョン確認
pip show bedrock-agentcore-starter-toolkit

# 最新版へのアップデート
pip install --upgrade bedrock-agentcore-starter-toolkit

# バージョン確認
pip show bedrock-agentcore-starter-toolkit
```

### ステップ 3: AgentCore のデプロイ

#### 3.1 既存設定のバックアップ（既存環境の場合）

```bash
cd app/agentcore

# 設定ファイルのバックアップ
cp .bedrock_agentcore.yaml .bedrock_agentcore.yaml.backup 2>/dev/null || true
cp Dockerfile Dockerfile.backup 2>/dev/null || true
cp .dockerignore .dockerignore.backup 2>/dev/null || true
```

#### 3.2 AgentCore 設定の生成

```bash
# 既存の自動生成ファイルを削除（クリーンな状態で開始）
rm -f .bedrock_agentcore.yaml Dockerfile .dockerignore

# 新しいアカウント用設定の生成
export AWS_PROFILE=YOUR_PROFILE_NAME
agentcore configure --entrypoint agent_main.py
```

**設定時の選択:**

- **Execution role**: **Enter**（自動作成）
- **ECR Repository**: **Enter**（自動作成）
- **Dependency file**: **Enter**（requirements.txt 使用）
- **OAuth authorizer**: **no**（IAM 認証使用）

#### 3.3 環境変数の設定

AgentCore デプロイ前に、Teams 連携用の Webhook URL とセキュリティトークンを設定する必要があります：

```bash
# セキュリティトークンの生成（64文字のランダム文字列）
SECURITY_TOKEN=$(openssl rand -hex 32)
echo "生成されたセキュリティトークン: $SECURITY_TOKEN"

# .envファイルの作成（プロジェクトルート）
cat > .env << EOF
POWER_AUTOMATE_WEBHOOK_URL=https://prod-XX.japaneast.logic.azure.com/workflows/YOUR-WORKFLOW-ID/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=YOUR-SIGNATURE
POWER_AUTOMATE_SECURITY_TOKEN=$SECURITY_TOKEN
AGENTCORE_MEMORY_ID=CloudCoPassAgentMemory_XXXXXXXXX-XXXXXXXXXX
EOF
```

**⚠️ 重要**:

- `POWER_AUTOMATE_WEBHOOK_URL`、`POWER_AUTOMATE_SECURITY_TOKEN`、`AGENTCORE_MEMORY_ID`の全てが設定されていない場合、デプロイは失敗します
- セキュリティトークンは Webhook URL 漏洩対策として必須です
- AgentCore Memory ID はジャンル分散機能に必要です（事前に `uv run python scripts/create_agentcore_memory.py` で作成）
- 生成されたセキュリティトークンは後で Power Automate フローの設定で使用します

#### 3.4 AgentCore のデプロイ実行

```bash
# 環境変数設定
export AWS_PROFILE=YOUR_PROFILE_NAME

# デプロイスクリプト実行（.envから自動的にWebhook URLを読み込み）
./scripts/deploy-agentcore.sh
```

**デプロイで自動作成されるリソース:**

- ECR リポジトリ: `bedrock-agentcore-agent_main`
- IAM ロール: 実行ロール・ビルドロール
- S3 バケット: CodeBuild 用ソース保存
- CodeBuild プロジェクト: ARM64 コンテナビルド
- AgentCore Runtime

#### 3.5 AgentCore Memory 権限の追加（ジャンル分散機能用）

AgentCore がジャンル分散機能を使用するために、Memory アクセス権限を追加します：

```bash
# Memory権限を追加
export AWS_PROFILE=YOUR_PROFILE_NAME
./scripts/setup-memory-permissions.sh
```

**追加される権限:**

- `bedrock-agentcore:ListEvents` - 学習分野履歴の取得
- `bedrock-agentcore:CreateEvent` - 学習分野履歴の記録

**対象リソース:**

- AgentCore Memory ID（`.env`ファイルの`AGENTCORE_MEMORY_ID`で指定）

**⚠️ 重要**: この手順は AgentCore デプロイ後に実行してください。Memory ID が `.env` ファイルに設定されていない場合はスクリプトが失敗します。

#### 3.6 AgentCore 動作確認

```bash
# AgentCore 動作確認テスト
./scripts/test-agentcore.sh
```

### ステップ 4: AgentCore ARN の確認

#### 4.1 ARN 確認スクリプトの実行

```bash
# AgentCore ARN確認
./scripts/get-agentcore-arn.sh
```

#### 4.2 ARN の記録

出力された `Agent Arn:` の値を記録してください：

```
arn:aws:bedrock-agentcore:us-east-1:123456789012:runtime/agent_main-XXXXX
```

### ステップ 5: Lambda + EventBridge Scheduler のデプロイ

#### 5.1 EventBridge Scheduler デプロイ

```bash
# EventBridge Scheduler デプロイ
./scripts/deploy-eventbridge-scheduler.sh
```

**デプロイ時の入力:**

- **AgentCore Runtime ARN**: ステップ 4.2 で記録した ARN を入力
- **デプロイ確認**: `y` を入力

**デプロイで自動作成されるリソース:**

- Lambda 関数: `aws-exam-agent-trigger-development`
- IAM ロール: Lambda 実行ロール・Scheduler 実行ロール
- S3 バケット: Lambda 関数パッケージ保存用
- EventBridge Schedule: `aws-exam-agent-daily-development` (平日午前 9 時実行)

#### 5.2 Lambda 関数テスト

```bash
# Lambda関数テスト実行
./scripts/test-lambda.sh
```

**テスト時の入力:**

- **AgentCore Runtime ARN**: ステップ 4.2 で記録した ARN を入力

### ステップ 6: EventBridge Scheduler 実行テスト

#### 6.1 テストスケジュールの作成

```bash
# 2分後に実行されるテストスケジュールを作成
export AWS_PROFILE=YOUR_PROFILE_NAME
EXEC_TIME=$(TZ=Asia/Tokyo date -v+2M '+%M %H %d %m')
echo "実行予定時刻: $(TZ=Asia/Tokyo date -v+2M '+%Y-%m-%d %H:%M:%S')"

aws scheduler create-schedule \
  --name "aws-exam-agent-test-2min" \
  --description "Test schedule for Cloud CoPassAgent (runs once in 2 minutes)" \
  --schedule-expression "cron($EXEC_TIME ? 2025)" \
  --schedule-expression-timezone "Asia/Tokyo" \
  --state "ENABLED" \
  --flexible-time-window Mode=OFF \
  --target '{
    "Arn": "arn:aws:scheduler:::aws-sdk:lambda:invoke",
    "RoleArn": "arn:aws:iam::ACCOUNT_ID:role/EventBridgeSchedulerExecutionRole-development",
    "Input": "{\"FunctionName\": \"aws-exam-agent-trigger-development\", \"InvocationType\": \"Event\", \"Payload\": \"{\\\"agentRuntimeArn\\\":\\\"YOUR_AGENTCORE_ARN\\\",\\\"exam_type\\\":\\\"AWS-SAP\\\",\\\"question_count\\\":1}\"}"
  }' \
  --action-after-completion DELETE \
  --region us-east-1
```

#### 6.2 実行結果の確認

```bash
# Lambda関数のログを確認（実行後）
aws logs tail /aws/lambda/aws-exam-agent-trigger-development --since 10m --profile $AWS_PROFILE
```

### ステップ 7: 最終確認

#### 7.1 全体システムの確認

```bash
# AgentCore ステータス確認
cd app/agentcore && agentcore status

# EventBridge Scheduler確認
aws scheduler get-schedule --name aws-exam-agent-daily-development --profile $AWS_PROFILE

# Lambda関数確認
aws lambda get-function --function-name aws-exam-agent-trigger-development --profile $AWS_PROFILE
```

#### 7.2 ログ確認

```bash
# AgentCore ログ確認
./scripts/show-agentcore-logs.sh

# Lambda関数ログ確認
aws logs tail /aws/lambda/aws-exam-agent-trigger-development --follow --profile $AWS_PROFILE
```

## 🔧 トラブルシューティング

### よくある問題と解決方法

#### 1. SSO セッション期限切れ

**症状:**

```
TokenRefreshRequired: Token refresh required
```

**解決方法:**

```bash
# 再ログイン
aws sso login --profile $AWS_PROFILE
aws sts get-caller-identity --profile $AWS_PROFILE
```

#### 2. Bedrock モデルアクセスエラー

**症状:**

```
AccessDeniedException: User is not authorized to perform: bedrock:InvokeModelWithResponseStream
```

**原因と対策:**

1. **Service Control Policy (SCP) 制限**

   - 組織管理者に SCP 制限の解除を依頼

2. **クロスリージョン推論の問題**

   - 推論プロファイル使用時に意図しないリージョンにアクセス
   - 直接モデル ID（ON_DEMAND 対応）への変更を検討

3. **モデルアクセス権限不足**
   - IAM ロールに適切な Bedrock 権限を追加

#### 3. ARN 入力ミス

**症状:** Lambda 関数テストで ARN エラー

**解決方法:**

```bash
# ARNを再確認
./scripts/get-agentcore-arn.sh

# 正しいARNで環境変数設定
export AGENTCORE_ARN="arn:aws:bedrock-agentcore:us-east-1:123456789012:runtime/agent_main-XXXXX"
./scripts/test-lambda.sh
```

#### 4. プロファイル指定忘れ

**症状:** 間違ったアカウントにデプロイされる

**解決方法:**

```bash
# 環境変数での統一的な指定
export AWS_PROFILE=YOUR_PROFILE_NAME

# 全てのスクリプトでこの環境変数が使用される
./scripts/deploy-agentcore.sh
./scripts/deploy-eventbridge-scheduler.sh
./scripts/test-lambda.sh
```

## 📚 利用可能なスクリプト

### デプロイ関連

| スクリプト                                  | 用途                             | 前提条件               | 使用例                                                          |
| ------------------------------------------- | -------------------------------- | ---------------------- | --------------------------------------------------------------- |
| `./scripts/deploy-agentcore.sh`             | AgentCore のデプロイ             | AWS SSO ログイン済み   | `AWS_PROFILE=sandbox ./scripts/deploy-agentcore.sh`             |
| `./scripts/setup-memory-permissions.sh`     | AgentCore Memory 権限追加        | AgentCore デプロイ済み | `AWS_PROFILE=sandbox ./scripts/setup-memory-permissions.sh`     |
| `./scripts/deploy-eventbridge-scheduler.sh` | EventBridge Scheduler のデプロイ | AgentCore デプロイ済み | `AWS_PROFILE=sandbox ./scripts/deploy-eventbridge-scheduler.sh` |
| `./scripts/build-lambda.sh`                 | Lambda 関数のビルド              | Python 3.12+           | `./scripts/build-lambda.sh`                                     |

### 確認・テスト関連

| スクリプト                         | 用途               | 前提条件               | 使用例                                                 |
| ---------------------------------- | ------------------ | ---------------------- | ------------------------------------------------------ |
| `./scripts/get-agentcore-arn.sh`   | AgentCore ARN 確認 | AgentCore デプロイ済み | `AWS_PROFILE=sandbox ./scripts/get-agentcore-arn.sh`   |
| `./scripts/test-agentcore.sh`      | AgentCore 動作確認 | AgentCore デプロイ済み | `AWS_PROFILE=sandbox ./scripts/test-agentcore.sh`      |
| `./scripts/test-lambda.sh`         | Lambda 関数テスト  | Lambda デプロイ済み    | `AWS_PROFILE=sandbox ./scripts/test-lambda.sh`         |
| `./scripts/show-agentcore-logs.sh` | AgentCore ログ確認 | AgentCore デプロイ済み | `AWS_PROFILE=sandbox ./scripts/show-agentcore-logs.sh` |

### 削除・クリーンアップ関連

| スクリプト                              | 用途               | 前提条件                     | 使用例                                                      |
| --------------------------------------- | ------------------ | ---------------------------- | ----------------------------------------------------------- |
| `./scripts/cleanup-source-resources.sh` | 移行元リソース削除 | 移行完了・移行元アクセス可能 | `AWS_PROFILE=default ./scripts/cleanup-source-resources.sh` |

### 開発・品質管理関連

| スクリプト                                  | 用途                            | 前提条件                 | 使用例                                      |
| ------------------------------------------- | ------------------------------- | ------------------------ | ------------------------------------------- |
| `./scripts/setup-dev.sh`                    | 開発環境セットアップ            | Python 3.12+, uv         | `./scripts/setup-dev.sh`                    |
| `./scripts/python-quality-check.sh`         | Python 品質チェック・テスト実行 | 開発環境セットアップ済み | `./scripts/python-quality-check.sh`         |
| `./scripts/infrastructure-quality-check.sh` | インフラ品質チェック            | yamllint, cfn-lint       | `./scripts/infrastructure-quality-check.sh` |

## 🔄 継続的な運用

### 日常的な作業フロー

```bash
# 1. 作業開始時
export AWS_PROFILE=YOUR_PROFILE_NAME
aws sso login --profile $AWS_PROFILE

# 2. AgentCore コード修正後のデプロイ
./scripts/deploy-agentcore.sh

# 2.1. Memory権限の確認・追加（必要に応じて）
./scripts/setup-memory-permissions.sh

# 3. Lambda関数修正後のデプロイ
./scripts/deploy-eventbridge-scheduler.sh

# 4. 動作確認
./scripts/test-agentcore.sh
./scripts/test-lambda.sh

# 5. 問題発生時のログ確認
./scripts/show-agentcore-logs.sh
```

### 定期的なメンテナンス

1. **bedrock-agentcore-starter-toolkit の定期更新**
2. **SSO セッションの管理**
3. **CloudWatch Logs の監視**
4. **コスト最適化の検討**

## ✅ デプロイ完了チェックリスト

- [ ] AWS SSO プロファイル設定完了
- [ ] SSO ログイン・接続確認完了
- [ ] bedrock-agentcore-starter-toolkit 最新版への更新完了
- [ ] AgentCore デプロイ完了（`./scripts/deploy-agentcore.sh`）
- [ ] AgentCore Memory 権限追加完了（`./scripts/setup-memory-permissions.sh`）
- [ ] AgentCore ARN 確認完了（`./scripts/get-agentcore-arn.sh`）
- [ ] EventBridge Scheduler デプロイ完了（`./scripts/deploy-eventbridge-scheduler.sh`）
- [ ] AgentCore 動作確認完了（`./scripts/test-agentcore.sh`）
- [ ] Lambda 関数テスト完了（`./scripts/test-lambda.sh`）
- [ ] EventBridge Scheduler 実行テスト完了
- [ ] ログ確認完了（`./scripts/show-agentcore-logs.sh`）
- [ ] エラーがないことを確認完了

## 📋 生成される AWS リソース

デプロイ完了後、以下のリソースが自動作成されます：

### AgentCore 関連

- **ECR リポジトリ**: `bedrock-agentcore-agent_main`
- **IAM ロール**:
  - `AmazonBedrockAgentCoreSDKRuntime-us-east-1-xxx` (実行ロール)
  - `AmazonBedrockAgentCoreSDKCodeBuild-us-east-1-xxx` (ビルドロール)
- **S3 バケット**: `bedrock-agentcore-codebuild-sources-{account-id}-us-east-1`
- **CodeBuild プロジェクト**: `bedrock-agentcore-agent_main-builder`
- **AgentCore Runtime**: `agent_main-xxx`

### Lambda + EventBridge Scheduler 関連

- **Lambda 関数**: `aws-exam-agent-trigger-development`
- **IAM ロール**:
  - `LambdaTriggerFunctionRole-development` (Lambda 実行ロール)
  - `EventBridgeSchedulerExecutionRole-development` (Scheduler 実行ロール)
- **S3 バケット**: `aws-exam-agent-deployments-development-{account-id}`
- **EventBridge Schedule**: `aws-exam-agent-daily-development`

## 🗑️ 移行元リソースの削除

移行が完了し、移行先での動作確認が済んだ後は、移行元アカウントのリソースを削除してください。

### 削除前の確認事項

1. **移行先での動作確認完了**: 全ての機能が正常に動作することを確認
2. **移行元アカウントへのアクセス**: 移行元アカウント用の AWS プロファイルが利用可能
3. **バックアップファイルの存在**: `app/agentcore/.bedrock_agentcore.yaml.backup` が存在することを確認

### 削除手順

#### ステップ 1: 移行元アカウントプロファイルの確認

```bash
# プロファイル一覧確認
aws configure list-profiles

# 移行元アカウントの特定
for profile in $(aws configure list-profiles); do
  echo "Profile: $profile"
  aws sts get-caller-identity --profile $profile --query 'Account' --output text 2>/dev/null || echo "  アクセス不可"
done
```

#### ステップ 2: 削除スクリプトの実行

```bash
# 移行元アカウントのプロファイルを指定（例：default）
export AWS_PROFILE=default

# 削除スクリプト実行
./scripts/cleanup-source-resources.sh
```

#### ステップ 3: 削除内容の確認

削除スクリプトは以下の手順でリソースを削除します：

1. **ECR リポジトリの強制削除**

   - CloudFormation 削除失敗を防ぐため事前実行
   - 全コンテナイメージを含めて削除

2. **CloudFormation スタックの削除**

   - EventBridge Schedule、Lambda 関数、IAM ロールが自動削除

3. **残存リソースの個別削除**
   - CodeBuild プロジェクト、S3 バケット、IAM ロールを個別削除

### 削除されるリソース

| リソースタイプ          | リソース名例                               | 削除方法                       |
| ----------------------- | ------------------------------------------ | ------------------------------ |
| ECR リポジトリ          | `aws-exam-agent-runtime-development`       | 強制削除（イメージ含む）       |
| CloudFormation スタック | `aws-exam-agent-scheduler-development`     | スタック削除                   |
| CloudFormation スタック | `aws-exam-agent-agentcore`                 | スタック削除                   |
| Lambda 関数             | `aws-exam-agent-trigger-development`       | 個別削除                       |
| CodeBuild プロジェクト  | `bedrock-agentcore-agent_main-builder`     | 個別削除                       |
| S3 バケット             | `aws-exam-agent-deployments-development-*` | オブジェクト削除後バケット削除 |
| S3 バケット             | `bedrock-agentcore-codebuild-sources-*`    | オブジェクト削除後バケット削除 |
| IAM ロール              | `AmazonBedrockAgentCore*`                  | ポリシーデタッチ後削除         |
| IAM ロール              | `LambdaTriggerFunctionRole*`               | ポリシーデタッチ後削除         |
| IAM ロール              | `EventBridgeSchedulerExecutionRole*`       | ポリシーデタッチ後削除         |

### 削除後の確認と後処理

#### ステップ 1: 移行先での動作確認

```bash
# 移行先での動作確認
export AWS_PROFILE=sandbox
./scripts/test-agentcore.sh
./scripts/test-lambda.sh
```

#### ステップ 2: バックアップファイルの削除

移行元リソース削除が完了し、移行先での動作確認も済んだら、不要になったバックアップファイルを削除：

```bash
# 移行元設定のバックアップファイル削除
rm -f app/agentcore/.bedrock_agentcore.yaml.backup
rm -f app/agentcore/Dockerfile.backup
rm -f app/agentcore/.dockerignore.backup

# 削除確認
ls -la app/agentcore/ | grep backup || echo "バックアップファイルは全て削除されました"
```

**削除するファイル:**

- `.bedrock_agentcore.yaml.backup`: 移行元 AgentCore 設定
- `Dockerfile.backup`: 移行元 Docker ファイル
- `.dockerignore.backup`: 移行元 Docker ignore 設定

**注意:**

- これらのファイルは移行元リソース削除時に必要でしたが、削除完了後は不要です
- 削除スクリプト実行後に表示されるコマンドをコピーして実行してください

### トラブルシューティング

#### CloudFormation 削除失敗

**症状**: ECR リポジトリにイメージが残っているためスタック削除が失敗

**対応**: 削除スクリプトが ECR リポジトリを事前削除するため、通常は発生しません

#### IAM ロール削除失敗

**症状**: ポリシーがアタッチされているためロール削除が失敗

**対応**: 削除スクリプトが自動的にポリシーをデタッチしてからロールを削除します

## 🚨 既知の制限事項

### Bedrock モデルアクセス制限

**現象**: AgentCore でのモデル呼び出し時に AccessDeniedException が発生

**原因**:

- Service Control Policy (SCP) による制限
- クロスリージョン推論による意図しないリージョンへのアクセス

**対応**: 組織管理者に SCP 制限の解除を依頼
