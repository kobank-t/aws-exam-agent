# AWS Exam Agent 運用ガイド

AWS Exam Agent の日常運用、監視、メンテナンスに関する包括的なガイドです。

## 📋 概要

このガイドでは、デプロイ済みの AWS Exam Agent システムの運用に必要な情報を提供します。

## 🏗️ システム構成

```
EventBridge Scheduler → Lambda Function → AgentCore Runtime → Bedrock Models
     (定期実行)         (トリガー関数)      (問題生成AI)        (Claude等)
        ↓                    ↓                  ↓
   CloudWatch Events    CloudWatch Logs   CloudWatch Logs
```

## 📊 監視・ログ確認

### AgentCore の監視

#### ステータス確認

```bash
# 基本ステータス確認
export AWS_PROFILE=YOUR_PROFILE_NAME
cd app/agentcore
agentcore status
```

#### ログ確認

```bash
# インタラクティブなログ確認
./scripts/show-agentcore-logs.sh

# 直接ログ確認（Agent IDは実際の値に置き換え）
aws logs tail /aws/bedrock-agentcore/runtimes/agent_main-XXXXX-DEFAULT --follow --profile $AWS_PROFILE

# 過去のログ確認
aws logs tail /aws/bedrock-agentcore/runtimes/agent_main-XXXXX-DEFAULT --since 1h --profile $AWS_PROFILE

# エラーログのみ確認
aws logs tail /aws/bedrock-agentcore/runtimes/agent_main-XXXXX-DEFAULT --since 1h --profile $AWS_PROFILE | grep -i error
```

### Lambda 関数の監視

#### 基本情報確認

```bash
# Lambda関数の設定確認
aws lambda get-function --function-name aws-exam-agent-trigger-development --profile $AWS_PROFILE

# Lambda関数の最新実行状況
aws lambda get-function --function-name aws-exam-agent-trigger-development --query 'Configuration.[LastModified,State,StateReason]' --output table --profile $AWS_PROFILE
```

#### ログ確認

```bash
# リアルタイムログ監視
aws logs tail /aws/lambda/aws-exam-agent-trigger-development --follow --profile $AWS_PROFILE

# 過去のログ確認
aws logs tail /aws/lambda/aws-exam-agent-trigger-development --since 1h --profile $AWS_PROFILE

# エラーログのみ確認
aws logs tail /aws/lambda/aws-exam-agent-trigger-development --since 1h --profile $AWS_PROFILE | grep -i error
```

#### メトリクス確認

```bash
# Lambda関数の実行統計（過去24時間）
aws logs filter-log-events \
  --log-group-name /aws/lambda/aws-exam-agent-trigger-development \
  --start-time $(date -d '24 hours ago' +%s)000 \
  --filter-pattern "REPORT" \
  --query 'events[*].[eventId,message]' \
  --output table \
  --profile $AWS_PROFILE
```

### EventBridge Scheduler の監視

#### スケジュール状態確認

```bash
# メインスケジュールの状態確認
aws scheduler get-schedule --name aws-exam-agent-daily-development --profile $AWS_PROFILE

# スケジュール一覧確認
aws scheduler list-schedules --profile $AWS_PROFILE
```

#### 実行履歴確認

```bash
# CloudWatch Events での実行履歴確認
aws logs filter-log-events \
  --log-group-name /aws/events/rule/aws-exam-agent-daily-development \
  --start-time $(date -d '7 days ago' +%s)000 \
  --profile $AWS_PROFILE 2>/dev/null || echo "EventBridge実行ログは別途CloudWatchコンソールで確認してください"
```

## 🔧 日常的なメンテナンス

### 定期的な確認項目

#### 毎日の確認

```bash
# 1. AgentCore の稼働状況確認
./scripts/get-agentcore-arn.sh

# 2. 前日の実行ログ確認
aws logs tail /aws/lambda/aws-exam-agent-trigger-development --since 24h --profile $AWS_PROFILE

# 3. エラーの有無確認
aws logs tail /aws/bedrock-agentcore/runtimes/agent_main-XXXXX-DEFAULT --since 24h --profile $AWS_PROFILE | grep -i error || echo "エラーなし"
```

#### 週次の確認

```bash
# 1. システム全体の稼働状況確認
./scripts/test-agentcore.sh
./scripts/test-lambda.sh

# 2. リソース使用状況確認
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=aws-exam-agent-trigger-development \
  --start-time $(date -d '7 days ago' --iso-8601) \
  --end-time $(date --iso-8601) \
  --period 86400 \
  --statistics Average,Maximum \
  --profile $AWS_PROFILE
```

#### 月次の確認

```bash
# 1. 依存ツールの更新確認
pip list --outdated | grep bedrock-agentcore-starter-toolkit

# 2. コスト確認
aws ce get-cost-and-usage \
  --time-period Start=$(date -d '1 month ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=SERVICE \
  --profile $AWS_PROFILE
```

### 設定変更

#### スケジュール変更

```bash
# スケジュール式の変更（例：毎日9時から毎日18時に変更）
aws scheduler update-schedule \
  --name aws-exam-agent-daily-development \
  --schedule-expression "cron(0 18 * * ? *)" \
  --profile $AWS_PROFILE
```

#### 問題生成パラメータの変更

```bash
# EventBridge Schedulerのペイロード変更（例：問題数を2に変更）
# 注意: これはCloudFormationテンプレートの更新が推奨されます
aws scheduler update-schedule \
  --name aws-exam-agent-daily-development \
  --target '{
    "Arn": "arn:aws:scheduler:::aws-sdk:lambda:invoke",
    "RoleArn": "arn:aws:iam::ACCOUNT_ID:role/EventBridgeSchedulerExecutionRole-development",
    "Input": "{\"FunctionName\": \"aws-exam-agent-trigger-development\", \"InvocationType\": \"Event\", \"Payload\": \"{\\\"agentRuntimeArn\\\":\\\"YOUR_ARN\\\",\\\"exam_type\\\":\\\"SAP\\\",\\\"question_count\\\":2}\"}"
  }' \
  --profile $AWS_PROFILE
```

## 🚨 アラート・通知設定

### CloudWatch アラームの設定

#### Lambda 関数エラー率アラーム

```bash
# Lambda関数のエラー率が10%を超えた場合のアラーム
aws cloudwatch put-metric-alarm \
  --alarm-name "aws-exam-agent-lambda-error-rate" \
  --alarm-description "Lambda function error rate exceeds 10%" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --threshold 1 \
  --comparison-operator GreaterThanOrEqualToThreshold \
  --dimensions Name=FunctionName,Value=aws-exam-agent-trigger-development \
  --evaluation-periods 2 \
  --profile $AWS_PROFILE
```

#### AgentCore 応答時間アラーム

```bash
# AgentCore の応答時間が30秒を超えた場合のアラーム
aws cloudwatch put-metric-alarm \
  --alarm-name "aws-exam-agent-agentcore-duration" \
  --alarm-description "AgentCore response time exceeds 30 seconds" \
  --metric-name Duration \
  --namespace AWS/Lambda \
  --statistic Average \
  --period 300 \
  --threshold 30000 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=FunctionName,Value=aws-exam-agent-trigger-development \
  --evaluation-periods 1 \
  --profile $AWS_PROFILE
```

## 🔄 更新・デプロイ

### AgentCore の更新

```bash
# 1. コード変更後の再デプロイ
export AWS_PROFILE=YOUR_PROFILE_NAME
./scripts/deploy-agentcore.sh

# 2. 動作確認
./scripts/test-agentcore.sh

# 3. ログ確認
./scripts/show-agentcore-logs.sh
```

### Lambda 関数の更新

```bash
# 1. Lambda関数とEventBridge Schedulerの再デプロイ
./scripts/deploy-eventbridge-scheduler.sh

# 2. 動作確認
./scripts/test-lambda.sh

# 3. ログ確認
aws logs tail /aws/lambda/aws-exam-agent-trigger-development --since 10m --profile $AWS_PROFILE
```

### 依存ツールの更新

```bash
# bedrock-agentcore-starter-toolkit の更新
pip install --upgrade bedrock-agentcore-starter-toolkit

# 更新後のバージョン確認
pip show bedrock-agentcore-starter-toolkit
```

## 💰 コスト管理

### コスト確認

```bash
# 月次コスト確認
aws ce get-cost-and-usage \
  --time-period Start=$(date -d '1 month ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=SERVICE \
  --profile $AWS_PROFILE

# サービス別詳細コスト
aws ce get-cost-and-usage \
  --time-period Start=$(date -d '1 month ago' +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=SERVICE \
  --filter file://cost-filter.json \
  --profile $AWS_PROFILE
```

### コスト最適化

#### 1. Lambda 関数の最適化

```bash
# Lambda関数のメモリ使用量確認
aws logs filter-log-events \
  --log-group-name /aws/lambda/aws-exam-agent-trigger-development \
  --filter-pattern "REPORT" \
  --start-time $(date -d '7 days ago' +%s)000 \
  --query 'events[*].message' \
  --output text \
  --profile $AWS_PROFILE | grep "Max Memory Used"
```

#### 2. AgentCore の最適化

- **不要なログレベルの調整**
- **実行頻度の見直し**
- **問題生成数の最適化**

## 🔒 セキュリティ管理

### IAM ロールの確認

```bash
# Lambda実行ロールの権限確認
aws iam get-role-policy \
  --role-name LambdaTriggerFunctionRole-development \
  --policy-name AgentCoreInvokePolicy \
  --profile $AWS_PROFILE

# AgentCore実行ロールの権限確認
aws iam list-attached-role-policies \
  --role-name AmazonBedrockAgentCoreSDKRuntime-us-east-1-XXXXX \
  --profile $AWS_PROFILE
```

### セキュリティベストプラクティス

1. **最小権限の原則**: 必要最小限の権限のみ付与
2. **定期的な権限レビュー**: 月次での権限確認
3. **ログ監視**: 異常なアクセスパターンの監視
4. **SSO セッション管理**: 適切なセッション期限設定

## 🗑️ 削除・クリーンアップ

### 移行元リソースの削除

移行作業完了後、移行元アカウントのリソースを削除する場合：

```bash
# 移行元アカウントのプロファイルを指定
export AWS_PROFILE=source-account

# 削除スクリプト実行
./scripts/cleanup-source-resources.sh
```

**削除されるリソース:**
- ECRリポジトリ（全イメージ含む）
- CloudFormationスタック
- Lambda関数
- CodeBuildプロジェクト
- S3バケット
- IAMロール

**注意事項:**
- 移行先での動作確認完了後に実行
- 削除は取り消せません
- バックアップファイル（`.bedrock_agentcore.yaml.backup`）が必要

### 不要なログの削除

```bash
# 古いログの削除（30日以上前）
aws logs delete-log-group --log-group-name /aws/bedrock-agentcore/runtimes/agent_main-OLD-ID-DEFAULT --profile $AWS_PROFILE

# Lambda関数の古いログ削除
aws logs delete-log-group --log-group-name /aws/lambda/aws-exam-agent-trigger-development --profile $AWS_PROFILE
```

### S3バケットのクリーンアップ

```bash
# 古いLambda関数パッケージの削除
aws s3 ls s3://aws-exam-agent-deployments-development-ACCOUNT-ID/lambda-packages/ --profile $AWS_PROFILE
aws s3 rm s3://aws-exam-agent-deployments-development-ACCOUNT-ID/lambda-packages/OLD-PACKAGE.zip --profile $AWS_PROFILE
```

## 📞 サポート・エスカレーション

### 問題発生時の対応フロー

1. **初期調査**
   ```bash
   # システム全体の状況確認
   ./scripts/get-agentcore-arn.sh
   ./scripts/test-agentcore.sh
   ./scripts/test-lambda.sh
   ```

2. **ログ分析**
   ```bash
   # エラーログの確認
   ./scripts/show-agentcore-logs.sh
   # オプション 6（エラーログのみ）を選択
   ```

3. **詳細調査**
   - [トラブルシューティングガイド](./troubleshooting-guide.md) を参照

4. **エスカレーション**
   - GitHub Issues での報告
   - 作業記録への記載

### 緊急時の連絡先

- **GitHub Issues**: バグ報告・機能要望
- **作業記録**: [WORK_LOG.md](../WORK_LOG.md)
- **設計判断記録**: [技術選択記録](../.kiro/specs/aws-exam-agent/design/09-decisions.md)

## 📚 関連ドキュメント

- [デプロイガイド](./deployment-guide.md): 新規環境へのデプロイ
- [トラブルシューティングガイド](./troubleshooting-guide.md): 問題解決手法
- [環境変数リファレンス](./environment-variables-guide.md): 設定詳細
