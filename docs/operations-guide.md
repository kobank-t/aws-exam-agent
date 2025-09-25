# Cloud CoPassAgent 運用ガイド

Cloud CoPassAgent の日常運用、監視、メンテナンスに関する包括的なガイドです。

## 📋 概要

このガイドでは、デプロイ済みの Cloud CoPassAgent システムの運用に必要な情報を提供します。

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

## 🧠 AgentCore Memory 管理

### Memory 管理スクリプト

AgentCore Memory（ジャンル分散機能）の管理には以下のスクリプトを使用します：

#### 統合管理スクリプト（推奨）

```bash
# Memory リソース管理
python scripts/agentcore_memory/manage.py <command>
```

| コマンド     | 説明                      | 使用例                                                 |
| ------------ | ------------------------- | ------------------------------------------------------ |
| `create`     | Memory リソース作成       | `python scripts/agentcore_memory/manage.py create`     |
| `list`       | Memory リソース一覧表示   | `python scripts/agentcore_memory/manage.py list`       |
| `delete-old` | 古い Memory リソース削除  | `python scripts/agentcore_memory/manage.py delete-old` |
| `show`       | Memory 内容を表示         | `python scripts/agentcore_memory/manage.py show`       |
| `analyze`    | Memory 使用状況を詳細分析 | `python scripts/agentcore_memory/manage.py analyze`    |
| `cleanup`    | 最新イベント以外を削除    | `python scripts/agentcore_memory/manage.py cleanup`    |
| `clear`      | 全イベントを削除          | `python scripts/agentcore_memory/manage.py clear`      |
| `help`       | ヘルプを表示              | `python scripts/agentcore_memory/manage.py help`       |

#### bash 版管理スクリプト

```bash
export AWS_PROFILE=YOUR_PROFILE_NAME
./scripts/manage-agentcore-memory.sh <command>
```

| コマンド  | 説明                      | 使用例                                         |
| --------- | ------------------------- | ---------------------------------------------- |
| `show`    | Memory 内容を表示         | `./scripts/manage-agentcore-memory.sh show`    |
| `analyze` | Memory 使用状況を詳細分析 | `./scripts/manage-agentcore-memory.sh analyze` |
| `cleanup` | 最新イベント以外を削除    | `./scripts/manage-agentcore-memory.sh cleanup` |
| `clear`   | 全イベントを削除          | `./scripts/manage-agentcore-memory.sh clear`   |
| `help`    | ヘルプを表示              | `./scripts/manage-agentcore-memory.sh help`    |

#### Memory 内容の確認

```bash
# 基本的な内容確認
./scripts/manage-agentcore-memory.sh show
```

**出力例:**

```
📊 AgentCore Memory 内容
=========================
📋 基本情報:
   Memory ID: CloudCoPassAgentMemory_1758470667-YvBRIT3DdL
   Session ID: AWS-SAP
   Actor ID: cloud-copass-agent
   総イベント数: 5

📈 学習分野別統計:
┌─────────────────────────────────────────────────────────┬───────┐
│ 学習分野                                                │ 回数  │
├─────────────────────────────────────────────────────────┼───────┤
│ コンピューティング                                      │     2 │
│ ストレージ                                              │     2 │
│ ネットワーキング                                        │     1 │
└─────────────────────────────────────────────────────────┴───────┘

⏰ 最新イベント（最新10件）:
┌──────────────────────┬─────────────────────────────────────────────┐
│ 日時                 │ 学習分野                                    │
├──────────────────────┼─────────────────────────────────────────────┤
│ 2025-09-22 09:00     │ ネットワーキング                            │
│ 2025-09-21 18:00     │ ストレージ                                  │
│ 2025-09-21 09:00     │ コンピューティング                          │
└──────────────────────┴─────────────────────────────────────────────┘
```

#### ジャンル分散効果の分析

```bash
# 詳細分析の実行
./scripts/manage-agentcore-memory.sh analyze
```

**出力例:**

```
📊 AgentCore Memory 詳細分析
=============================
📋 基本情報:
   Memory ID: CloudCoPassAgentMemory_1758470667-YvBRIT3DdL
   Session ID: AWS-SAP
   総イベント数: 5

🎯 ジャンル分散効果分析:
   📋 総学習分野数: 3
   📊 多様性比率: 0.60 (1.0が最高)
   📋 最近5回の学習分野多様性: 3/5 分野
   📊 使用頻度の偏り比率: 2.00 (最大/最小)
   ✅ 分散効果: 良好（偏りが少ない）

💡 推奨アクション:
   📈 より多くの学習データ蓄積により、分散効果が向上します
```

#### Memory のメンテナンス

##### 最新イベント以外の削除

```bash
# 最新のイベントのみを残して古いイベントを削除
./scripts/manage-agentcore-memory.sh cleanup
```

**用途:**

- Memory 容量の節約
- 最新の学習傾向のみを保持
- テスト後のクリーンアップ

##### 全イベントの削除

```bash
# 全てのMemoryイベントを削除（初期化）
./scripts/manage-agentcore-memory.sh clear
```

**用途:**

- 完全な初期化
- 新しい学習パターンでの開始
- 問題のあるデータのリセット

**⚠️ 注意事項:**

- 削除操作は取り消せません
- 削除前に確認プロンプトが表示されます
- 削除後はジャンル分散機能が初期状態に戻ります

### Memory 監視のベストプラクティス

#### 日次確認

```bash
# 毎日の問題生成後にMemory状況を確認
./scripts/manage-agentcore-memory.sh show
```

**確認ポイント:**

- 新しい学習分野が記録されているか
- 特定分野への偏りが発生していないか
- 総イベント数が適切な範囲内か

#### 週次分析

```bash
# 週次でジャンル分散効果を詳細分析
./scripts/manage-agentcore-memory.sh analyze
```

**確認ポイント:**

- 多様性比率が 0.7 以上を維持しているか
- 偏り比率が 3.0 以下を維持しているか
- 推奨アクションに従った改善が必要か

#### 月次メンテナンス

```bash
# 月次で古いイベントをクリーンアップ
./scripts/manage-agentcore-memory.sh cleanup
```

**メンテナンス理由:**

- Memory 容量の最適化
- 最新の学習傾向への集中
- システムパフォーマンスの維持

### トラブルシューティング

#### Memory 機能が動作しない場合

1. **Memory 設定の確認**

   ```bash
   # .envファイルでMemory IDが設定されているか確認
   grep AGENTCORE_MEMORY_ID .env
   ```

2. **AWS 権限の確認**

   ```bash
   # AgentCore Memory APIへのアクセス権限確認
   aws bedrock-agentcore list-events --memory-id CloudCoPassAgentMemory_1758470667-YvBRIT3DdL --session-id AWS-SAP --actor-id cloud-copass-agent --region us-east-1 --no-include-payloads --profile $AWS_PROFILE
   ```

3. **AgentCore ログの確認**
   ```bash
   # Memory関連のエラーログを確認
   ./scripts/show-agentcore-logs.sh
   # オプション 6（エラーログのみ）を選択し、"memory"で検索
   ```

#### Memory 容量の問題

- **症状**: Memory 書き込みエラー
- **対処**: 古いイベントの削除
  ```bash
  ./scripts/manage-agentcore-memory.sh cleanup
  ```

#### 分散効果が低い場合

- **症状**: 偏り比率が 3.0 を超える
- **対処**:
  1. 問題生成頻度の調整
  2. 試験ガイドの内容確認
  3. プロンプト調整の検討

## 🔧 日常的なメンテナンス

### 定期的な確認項目

#### 平日の確認

```bash
# 1. AgentCore の稼働状況確認
./scripts/get-agentcore-arn.sh

# 2. 前日の実行ログ確認
aws logs tail /aws/lambda/aws-exam-agent-trigger-development --since 24h --profile $AWS_PROFILE

# 3. エラーの有無確認
aws logs tail /aws/bedrock-agentcore/runtimes/agent_main-XXXXX-DEFAULT --since 24h --profile $AWS_PROFILE | grep -i error || echo "エラーなし"

# 4. Memory状況確認（ジャンル分散機能）
./scripts/manage-agentcore-memory.sh show
```

#### 週次の確認

```bash
# 1. システム全体の稼働状況確認
./scripts/test-agentcore.sh
./scripts/test-lambda.sh

# 2. ジャンル分散効果の詳細分析
./scripts/manage-agentcore-memory.sh analyze

# 3. リソース使用状況確認
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

# 2. Memory メンテナンス（古いイベントのクリーンアップ）
./scripts/manage-agentcore-memory.sh cleanup

# 3. コスト確認
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
# スケジュール式の変更（例：平日9時から平日18時に変更）
aws scheduler update-schedule \
  --name aws-exam-agent-daily-development \
  --schedule-expression "cron(0 18 ? * MON-FRI *)" \
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
    "Input": "{\"FunctionName\": \"aws-exam-agent-trigger-development\", \"InvocationType\": \"Event\", \"Payload\": \"{\\\"agentRuntimeArn\\\":\\\"YOUR_ARN\\\",\\\"exam_type\\\":\\\"AWS-SAP\\\",\\\"question_count\\\":2}\"}"
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

- ECR リポジトリ（全イメージ含む）
- CloudFormation スタック
- Lambda 関数
- CodeBuild プロジェクト
- S3 バケット
- IAM ロール

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

### S3 バケットのクリーンアップ

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

## 📚 関連ドキュメント

- [デプロイガイド](./deployment-guide.md): 新規環境へのデプロイ
- [トラブルシューティングガイド](./troubleshooting-guide.md): 問題解決手法
- [テストガイド](./testing-guide.md): テスト実行と Memory 機能の検証
- スクリプトリファレンス:
  - `scripts/agentcore_memory/manage.py`: AgentCore Memory 統合管理（推奨）
  - `./scripts/manage-agentcore-memory.sh`: AgentCore Memory 管理（bash 版）
  - `./scripts/test-agentcore.sh`: AgentCore 動作テスト
  - `./scripts/show-agentcore-logs.sh`: ログ確認
