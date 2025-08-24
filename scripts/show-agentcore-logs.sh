#!/bin/bash

# AgentCore ログ確認スクリプト

set -e

# プロファイル指定の確認
if [ -z "$AWS_PROFILE" ]; then
    echo "⚠️  AWS_PROFILE 環境変数が設定されていません"
    echo "💡 使用例: export AWS_PROFILE=sandbox && ./scripts/show-agentcore-logs.sh"
    exit 1
fi

echo "🔍 AgentCore ログ確認"
echo "===================="
echo "📋 使用プロファイル: $AWS_PROFILE"

# AgentCore IDを取得
cd app/agentcore
echo ""
echo "📋 AgentCore ステータス確認..."
AGENT_STATUS=$(agentcore status 2>/dev/null || echo "")

if [ -z "$AGENT_STATUS" ]; then
    echo "❌ AgentCore が見つかりません"
    echo "💡 先にデプロイを実行してください: ./scripts/deploy-agentcore.sh"
    exit 1
fi

# Agent IDを抽出（statusコマンドの出力から）
AGENT_ID=$(echo "$AGENT_STATUS" | grep "Agent ID:" | sed 's/.*Agent ID: \([^ ]*\).*/\1/' | tr -d '│ ')

if [ -z "$AGENT_ID" ]; then
    echo "❌ Agent ID を取得できませんでした"
    exit 1
fi

echo "📋 Agent ID: $AGENT_ID"

# ログパス構築
LOG_GROUP="/aws/bedrock-agentcore/runtimes/${AGENT_ID}-DEFAULT"
RUNTIME_LOG_GROUP="/aws/bedrock-agentcore/runtimes/${AGENT_ID}-DEFAULT/runtime-logs"

echo "📋 ログパス: $LOG_GROUP"
echo "📋 ランタイムログパス: $RUNTIME_LOG_GROUP"

# ログ確認オプション
echo ""
echo "🔍 ログ確認オプション:"
echo "1. リアルタイムログ監視"
echo "2. 過去1時間のログ"
echo "3. 過去24時間のログ"
echo "4. ランタイムログ（リアルタイム）"
echo "5. ログストリーム一覧"
echo "6. エラーログのみ表示"

read -p "選択してください (1-6): " -n 1 -r
echo

case $REPLY in
    1)
        echo "📡 リアルタイムログ監視開始..."
        echo "💡 終了するには Ctrl+C を押してください"
        aws logs tail "$LOG_GROUP" --follow --profile "$AWS_PROFILE"
        ;;
    2)
        echo "📄 過去1時間のログ表示..."
        aws logs tail "$LOG_GROUP" --since 1h --profile "$AWS_PROFILE"
        ;;
    3)
        echo "📄 過去24時間のログ表示..."
        aws logs tail "$LOG_GROUP" --since 24h --profile "$AWS_PROFILE"
        ;;
    4)
        echo "📡 ランタイムログ監視開始..."
        echo "💡 終了するには Ctrl+C を押してください"
        aws logs tail "$RUNTIME_LOG_GROUP" --follow --profile "$AWS_PROFILE" 2>/dev/null || \
        (echo "⚠️  ランタイムログが見つかりません。メインログを表示します..." && \
        aws logs tail "$LOG_GROUP" --follow --profile "$AWS_PROFILE")
        ;;
    5)
        echo "📋 ログストリーム一覧..."
        aws logs describe-log-streams --log-group-name "$LOG_GROUP" --profile "$AWS_PROFILE" --query 'logStreams[*].[logStreamName,creationTime,lastEventTime]' --output table
        ;;
    6)
        echo "🚨 エラーログのみ表示（過去1時間）..."
        aws logs tail "$LOG_GROUP" --since 1h --profile "$AWS_PROFILE" | grep -i "error\|exception\|failed\|denied" || echo "エラーログが見つかりませんでした"
        ;;
    *)
        echo "❌ 無効な選択です"
        exit 1
        ;;
esac

echo ""
echo "💡 便利なログコマンド:"
echo "   リアルタイム: aws logs tail '$LOG_GROUP' --follow --profile $AWS_PROFILE"
echo "   過去1時間: aws logs tail '$LOG_GROUP' --since 1h --profile $AWS_PROFILE"
echo "   エラーのみ: aws logs tail '$LOG_GROUP' --since 1h --profile $AWS_PROFILE | grep -i error"
