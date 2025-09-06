# 開発環境セットアップガイド

Cloud CoPassAgent の開発環境を構築する手順です。

## 🚀 10 分で開始：開発環境セットアップ

### 前提条件

- **Python 3.12+** がインストール済み
- **AWS CLI** が設定済み（`aws sts get-caller-identity` で確認）
- **Git** がインストール済み

### 1. リポジトリのクローン

```bash
git clone https://github.com/kobank-t/aws-exam-agent.git
cd aws-exam-agent
```

### 2. 開発環境の自動セットアップ

```bash
# 開発環境セットアップスクリプトの実行
./scripts/setup-dev.sh
```

このスクリプトは以下を自動実行します：

- **uv** のインストール（Python パッケージマネージャー）
- **依存関係** のインストール
- **pre-commit フック** の設定
- **VS Code 設定** の適用

### 3. 環境変数の設定

プロジェクトルートに `.env` ファイルを作成：

```bash
# セキュリティトークンの生成（64文字のランダム文字列）
SECURITY_TOKEN=$(openssl rand -hex 32)
echo $SECURITY_TOKEN
# 例: a1b2c3d4e5f6789... （実際の値は毎回異なります）

# .envファイルの作成
cat > .env << EOF
# AWS 設定
AWS_DEFAULT_REGION=us-east-1
# AWS_PROFILE=sandbox  # 任意: 特定のプロファイルを使用する場合

# Teams 連携（必須）
POWER_AUTOMATE_WEBHOOK_URL=https://prod-XX.japaneast.logic.azure.com/workflows/YOUR-WORKFLOW-ID/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=YOUR-SIGNATURE

# セキュリティトークン（必須）
POWER_AUTOMATE_SECURITY_TOKEN=$SECURITY_TOKEN
EOF
```

**重要**: 上記の例の値は実際には使用しないでください。必ず `openssl rand -hex 32` で生成した値を使用してください。

> **詳細**: [環境変数ガイド](environment-variables-guide.md)

### 4. 動作確認

```bash
# ローカル実行テスト
uv run python app/agentcore/agent_main.py --test

# 品質チェック
./scripts/python-quality-check.sh
```

## 🔧 手動セットアップ（トラブル時）

自動セットアップが失敗した場合の手動手順：

### uv のインストール

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 依存関係のインストール

```bash
# Python 依存関係
uv sync

# pre-commit フックの設定
uv run pre-commit install
```

## 🚨 トラブルシューティング

### よくある問題

**Q: `uv` コマンドが見つからない**

```bash
# パスの確認
echo $PATH
# シェルの再起動
source ~/.bashrc  # または ~/.zshrc
```

**Q: AWS CLI の設定エラー**

```bash
# AWS CLI の設定確認
aws configure list
aws sts get-caller-identity
```

**Q: Python バージョンエラー**

```bash
# Python バージョン確認
python3 --version
# 3.12+ が必要
```

> **詳細**: [トラブルシューティングガイド](troubleshooting-guide.md)

## 🎯 次のステップ

- [デプロイガイド](deployment-guide.md) - 本番環境への展開
- [運用ガイド](operations-guide.md) - 日常運用の手順
- [開発ルール](.kiro/steering/) - コーディング規約とベストプラクティス
