#!/bin/bash

# Cloud CoPassAgent - AgentCore デプロイスクリプト（プロファイル対応版）

set -e

# プロファイル指定の確認
if [ -z "$AWS_PROFILE" ]; then
    echo "⚠️  AWS_PROFILE 環境変数が設定されていません"
    echo "💡 使用例: export AWS_PROFILE=sandbox && ./scripts/deploy-agentcore.sh"
    echo "💡 または: AWS_PROFILE=sandbox ./scripts/deploy-agentcore.sh"
    exit 1
fi

echo "🚀 Cloud CoPassAgent - AgentCore デプロイ開始"
echo "=========================================="
echo "📋 使用プロファイル: $AWS_PROFILE"

# アカウント確認
echo ""
echo "🔍 デプロイ先アカウント確認..."
ACCOUNT_INFO=$(aws sts get-caller-identity --profile "$AWS_PROFILE")
echo "$ACCOUNT_INFO"

ACCOUNT_ID=$(echo "$ACCOUNT_INFO" | jq -r '.Account')
echo "📋 デプロイ先アカウント ID: $ACCOUNT_ID"

# 確認プロンプト
echo ""
read -p "このアカウントにデプロイしますか？ (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ デプロイをキャンセルしました"
    exit 1
fi

# .envファイルから環境変数を読み込み
echo ""
echo "🔧 環境変数設定..."

# プロジェクトルートの.envファイルパスを設定
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$PROJECT_ROOT/.env"

echo "📋 プロジェクトルート: $PROJECT_ROOT"
echo "📋 .envファイルパス: $ENV_FILE"

if [ ! -f "$ENV_FILE" ]; then
    echo "❌ .env ファイルが見つかりません: $ENV_FILE"
    echo "💡 プロジェクトルートに .env ファイルを作成してください"
    exit 1
fi

# .envファイルから POWER_AUTOMATE_WEBHOOK_URL を抽出
WEBHOOK_URL=$(grep "^POWER_AUTOMATE_WEBHOOK_URL=" "$ENV_FILE" | cut -d'=' -f2-)
if [ -z "$WEBHOOK_URL" ]; then
    echo "❌ POWER_AUTOMATE_WEBHOOK_URL が .env ファイルに設定されていません"
    echo "💡 .env ファイルに以下の形式で設定してください:"
    echo "   POWER_AUTOMATE_WEBHOOK_URL=https://your-webhook-url"
    exit 1
fi

# .envファイルから POWER_AUTOMATE_SECURITY_TOKEN を抽出
SECURITY_TOKEN=$(grep "^POWER_AUTOMATE_SECURITY_TOKEN=" "$ENV_FILE" | cut -d'=' -f2-)
if [ -z "$SECURITY_TOKEN" ]; then
    echo "❌ POWER_AUTOMATE_SECURITY_TOKEN が .env ファイルに設定されていません"
    echo "💡 .env ファイルに以下の形式で設定してください:"
    echo "   POWER_AUTOMATE_SECURITY_TOKEN=your-security-token"
    exit 1
fi

echo "✅ POWER_AUTOMATE_WEBHOOK_URL を .env から読み込みました"
echo "✅ POWER_AUTOMATE_SECURITY_TOKEN を .env から読み込みました"
ENV_ARGS="--env POWER_AUTOMATE_WEBHOOK_URL=$WEBHOOK_URL --env POWER_AUTOMATE_SECURITY_TOKEN=$SECURITY_TOKEN"

# AgentCore ディレクトリに移動
cd app/agentcore

# デプロイ実行
echo ""
echo "🚀 AgentCore デプロイ実行..."
echo "📋 環境変数付きでデプロイします"
agentcore launch --auto-update-on-conflict $ENV_ARGS

# デプロイ結果確認
echo ""
echo "📋 デプロイ結果確認..."
AGENT_STATUS=$(agentcore status)
echo "$AGENT_STATUS"

# Agent IDを抽出してログパス表示
AGENT_ID=$(echo "$AGENT_STATUS" | grep "Agent ID:" | sed 's/.*Agent ID: \([^ ]*\).*/\1/' | tr -d '│ ')

if [ -n "$AGENT_ID" ]; then
    LOG_GROUP="/aws/bedrock-agentcore/runtimes/${AGENT_ID}-DEFAULT"
    
    echo ""
    echo "📋 ログ情報:"
    echo "   Agent ID: $AGENT_ID"
    echo "   ログパス: $LOG_GROUP"
fi

echo ""
echo "✅ デプロイ完了！"
echo "==============="
echo ""
echo "💡 次のステップ:"
echo "- 動作確認: AWS_PROFILE=$AWS_PROFILE ./scripts/test-agentcore.sh"
if [ -n "$AGENT_ID" ]; then
    echo "- ログ確認: AWS_PROFILE=$AWS_PROFILE ./scripts/show-agentcore-logs.sh"
    echo "- 直接ログ: aws logs tail '$LOG_GROUP' --follow --profile $AWS_PROFILE"
fi
