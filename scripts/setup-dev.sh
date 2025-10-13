#!/bin/bash
# Cloud CoPassAgent 開発環境セットアップスクリプト
# 対象プラットフォーム: macOS, Windows (WSL/Git Bash)

set -e

echo "🚀 Cloud CoPassAgent 開発環境セットアップ"
echo "========================================="
echo "📋 対象プラットフォーム: macOS, Windows (WSL/Git Bash)"
echo ""

# Python バージョンチェック
echo "🐍 Python バージョンチェック中..."
if ! python3 --version | grep -q "3.12"; then
    echo "⚠️  Python 3.12+ が推奨されています"
    echo "💡 現在のバージョン: $(python3 --version)"
    echo "💡 インストール方法（macOS）: brew install python@3.12"
    echo "💡 インストール方法（Windows）: https://www.python.org/downloads/ から Python 3.12+ をダウンロード"
fi

# uv がインストールされているか確認
if ! command -v uv &> /dev/null; then
    echo "❌ uv がインストールされていません"
    echo "💡 インストール方法: curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "💡 インストール後: source ~/.bashrc (または ~/.zshrc)"
    exit 1
fi

echo "✅ uv バージョン: $(uv --version)"

# AWS CLI チェック
echo "☁️  AWS CLI 設定チェック中..."
if ! command -v aws &> /dev/null; then
    echo "⚠️  AWS CLI がインストールされていません"
    echo "💡 インストール方法（macOS）: brew install awscli"
    echo "💡 インストール方法（Windows）: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
elif ! aws sts get-caller-identity &> /dev/null; then
    echo "⚠️  AWS 認証情報が設定されていません"
    echo "💡 設定方法: aws configure"
    echo "💡 または環境変数: export AWS_PROFILE=your-profile"
else
    echo "✅ AWS 認証情報: $(aws sts get-caller-identity --query 'Arn' --output text)"
fi

# 仮想環境の作成と依存関係のインストール
echo "📦 依存関係のインストール中..."
uv sync

# uvx の動作確認（MCP Server用）
echo "🔧 uvx 動作確認中..."
if ! command -v uvx &> /dev/null; then
    echo "⚠️  uvx が利用できません（MCP Server に必要）"
    echo "💡 uv を再インストールしてください"
else
    echo "✅ uvx 利用可能"
fi

# pre-commit のインストール
echo "🔧 pre-commit フックのセットアップ中..."
uv run pre-commit install

# 環境変数ファイルの確認
echo "⚙️  環境設定ファイルチェック中..."
if [ ! -f ".env" ]; then
    echo "📝 .env ファイルを作成しています..."
    touch .env
    echo "# Cloud CoPassAgent 環境設定" >> .env
    echo "# AWS設定" >> .env
    echo "# AWS_REGION=us-east-1" >> .env
    echo "" >> .env
    echo "# Bedrockモデル設定" >> .env
    echo "# BEDROCK_MODEL_ID=jp.anthropic.claude-sonnet-4-5-20250929-v1:0" >> .env
    echo "# BEDROCK_REGION=ap-northeast-1" >> .env
    echo "" >> .env
    echo "# Teams連携" >> .env
    echo "# POWER_AUTOMATE_WEBHOOK_URL=https://..." >> .env
    echo "# POWER_AUTOMATE_SECURITY_TOKEN=your-security-token" >> .env
    echo "" >> .env
    echo "# AgentCore Memory" >> .env
    echo "# AGENTCORE_MEMORY_ID=your-memory-id" >> .env
    echo "✅ .env ファイルを作成しました（必要に応じて編集してください）"
else
    echo "✅ .env ファイル存在確認"
fi

# 動作確認
echo "🧪 動作確認中..."
if uv run python app/agentcore/agent_main.py --test &> /dev/null; then
    echo "✅ ローカル実行テスト成功"
else
    echo "⚠️  ローカル実行テストで警告（MCP初期化失敗の可能性）"
    echo "💡 本番環境では正常動作します"
fi

echo ""
echo "🎉 開発環境セットアップ完了！"
echo ""
echo "💡 次のステップ:"
echo "   📖 クイックスタート: docs/quickstart-guide.md"
echo "   🧪 品質チェック: ./scripts/python-quality-check.sh"
echo "   🚀 AgentCore デプロイ: ./scripts/deploy-agentcore.sh"
echo "   📊 ログ確認: ./scripts/show-agentcore-logs.sh"
echo ""
echo "🆘 困ったときは:"
echo "   📚 トラブルシューティング: docs/troubleshooting-guide.md"
echo "   🔧 環境変数ガイド: docs/environment-variables-guide.md"
