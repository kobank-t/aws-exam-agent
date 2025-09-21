#!/bin/bash

# Cloud CoPassAgent - AgentCore Memory 権限設定スクリプト

set -e

# プロファイル指定の確認
if [ -z "$AWS_PROFILE" ]; then
    echo "⚠️  AWS_PROFILE 環境変数が設定されていません"
    echo "💡 使用例: export AWS_PROFILE=sandbox && ./scripts/setup-memory-permissions.sh"
    exit 1
fi

echo "🔧 Cloud CoPassAgent - AgentCore Memory 権限設定"
echo "=============================================="
echo "📋 使用プロファイル: $AWS_PROFILE"

# .envファイルから AGENTCORE_MEMORY_ID を取得
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$PROJECT_ROOT/.env"

if [ ! -f "$ENV_FILE" ]; then
    echo "❌ .env ファイルが見つかりません: $ENV_FILE"
    exit 1
fi

MEMORY_ID=$(grep "^AGENTCORE_MEMORY_ID=" "$ENV_FILE" | cut -d'=' -f2-)
if [ -z "$MEMORY_ID" ]; then
    echo "❌ AGENTCORE_MEMORY_ID が .env ファイルに設定されていません"
    exit 1
fi

echo "📋 Memory ID: $MEMORY_ID"

# 既存のロール名を取得
ROLE_NAME="AmazonBedrockAgentCoreSDKRuntime-us-east-1-fd4e75a30a"
POLICY_NAME="BedrockAgentCoreMemoryAccess"

# アカウント情報取得
ACCOUNT_ID=$(aws sts get-caller-identity --profile "$AWS_PROFILE" --query 'Account' --output text)
REGION=$(aws configure get region --profile "$AWS_PROFILE")
if [ -z "$REGION" ]; then
    REGION="us-east-1"
fi

echo "📋 アカウント ID: $ACCOUNT_ID"
echo "📋 リージョン: $REGION"
echo "📋 対象ロール: $ROLE_NAME"

# 確認プロンプト
echo ""
read -p "このロールにMemory権限を追加しますか？ (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 権限設定をキャンセルしました"
    exit 1
fi

# ポリシードキュメント作成
POLICY_DOCUMENT=$(cat <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "BedrockAgentCoreMemoryAccess",
            "Effect": "Allow",
            "Action": [
                "bedrock-agentcore:ListEvents",
                "bedrock-agentcore:CreateEvent"
            ],
            "Resource": [
                "arn:aws:bedrock-agentcore:${REGION}:${ACCOUNT_ID}:memory/${MEMORY_ID}"
            ]
        }
    ]
}
EOF
)

echo ""
echo "🔧 Memory権限ポリシーを追加中..."

# インラインポリシーとして追加
aws iam put-role-policy \
    --role-name "$ROLE_NAME" \
    --policy-name "$POLICY_NAME" \
    --policy-document "$POLICY_DOCUMENT" \
    --profile "$AWS_PROFILE"

echo "✅ Memory権限ポリシーを追加しました"

# 確認
echo ""
echo "📋 追加されたポリシーを確認中..."
aws iam get-role-policy \
    --role-name "$ROLE_NAME" \
    --policy-name "$POLICY_NAME" \
    --profile "$AWS_PROFILE" \
    --query 'PolicyDocument' \
    --output json

echo ""
echo "✅ AgentCore Memory 権限設定完了！"
echo "================================="
echo ""
echo "💡 次のステップ:"
echo "- 動作確認: AWS_PROFILE=$AWS_PROFILE ./scripts/test-agentcore.sh"
echo "- ログ確認: AWS_PROFILE=$AWS_PROFILE ./scripts/show-agentcore-logs.sh"