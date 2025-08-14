#!/bin/bash

# AWS Exam Agent - AgentCore 動作確認スクリプト
# このスクリプトは AgentCore の動作確認を行います

set -e

echo "🚀 AWS Exam Agent - AgentCore 動作確認開始"
echo "============================================"

# AgentCore ディレクトリに移動
cd app/agentcore

# AgentCore のステータス確認
echo ""
echo "📋 AgentCore ステータス確認..."
agentcore status

# 動作確認テスト
echo ""
echo "🧪 動作確認テスト実行..."

# テスト: コンピューティングカテゴリ
echo ""
echo "テスト: コンピューティングカテゴリの問題生成"
echo "----------------------------------------------"
agentcore invoke '{"exam_type": "SAP", "category": ["コンピューティング"]}'

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