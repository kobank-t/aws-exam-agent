# Cloud CoPassAgent

クラウド資格学習を通じて組織内のコミュニケーション活性化を支援する AI エージェント

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![Cloud](https://img.shields.io/badge/Cloud-Bedrock%20%7C%20Lambda%20%7C%20AgentCore-orange.svg)](https://aws.amazon.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-pytest-brightgreen.svg)](tests/)

## 📋 目次

- [🎯 プロジェクト概要](#-プロジェクト概要)
- [🚀 クイックスタート](#-クイックスタート)
- [📁 プロジェクト構造](#-プロジェクト構造)
- [🤖 技術スタック](#-技術スタック)
- [📚 ドキュメント](#-ドキュメント)
- [🚀 デプロイメント](#-デプロイメント)
- [🤝 コントリビューション](#-コントリビューション)
- [📄 ライセンス](#-ライセンス)
  - [🤖 技術スタック](#-技術スタック)
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

### 動作確認（30 秒）

```bash
# 既存環境での動作テスト
uv run python app/agentcore/agent_main.py --test
```

### 初回セットアップ

- **開発環境**: [セットアップガイド](docs/setup-guide.md)
- **本番デプロイ**: [デプロイガイド](docs/deployment-guide.md)

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
│   ├── setup-guide.md           # セットアップガイド
│   ├── deployment-guide.md      # デプロイメントガイド
│   ├── operations-guide.md      # 運用ガイド
│   ├── security-guide.md        # セキュリティガイド
│   ├── testing-guide.md         # テストガイド
│   ├── cost-guide.md           # コストガイド
│   └── troubleshooting-guide.md # トラブルシューティング
├── .kiro/                       # Kiro IDE設定・仕様書
│   ├── specs/aws-exam-agent/   # プロジェクト仕様書
│   └── steering/               # 開発ルール・ガイドライン
├── .vscode/                     # VS Code設定
└── pyproject.toml              # Python プロジェクト設定
```

## 🤖 技術スタック

- **AI 基盤**: Amazon Bedrock (Claude 3.5 Sonnet) + AgentCore + Strands Agents + MCP 統合
- **バックエンド**: Lambda + EventBridge Scheduler
- **フロントエンド**: Power Automate + Teams
- **言語**: Python 3.12 + uv

> **詳細**: [統合設計書](.kiro/specs/aws-exam-agent/design.md)

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
