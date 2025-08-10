#!/bin/bash
# エージェントテストスクリプト

set -e

echo "🤖 AWS Exam Agent テストを開始します..."

# 設定確認（config.pyに一元化済み）
echo "📋 設定管理: app/shared/config.py に一元化"

# 仮想環境の確認
if [ ! -d ".venv" ]; then
    echo "❌ 仮想環境が見つかりません。uv sync を実行してください。"
    exit 1
fi

echo "📋 環境情報:"
echo "  Python: $(uv run python --version)"
echo "  作業ディレクトリ: $(pwd)"

# 単体テストの実行
echo ""
echo "🧪 単体テストの実行..."
uv run pytest tests/unit/ -v --tb=short

# 統合テストの実行
echo ""
echo "🔗 統合テストの実行..."
uv run pytest tests/integration/ -v --tb=short

# AgentCore ローカルテストの実行
echo ""
echo "🤖 AgentCore ローカルテストの実行..."
echo "メインエージェントのテスト実行中..."
uv run python app/agentcore/agent_main.py

# コード品質チェック
echo ""
echo "🔍 コード品質チェック..."
echo "Ruff リンティング:"
uv run ruff check app/ tests/

echo ""
echo "Ruff フォーマット確認:"
uv run ruff format --check app/ tests/

# 型チェック
echo ""
echo "📝 型チェック..."
uv run mypy app/ --ignore-missing-imports

echo ""
echo "✅ すべてのテストが完了しました！"