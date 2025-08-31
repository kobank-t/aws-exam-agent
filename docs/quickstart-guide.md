# Cloud CoPassAgent クイックスタートガイド

## 🎯 5 分で理解：Cloud CoPassAgent とは？

「Cloud CoPassAgent」は、クラウド資格学習を通じて組織内のコミュニケーション(Co)を促し、合格とスキルの橋渡し(Pass)を支援する AI エージェントです。

### 現在の機能（MVP）

- **問題生成**: AWS SAP レベルの試験問題を AI が自動生成
- **Teams 投稿**: 生成された問題を Teams チャンネルに自動投稿
- **定期実行**: EventBridge Scheduler による定期的な問題配信

### 組織への価値

- **AI エージェント技術のスキルアップ**（開発側）
- **組織内コミュニケーション活性化、クラウド用語の習慣化**（利用側）
- **強強メンバから経験の浅いメンバへのスキルトランスファー**

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
# 開発環境セットアップ（uv、依存関係、pre-commit）
./scripts/setup-dev.sh
```

### 3. 環境設定

```bash
# 環境変数ファイルは setup-dev.sh で自動作成されます
# 必要に応じて .env ファイルを編集:
# TEAMS_WEBHOOK_URL=https://...（Teams 投稿用）
# AWS_REGION=us-east-1（デフォルト）
```

### 4. 動作確認

```bash
# ローカル実行テスト
uv run python app/agentcore/agent_main.py --test

# 品質チェック
./scripts/python-quality-check.sh
```

## 🔧 よくあるつまずきポイント

### ❌ uv がインストールされていない

```bash
# エラー: command not found: uv
# 解決方法:
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc  # または ~/.zshrc
```

### ❌ AWS 認証情報が設定されていない

```bash
# エラー: Unable to locate credentials
# 解決方法:
aws configure
# または
export AWS_PROFILE=your-profile
```

### ❌ Python バージョンが古い

```bash
# エラー: Python 3.12+ required
# 解決方法（macOS）:
brew install python@3.12
# 解決方法（Ubuntu）:
sudo apt update && sudo apt install python3.12
```

### ❌ MCP Server 接続エラー

```bash
# エラー: MCP initialization failed
# 解決方法:
# 1. uvx のインストール確認
uvx --version

# 2. MCP Server の手動テスト
uvx awslabs.aws-documentation-mcp-server@latest

# 3. ネットワーク接続確認
curl -I https://pypi.org/
```

## 📋 開発ワークフロー

### 日常的な開発作業

```bash
# 1. 品質チェック（開発前）
./scripts/python-quality-check.sh

# 2. コード変更

# 3. テスト実行
uv run pytest tests/unit/ -v

# 4. ローカル動作確認
uv run python app/agentcore/agent_main.py --test

# 5. コミット（pre-commit が自動実行）
git add .
git commit -m "feat: 新機能追加"
```

### デプロイ作業

```bash
# AgentCore デプロイ
./scripts/deploy-agentcore.sh

# EventBridge Scheduler デプロイ
./scripts/deploy-eventbridge-scheduler.sh

# ログ確認
./scripts/show-agentcore-logs.sh
```

## 🎯 次のステップ

### 開発者向け

1. **詳細理解**: [統合設計書](../.kiro/specs/aws-exam-agent/design.md) を読む
2. **実装タスク**: [タスクリスト](../.kiro/specs/aws-exam-agent/tasks.md) で進捗確認
3. **コーディング規約**: [Python 規約](../.kiro/steering/python-coding-standards.md) を確認

### 運用者向け

1. **デプロイ**: [デプロイメントガイド](deployment-guide.md) で本番環境構築
2. **監視**: [運用ガイド](operations-guide.md) で日常運用を理解
3. **トラブル対応**: [トラブルシューティング](troubleshooting-guide.md) で問題解決

### 新機能開発者向け

1. **要件定義**: [要件定義](../.kiro/specs/aws-exam-agent/requirements.md) で現在の機能範囲を確認
2. **アーキテクチャ**: システム構成を理解してから拡張計画を立案
3. **品質基準**: [テスト設計標準](../.kiro/steering/test-design-standards.md) で品質要件を確認

## 🆘 困ったときは

### ドキュメント

- **基本情報**: [README.md](../README.md)
- **技術詳細**: [統合設計書](../.kiro/specs/aws-exam-agent/design.md)
- **作業履歴**: [WORK_LOG.md](../WORK_LOG.md)

### 実際の問題解決

- **トラブルシューティング**: [troubleshooting-guide.md](troubleshooting-guide.md)
- **環境設定**: [environment-variables-guide.md](environment-variables-guide.md)
- **セキュリティ**: [security-guide.md](security-guide.md)

### コミュニティ

- **GitHub Issues**: バグ報告・機能要望
- **Teams チャンネル**: 組織内での質問・議論

---

**作成日**: 2025 年 8 月 26 日  
**対象**: 新規参加者・開発者・運用者  
**目的**: 最短経路でのプロジェクト理解と開発開始
