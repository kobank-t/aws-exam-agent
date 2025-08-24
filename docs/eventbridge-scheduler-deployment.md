# EventBridge Scheduler デプロイ・テスト手順書

## 📋 概要

AWS Exam Agent プロジェクトにおけるEventBridge Schedulerの定期実行システムのデプロイとテスト手順をまとめています。

## 🏗️ アーキテクチャ

```
EventBridge Scheduler → Lambda Function → AgentCore Runtime
     (定期実行)         (トリガー関数)      (問題生成AI)
```

### 構成要素

- **EventBridge Schedule**: `aws-exam-agent-daily-development`
- **Lambda Function**: `aws-exam-agent-trigger-development`
- **S3 Bucket**: `aws-exam-agent-deployments-development-{AccountId}`
- **IAM Roles**: 
  - `EventBridgeSchedulerExecutionRole-development`
  - `LambdaTriggerFunctionRole-development`

## 🚀 デプロイ手順

### 前提条件

- AWS CLI設定済み
- AgentCore Runtime デプロイ済み
- 適切なIAM権限
- Python 3.12+ (Lambda関数ビルド用)

### 1. AgentCore Runtime ARNの確認

```bash
# .bedrock_agentcore.yamlからARNを確認
grep "agent_arn:" app/agentcore/.bedrock_agentcore.yaml
```

### 2. Lambda関数のコード品質チェック

```bash
# コード品質チェック実行
./scripts/python-quality-check.sh

# 個別チェック
uv run ruff check app/lambda/trigger/lambda_function.py
uv run mypy app/lambda/trigger/lambda_function.py
```

### 3. 統合デプロイ実行

```bash
# 統合デプロイスクリプトの実行
./scripts/deploy-eventbridge-scheduler.sh
```

#### デプロイスクリプトの処理内容

1. **Lambda関数ビルド**: 最新のboto3を含むパッケージ作成
2. **S3アップロード**: Lambda関数パッケージをS3にアップロード
3. **CloudFormationデプロイ**: インフラストラクチャの作成・更新
4. **結果確認**: デプロイ結果の表示

### 4. デプロイ結果の確認

```bash
# スタック情報の確認
aws cloudformation describe-stacks \
    --stack-name aws-exam-agent-scheduler-development \
    --query 'Stacks[0].Outputs' \
    --output table
```

## ⚙️ 設定パラメータ

### デフォルト設定

| パラメータ | 値 | 説明 |
|-----------|-----|------|
| `ScheduleExpression` | `cron(0 9 * * ? *)` | 毎日9時JST実行 |
| `ScheduleTimezone` | `Asia/Tokyo` | 日本時間 |
| `ExamType` | `SAP` | AWS Certified Solutions Architect - Professional |
| `QuestionCount` | `1` | 生成する問題数 |
| `ScheduleState` | `ENABLED` | スケジュール有効 |

### Lambda関数の特徴

- **Runtime**: Python 3.12
- **Handler**: `lambda_function.lambda_handler`
- **Timeout**: 300秒
- **Memory**: 256MB
- **Dependencies**: boto3 1.40.11+ (bedrock-agentcore対応)

## 🧪 テスト手順

### 1. 本番スケジュールの確認

```bash
# スケジュール詳細の確認
aws scheduler get-schedule \
    --name aws-exam-agent-daily-development \
    --region us-east-1
```

### 2. テストスケジュールによる即座の動作確認

EventBridge Schedulerには手動実行機能がないため、短期間で実行されるテストスケジュールを作成します。

#### 2.1 テストスケジュール作成

```bash
# 5分後の時刻を計算
EXEC_TIME=$(TZ=Asia/Tokyo date -v+5M '+%M %H %d %m')
echo "実行時刻: $EXEC_TIME"

# テストスケジュール設定ファイル作成
cat > /tmp/test-schedule.json << EOF
{
  "Name": "aws-exam-agent-test-5min",
  "Description": "Test schedule for AWS Exam Agent (runs once in 5 minutes)",
  "ScheduleExpression": "cron($EXEC_TIME ? 2025)",
  "ScheduleExpressionTimezone": "Asia/Tokyo",
  "State": "ENABLED",
  "FlexibleTimeWindow": {
    "Mode": "OFF"
  },
  "Target": {
    "Arn": "arn:aws:scheduler:::aws-sdk:lambda:invoke",
    "RoleArn": "arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/EventBridgeSchedulerExecutionRole-development",
    "Input": "{\n  \"FunctionName\": \"aws-exam-agent-trigger-development\",\n  \"InvocationType\": \"Event\",\n  \"Payload\": \"{\\\"agentRuntimeArn\\\":\\\"$(grep 'agent_arn:' app/agentcore/.bedrock_agentcore.yaml | awk '{print $2}')\\\",\\\"exam_type\\\":\\\"SAP\\\",\\\"question_count\\\":1}\"\n}",
    "RetryPolicy": {
      "MaximumRetryAttempts": 3,
      "MaximumEventAgeInSeconds": 3600
    }
  },
  "ActionAfterCompletion": "DELETE"
}
EOF

# テストスケジュール作成
aws scheduler create-schedule \
    --cli-input-json file:///tmp/test-schedule.json \
    --region us-east-1
```

#### 2.2 テスト実行の監視

```bash
# スケジュール状態確認
aws scheduler get-schedule \
    --name aws-exam-agent-test-5min \
    --region us-east-1

# 実行後（スケジュールが自動削除されることを確認）
aws scheduler get-schedule \
    --name aws-exam-agent-test-5min \
    --region us-east-1 2>&1 | grep -q "does not exist" && echo "✅ テストスケジュール実行完了（自動削除済み）"
```

### 3. 実行結果の確認

#### 3.1 CloudWatch Logsの確認

```bash
# 最新のログストリーム確認
aws logs describe-log-streams \
    --log-group-name "/aws/lambda/aws-exam-agent-trigger-development" \
    --order-by LastEventTime \
    --descending \
    --max-items 1 \
    --region us-east-1

# ログの内容確認（STREAM_NAMEは上記コマンドの結果から取得）
aws logs get-log-events \
    --log-group-name "/aws/lambda/aws-exam-agent-trigger-development" \
    --log-stream-name "STREAM_NAME" \
    --region us-east-1
```

#### 3.2 期待されるログ内容

正常実行時のログ例：
```
[INFO] Received event: {"agentRuntimeArn":"arn:aws:bedrock-agentcore:...","exam_type":"SAP","question_count":1}
[INFO] boto3 version: 1.40.11
[INFO] Invoking AgentCore Runtime: arn:aws:bedrock-agentcore:...
[INFO] Payload: {"exam_type":"SAP","question_count":1}
[INFO] AgentCore invocation successful
[INFO] Response content type: application/json
```

### 4. Lambda関数の直接テスト

#### 4.1 AWS CLI経由でのLambda関数テスト

AWS CLIでLambda関数を直接呼び出してテストできます。

##### Base64エンコーディング方式（推奨）

```bash
# 1. テストペイロードをBase64エンコード
PAYLOAD=$(echo '{"agentRuntimeArn":"arn:aws:bedrock-agentcore:us-east-1:792223357133:runtime/agent_main-4h7OvMAtVL","exam_type":"SAP","question_count":1}' | base64)

# 2. Lambda関数を実行
aws lambda invoke \
    --function-name aws-exam-agent-trigger-development \
    --region us-east-1 \
    --payload $PAYLOAD \
    /tmp/lambda-test-response.json

# 3. 実行結果の確認
echo "=== Lambda実行結果 ==="
cat /tmp/lambda-test-response.json
```

##### 期待される実行結果

**成功時のレスポンス**:
```json
{
  "StatusCode": 200,
  "ExecutedVersion": "$LATEST"
}
```

**Lambda関数のレスポンス内容**:
```json
{
  "statusCode": 200,
  "body": "{\"message\": \"Question generation triggered successfully\", \"agentRuntimeArn\": \"arn:aws:bedrock-agentcore:...\", \"payload\": {\"exam_type\": \"SAP\", \"question_count\": 1}, \"responseContentType\": \"application/json\"}"
}
```

##### 実行ログの確認

```bash
# 最新のログストリーム取得
LOG_STREAM=$(aws logs describe-log-streams \
    --log-group-name "/aws/lambda/aws-exam-agent-trigger-development" \
    --order-by LastEventTime \
    --descending \
    --max-items 1 \
    --region us-east-1 \
    --query 'logStreams[0].logStreamName' \
    --output text)

# ログ内容確認
aws logs get-log-events \
    --log-group-name "/aws/lambda/aws-exam-agent-trigger-development" \
    --log-stream-name "$LOG_STREAM" \
    --region us-east-1
```

##### 期待されるログ内容

正常実行時のログ例：
```
[INFO] Received event: {"agentRuntimeArn":"arn:aws:bedrock-agentcore:...","exam_type":"SAP","question_count":1}
[INFO] boto3 version: 1.40.11
[INFO] Found credentials in environment variables.
[INFO] Invoking AgentCore Runtime: arn:aws:bedrock-agentcore:...
[INFO] Payload: {"exam_type":"SAP","question_count":1}
[INFO] AgentCore invocation successful
[INFO] Response content type: application/json
REPORT RequestId: ... Duration: 35825.03 ms Billed Duration: 35826 ms Memory Size: 256 MB Max Memory Used: 80 MB
```

#### 4.2 AWS Console経由でのテスト（代替手段）

CLI実行に問題がある場合の代替手段：

```bash
# AWS Lambda Console URL
echo "AWS Lambda Console: https://console.aws.amazon.com/lambda/home?region=us-east-1#/functions/aws-exam-agent-trigger-development"
```

**テストペイロード（Console用）**:
```json
{
  "agentRuntimeArn": "arn:aws:bedrock-agentcore:us-east-1:792223357133:runtime/agent_main-4h7OvMAtVL",
  "exam_type": "SAP",
  "question_count": 1
}
```

#### 4.3 CLI実行時のトラブルシューティング

##### 問題: 文字エンコーディングエラー

**エラー例**:
```
An error occurred (InvalidRequestContentException) when calling the Invoke operation: Could not parse request body into json: Could not parse payload into json: Invalid UTF-8 start byte 0xa7
```

**原因**: AWS CLIのペイロード処理における文字エンコーディング問題

**解決方法**: Base64エンコーディングを使用（上記の推奨方式）

##### 問題: IAM権限エラー

**エラー例**:
```
[ERROR] Unexpected error: An error occurred (AccessDeniedException) when calling the InvokeAgentRuntime operation: User: ... is not authorized to perform: bedrock-agentcore:InvokeAgentRuntime
```

**解決方法**: CloudFormationテンプレートの再デプロイ
```bash
./scripts/deploy-eventbridge-scheduler.sh
```

##### 問題: AgentCore Runtime ARNが見つからない

**エラー例**:
```
[ERROR] Validation error: Missing required parameter: agentRuntimeArn
```

**解決方法**: 正しいARNを確認
```bash
grep "agent_arn:" app/agentcore/.bedrock_agentcore.yaml
```

## 🔧 トラブルシューティング

### よくある問題と解決方法

#### 1. Lambda関数のboto3バージョン問題

**症状**: `Unknown service: 'bedrock-agentcore'`

**解決方法**: 
```bash
# 最新のLambda関数を再デプロイ
./scripts/deploy-eventbridge-scheduler.sh
```

#### 2. AgentCore Runtime ARN が見つからない

**エラー**: `AgentCore Runtime ARN が見つかりません`

**解決方法**:
```bash
# AgentCore設定ファイルの確認
ls -la app/agentcore/.bedrock_agentcore.yaml

# 手動でARNを確認
agentcore list
```

#### 3. IAM権限エラー

**エラー**: `User: ... is not authorized to perform: scheduler:CreateSchedule`

**解決方法**:
```bash
# 必要なIAM権限を確認
aws iam get-user-policy --user-name YOUR_USER --policy-name SchedulerPolicy

# 管理者権限で実行するか、適切なポリシーをアタッチ
```

#### 4. Lambda関数実行エラー

**確認方法**:
```bash
# Lambda関数のエラーログ確認
aws logs filter-log-events \
    --log-group-name "/aws/lambda/aws-exam-agent-trigger-development" \
    --filter-pattern "ERROR" \
    --region us-east-1
```

#### 5. コード品質問題

**確認・修正方法**:
```bash
# コード品質チェック
./scripts/python-quality-check.sh

# 自動修正
uv run ruff check app/lambda/trigger/lambda_function.py --fix
```

## 📊 監視・運用

### 定期的な確認項目

1. **スケジュール状態の確認**
   ```bash
   aws scheduler get-schedule --name aws-exam-agent-daily-development --region us-east-1
   ```

2. **Lambda関数の実行状況**
   ```bash
   aws lambda get-function --function-name aws-exam-agent-trigger-development --region us-east-1
   ```

3. **CloudWatch メトリクスの確認**
   - Lambda実行回数
   - エラー率
   - 実行時間

### アラート設定

CloudWatch Alarmを設定して、以下の状況を監視：

- Lambda関数の実行失敗
- AgentCore Runtime の呼び出しエラー
- スケジュール実行の失敗

## 🗑️ クリーンアップ

### テストリソースの削除

```bash
# テストスケジュールの削除（通常は自動削除）
aws scheduler delete-schedule \
    --name aws-exam-agent-test-5min \
    --region us-east-1

# スタック全体の削除
aws cloudformation delete-stack \
    --stack-name aws-exam-agent-scheduler-development \
    --region us-east-1
```

## 📚 参考資料

- [EventBridge Scheduler User Guide](https://docs.aws.amazon.com/scheduler/latest/UserGuide/)
- [EventBridge Scheduler CLI Reference](https://docs.aws.amazon.com/cli/latest/reference/scheduler/)
- [Lambda with EventBridge Scheduler](https://docs.aws.amazon.com/lambda/latest/dg/with-eventbridge-scheduler.html)
- [Cron Expressions for EventBridge](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-create-rule-schedule.html#eb-cron-expressions)

## 🔄 更新履歴

- **2025-08-17**: 初版作成
- **2025-08-17**: Lambda関数の外部ファイル化、buildspec.yml対応
- **2025-08-17**: テストスケジュール手順追加、コード品質チェック追加

---

**最終更新**: 2025-08-17  
**作成者**: AWS Exam Agent Development Team
