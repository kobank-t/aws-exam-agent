# AgentCore 運用・保守ガイド

AWS Exam Agent の AgentCore Runtime の日常運用、保守、監視に関する詳細ガイドです。

## 📋 目次

- [日常運用手順](#日常運用手順)
- [監視とアラート](#監視とアラート)
- [パフォーマンス最適化](#パフォーマンス最適化)
- [セキュリティ管理](#セキュリティ管理)
- [バックアップとリストア](#バックアップとリストア)
- [緊急時対応](#緊急時対応)
- [コスト最適化](#コスト最適化)

## 🔄 日常運用手順

### 毎日の確認項目

#### 1. システム稼働状況確認

```bash
# AgentCore ステータス確認
cd app/agentcore
agentcore status

# 期待される出力
# {
#   "status": "READY",
#   "agent_name": "agent_main",
#   "last_updated": "2025-08-17T14:37:32Z"
# }
```

#### 2. Teams 投稿成功率確認

```bash
# 過去24時間のTeams投稿成功数
aws logs filter-log-events \
  --log-group-name "/aws/bedrock-agentcore/runtimes/agent_main-4h7OvMAtVL-DEFAULT" \
  --filter-pattern "Teams投稿完了" \
  --start-time $(date -v-1d +%s)000 \
  --region us-east-1 \
  --query 'length(events)'

# 過去24時間のTeams投稿失敗数
aws logs filter-log-events \
  --log-group-name "/aws/bedrock-agentcore/runtimes/agent_main-4h7OvMAtVL-DEFAULT" \
  --filter-pattern "Teams投稿に失敗" \
  --start-time $(date -v-1d +%s)000 \
  --region us-east-1 \
  --query 'length(events)'
```

#### 3. エラーログ確認

```bash
# 過去24時間のエラーログ
aws logs filter-log-events \
  --log-group-name "/aws/bedrock-agentcore/runtimes/agent_main-4h7OvMAtVL-DEFAULT" \
  --filter-pattern "ERROR" \
  --start-time $(date -v-1d +%s)000 \
  --region us-east-1 \
  --query 'events[*].[timestamp,message]' \
  --output table
```

#### 4. 問題生成数確認

```bash
# 過去24時間の問題生成数
aws logs filter-log-events \
  --log-group-name "/aws/bedrock-agentcore/runtimes/agent_main-4h7OvMAtVL-DEFAULT" \
  --filter-pattern "questions" \
  --start-time $(date -v-1d +%s)000 \
  --region us-east-1 \
  --query 'length(events)'
```

### 週次の確認項目

#### 1. パフォーマンスメトリクス分析

```bash
# 過去7日間の平均応答時間
aws logs filter-log-events \
  --log-group-name "/aws/bedrock-agentcore/runtimes/agent_main-4h7OvMAtVL-DEFAULT" \
  --filter-pattern "Invocation completed successfully" \
  --start-time $(date -v-7d +%s)000 \
  --region us-east-1 \
  --query 'events[*].message' \
  --output text | grep -o '[0-9]*\.[0-9]*s' | sed 's/s//' | awk '{sum+=$1; count++} END {print "Average response time:", sum/count, "seconds"}'
```

#### 2. コスト使用量確認

```bash
# Bedrock 使用量確認（過去7日間）
aws ce get-cost-and-usage \
  --time-period Start=$(date -v-7d +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity DAILY \
  --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=SERVICE \
  --filter file://cost-filter.json
```

#### 3. セキュリティ監査

```bash
# IAM ロールの権限確認
aws iam get-role --role-name BedrockAgentCoreExecutionRole-development

# ECR リポジトリのアクセス権限確認
aws ecr describe-repository --repository-name aws-exam-agent-runtime-development
```

### 月次の確認項目

#### 1. 設定ファイルのバックアップ

```bash
# 設定ファイルのバックアップ
mkdir -p backups/$(date +%Y%m)
cp app/agentcore/.bedrock_agentcore.yaml backups/$(date +%Y%m)/.bedrock_agentcore.yaml.$(date +%Y%m%d)
```

#### 2. ログの長期保存設定確認

```bash
# CloudWatch Logs の保持期間確認
aws logs describe-log-groups \
  --log-group-name-prefix "/aws/bedrock-agentcore/runtimes/agent_main" \
  --query 'logGroups[*].[logGroupName,retentionInDays]' \
  --output table
```

## 📊 監視とアラート

### CloudWatch メトリクス設定

#### 1. カスタムメトリクス作成

```bash
# Teams投稿成功率メトリクス
aws cloudwatch put-metric-data \
  --namespace "AWS-Exam-Agent/AgentCore" \
  --metric-data MetricName=TeamsPostSuccess,Value=1,Unit=Count

# 問題生成数メトリクス
aws cloudwatch put-metric-data \
  --namespace "AWS-Exam-Agent/AgentCore" \
  --metric-data MetricName=QuestionsGenerated,Value=1,Unit=Count
```

#### 2. アラーム設定

```bash
# エラー率アラーム
aws cloudwatch put-metric-alarm \
  --alarm-name "AgentCore-High-Error-Rate" \
  --alarm-description "AgentCore error rate exceeds threshold" \
  --metric-name "Errors" \
  --namespace "AWS-Exam-Agent/AgentCore" \
  --statistic "Sum" \
  --period 300 \
  --threshold 5 \
  --comparison-operator "GreaterThanThreshold" \
  --evaluation-periods 2 \
  --alarm-actions "arn:aws:sns:us-east-1:792223357133:agentcore-alerts"

# Teams投稿失敗アラーム
aws cloudwatch put-metric-alarm \
  --alarm-name "AgentCore-Teams-Post-Failure" \
  --alarm-description "Teams post failure detected" \
  --metric-name "TeamsPostFailure" \
  --namespace "AWS-Exam-Agent/AgentCore" \
  --statistic "Sum" \
  --period 600 \
  --threshold 1 \
  --comparison-operator "GreaterThanOrEqualToThreshold" \
  --evaluation-periods 1 \
  --alarm-actions "arn:aws:sns:us-east-1:792223357133:agentcore-alerts"

# 応答時間アラーム
aws cloudwatch put-metric-alarm \
  --alarm-name "AgentCore-High-Response-Time" \
  --alarm-description "AgentCore response time is too high" \
  --metric-name "ResponseTime" \
  --namespace "AWS-Exam-Agent/AgentCore" \
  --statistic "Average" \
  --period 300 \
  --threshold 60 \
  --comparison-operator "GreaterThanThreshold" \
  --evaluation-periods 3 \
  --alarm-actions "arn:aws:sns:us-east-1:792223357133:agentcore-alerts"
```

### ダッシュボード作成

```bash
# CloudWatch ダッシュボード作成
aws cloudwatch put-dashboard \
  --dashboard-name "AWS-Exam-Agent-AgentCore" \
  --dashboard-body file://dashboard-config.json
```

**dashboard-config.json**:
```json
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS-Exam-Agent/AgentCore", "TeamsPostSuccess"],
          [".", "TeamsPostFailure"],
          [".", "QuestionsGenerated"]
        ],
        "period": 300,
        "stat": "Sum",
        "region": "us-east-1",
        "title": "AgentCore Metrics"
      }
    }
  ]
}
```

## ⚡ パフォーマンス最適化

### 応答時間の最適化

#### 1. モデル選択の最適化

```python
# agent_main.py での最適化例
BEDROCK_MODEL_CONFIG = {
    "model_id": "anthropic.claude-3-haiku-20240307-v1:0",  # より高速なモデル
    "max_tokens": 4000,  # トークン数の最適化
    "temperature": 0.7
}
```

#### 2. キャッシュ戦略

```python
# レスポンスキャッシュの実装例
import functools
import time

@functools.lru_cache(maxsize=100)
def generate_question_cached(topic: str, difficulty: str) -> str:
    """キャッシュ付き問題生成"""
    return generate_question(topic, difficulty)
```

#### 3. 並列処理の最適化

```python
# 並列処理での最適化
import asyncio
import aiohttp

async def parallel_processing():
    """並列処理による高速化"""
    tasks = []
    async with aiohttp.ClientSession() as session:
        for i in range(5):
            task = asyncio.create_task(process_request(session, i))
            tasks.append(task)
        results = await asyncio.gather(*tasks)
    return results
```

### リソース使用量の最適化

#### 1. メモリ使用量監視

```bash
# メモリ使用量の確認
aws logs filter-log-events \
  --log-group-name "/aws/bedrock-agentcore/runtimes/agent_main-4h7OvMAtVL-DEFAULT" \
  --filter-pattern "memory" \
  --start-time $(date -v-1H +%s)000 \
  --region us-east-1
```

#### 2. CPU 使用率監視

```bash
# CloudWatch メトリクスでCPU使用率確認
aws cloudwatch get-metric-statistics \
  --namespace "AWS/BedrockAgentCore" \
  --metric-name "CPUUtilization" \
  --dimensions Name=AgentName,Value=agent_main \
  --start-time $(date -v-1H -u +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average,Maximum
```

## 🔒 セキュリティ管理

### アクセス権限の定期確認

#### 1. IAM ロールの監査

```bash
# 実行ロールの権限確認
aws iam list-attached-role-policies \
  --role-name BedrockAgentCoreExecutionRole-development

# インラインポリシーの確認
aws iam list-role-policies \
  --role-name BedrockAgentCoreExecutionRole-development
```

#### 2. ECR リポジトリのセキュリティ

```bash
# ECR リポジトリの脆弱性スキャン
aws ecr start-image-scan \
  --repository-name aws-exam-agent-runtime-development \
  --image-id imageTag=latest

# スキャン結果の確認
aws ecr describe-image-scan-findings \
  --repository-name aws-exam-agent-runtime-development \
  --image-id imageTag=latest
```

#### 3. 環境変数の暗号化

```bash
# AWS Systems Manager Parameter Store での環境変数管理
aws ssm put-parameter \
  --name "/aws-exam-agent/power-automate-webhook-url" \
  --value "https://prod-04.japaneast.logic.azure.com/workflows/..." \
  --type "SecureString" \
  --description "Power Automate Webhook URL for Teams integration"
```

### ログの監査

```bash
# 不審なアクセスパターンの検出
aws logs filter-log-events \
  --log-group-name "/aws/bedrock-agentcore/runtimes/agent_main-4h7OvMAtVL-DEFAULT" \
  --filter-pattern "[timestamp, request_id, level=\"ERROR\", ...]" \
  --start-time $(date -v-1d +%s)000 \
  --region us-east-1
```

## 💾 バックアップとリストア

### 設定ファイルのバックアップ

#### 1. 自動バックアップスクリプト

```bash
#!/bin/bash
# backup-agentcore-config.sh

BACKUP_DIR="backups/agentcore"
DATE=$(date +%Y%m%d_%H%M%S)

# バックアップディレクトリの作成
mkdir -p $BACKUP_DIR

# 設定ファイルのバックアップ
cp app/agentcore/.bedrock_agentcore.yaml $BACKUP_DIR/.bedrock_agentcore.yaml.$DATE

# 古いバックアップの削除（30日以上古いもの）
find $BACKUP_DIR -name "*.yaml.*" -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR/.bedrock_agentcore.yaml.$DATE"
```

#### 2. S3 への自動バックアップ

```bash
# S3 バケットへのバックアップ
aws s3 cp app/agentcore/.bedrock_agentcore.yaml \
  s3://aws-exam-agent-backups/agentcore/config-$(date +%Y%m%d_%H%M%S).yaml

# バックアップの確認
aws s3 ls s3://aws-exam-agent-backups/agentcore/ --recursive
```

### リストア手順

#### 1. 設定ファイルのリストア

```bash
# バックアップからのリストア
cp backups/agentcore/.bedrock_agentcore.yaml.20250817_143000 \
   app/agentcore/.bedrock_agentcore.yaml

# 設定の確認
agentcore status
```

#### 2. 緊急時の完全リストア

```bash
# S3 からの緊急リストア
aws s3 cp s3://aws-exam-agent-backups/agentcore/config-20250817_143000.yaml \
  app/agentcore/.bedrock_agentcore.yaml

# 再デプロイ
agentcore launch --auto-update-on-conflict
```

## 🚨 緊急時対応

### 障害対応手順

#### 1. 障害の検知と初期対応

```bash
# 1. システム状態の確認
agentcore status

# 2. 最新のエラーログ確認
aws logs tail /aws/bedrock-agentcore/runtimes/agent_main-4h7OvMAtVL-DEFAULT --since 10m

# 3. Teams投稿の状況確認
aws logs filter-log-events \
  --log-group-name "/aws/bedrock-agentcore/runtimes/agent_main-4h7OvMAtVL-DEFAULT" \
  --filter-pattern "Teams" \
  --start-time $(date -v-30M +%s)000 \
  --region us-east-1
```

#### 2. 一般的な障害パターンと対処法

**パターン1: Teams投稿失敗**
```bash
# 環境変数の再設定
agentcore launch \
  --env POWER_AUTOMATE_WEBHOOK_URL="<webhook_url>" \
  --auto-update-on-conflict
```

**パターン2: 問題生成失敗**
```bash
# Bedrock サービスの状態確認
aws bedrock list-foundation-models --region us-east-1

# モデルアクセス権限の確認
aws bedrock get-model-invocation-logging-configuration --region us-east-1
```

**パターン3: 完全なサービス停止**
```bash
# 緊急再デプロイ
cd app/agentcore
agentcore launch --auto-update-on-conflict

# 状態確認
agentcore status
```

#### 3. エスカレーション手順

1. **Level 1**: 自動復旧スクリプトの実行
2. **Level 2**: 手動での再デプロイ
3. **Level 3**: AWS サポートへの連絡

### 災害復旧計画

#### 1. RTO/RPO 目標

- **RTO (Recovery Time Objective)**: 30分
- **RPO (Recovery Point Objective)**: 1時間

#### 2. 復旧手順

```bash
# 1. 最新バックアップの確認
aws s3 ls s3://aws-exam-agent-backups/agentcore/ --recursive | tail -5

# 2. 設定ファイルの復元
aws s3 cp s3://aws-exam-agent-backups/agentcore/config-latest.yaml \
  app/agentcore/.bedrock_agentcore.yaml

# 3. 完全再デプロイ
agentcore launch --env POWER_AUTOMATE_WEBHOOK_URL="<webhook_url>"

# 4. 動作確認
agentcore invoke '{"prompt": "テスト"}'
```

## 💰 コスト最適化

### コスト監視

#### 1. 日次コスト確認

```bash
# Bedrock 使用コスト（過去24時間）
aws ce get-cost-and-usage \
  --time-period Start=$(date -v-1d +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity DAILY \
  --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=SERVICE \
  --filter '{"Dimensions":{"Key":"SERVICE","Values":["Amazon Bedrock"]}}'
```

#### 2. 使用量ベースの最適化

```bash
# トークン使用量の分析
aws logs filter-log-events \
  --log-group-name "/aws/bedrock-agentcore/runtimes/agent_main-4h7OvMAtVL-DEFAULT" \
  --filter-pattern "tokens" \
  --start-time $(date -v-1d +%s)000 \
  --region us-east-1 \
  --query 'events[*].message' | grep -o '[0-9]* tokens' | awk '{sum+=$1; count++} END {print "Average tokens per request:", sum/count}'
```

### 最適化施策

#### 1. モデル選択の最適化

```python
# コスト効率の良いモデル選択
MODEL_COST_EFFICIENCY = {
    "claude-3-haiku": {"cost_per_token": 0.00025, "speed": "fast"},
    "claude-3-sonnet": {"cost_per_token": 0.003, "speed": "medium"},
    "claude-3-opus": {"cost_per_token": 0.015, "speed": "slow"}
}
```

#### 2. リクエスト頻度の最適化

```bash
# EventBridge Scheduler の頻度調整
aws scheduler update-schedule \
  --name "aws-exam-agent-daily-trigger" \
  --schedule-expression "rate(2 hours)"  # 1時間から2時間に変更
```

#### 3. 予算アラートの設定

```bash
# 月次予算アラートの設定
aws budgets create-budget \
  --account-id 792223357133 \
  --budget '{
    "BudgetName": "AWS-Exam-Agent-Monthly",
    "BudgetLimit": {
      "Amount": "100",
      "Unit": "USD"
    },
    "TimeUnit": "MONTHLY",
    "BudgetType": "COST"
  }' \
  --notifications-with-subscribers '[{
    "Notification": {
      "NotificationType": "ACTUAL",
      "ComparisonOperator": "GREATER_THAN",
      "Threshold": 80
    },
    "Subscribers": [{
      "SubscriptionType": "EMAIL",
      "Address": "admin@example.com"
    }]
  }]'
```

## 📚 運用チェックリスト

### 日次チェックリスト

- [ ] AgentCore ステータス確認
- [ ] Teams 投稿成功率確認
- [ ] エラーログ確認
- [ ] 問題生成数確認
- [ ] 応答時間確認

### 週次チェックリスト

- [ ] パフォーマンスメトリクス分析
- [ ] コスト使用量確認
- [ ] セキュリティ監査
- [ ] アラート設定確認
- [ ] バックアップ状況確認

### 月次チェックリスト

- [ ] 設定ファイルバックアップ
- [ ] ログ保持期間確認
- [ ] IAM 権限監査
- [ ] ECR 脆弱性スキャン
- [ ] 災害復旧テスト
- [ ] コスト最適化レビュー

---

**最終更新**: 2025-08-17  
**バージョン**: 1.0.0
