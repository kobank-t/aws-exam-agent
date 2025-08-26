# AWS Exam Agent

AI エージェントによる AWS 試験問題自動生成・配信システム

## 🎯 プロジェクト概要

AWS Exam Agent は、Strands Agents フレームワークと AWS Bedrock AgentCore を活用した AI エージェントによる自動問題生成を核とした組織内コラボレーション学習プラットフォームです。200 名のエンジニア組織において、AWS Certified Solutions Architect - Professional の学習を通じてコミュニケーション活性化とスキルトランスファーを促進します。

### 主要目的

- **AI エージェント技術のスキルアップ**（開発側）
- **組織内コミュニケーション活性化**（利用側）
- **強強メンバから経験の浅いメンバへのスキルトランスファー**

### 技術スタック

- **AI 基盤**: AWS Bedrock AgentCore + Strands Agents + MCP 統合
- **バックエンド**: Python 3.12 + uv + DynamoDB + Lambda
- **フロントエンド**: Power Automate + Teams リアクション
- **テスト**: Playwright E2E + pytest + moto

## 🚀 クイックスタート

### 前提条件

- Python 3.12+
- uv (Python パッケージ管理)
- AWS CLI (設定済み)
- VS Code (推奨)

### 開発環境セットアップ

```bash
# リポジトリのクローン
git clone https://github.com/kobank-t/aws-exam-agent.git
cd aws-exam-agent

# 開発環境の自動セットアップ
./scripts/setup-dev.sh

# 環境設定ファイルの編集
cp .env.example .env
# .env ファイルを編集して実際の値を設定

# 開発サーバーの起動（テスト）
uv run python app/agentcore/agent_main.py
```

### テストの実行

```bash
# 包括的な品質チェック（推奨）
./scripts/python-quality-check.sh

# 単体テストのみ
uv run pytest tests/unit/ -v

# 特定のテストファイル
uv run pytest tests/unit/agentcore/test_agent_main.py -v

# カバレッジ付きテスト実行
uv run pytest tests/unit/ --cov=app --cov-report=html

# コード品質チェック（個別実行）
uv run ruff check app/ tests/
uv run ruff format app/ tests/
uv run mypy app/
```

## 📁 プロジェクト構造

> **詳細な構造情報**: [02-architecture.md](/.kiro/specs/aws-exam-agent/design/02-architecture.md) を参照

```
aws-exam-agent/
├── app/                          # 全ソースコード集約
│   ├── agentcore/               # AgentCore Runtime用（メイン）
│   │   ├── agent_main.py        # メインエージェント（監督者）
│   │   ├── requirements.txt     # エージェント依存関係
│   │   └── mcp/                 # MCP統合
│   ├── trigger/                 # EventBridge Scheduler用トリガー関数
│   │   ├── lambda_function.py   # Lambda関数メインファイル
│   │   ├── requirements.txt     # Lambda依存関係
│   │   └── buildspec.yml        # Lambda専用ビルド設定
│   ├── models/                  # データモデル
│   ├── services/                # ビジネスロジック
│   └── shared/                  # 共通モジュール
├── tests/                       # テストコード
│   ├── unit/                    # 単体テスト
│   │   ├── agentcore/          # AgentCore関連テスト
│   │   ├── trigger/            # Lambda関数テスト
│   │   └── shared/             # 共通モジュールテスト
│   ├── integration/             # 統合テスト
│   └── e2e/                     # E2Eテスト
├── infrastructure/              # インフラ定義
│   ├── eventbridge-scheduler.yaml   # EventBridge Scheduler定義
│   └── parameters-development.json  # 開発環境パラメータ
├── scripts/                     # デプロイ・運用スクリプト
│   ├── build-lambda.sh          # Lambda関数ビルド
│   ├── deploy-eventbridge-scheduler.sh  # 統合デプロイ
│   └── python-quality-check.sh  # 品質チェック自動化
├── docs/                        # ドキュメント
│   ├── testing-guide.md         # テスト実装ガイド
│   ├── security-guide.md        # セキュリティガイド
│   └── [その他運用ドキュメント]
├── .kiro/specs/aws-exam-agent/  # 設計書・仕様書
└── pyproject.toml              # Python プロジェクト設定
```

## 🤖 AI エージェント構成

### マルチエージェントシステム

- **監督者エージェント**: Agent-as-Tools パターンで専門エージェントを統合
- **AWS 情報取得エージェント**: MCP Server を通じた最新情報取得
- **問題生成エージェント**: Professional レベル問題の自動生成
- **品質管理エージェント**: 技術的正確性と適切な難易度の検証

### MCP (Model Context Protocol) 統合

- **AWS Documentation MCP Server**: AWS 公式ドキュメント取得
- **AWS Knowledge MCP Server**: AWS 包括的知識ベース（ドキュメント・ブログ・What's New・Well-Architected 等）
- **標準化されたコンテキスト提供**: uvx による統一的なサーバー起動

## 📋 開発ワークフロー

### 実装タスク

現在の実装状況は `.kiro/specs/aws-exam-agent/tasks.md` で管理されています。

**Phase 1: 環境セットアップ** ✅

1. Python 開発環境のセットアップ ✅
2. AgentCore 開発環境のセットアップ ✅
3. テスト環境のセットアップ ✅
4. 品質管理基盤の構築 ✅
5. テストガイドとコメントスタイル統一 ✅

**Phase 2: データ基盤とコア機能** 🚧

4. データモデルと DynamoDB 基盤の実装
5. キャッシュシステムの実装

**Phase 3: マルチエージェントシステムのコア機能** 📋

6. MCP 統合と AWS 情報取得エージェントの実装
7. 問題生成エージェントの実装
8. 品質管理エージェントと監督者エージェントの実装

### コーディング規約

- **Python**: PEP8 準拠 + Ruff による自動フォーマット
- **型ヒント**: 必須（mypy による型チェック）
- **テスト**: pytest + 契約による設計アプローチ
- **コミット**: Conventional Commits 形式

### 品質管理

#### テスト品質基準
- **カバレッジ**: 90%以上を維持
- **テストスタイル**: 契約による設計 + Given-When-Then パターン
- **コメント統一**: docstring と インラインコメントの統一フォーマット
- **品質チェック**: 全テスト実行前に自動品質チェック必須

#### 品質チェック自動化
```bash
# 包括的品質チェック（推奨）
./scripts/python-quality-check.sh

# 個別チェック
uv run ruff check app/ tests/     # コードスタイル
uv run mypy app/                  # 型チェック  
uv run pytest tests/unit/ --cov=app  # テスト + カバレッジ
```

## 🔧 開発ツール

### VS Code 設定

プロジェクトには以下の VS Code 設定が含まれています：

- Python 開発環境の自動設定
- Ruff による自動リンティング・フォーマット
- pytest テスト実行設定
- AWS Toolkit 統合
- デバッグ設定（AgentCore ローカルテスト対応）

#### 個人設定のカスタマイズ

個人固有の設定は `.vscode/settings.json.local` に記述してください：

```json
{
  "aws.samcli.location": "/your/custom/path/to/sam",
  "python.defaultInterpreterPath": "/your/custom/python/path"
}
```

### pre-commit フック

コミット前の自動品質チェック：

```bash
# pre-commit のインストール
uv run pre-commit install

# 手動実行
uv run pre-commit run --all-files
```

## 📚 ドキュメント

### 設計書

詳細な設計書は `.kiro/specs/aws-exam-agent/design/` に分割して格納されています：

- [01. システム概要](/.kiro/specs/aws-exam-agent/design/01-overview.md)
- [02. アーキテクチャ](/.kiro/specs/aws-exam-agent/design/02-architecture.md)
- [03. AI エンジン](/.kiro/specs/aws-exam-agent/design/03-ai-engine.md)
- [04. Teams 連携](/.kiro/specs/aws-exam-agent/design/04-teams-integration.md)
- [05. データモデル](/.kiro/specs/aws-exam-agent/design/05-data-models.md)
- [06. デプロイメント](/.kiro/specs/aws-exam-agent/design/06-deployment.md)
- [07. エラーハンドリング](/.kiro/specs/aws-exam-agent/design/07-error-handling.md)
- [08. テスト戦略](/.kiro/specs/aws-exam-agent/design/08-testing.md)

### 要件定義

- [要件定義書](/.kiro/specs/aws-exam-agent/requirements.md)
- [実装タスクリスト](/.kiro/specs/aws-exam-agent/tasks.md)

## 🚀 デプロイメント

### AgentCore Runtime デプロイ

```bash
# AgentCore 設定
agentcore configure

# デプロイ実行
agentcore launch
```

**詳細な手順**: [AgentCore デプロイメントガイド](docs/agentcore-deployment-guide.md)

### EventBridge Scheduler デプロイ

```bash
# 定期実行システムのデプロイ
./scripts/deploy-eventbridge-scheduler.sh
```

**詳細な手順**: [EventBridge Scheduler デプロイ手順書](docs/eventbridge-scheduler-deployment.md)

### Lambda + API Gateway デプロイ

```bash
# SAM ビルド・デプロイ
sam build
sam deploy --guided
```

## 📖 運用ドキュメント

### AgentCore 関連

- **[デプロイメントガイド](docs/deployment-guide.md)** - デプロイ、設定、動作確認の包括的なガイド
- **[運用・保守ガイド](docs/operations-guide.md)** - 日常運用、監視、トラブルシューティング
- **[環境変数設定ガイド](docs/environment-variables-guide.md)** - 環境変数設定のクイックリファレンス
- **[トラブルシューティングガイド](docs/troubleshooting-guide.md)** - 問題解決の系統的アプローチ

### セキュリティ・品質管理

- **[セキュリティガイド](docs/security-guide.md)** - セキュリティ機能と運用上のセキュリティ考慮事項
- **[テストガイド](docs/testing-guide.md)** - 包括的なテスト戦略とテスト実行手順

## 🤝 コントリビューション

1. フィーチャーブランチの作成: `git checkout -b feature/new-feature`
2. 変更のコミット: `git commit -m 'feat: add new feature'`
3. ブランチのプッシュ: `git push origin feature/new-feature`
4. プルリクエストの作成

## 📄 ライセンス

MIT License

## 📞 サポート

- **GitHub Issues**: バグ報告・機能要望
- **作業記録**: [WORK_LOG.md](/WORK_LOG.md)
- **設計判断記録**: [技術選択記録](/.kiro/specs/aws-exam-agent/design/09-decisions.md)
