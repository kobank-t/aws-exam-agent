#!/bin/bash

# AgentCore ARN 確認用ヘルパースクリプト

set -e

# プロファイル指定の確認
if [ -z "$AWS_PROFILE" ]; then
    echo "⚠️  AWS_PROFILE 環境変数が設定されていません"
    echo "💡 使用例: export AWS_PROFILE=sandbox && ./scripts/get-agentcore-arn.sh"
    exit 1
fi

echo "🔍 AgentCore ARN 確認"
echo "===================="
echo "📋 使用プロファイル: $AWS_PROFILE"

# AgentCore ディレクトリに移動
cd app/agentcore

echo ""
echo "📋 AgentCore ステータス:"
echo "========================"
agentcore status

echo ""
echo "💡 上記の出力から 'Agent Arn:' の行を確認してください"
echo "💡 ARNは以下のような形式です:"
echo "   arn:aws:bedrock-agentcore:us-east-1:ACCOUNT_ID:runtime/agent_main-XXXXX"
echo ""
echo "🎯 次のステップ:"
echo "   確認したARNを使用してEventBridge Schedulerをデプロイ:"
echo "   ./scripts/deploy-eventbridge-scheduler.sh"
