#!/bin/bash
# タスク2: AgentCore Runtime 事前リソースのデプロイ

set -e

# 設定値
STACK_NAME="aws-exam-agent-agentcore"
ENVIRONMENT="development"
REGION="us-east-1"  # Virginia - Bedrock AgentCore対応リージョン
TEMPLATE_FILE="infrastructure/agentcore-resources.yaml"

echo "🚀 Deploying AgentCore Runtime Resources (Task 2)..."
echo "Stack Name: $STACK_NAME"
echo "Environment: $ENVIRONMENT"
echo "Region: $REGION"

# SAMテンプレートの検証
echo "🔍 Validating SAM template..."
sam validate --template $TEMPLATE_FILE

# SAMデプロイ
echo "🚀 Deploying SAM application..."
sam deploy \
  --template-file $TEMPLATE_FILE \
  --stack-name $STACK_NAME \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
  --parameter-overrides \
    Environment=$ENVIRONMENT \
    AgentName=supervisor-agent \
  --no-confirm-changeset \
  --no-fail-on-empty-changeset \
  --region $REGION

echo "✅ AgentCore resources deployment completed!"

# 出力値の取得と表示
echo "📋 Getting stack outputs..."
EXECUTION_ROLE_ARN=$(aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --query 'Stacks[0].Outputs[?OutputKey==`AgentCoreExecutionRoleArn`].OutputValue' \
  --output text \
  --region $REGION)

ECR_REPOSITORY_URI=$(aws cloudformation describe-stacks \
  --stack-name $STACK_NAME \
  --query 'Stacks[0].Outputs[?OutputKey==`ECRRepositoryURI`].OutputValue' \
  --output text \
  --region $REGION)

echo "✅ Resources created successfully:"
echo "  Execution Role ARN: $EXECUTION_ROLE_ARN"
echo "  ECR Repository URI: $ECR_REPOSITORY_URI"

# 次のステップの案内
echo ""
echo "🔄 Next Step: Configure AgentCore with the created resources"
echo "Run the following command to complete the setup:"
echo ""
echo "  cd app/agentcore"
echo "  agentcore configure --entrypoint agent_main.py \\"
echo "    --requirements-file requirements.txt \\"
echo "    --execution-role $EXECUTION_ROLE_ARN \\"
echo "    --ecr $ECR_REPOSITORY_URI \\"
echo "    --region $REGION \\"
echo "    --verbose"
echo ""
echo "This will generate the proper configuration files (Dockerfile, .dockerignore, etc.)"