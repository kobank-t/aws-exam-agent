#!/bin/bash
# 開発環境セットアップスクリプト

set -e

echo "🚀 AWS Exam Agent 開発環境セットアップ"
echo "===================================="

# uv がインストールされているか確認
if ! command -v uv &> /dev/null; then
    echo "❌ uv がインストールされていません"
    echo "💡 インストール方法: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✅ uv バージョン: $(uv --version)"

# 仮想環境の作成と依存関係のインストール
echo "📦 依存関係のインストール中..."
uv sync

# pre-commit のインストール
echo "🔧 pre-commit フックのセットアップ中..."
uv run pre-commit install

echo ""
echo "🎉 開発環境セットアップ完了！"
echo ""
echo "💡 次のステップ:"
echo "   テスト・品質チェック: ./scripts/python-quality-check.sh"
echo "   AgentCore デプロイ: ./scripts/deploy-agentcore.sh"
