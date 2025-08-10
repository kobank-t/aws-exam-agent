#!/bin/bash
# 開発環境セットアップスクリプト

set -e

echo "🚀 AWS Exam Agent 開発環境セットアップを開始します..."

# Python バージョン確認
echo "📋 Python バージョン確認..."
python3 --version

# uv がインストールされているか確認
if ! command -v uv &> /dev/null; then
    echo "❌ uv がインストールされていません。インストールしてください："
    echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✅ uv バージョン: $(uv --version)"

# 仮想環境の作成と依存関係のインストール
echo "📦 仮想環境の作成と依存関係のインストール..."
uv sync

# pre-commit のインストール
echo "🔧 pre-commit フックのセットアップ..."
uv run pre-commit install

# VS Code 設定の確認
if [ -d ".vscode" ]; then
    echo "✅ VS Code 設定が見つかりました"
else
    echo "⚠️  VS Code 設定が見つかりません"
fi

# AWS CLI の確認
if command -v aws &> /dev/null; then
    echo "✅ AWS CLI が利用可能です"
    aws --version
    echo "📋 AWS プロファイル確認:"
    aws configure list
else
    echo "⚠️  AWS CLI がインストールされていません"
fi

# 設定管理の説明
echo "📝 設定管理について:"
echo "  設定は app/shared/config.py に一元化されています"
echo "  学習用に適した値がデフォルトで設定済みです"
echo "  必要に応じて config.py を直接編集してください"

# テストの実行
echo "🧪 基本テストの実行..."
uv run pytest tests/ -v --tb=short || echo "⚠️  テストが失敗しました（まだテストファイルがない可能性があります）"

echo ""
echo "🎉 開発環境セットアップが完了しました！"
echo ""
echo "次のステップ:"
echo "1. app/shared/config.py の設定を確認（必要に応じて編集）"
echo "2. AWS 認証情報の設定確認"
echo "3. VS Code で開発を開始"
echo ""
echo "開発サーバーの起動:"
echo "  uv run python app/agentcore/agent_main.py"
echo ""
echo "テストの実行:"
echo "  uv run pytest"
echo ""
echo "コード品質チェック:"
echo "  uv run ruff check app/"
echo "  uv run ruff format app/"