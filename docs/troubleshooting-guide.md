# AWS Exam Agent トラブルシューティングガイド

AWS Exam Agent で発生する問題の診断・解決方法を体系的にまとめたガイドです。

## 📋 概要

このガイドでは、AWS Exam Agent の運用中に発生する可能性のある問題を分類し、効率的な解決方法を提供します。

## 🔍 問題の分類と診断フロー

### 問題の分類

1. **認証・権限関連**: SSO、IAM、SCP制限
2. **AgentCore関連**: デプロイ、実行、モデルアクセス
3. **Lambda関連**: 実行エラー、タイムアウト、権限
4. **EventBridge Scheduler関連**: スケジュール実行、設定
5. **ネットワーク・接続関連**: API呼び出し、リージョン

### 診断フロー

```
問題発生
    ↓
1. 基本情報収集
    ↓
2. ログ確認・分析
    ↓
3. 問題分類
    ↓
4. 対応策実行
    ↓
5. 動作確認
```

## 🚨 緊急時の初期対応

### 1. システム全体の状況確認

```bash
# 環境変数設定
export AWS_PROFILE=YOUR_PROFILE_NAME

# 基本接続確認
aws sts get-caller-identity

# AgentCore 状況確認
cd app/agentcore && agentcore status

# Lambda関数状況確認
aws lambda get-function --function-name aws-exam-agent-trigger-development --query 'Configuration.State'

# EventBridge Scheduler状況確認
aws scheduler get-schedule --name aws-exam-agent-daily-development --query 'State'
```

### 2. 最新ログの確認

```bash
# AgentCore ログ（過去1時間）
aws logs tail /aws/bedrock-agentcore/runtimes/agent_main-XXXXX-DEFAULT --since 1h

# Lambda ログ（過去1時間）
aws logs tail /aws/lambda/aws-exam-agent-trigger-development --since 1h

# エラーログのみ抽出
aws logs tail /aws/bedrock-agentcore/runtimes/agent_main-XXXXX-DEFAULT --since 1h | grep -i "error\|exception\|failed"
```

## 🔐 認証・権限関連の問題

### SSO セッション期限切れ

**症状:**
```
TokenRefreshRequired: Token refresh required
ExpiredTokenException: The security token included in the request is expired
```

**診断:**
```bash
# セッション状態確認
aws sts get-caller-identity --profile $AWS_PROFILE
```

**解決方法:**
```bash
# 再ログイン
aws sso login --profile $AWS_PROFILE

# 接続確認
aws sts get-caller-identity --profile $AWS_PROFILE
```

### IAM 権限不足

**症状:**
```
AccessDeniedException: User is not authorized to perform: [ACTION] on resource: [RESOURCE]
```

**診断:**
```bash
# 現在の権限確認
aws sts get-caller-identity --profile $AWS_PROFILE

# 使用中のロール確認
aws iam get-role --role-name $(aws sts get-caller-identity --query 'Arn' --output text | cut -d'/' -f2) --profile $AWS_PROFILE
```

**解決方法:**
1. **必要な権限の確認**: エラーメッセージから不足している権限を特定
2. **IAM ポリシーの更新**: 管理者に権限追加を依頼
3. **一時的な権限昇格**: 管理者権限での実行を検討

### Service Control Policy (SCP) 制限

**症状:**
```
AccessDeniedException: ... with an explicit deny in a service control policy
```

**診断:**
```bash
# 組織情報確認
aws organizations describe-organization --profile $AWS_PROFILE 2>/dev/null || echo "組織外アカウントまたは権限不足"

# アカウント情報確認
aws sts get-caller-identity --profile $AWS_PROFILE
```

**解決方法:**
1. **組織管理者への連絡**: SCP制限の解除を依頼
2. **代替サービスの検討**: 制限されていないサービスでの代替実装
3. **一時的な制限解除**: テスト期間中の制限緩和を依頼

## 🤖 AgentCore関連の問題

### AgentCore デプロイエラー

**症状:**
```
agentcore launch failed
CodeBuild build failed
ECR push failed
```

**診断:**
```bash
# AgentCore 設定確認
cd app/agentcore
cat .bedrock_agentcore.yaml

# CodeBuild ログ確認
aws codebuild batch-get-builds --ids $(aws codebuild list-builds-for-project --project-name bedrock-agentcore-agent_main-builder --query 'ids[0]' --output text) --query 'builds[0].logs.cloudWatchLogs.groupName' --profile $AWS_PROFILE
```

**解決方法:**
```bash
# 1. 設定の再生成
rm -f .bedrock_agentcore.yaml Dockerfile .dockerignore
agentcore configure --entrypoint agent_main.py

# 2. 再デプロイ
agentcore launch --auto-update-on-conflict

# 3. 詳細ログ確認
agentcore launch --verbose
```

### Bedrock モデルアクセスエラー

**症状:**
```
AccessDeniedException: User is not authorized to perform: bedrock:InvokeModelWithResponseStream
```

**診断:**
```bash
# 使用しているモデルID確認
grep -n "model_id\|MODEL_ID" app/agentcore/agent_main.py

# 利用可能なモデル確認
aws bedrock list-foundation-models --region us-east-1 --profile $AWS_PROFILE

# 推論プロファイル確認
aws bedrock list-inference-profiles --region us-east-1 --profile $AWS_PROFILE
```

**解決方法:**

1. **SCP制限の場合:**
   ```bash
   # 組織管理者にSCP制限解除を依頼
   echo "組織管理者に以下の制限解除を依頼:"
   echo "- bedrock:InvokeModel*"
   echo "- 対象リージョン: us-east-1, us-east-2, us-west-2"
   ```

2. **クロスリージョン推論の問題:**
   ```bash
   # 直接モデルIDに変更（推論プロファイルを避ける）
   # app/agentcore/agent_main.py の MODEL_ID を確認・修正
   ```

3. **モデル利用権限の追加:**
   ```bash
   # IAM ロールに Bedrock 権限を追加
   aws iam attach-role-policy \
     --role-name AmazonBedrockAgentCoreSDKRuntime-us-east-1-XXXXX \
     --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess \
     --profile $AWS_PROFILE
   ```

### AgentCore 応答遅延・タイムアウト

**症状:**
```
Task timed out after 300.00 seconds
AgentCore response time exceeds expected duration
```

**診断:**
```bash
# 最近の実行時間確認
aws logs filter-log-events \
  --log-group-name /aws/lambda/aws-exam-agent-trigger-development \
  --filter-pattern "REPORT" \
  --start-time $(date -d '24 hours ago' +%s)000 \
  --query 'events[*].message' \
  --profile $AWS_PROFILE | grep Duration
```

**解決方法:**
1. **タイムアウト値の調整**: Lambda関数のタイムアウトを延長
2. **処理の最適化**: 問題生成数の削減、プロンプトの最適化
3. **リソースの増強**: Lambda関数のメモリ増加

## 🔧 Lambda関連の問題

### Lambda 関数実行エラー

**症状:**
```
{
  "errorMessage": "...",
  "errorType": "...",
  "stackTrace": [...]
}
```

**診断:**
```bash
# 最新のエラーログ確認
aws logs tail /aws/lambda/aws-exam-agent-trigger-development --since 1h --profile $AWS_PROFILE | grep -A 10 -B 5 ERROR

# Lambda関数の設定確認
aws lambda get-function --function-name aws-exam-agent-trigger-development --profile $AWS_PROFILE
```

**解決方法:**

1. **権限エラーの場合:**
   ```bash
   # IAM ロールの権限確認・修正
   aws iam get-role-policy --role-name LambdaTriggerFunctionRole-development --policy-name AgentCoreInvokePolicy --profile $AWS_PROFILE
   ```

2. **コードエラーの場合:**
   ```bash
   # Lambda関数の再デプロイ
   ./scripts/deploy-eventbridge-scheduler.sh
   ```

3. **環境変数エラーの場合:**
   ```bash
   # 環境変数の確認・設定
   aws lambda get-function-configuration --function-name aws-exam-agent-trigger-development --query 'Environment' --profile $AWS_PROFILE
   ```

### Lambda 関数タイムアウト

**症状:**
```
Task timed out after X.XX seconds
```

**診断:**
```bash
# 実行時間の傾向確認
aws logs filter-log-events \
  --log-group-name /aws/lambda/aws-exam-agent-trigger-development \
  --filter-pattern "REPORT" \
  --start-time $(date -d '7 days ago' +%s)000 \
  --profile $AWS_PROFILE | grep Duration | tail -10
```

**解決方法:**
```bash
# タイムアウト値の増加（例：300秒→600秒）
aws lambda update-function-configuration \
  --function-name aws-exam-agent-trigger-development \
  --timeout 600 \
  --profile $AWS_PROFILE
```

## 📅 EventBridge Scheduler関連の問題

### スケジュール実行されない

**症状:**
- 予定時刻にLambda関数が実行されない
- EventBridge Schedulerのログにエラー

**診断:**
```bash
# スケジュール状態確認
aws scheduler get-schedule --name aws-exam-agent-daily-development --profile $AWS_PROFILE

# スケジュール式の確認
aws scheduler get-schedule --name aws-exam-agent-daily-development --query 'ScheduleExpression' --profile $AWS_PROFILE

# IAM ロール確認
aws scheduler get-schedule --name aws-exam-agent-daily-development --query 'Target.RoleArn' --profile $AWS_PROFILE
```

**解決方法:**

1. **スケジュール状態の修正:**
   ```bash
   # スケジュールの有効化
   aws scheduler update-schedule \
     --name aws-exam-agent-daily-development \
     --state ENABLED \
     --profile $AWS_PROFILE
   ```

2. **スケジュール式の修正:**
   ```bash
   # 正しいcron式に修正（例：毎日9時）
   aws scheduler update-schedule \
     --name aws-exam-agent-daily-development \
     --schedule-expression "cron(0 9 * * ? *)" \
     --profile $AWS_PROFILE
   ```

3. **IAM ロールの修正:**
   ```bash
   # EventBridge Scheduler実行ロールの権限確認
   aws iam get-role-policy \
     --role-name EventBridgeSchedulerExecutionRole-development \
     --policy-name SchedulerExecutionPolicy \
     --profile $AWS_PROFILE
   ```

### スケジュール設定エラー

**症状:**
```
ValidationException: Invalid schedule expression
InvalidParameterValueException: Invalid target configuration
```

**診断:**
```bash
# 現在の設定確認
aws scheduler get-schedule --name aws-exam-agent-daily-development --profile $AWS_PROFILE | jq '.'
```

**解決方法:**
1. **cron式の修正**: [cron式ジェネレーター](https://crontab.guru/) で正しい式を生成
2. **ターゲット設定の修正**: JSON形式の確認・修正
3. **タイムゾーンの確認**: `Asia/Tokyo` 等の正しいタイムゾーン指定

## 🌐 ネットワーク・接続関連の問題

### API呼び出しエラー

**症状:**
```
ConnectTimeoutError: Connect timeout on endpoint URL
ReadTimeoutError: Read timeout on endpoint URL
```

**診断:**
```bash
# ネットワーク接続確認
curl -I https://bedrock-agentcore.us-east-1.amazonaws.com/

# DNS解決確認
nslookup bedrock-agentcore.us-east-1.amazonaws.com
```

**解決方法:**
1. **タイムアウト値の調整**: boto3 設定でタイムアウト値を増加
2. **リトライ設定の調整**: 指数バックオフでのリトライ実装
3. **ネットワーク環境の確認**: プロキシ、ファイアウォール設定の確認

### リージョン関連エラー

**症状:**
```
EndpointConnectionError: Could not connect to the endpoint URL
InvalidRegionError: Invalid region specified
```

**診断:**
```bash
# 設定されているリージョン確認
aws configure get region --profile $AWS_PROFILE

# 利用可能なリージョン確認
aws ec2 describe-regions --query 'Regions[*].RegionName' --profile $AWS_PROFILE
```

**解決方法:**
```bash
# 正しいリージョンの設定
aws configure set region us-east-1 --profile $AWS_PROFILE

# 環境変数での上書き
export AWS_DEFAULT_REGION=us-east-1
```

## 🔧 高度なトラブルシューティング

### ログ分析の自動化

```bash
# エラーパターンの自動抽出
aws logs filter-log-events \
  --log-group-name /aws/bedrock-agentcore/runtimes/agent_main-XXXXX-DEFAULT \
  --filter-pattern "ERROR" \
  --start-time $(date -d '24 hours ago' +%s)000 \
  --query 'events[*].[eventId,message]' \
  --output table \
  --profile $AWS_PROFILE
```

### パフォーマンス分析

```bash
# Lambda関数の実行時間分析
aws logs filter-log-events \
  --log-group-name /aws/lambda/aws-exam-agent-trigger-development \
  --filter-pattern "REPORT" \
  --start-time $(date -d '7 days ago' +%s)000 \
  --query 'events[*].message' \
  --output text \
  --profile $AWS_PROFILE | \
  grep -o 'Duration: [0-9.]*' | \
  awk '{print $2}' | \
  sort -n
```

### 設定の整合性チェック

```bash
# AgentCore ARN の整合性確認
AGENTCORE_ARN=$(cd app/agentcore && agentcore status | grep -oE 'arn:aws:bedrock-agentcore:[^│]+' | head -1)
LAMBDA_ARN=$(aws scheduler get-schedule --name aws-exam-agent-daily-development --query 'Target.Input' --output text --profile $AWS_PROFILE | jq -r '.Payload' | jq -r '.agentRuntimeArn')

echo "AgentCore ARN: $AGENTCORE_ARN"
echo "Lambda設定ARN: $LAMBDA_ARN"

if [ "$AGENTCORE_ARN" = "$LAMBDA_ARN" ]; then
  echo "✅ ARN整合性OK"
else
  echo "❌ ARN不整合 - EventBridge Schedulerの再デプロイが必要"
fi
```

## 📞 エスカレーション

### 問題解決できない場合

1. **情報収集の完了確認**
   - エラーメッセージの完全なコピー
   - 関連するログの収集
   - 実行環境の詳細情報

2. **GitHub Issues での報告**
   - 問題の詳細な説明
   - 再現手順
   - 期待される動作と実際の動作

3. **作業記録への記載**
   - [WORK_LOG.md](../WORK_LOG.md) への問題と対応の記録

### 緊急時の連絡先

- **GitHub Issues**: https://github.com/your-org/aws-exam-agent/issues
- **作業記録**: [WORK_LOG.md](../WORK_LOG.md)
- **設計判断記録**: [技術選択記録](../.kiro/specs/aws-exam-agent/design/09-decisions.md)

## 📚 関連ドキュメント

- [デプロイガイド](./deployment-guide.md): 新規環境へのデプロイ
- [運用ガイド](./operations-guide.md): 日常運用・監視
- [環境変数リファレンス](./environment-variables-guide.md): 設定詳細

## 🔄 継続的改善

### トラブルシューティングの記録

問題が解決した際は、以下の情報を記録してください：

1. **問題の詳細**: 症状、エラーメッセージ
2. **根本原因**: 問題の真の原因
3. **解決方法**: 実際に効果があった対応
4. **予防策**: 同様の問題を防ぐための改善点

### ドキュメントの更新

新しい問題や解決方法が見つかった場合は、このドキュメントを更新してください。
