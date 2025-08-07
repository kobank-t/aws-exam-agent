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

# 環境変数ファイルの作成
if [ ! -f ".env" ]; then
    echo "📝 .env ファイルを作成します..."
    cat > .env << EOF
# AWS Exam Agent 環境設定

# 基本設定
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# AWS 設定
AWS_REGION=ap-northeast-1
AWS_PROFILE=default

# DynamoDB 設定
DYNAMODB_TABLE_NAME=aws-exam-agent-questions-dev
DYNAMODB_REGION=ap-northeast-1

# Bedrock 設定
BEDROCK_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0

# Teams 設定（実際の値に置き換えてください）
# TEAMS_WEBHOOK_URL=https://your-teams-webhook-url
# TEAMS_CHANNEL_ID=your-channel-id

# MCP 設定
MCP_AWS_DOCS_SERVER_ENABLED=true
MCP_AWS_KNOWLEDGE_SERVER_ENABLED=true
MCP_SERVER_TIMEOUT=30
EOF
    echo "✅ .env ファイルを作成しました。必要に応じて設定を更新してください。"
else
    echo "✅ .env ファイルが既に存在します"
fi

# テストの実行
echo "🧪 基本テストの実行..."
uv run pytest tests/ -v --tb=short || echo "⚠️  テストが失敗しました（まだテストファイルがない可能性があります）"

echo ""
echo "🎉 開発環境セットアップが完了しました！"
echo ""
echo "次のステップ:"
echo "1. .env ファイルの設定を確認・更新"
echo "2. AWS 認証情報の設定確認"
echo "3. VS Code で開発を開始"
echo ""
echo "開発サーバーの起動:"
echo "  uv run python app/agentcore/docker/agent_main.py"
echo ""
echo "テストの実行:"
echo "  uv run pytest"
echo ""
echo "コード品質チェック:"
echo "  uv run ruff check app/"
echo "  uv run ruff format app/"