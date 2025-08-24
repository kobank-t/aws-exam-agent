# AgentCore デプロイメントガイド

AWS Exam Agent の AgentCore Runtime のデプロイ、設定、動作確認の包括的なガイドです。

## 📋 目次

- [前提条件](#前提条件)
- [初回セットアップ](#初回セットアップ)
- [環境変数設定](#環境変数設定)
- [デプロイメント](#デプロイメント)
- [動作確認](#動作確認)
- [トラブルシューティング](#トラブルシューティング)
- [運用・監視](#運用監視)

## 🔧 前提条件

### 必要なツール

- **Python 3.12+**
- **uv** (Python パッケージ管理)
- **AWS CLI** (設定済み)
- **bedrock-agentcore CLI**

### AWS 権限

以下の AWS サービスへのアクセス権限が必要です：

- Amazon Bedrock AgentCore
- Amazon ECR
- AWS CodeBuild
- Amazon S3
- AWS IAM
- Amazon CloudWatch Logs

### 環境変数

ローカル開発用の `.env` ファイルに以下を設定：

```bash
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1
POWER_AUTOMATE_WEBHOOK_URL=https://prod-04.japaneast.logic.azure.com/workflows/...
```

## 🚀 初回セットアップ

### 1. プロジェクトのクローンと環境構築

```bash
# リポジトリのクローン
git clone https://github.com/kobank-t/aws-exam-agent.git
cd aws-exam-agent

# 開発環境の自動セットアップ
./scripts/setup-dev.sh

# 環境設定ファイルの作成
cp .env.example .env
# .env ファイルを編集して実際の値を設定
```

### 2. AgentCore CLI のインストール確認

```bash
# AgentCore CLI の動作確認
agentcore --help

# バージョン確認
agentcore configure --help
```

### 3. 設定ファイルの確認

AgentCore の設定ファイルは `app/agentcore/.bedrock_agentcore.yaml` に配置されています：

```yaml
default_agent: agent_main
agents:
  agent_main:
    name: agent_main
    entrypoint: agent_main.py
    platform: linux/arm64
    container_runtime: docker
    aws:
      execution_role: arn:aws:iam::792223357133:role/BedrockAgentCoreExecutionRole-development
      region: us-east-1
      ecr_repository: 792223357133.dkr.ecr.us-east-1.amazonaws.com/aws-exam-agent-runtime-development
      # ... その他の設定
```

## 🔐 環境変数設定

### ローカル開発環境

`.env` ファイルに環境変数を設定：

```bash
# Teams 連携用 Power Automate Webhook URL
POWER_AUTOMATE_WEBHOOK_URL=https://prod-04.japaneast.logic.azure.com/workflows/8be560e9f99a43cfa51d487553591556/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=2mqOUM7CoKfr9qbTwUZ-iwENDYr78DIMoeGIwTt5QkM
```

### AgentCore Runtime 環境

AgentCore Runtime への環境変数設定は、デプロイ時に `--env` オプションで指定します：

```bash
agentcore launch --env POWER_AUTOMATE_WEBHOOK_URL="<webhook_url>" --auto-update-on-conflict
```

## 📦 デプロイメント

### 基本デプロイ手順

1. **AgentCore ディレクトリに移動**

```bash
cd app/agentcore
```

2. **環境変数付きデプロイ実行**

```bash
# 環境変数を指定してデプロイ
agentcore launch \
  --env POWER_AUTOMATE_WEBHOOK_URL="https://prod-04.japaneast.logic.azure.com/workflows/8be560e9f99a43cfa51d487553591556/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=2mqOUM7CoKfr9qbTwUZ-iwENDYr78DIMoeGIwTt5QkM" \
  --auto-update-on-conflict
```

### デプロイオプション

AgentCore は3つのデプロイモードをサポートしています：

#### 1. CodeBuild モード（推奨・デフォルト）

```bash
agentcore launch --env POWER_AUTOMATE_WEBHOOK_URL="<webhook_url>"
```

- **特徴**: クラウドで ARM64 コンテナをビルド
- **利点**: ローカル Docker 不要、本番環境対応
- **用途**: 本番デプロイメント

#### 2. ローカル開発モード

```bash
agentcore launch --local --env POWER_AUTOMATE_WEBHOOK_URL="<webhook_url>"
```

- **特徴**: ローカルでビルド・実行
- **利点**: 高速な開発サイクル
- **用途**: 開発・テスト

#### 3. ローカルビルド + クラウドデプロイ

```bash
agentcore launch --local-build --env POWER_AUTOMATE_WEBHOOK_URL="<webhook_url>"
```

- **特徴**: ローカルビルド、クラウドデプロイ
- **利点**: カスタムビルド制御
- **用途**: 特殊な要件がある場合

### デプロイ成功の確認

デプロイが成功すると以下のような出力が表示されます：

```
✓ CodeBuild completed: bedrock-agentcore-agent_main-builder:xxxxx
✓ ARM64 image pushed to ECR: 792223357133.dkr.ecr.us-east-1.amazonaws.com/aws-exam-agent-runtime-development:latest

╭─────────────────────────────────────────────────────────────────────────────
│ CodeBuild ARM64 Deployment Successful!
│ 
│ Agent Name: agent_main
│ Agent ARN: arn:aws:bedrock-agentcore:us-east-1:792223357133:runtime/agent_main-4h7OvMAtVL
│ 
│ You can now check the status with: agentcore status
│ You can now invoke with: agentcore invoke '{"prompt": "Hello"}'
╰─────────────────────────────────────────────────────────────────────────────
```

## ✅ 動作確認

### 1. AgentCore ステータス確認

```bash
cd app/agentcore
agentcore status
```

**期待される出力例**：
```json
{
  "status": "READY",
  "agent_name": "agent_main",
  "agent_arn": "arn:aws:bedrock-agentcore:us-east-1:792223357133:runtime/agent_main-4h7OvMAtVL",
  "last_updated": "2025-08-17T14:37:32Z"
}
```

### 2. 基本動作テスト

```bash
# 簡単なテスト
agentcore invoke '{"prompt": "Hello"}'

# AWS SAP試験問題生成テスト
agentcore invoke '{"prompt": "AWS SAP試験問題を1問生成してください"}'
```

### 3. Teams 投稿テスト

Teams 投稿が正常に動作しているかを確認：

```bash
# CloudWatch ログで Teams 投稿を確認
aws logs filter-log-events \
  --log-group-name "/aws/bedrock-agentcore/runtimes/agent_main-4h7OvMAtVL-DEFAULT" \
  --start-time $(date -v-5M +%s)000 \
  --query 'events[*].[timestamp,message]' \
  --output table \
  --region us-east-1 | grep -i teams
```

**期待されるログ**：
```
Teams投稿完了 (HTTP 202)
HTTP Request: POST https://prod-04.japaneast.logic.azure.com/workflows/... "HTTP/1.1 202 Accepted"
```

### 4. 継続的監視

```bash
# リアルタイムログ監視
aws logs tail /aws/bedrock-agentcore/runtimes/agent_main-4h7OvMAtVL-DEFAULT --follow

# 過去1時間のログ確認
aws logs tail /aws/bedrock-agentcore/runtimes/agent_main-4h7OvMAtVL-DEFAULT --since 1h
```

## 🔧 トラブルシューティング

### よくある問題と解決方法

#### 1. インポートエラー

**エラー**: `ModuleNotFoundError: No module named 'app'`

**解決方法**: インポート文を相対インポートに修正
```python
# ❌ 間違い
from app.agentcore.teams_client import TeamsClient

# ✅ 正しい
from .teams_client import TeamsClient
```

#### 2. 環境変数が設定されていない

**エラー**: `POWER_AUTOMATE_WEBHOOK_URL が設定されていません`

**解決方法**: デプロイ時に環境変数を指定
```bash
agentcore launch --env POWER_AUTOMATE_WEBHOOK_URL="<webhook_url>" --auto-update-on-conflict
```

#### 3. Teams 投稿失敗

**症状**: Teams にメッセージが投稿されない

**確認手順**:
1. CloudWatch ログで HTTP ステータスコードを確認
2. Power Automate Webhook URL の有効性を確認
3. 環境変数の設定を再確認

#### 4. デプロイ失敗

**症状**: CodeBuild でビルドが失敗する

**確認手順**:
1. AWS 権限の確認
2. ECR リポジトリの存在確認
3. IAM ロールの設定確認

### ログ確認コマンド

```bash
# エラーログの確認
aws logs filter-log-events \
  --log-group-name "/aws/bedrock-agentcore/runtimes/agent_main-4h7OvMAtVL-DEFAULT" \
  --filter-pattern "ERROR" \
  --start-time $(date -v-1H +%s)000 \
  --region us-east-1

# 警告ログの確認
aws logs filter-log-events \
  --log-group-name "/aws/bedrock-agentcore/runtimes/agent_main-4h7OvMAtVL-DEFAULT" \
  --filter-pattern "WARN" \
  --start-time $(date -v-1H +%s)000 \
  --region us-east-1
```

## 📊 運用・監視

### 定期的な確認項目

#### 日次確認

1. **AgentCore ステータス確認**
```bash
agentcore status
```

2. **Teams 投稿の成功確認**
```bash
aws logs filter-log-events \
  --log-group-name "/aws/bedrock-agentcore/runtimes/agent_main-4h7OvMAtVL-DEFAULT" \
  --filter-pattern "Teams投稿完了" \
  --start-time $(date -v-1d +%s)000 \
  --region us-east-1
```

#### 週次確認

1. **エラーログの確認**
2. **パフォーマンスメトリクスの確認**
3. **コスト使用量の確認**

### アラート設定

CloudWatch アラームの設定例：

```bash
# エラー率アラーム
aws cloudwatch put-metric-alarm \
  --alarm-name "AgentCore-Error-Rate" \
  --alarm-description "AgentCore error rate is high" \
  --metric-name "Errors" \
  --namespace "AWS/BedrockAgentCore" \
  --statistic "Sum" \
  --period 300 \
  --threshold 5 \
  --comparison-operator "GreaterThanThreshold" \
  --evaluation-periods 2
```

### バックアップとリストア

#### 設定ファイルのバックアップ

```bash
# 設定ファイルのバックアップ
cp app/agentcore/.bedrock_agentcore.yaml backups/.bedrock_agentcore.yaml.$(date +%Y%m%d_%H%M%S)
```

#### 緊急時のロールバック

```bash
# 前のバージョンに戻す場合
agentcore launch --auto-update-on-conflict
```

## 📚 関連ドキュメント

- [EventBridge Scheduler デプロイ手順](./eventbridge-scheduler-deployment.md)
- [Teams 連携セットアップ](./teams-integration-setup.md)
- [AWS Exam Agent システム概要](../README.md)

## 🔗 有用なリンク

- [AWS Bedrock AgentCore 公式ドキュメント](https://docs.aws.amazon.com/bedrock/)
- [AWS CLI リファレンス](https://docs.aws.amazon.com/cli/)
- [CloudWatch Logs ユーザーガイド](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/)

---

**最終更新**: 2025-08-17  
**バージョン**: 1.0.0
