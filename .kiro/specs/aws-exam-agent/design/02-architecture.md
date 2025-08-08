# アーキテクチャ

## システム全体構成

```mermaid
graph LR
    A[AI問題生成システム] --> B[問題配信システム]
    B --> C[Teams チャネル]
    C --> D[組織メンバー]

    E[AWS公式ドキュメント] --> A
    F[試験ガイド] --> A
    A --> G[問題データベース]

    H[Power Automate] --> B
    I[HTTP API] --> B
    B --> J[配信ログ]

    C --> K[リアクション・スレッド]
    K --> L[議論・知識共有]
    L --> M[参加状況分析]
```

## 主要コンポーネント

### 1. AI 問題生成エンジン

- AWS 公式ドキュメント・試験ガイドからの情報取得
- Professional レベル問題の自動生成
- 品質検証・重複チェック

### 2. Teams 連携システム

- Power Automate による問題配信
- リアクション収集・分析
- スレッド議論の促進

### 3. データ管理システム

- 問題データベース
- 参加状況・学習分析
- 配信ログ・エラー管理

## 技術スタック概要

### AI エージェント基盤

- **エージェントフレームワーク**: Strands Agents (AWS 製オープンソース)
- **実行環境**: AWS Bedrock AgentCore Runtime (Preview)
- **LLM**: Amazon Bedrock (Claude Opus 4, Claude Sonnet 4, Claude 3.7 Sonnet, Claude 3 Haiku)
- **MCP 統合**: Model Context Protocol による標準化されたコンテキスト提供
- **マルチエージェント**: Agent-as-Tools パターンによる専門エージェント連携
- **ストリーミング**: リアルタイム処理状況監視とレスポンス配信

### バックエンド

- **言語**: Python 3.12
- **パッケージ管理**: uv (仮想環境 + 依存関係管理)
- **API**: AgentCore Runtime (AI 処理) + API Gateway + Lambda (外部連携)
- **データベース**: DynamoDB (問題・解析データ)
- **キャッシュ**: DynamoDB TTL + Lambda メモリキャッシュ

### 外部連携・プロトコル

- **MCP (Model Context Protocol)**: 標準化されたコンテキスト提供
- **AWS Documentation MCP Server**: AWS 公式ドキュメント取得 (uvx awslabs.aws-documentation-mcp-server)
- **AWS Knowledge MCP Server**: AWS 包括的知識ベース（ドキュメント・ブログ・What's New・Well-Architected 等）
- **AWS Pricing MCP Server**: 設計段階でのコスト試算・技術選択支援
- **Power Automate**: Teams 配信用 HTTP API

### インフラ・デプロイ

- **AI 処理**: AWS Bedrock AgentCore Runtime (完全サーバーレス)
- **外部連携 API**: API Gateway REST API (Regional エンドポイント) + Lambda
- **認証**: AgentCore IAM 認証 + API Gateway API Key
- **監視**: AgentCore オブザーバビリティ + CloudWatch Logs + X-Ray トレーシング
- **トリガー**: EventBridge スケジュール → API Gateway → AgentCore Runtime
- **デプロイ**: bedrock-agentcore-starter-toolkit + AWS SAM (ハイブリッド)

## プロジェクト構成（AgentCore 中心設計）

### 統一されたディレクトリ構造

```
aws-exam-agent/
├── app/                          # 全ソースコード集約
│   ├── agentcore/               # AgentCore Runtime用（メイン）
│   │   ├── agent_main.py        # メインエージェント（監督者）
│   │   ├── requirements.txt     # エージェント依存関係
│   │   └── mcp/                 # MCP統合
│   │       └── __init__.py
│   ├── lambda/                  # 補助Lambda関数（最小限）
│   │   └── __init__.py
│   ├── models/                  # データモデル
│   │   └── __init__.py
│   ├── services/                # ビジネスロジック
│   │   └── __init__.py
│   └── shared/                  # 共通モジュール
│       ├── __init__.py
│       ├── config.py
│       ├── constants.py
│       └── exceptions.py
├── tests/                       # テストコード
│   ├── unit/
│   │   ├── agentcore/          # test_プレフィックス削除済み
│   │   │   └── test_agent_main.py
│   │   └── shared/             # test_プレフィックス削除済み
│   │       ├── test_config.py
│   │       ├── test_constants.py
│   │       └── test_exceptions.py
│   ├── integration/
│   │   └── __init__.py
│   └── e2e/
├── infrastructure/              # インフラ定義（将来実装）
├── scripts/                     # デプロイ・運用スクリプト
│   ├── python-quality-check.sh
│   ├── setup-dev.sh
│   └── test-agents.sh
├── .kiro/                       # Kiro IDE設定・仕様書
│   ├── specs/aws-exam-agent/    # 設計書・仕様書
│   ├── steering/                # 開発ルール・規約
│   ├── hooks/                   # エージェントフック
│   └── settings/                # MCP設定等
├── .github/                     # CI/CD
│   └── workflows/
│       └── quality-check.yml
├── pyproject.toml              # Python プロジェクト設定
├── README.md
└── WORK_LOG.md
```

### 構成の利点

- **AgentCore 中心**: メイン処理を AgentCore Runtime で実行
- **シンプルな構造**: docker ディレクトリ削除によるフラットな構成
- **テスト構造統一**: test\_プレフィックス削除による一貫性
- **MCP 統合**: 標準化されたコンテキスト提供の明確な分離
- **デプロイ簡素化**: agentcore CLI による簡単デプロイ
- **監視統合**: AgentCore オブザーバビリティの活用

### 構造管理の改善

**問題**: ディレクトリ構造が複数ファイル（02-architecture.md, README.md, tasks.md 等）に散在し、保守性が低下

**解決策**:

- **単一情報源の原則**: 構造情報は 02-architecture.md に集約
- **参照による統一**: 他ファイルは 02-architecture.md を参照
- **自動同期**: 構造変更時の一括更新スクリプト導入を検討
