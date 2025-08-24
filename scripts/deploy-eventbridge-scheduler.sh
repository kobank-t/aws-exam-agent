#!/bin/bash

# EventBridge Scheduler デプロイスクリプト
# Lambda関数ビルド + CloudFormationデプロイの統合版

set -e

# 設定
STACK_NAME="aws-exam-agent-scheduler-development"
TEMPLATE_FILE="infrastructure/eventbridge-scheduler.yaml"
ENVIRONMENT="development"
BUCKET_NAME="aws-exam-agent-deployments-${ENVIRONMENT}-$(aws sts get-caller-identity --query Account --output text)"
LAMBDA_PACKAGE="app/lambda/trigger/trigger-function.zip"
LAMBDA_S3_KEY="lambda-packages/trigger-function-$(date +%Y%m%d-%H%M%S).zip"

# AgentCore Runtime ARN を .bedrock_agentcore.yaml から取得
AGENTCORE_ARN=$(grep "agent_arn:" app/agentcore/.bedrock_agentcore.yaml | awk '{print $2}')

if [ -z "$AGENTCORE_ARN" ]; then
    echo "❌ AgentCore Runtime ARN が見つかりません"
    echo "app/agentcore/.bedrock_agentcore.yaml を確認してください"
    exit 1
fi

echo "🚀 EventBridge Scheduler デプロイ開始"
echo "Stack Name: $STACK_NAME"
echo "Template: $TEMPLATE_FILE"
echo "AgentCore ARN: $AGENTCORE_ARN"
echo "Deployment Bucket: $BUCKET_NAME"

# 1. Lambda関数のビルド
echo "🔨 Lambda関数ビルド中..."
./scripts/build-lambda.sh

# 2. S3バケット作成（存在しない場合）
echo "🪣 S3バケット確認・作成中..."
if ! aws s3 ls "s3://$BUCKET_NAME" > /dev/null 2>&1; then
    aws s3 mb "s3://$BUCKET_NAME"
    echo "✅ S3バケット作成: $BUCKET_NAME"
else
    echo "✅ S3バケット存在確認: $BUCKET_NAME"
fi

# 3. Lambda関数パッケージをS3にアップロード
echo "⬆️ Lambda関数パッケージをS3にアップロード中..."
aws s3 cp "$LAMBDA_PACKAGE" "s3://$BUCKET_NAME/$LAMBDA_S3_KEY"
echo "✅ アップロード完了: s3://$BUCKET_NAME/$LAMBDA_S3_KEY"

# 4. CloudFormation テンプレートの検証
echo "📋 テンプレート検証中..."
aws cloudformation validate-template --template-body file://$TEMPLATE_FILE

# 5. パラメータファイルを更新
PARAM_FILE="infrastructure/parameters-development.json"
echo "📝 パラメータファイル更新中..."

# 一時的なパラメータファイルを作成（S3情報を含む）
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
    "ParameterValue": "cron(0 9 * * ? *)"
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

# 6. デプロイ実行
echo "🔧 デプロイ実行中..."
aws cloudformation deploy \
    --template-file $TEMPLATE_FILE \
    --stack-name $STACK_NAME \
    --parameter-overrides file://$TEMP_PARAM_FILE \
    --capabilities CAPABILITY_NAMED_IAM

# 7. 一時ファイルとビルド成果物のクリーンアップ
echo "🧹 クリーンアップ中..."
rm -f "$TEMP_PARAM_FILE"

# Lambda ZIPファイルの削除（デプロイ後は不要）
if [ -f "$LAMBDA_PACKAGE" ]; then
    echo "🗑️  Lambda ZIPファイルを削除: $LAMBDA_PACKAGE"
    rm -f "$LAMBDA_PACKAGE"
fi

# 8. デプロイ結果確認
echo "✅ デプロイ完了"
echo "📊 スタック情報:"
aws cloudformation describe-stacks --stack-name $STACK_NAME --query 'Stacks[0].Outputs' --output table

echo ""
echo "🎯 次のステップ:"
echo "1. Lambda関数の直接テスト:"
echo "   aws lambda invoke --function-name aws-exam-agent-trigger-development --region us-east-1 \\"
echo "   --payload '{\"agentRuntimeArn\":\"$AGENTCORE_ARN\",\"exam_type\":\"SAP\",\"question_count\":1}' \\"
echo "   /tmp/test-response.json && cat /tmp/test-response.json"
echo ""
echo "2. EventBridge Schedulerの確認:"
echo "   aws scheduler get-schedule --name aws-exam-agent-daily-development --region us-east-1"
