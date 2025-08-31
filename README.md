# Cloud CoPassAgent

クラウド資格学習を通じて組織内のコミュニケーション活性化を支援する AI エージェント

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![Cloud](https://img.shields.io/badge/Cloud-Bedrock%20%7C%20Lambda%20%7C%20AgentCore-orange.svg)](https://aws.amazon.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-pytest-brightgreen.svg)](tests/)

## 📋 目次

- [Cloud CoPassAgent](#cloud-copassagent)
  - [📋 目次](#-目次)
  - [🎯 プロジェクト概要](#-プロジェクト概要)
    - [目的・効果](#目的効果)
  - [🏗️ アーキテクチャ](#️-アーキテクチャ)
  - [🚀 クイックスタート](#-クイックスタート)
  - [📁 プロジェクト構造](#-プロジェクト構造)
  - [🤖 AI エージェント構成](#-ai-エージェント構成)
    - [技術スタック](#技術スタック)
  - [📋 開発ワークフロー](#-開発ワークフロー)
  - [🔧 開発ツール](#-開発ツール)
  - [🔍 運用・監視](#-運用監視)
  - [🔒 セキュリティ](#-セキュリティ)
  - [💰 コスト管理](#-コスト管理)
  - [🚨 トラブルシューティング](#-トラブルシューティング)
  - [📚 ドキュメント](#-ドキュメント)
    - [📋 プロジェクト仕様](#-プロジェクト仕様)
    - [📖 運用ガイド](#-運用ガイド)
  - [🚀 デプロイメント](#-デプロイメント)
  - [🤝 コントリビューション](#-コントリビューション)
  - [📄 ライセンス](#-ライセンス)

## 🎯 プロジェクト概要

**Cloud CoPassAgent**は、クラウド資格学習を通じて組織内のコミュニケーション(Co)を促し、合格とスキルの橋渡し(Pass)を支援する AI エージェントです。

**現在の MVP**: AWS SAP を題材とした問題生成から投稿までの最小限フロー  
**将来展望**: 様々なクラウド資格への汎用化

### 目的・効果

- **AI エージェント技術のスキルアップ**（開発側）
- **組織内コミュニケーション活性化、クラウド用語の習慣化**（利用側）
- **強強メンバから経験の浅いメンバへのスキルトランスファー**

> **詳細**: [要件定義](.kiro/specs/aws-exam-agent/requirements.md) | [統合設計書](.kiro/specs/aws-exam-agent/design.md)

## 🏗️ アーキテクチャ

![システム構成図](docs/diagram.drawio.svg)

> **詳細**: [統合設計書](.kiro/specs/aws-exam-agent/design.md)

## 🚀 クイックスタート

```bash
# 開発環境セットアップ
./scripts/setup-dev.sh

# ローカル実行テスト
uv run python app/agentcore/agent_main.py --test

# 品質チェック
./scripts/python-quality-check.sh
```

> **詳細**: [クイックスタートガイド](docs/quickstart-guide.md) | [デプロイメントガイド](docs/deployment-guide.md)

## 📁 プロジェクト構造

> **📍 単一情報源**: このセクションがプロジェクト構造の正式な情報源です  
> **詳細設計**: [統合設計書](.kiro/specs/aws-exam-agent/design.md)

```
aws-exam-agent/
├── app/                          # アプリケーションコード
│   ├── agentcore/               # AgentCore Runtime用（メイン）
│   │   ├── agent_main.py        # メインエージェント（監督者）
│   │   ├── teams_client.py      # Teams連携クライアント
│   │   └── requirements.txt     # エージェント依存関係
│   ├── trigger/                 # EventBridge Scheduler用トリガー関数
│   │   ├── lambda_function.py   # Lambda関数メインファイル
│   │   ├── requirements.txt     # Lambda依存関係
│   │   └── buildspec.yml        # Lambda専用ビルド設定
│   └── test_client.py           # テスト用クライアント
├── tests/                       # テストコード
│   └── unit/                    # 単体テスト
│       ├── agentcore/          # AgentCore関連テスト
│       └── trigger/            # Lambda関数テスト
├── templates/                   # テンプレートファイル
│   └── teams/                   # Teams関連テンプレート
├── infrastructure/              # インフラ定義
│   ├── agentcore-resources.yaml     # AgentCore リソース定義
│   ├── eventbridge-scheduler.yaml   # EventBridge Scheduler定義
│   └── parameters-development.json  # 開発環境パラメータ
├── scripts/                     # デプロイ・運用スクリプト
│   ├── deploy-agentcore.sh      # AgentCore デプロイ
│   ├── deploy-eventbridge-scheduler.sh  # EventBridge デプロイ
│   ├── python-quality-check.sh  # 品質チェック自動化
│   └── setup-dev.sh            # 開発環境セットアップ
├── docs/                        # ドキュメント
│   ├── deployment-guide.md      # デプロイメントガイド
│   ├── operations-guide.md      # 運用ガイド
│   ├── security-guide.md        # セキュリティガイド
│   ├── testing-guide.md         # テストガイド
│   └── troubleshooting-guide.md # トラブルシューティング
├── .kiro/                       # Kiro IDE設定・仕様書
│   ├── specs/aws-exam-agent/   # プロジェクト仕様書
│   └── steering/               # 開発ルール・ガイドライン
├── .vscode/                     # VS Code設定
└── pyproject.toml              # Python プロジェクト設定
```

## 🤖 AI エージェント構成

- **AI 基盤**: Amazon Bedrock (Claude 3.5 Sonnet) + AgentCore + Strands Agents + MCP 統合
- **問題生成**: クラウド資格試験問題の自動生成（現在は AWS SAP 対応）
- **Teams 統合**: Power Automate 経由での自動投稿

### 技術スタック

- **AI 基盤**: Amazon Bedrock + AgentCore + Strands Agents + MCP 統合
- **バックエンド**: Lambda + EventBridge Scheduler
- **フロントエンド**: Power Automate + Teams
- **言語**: Python 3.12 + uv

> **詳細**: [統合設計書](.kiro/specs/aws-exam-agent/design.md)

## 📋 開発ワークフロー

**実装状況**: MVP 完了（AWS SAP 問題生成 + Teams 投稿）

**改善予定**:

- 問題生成精度の向上（試験ガイド・サンプル問題の活用）
- 生成問題の品質評価・再生成機能
- AWS SAP 以外の様々な資格への汎用化
- 蓄積問題の MS365 Copilot Agent 活用

> **詳細**: [実装タスク](.kiro/specs/aws-exam-agent/tasks.md) | [作業記録](WORK_LOG.md)

**開発規約**:

> **詳細**: [Python コーディング規約](.kiro/steering/python-coding-standards.md) | [テスト設計標準](.kiro/steering/test-design-standards.md)

## 🔧 開発ツール

- **Python 3.12** + **uv** (パッケージ管理)
- **VS Code** 設定済み (`.vscode/`)
- **品質チェック**: `./scripts/python-quality-check.sh`

> **詳細**: [環境変数ガイド](docs/environment-variables-guide.md)

## 🔍 運用・監視

```bash
# AgentCore ログ確認
./scripts/show-agentcore-logs.sh

# 動作確認
./scripts/test-agentcore.sh
```

> **詳細**: [運用ガイド](docs/operations-guide.md)

## 🔒 セキュリティ

- **最小権限の原則**: IAM ロール設計
- **暗号化**: HTTPS/TLS 通信
- **機密情報管理**: 環境変数

> **詳細**: [セキュリティガイド](docs/security-guide.md)

## 💰 コスト管理

**推定**: $11-21/月 (Bedrock + Lambda + AgentCore)  
**MVP 段階**: AWS SAP 問題生成に最適化

> **詳細**: [コストガイド](docs/cost-guide.md)

## 🚨 トラブルシューティング

```bash
# ログ確認
./scripts/show-agentcore-logs.sh

# 動作テスト
uv run python app/agentcore/agent_main.py --test
```

> **詳細**: [トラブルシューティングガイド](docs/troubleshooting-guide.md)

## 📚 ドキュメント

### 📋 プロジェクト仕様

- [要件定義](.kiro/specs/aws-exam-agent/requirements.md)
- [統合設計書](.kiro/specs/aws-exam-agent/design.md)
- [実装タスク](.kiro/specs/aws-exam-agent/tasks.md)

### 📖 運用ガイド

- [デプロイメントガイド](docs/deployment-guide.md)
- [運用ガイド](docs/operations-guide.md)
- [セキュリティガイド](docs/security-guide.md)
- [テストガイド](docs/testing-guide.md)
- [トラブルシューティング](docs/troubleshooting-guide.md)
- [コストガイド](docs/cost-guide.md)
- [環境変数ガイド](docs/environment-variables-guide.md)

## 🚀 デプロイメント

```bash
# AgentCore デプロイ
./scripts/deploy-agentcore.sh

# EventBridge Scheduler デプロイ
./scripts/deploy-eventbridge-scheduler.sh
```

> **詳細**: [デプロイメントガイド](docs/deployment-guide.md)

## 🤝 コントリビューション

1. フィーチャーブランチの作成: `git checkout -b feature/new-feature`
2. 変更のコミット: `git commit -m 'feat: add new feature'`
3. ブランチのプッシュ: `git push origin feature/new-feature`
4. プルリクエストの作成

## 📄 ライセンス

MIT License
