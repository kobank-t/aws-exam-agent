#!/bin/bash

# Lambda関数テストスクリプト（手動ARN対応版）

set -e

# プロファイル指定の確認
if [ -z "$AWS_PROFILE" ]; then
    echo "⚠️  AWS_PROFILE 環境変数が設定されていません"
    echo "💡 使用例: export AWS_PROFILE=sandbox && ./scripts/test-lambda.sh"
    exit 1
fi

# 設定
FUNCTION_NAME="aws-exam-agent-trigger-development"
ENVIRONMENT="development"

echo "🧪 Lambda関数テスト開始"
echo "========================"
echo "📋 使用プロファイル: $AWS_PROFILE"
echo "📋 関数名: $FUNCTION_NAME"

# アカウント確認
echo ""
echo "🔍 アカウント確認..."
aws sts get-caller-identity --profile "$AWS_PROFILE"

# Lambda関数の存在確認
echo ""
echo "🔍 Lambda関数の存在確認..."
if ! aws lambda get-function --function-name "$FUNCTION_NAME" --profile "$AWS_PROFILE" > /dev/null 2>&1; then
    echo "❌ Lambda関数が見つかりません: $FUNCTION_NAME"
    echo "💡 先にEventBridge Schedulerをデプロイしてください: ./scripts/deploy-eventbridge-scheduler.sh"
    exit 1
fi

echo "✅ Lambda関数確認完了: $FUNCTION_NAME"

# AgentCore Runtime ARN の取得
echo ""
echo "🔍 AgentCore Runtime ARN の確認"
echo "================================"

# 環境変数から取得を試行
if [ -n "$AGENTCORE_ARN" ]; then
    echo "📋 環境変数からARNを取得: $AGENTCORE_ARN"
else
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
fi

# ARN の妥当性チェック
if [[ ! "$AGENTCORE_ARN" =~ ^arn:aws:bedrock-agentcore:.*:.*:runtime/.* ]]; then
    echo "❌ 入力されたARNが無効です: $AGENTCORE_ARN"
    echo "💡 正しい形式: arn:aws:bedrock-agentcore:REGION:ACCOUNT:runtime/AGENT_ID"
    exit 1
fi

echo "📋 使用するAgentCore ARN: $AGENTCORE_ARN"

# テストペイロード作成（JSON形式）
TEST_PAYLOAD_JSON="{\"agentRuntimeArn\":\"$AGENTCORE_ARN\",\"exam_type\":\"SAP\",\"question_count\":1}"
echo ""
echo "🧪 Lambda関数テスト実行..."
echo "📋 テストペイロード（JSON）: $TEST_PAYLOAD_JSON"

# Base64エンコード
TEST_PAYLOAD_BASE64=$(echo "$TEST_PAYLOAD_JSON" | base64)
echo "📋 テストペイロード（Base64）: $TEST_PAYLOAD_BASE64"

RESPONSE_FILE="/tmp/lambda-test-response-$(date +%s).json"
echo "📋 レスポンスファイル: $RESPONSE_FILE"

# Lambda関数呼び出し（Base64エンコード版）
echo ""
echo "🚀 Lambda関数呼び出し中（Base64エンコード）..."
aws lambda invoke \
    --function-name "$FUNCTION_NAME" \
    --payload "$TEST_PAYLOAD_BASE64" \
    --profile "$AWS_PROFILE" \
    "$RESPONSE_FILE"

# レスポンス表示
echo ""
echo "📄 Lambda関数レスポンス:"
echo "========================"
if command -v jq > /dev/null 2>&1; then
    cat "$RESPONSE_FILE" | jq '.'
else
    cat "$RESPONSE_FILE"
fi

# エラーチェック
if grep -q "errorMessage" "$RESPONSE_FILE"; then
    echo ""
    echo "❌ Lambda関数でエラーが発生しました"
    echo "🔍 詳細なログを確認してください:"
    echo "   aws logs tail /aws/lambda/$FUNCTION_NAME --since 10m --profile $AWS_PROFILE"
    
    # エラーメッセージを表示
    if command -v jq > /dev/null 2>&1; then
        ERROR_MSG=$(cat "$RESPONSE_FILE" | jq -r '.errorMessage // empty')
        if [ -n "$ERROR_MSG" ]; then
            echo "📋 エラーメッセージ: $ERROR_MSG"
        fi
    fi
    
    # クリーンアップしてから終了
    rm -f "$RESPONSE_FILE"
    exit 1
fi

# 成功チェック
if command -v jq > /dev/null 2>&1; then
    if cat "$RESPONSE_FILE" | jq -e '.statusCode == 200' > /dev/null 2>&1; then
        echo ""
        echo "✅ Lambda関数テスト成功！"
        
        # レスポンス内容の詳細表示
        RESPONSE_BODY=$(cat "$RESPONSE_FILE" | jq -r '.body // empty')
        if [ -n "$RESPONSE_BODY" ]; then
            echo "📋 レスポンス内容:"
            echo "$RESPONSE_BODY" | jq '.' 2>/dev/null || echo "$RESPONSE_BODY"
        fi
    else
        echo ""
        echo "⚠️  Lambda関数が期待されるレスポンスを返しませんでした"
    fi
else
    echo ""
    echo "✅ Lambda関数呼び出し完了（jqがないため詳細チェックをスキップ）"
fi

# クリーンアップ
rm -f "$RESPONSE_FILE"

echo ""
echo "🔍 トラブルシューティング:"
echo "   ログ確認: aws logs tail /aws/lambda/$FUNCTION_NAME --follow --profile $AWS_PROFILE"
echo "   関数詳細: aws lambda get-function --function-name $FUNCTION_NAME --profile $AWS_PROFILE"
echo ""
echo "🎯 次のステップ:"
echo "   EventBridge Scheduler確認: aws scheduler get-schedule --name aws-exam-agent-daily-development --profile $AWS_PROFILE"
