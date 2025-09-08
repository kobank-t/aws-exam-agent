#!/bin/bash

# Cloud CoPassAgent - AgentCore 動作確認スクリプト（ログパス表示対応版）
# このスクリプトは AgentCore の動作確認を行い、ログパスを表示します

set -e

# プロファイル指定の確認
if [ -z "$AWS_PROFILE" ]; then
    echo "⚠️  AWS_PROFILE 環境変数が設定されていません"
    echo "💡 使用例: export AWS_PROFILE=sandbox && ./scripts/test-agentcore.sh"
    echo "💡 または: AWS_PROFILE=sandbox ./scripts/test-agentcore.sh"
    exit 1
fi

echo "🚀 Cloud CoPassAgent - AgentCore 動作確認開始"
echo "============================================"
echo "📋 使用プロファイル: $AWS_PROFILE"

# アカウント確認
echo ""
echo "🔍 アカウント確認..."
aws sts get-caller-identity --profile "$AWS_PROFILE"

# AgentCore ディレクトリに移動
cd app/agentcore

# AgentCore のステータス確認
echo ""
echo "📋 AgentCore ステータス確認..."
AGENT_STATUS=$(agentcore status)
echo "$AGENT_STATUS"

# Agent IDを抽出
AGENT_ID=$(echo "$AGENT_STATUS" | grep "Agent ID:" | sed 's/.*Agent ID: \([^ ]*\).*/\1/' | tr -d '│ ')

if [ -n "$AGENT_ID" ]; then
    LOG_GROUP="/aws/bedrock-agentcore/runtimes/${AGENT_ID}-DEFAULT"
    RUNTIME_LOG_GROUP="/aws/bedrock-agentcore/runtimes/${AGENT_ID}-DEFAULT/runtime-logs"
    
    echo ""
    echo "📋 ログ情報:"
    echo "   Agent ID: $AGENT_ID"
    echo "   メインログ: $LOG_GROUP"
    echo "   ランタイムログ: $RUNTIME_LOG_GROUP"
fi

# 動作確認テスト
echo ""
echo "🧪 動作確認テスト実行..."

# テスト: コンピューティングカテゴリ
echo ""
echo "テスト: AWS-SAP 問題生成"
echo "----------------------------------------------"
TEST_RESULT=$(agentcore invoke '{"exam_type": "AWS-SAP", "question_count": 1}' 2>&1)
echo "$TEST_RESULT"

# エラーチェック
if echo "$TEST_RESULT" | grep -q "error\|Error\|ERROR"; then
    echo ""
    echo "⚠️  エラーが検出されました。詳細なログを確認してください:"
    if [ -n "$AGENT_ID" ]; then
        echo "   ログ確認スクリプト: ./scripts/show-agentcore-logs.sh"
        echo "   直接確認: aws logs tail '$LOG_GROUP' --since 10m --profile $AWS_PROFILE"
    fi
fi

# ルートディレクトリに戻る
cd ../..

echo ""
echo "✅ 動作確認完了！"
echo "================"
echo ""
echo "💡 確認ポイント:"
echo "- 日本語の問題が正常に生成されることを確認してください"
echo "- 文字化けがないか確認してください"
echo "- AWS公式ドキュメントのソースURLが含まれているか確認してください"
echo "- 問題・選択肢・解説が適切な品質であることを確認してください"

if [ -n "$AGENT_ID" ]; then
    echo ""
    echo "🔍 トラブルシューティング:"
    echo "   ログ確認: AWS_PROFILE=$AWS_PROFILE ./scripts/show-agentcore-logs.sh"
    echo "   リアルタイム: aws logs tail '$LOG_GROUP' --follow --profile $AWS_PROFILE"
    echo "   エラーのみ: aws logs tail '$LOG_GROUP' --since 1h --profile $AWS_PROFILE | grep -i error"
fi
