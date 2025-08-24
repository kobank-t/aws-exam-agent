#!/bin/bash

# EventBridge Scheduler デプロイスクリプト（手動ARN入力対応版）
# Lambda関数ビルド + CloudFormationデプロイの統合版

set -e

# プロファイル指定の確認
if [ -z "$AWS_PROFILE" ]; then
    echo "⚠️  AWS_PROFILE 環境変数が設定されていません"
    echo "💡 使用例: export AWS_PROFILE=sandbox && ./scripts/deploy-eventbridge-scheduler.sh"
    echo "💡 または: AWS_PROFILE=sandbox ./scripts/deploy-eventbridge-scheduler.sh"
    exit 1
fi

# アカウント情報取得
ACCOUNT_INFO=$(aws sts get-caller-identity --profile "$AWS_PROFILE")
ACCOUNT_ID=$(echo "$ACCOUNT_INFO" | jq -r '.Account')
REGION=$(aws configure get region --profile "$AWS_PROFILE" || echo "us-east-1")

# 設定
STACK_NAME="aws-exam-agent-scheduler-development"
TEMPLATE_FILE="infrastructure/eventbridge-scheduler.yaml"
ENVIRONMENT="development"
BUCKET_NAME="aws-exam-agent-deployments-${ENVIRONMENT}-${ACCOUNT_ID}"
LAMBDA_PACKAGE="app/lambda/trigger/trigger-function.zip"
LAMBDA_S3_KEY="lambda-packages/trigger-function-$(date +%Y%m%d-%H%M%S).zip"

echo "🚀 EventBridge Scheduler デプロイ開始"
echo "========================================"
echo "📋 使用プロファイル: $AWS_PROFILE"
echo "📋 デプロイ先アカウント: $ACCOUNT_ID"
echo "📋 デプロイ先リージョン: $REGION"
echo "📋 Stack Name: $STACK_NAME"
echo "📋 Template: $TEMPLATE_FILE"
echo "📋 Deployment Bucket: $BUCKET_NAME"

# AgentCore Runtime ARN の手動入力
echo ""
echo "🔍 AgentCore Runtime ARN の確認"
echo "================================"
echo "💡 AgentCore ARNを確認するには:"
echo "   ./scripts/get-agentcore-arn.sh"
echo ""
echo "💡 ARNの形式例:"
echo "   arn:aws:bedrock-agentcore:us-east-1:ACCOUNT_ID:runtime/agent_main-XXXXX"
echo ""

# ARN入力プロンプト
read -p "AgentCore Runtime ARN を入力してください: " AGENTCORE_ARN

# 入力チェック
if [ -z "$AGENTCORE_ARN" ]; then
    echo "❌ ARNが入力されていません"
    exit 1
fi

# ARN の妥当性チェック
if [[ ! "$AGENTCORE_ARN" =~ ^arn:aws:bedrock-agentcore:.*:.*:runtime/.* ]]; then
    echo "❌ 入力されたARNが無効です: $AGENTCORE_ARN"
    echo "💡 正しい形式: arn:aws:bedrock-agentcore:REGION:ACCOUNT:runtime/AGENT_ID"
    exit 1
fi

echo "📋 使用するAgentCore ARN: $AGENTCORE_ARN"

# 確認プロンプト
echo ""
read -p "このアカウントにEventBridge Schedulerをデプロイしますか？ (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ デプロイをキャンセルしました"
    exit 1
fi

# 1. Lambda関数のビルド
echo ""
echo "🔨 Lambda関数ビルド中..."
./scripts/build-lambda.sh

# 2. S3バケット作成（存在しない場合）
echo ""
echo "🪣 S3バケット確認・作成中..."
if ! aws s3 ls "s3://$BUCKET_NAME" --profile "$AWS_PROFILE" > /dev/null 2>&1; then
    aws s3 mb "s3://$BUCKET_NAME" --profile "$AWS_PROFILE" --region "$REGION"
    echo "✅ S3バケット作成: $BUCKET_NAME"
else
    echo "✅ S3バケット存在確認: $BUCKET_NAME"
fi

# 3. Lambda関数パッケージをS3にアップロード
echo ""
echo "⬆️ Lambda関数パッケージをS3にアップロード中..."
aws s3 cp "$LAMBDA_PACKAGE" "s3://$BUCKET_NAME/$LAMBDA_S3_KEY" --profile "$AWS_PROFILE"
echo "✅ アップロード完了: s3://$BUCKET_NAME/$LAMBDA_S3_KEY"

# 4. CloudFormation テンプレートの検証
echo ""
echo "📋 テンプレート検証中..."
aws cloudformation validate-template --template-body file://$TEMPLATE_FILE --profile "$AWS_PROFILE"

# 5. 動的パラメータファイルを作成
echo "📝 パラメータファイル作成中..."

TEMP_PARAM_FILE="/tmp/parameters-${ENVIRONMENT}-$(date +%s).json"
cat > "$TEMP_PARAM_FILE" << EOF
[
  {
    "ParameterKey": "Environment",
    "ParameterValue": "$ENVIRONMENT"
  },
  {
    "ParameterKey": "AgentCoreRuntimeArn",
    "ParameterValue": "$AGENTCORE_ARN"
  },
  {
    "ParameterKey": "ScheduleExpression",
    "ParameterValue": "cron(0 9 ? * MON-FRI *)"
  },
  {
    "ParameterKey": "ScheduleTimezone",
    "ParameterValue": "Asia/Tokyo"
  },
  {
    "ParameterKey": "ExamType",
    "ParameterValue": "SAP"
  },
  {
    "ParameterKey": "QuestionCount",
    "ParameterValue": "1"
  },
  {
    "ParameterKey": "ScheduleState",
    "ParameterValue": "ENABLED"
  },
  {
    "ParameterKey": "LambdaCodeBucket",
    "ParameterValue": "$BUCKET_NAME"
  },
  {
    "ParameterKey": "LambdaCodeKey",
    "ParameterValue": "$LAMBDA_S3_KEY"
  }
]
EOF

echo "📋 使用するパラメータ:"
cat "$TEMP_PARAM_FILE" | jq '.'

# 6. デプロイ実行
echo ""
echo "🔧 CloudFormation デプロイ実行中..."
aws cloudformation deploy \
    --template-file $TEMPLATE_FILE \
    --stack-name $STACK_NAME \
    --parameter-overrides file://$TEMP_PARAM_FILE \
    --capabilities CAPABILITY_NAMED_IAM \
    --profile "$AWS_PROFILE" \
    --region "$REGION"

# 7. 一時ファイルとビルド成果物のクリーンアップ
echo ""
echo "🧹 クリーンアップ中..."
rm -f "$TEMP_PARAM_FILE"

# Lambda ZIPファイルの削除（デプロイ後は不要）
if [ -f "$LAMBDA_PACKAGE" ]; then
    echo "🗑️  Lambda ZIPファイルを削除: $LAMBDA_PACKAGE"
    rm -f "$LAMBDA_PACKAGE"
fi

# 8. デプロイ結果確認
echo ""
echo "✅ デプロイ完了"
echo "=============="
echo "📊 スタック情報:"
aws cloudformation describe-stacks --stack-name $STACK_NAME --query 'Stacks[0].Outputs' --output table --profile "$AWS_PROFILE"

echo ""
echo "🎯 次のステップ:"
echo "1. Lambda関数テスト:"
echo "   AWS_PROFILE=$AWS_PROFILE AGENTCORE_ARN=\"$AGENTCORE_ARN\" ./scripts/test-lambda.sh"
echo ""
echo "2. EventBridge Schedulerの確認:"
echo "   aws scheduler get-schedule --name aws-exam-agent-daily-development --profile $AWS_PROFILE"
echo ""
echo "3. ログ確認:"
echo "   aws logs tail /aws/lambda/aws-exam-agent-trigger-development --follow --profile $AWS_PROFILE"
