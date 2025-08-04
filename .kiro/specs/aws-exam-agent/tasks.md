# Implementation Plan

## 概要

この実装計画は、Strands Agents フレームワークと AWS Bedrock AgentCore を活用した AWS Exam Agent の設計書に基づいて、テスト駆動開発（TDD）アプローチで段階的に機能を実装するためのタスクリストです。各タスクは独立して実行可能で、前のタスクの成果物を活用して次のタスクに進む構成になっています。

## 実装方針

- **AgentCore 中心**: メイン処理を AgentCore Runtime で実行
- **マルチエージェント**: Agent-as-Tools パターンによる専門エージェント連携
- **MCP 統合**: Model Context Protocol による標準化されたコンテキスト提供
- **テスト駆動開発**: 各機能の実装前にテストを作成
- **段階的実装**: 小さな単位で機能を実装し、早期に動作確認
- **ストリーミング対応**: リアルタイム処理状況監視

## 現在の状況

- **完了済み**: 要件定義、設計書（9 ファイル分割）、コーディング規約
- **更新完了**: Strands & AgentCore ハンズオン知見の反映
- **現在フェーズ**: 実装フェーズ開始準備完了
- **コードベース**: 未実装（README.md、WORK_LOG.md、設計書のみ存在）
- **次回開始**: タスク 1（Python 開発環境セットアップ）から実装開始

## タスクリスト

### Phase 1: 環境セットアップ

- [ ] 1. Python 開発環境のセットアップ

  - プロジェクト構造の作成（AgentCore 中心設計）
  - uv 環境と pyproject.toml の設定
  - 依存関係の定義（strands-agents、bedrock-agentcore、uv、pytest、moto 等）
  - 開発ツール設定（Ruff、pre-commit、VS Code 設定）
  - AgentCore 用ディレクトリ構造とファイル作成
  - _Requirements: 全体の基盤_

- [ ] 2. AgentCore 開発環境のセットアップ

  - AWS CLI 設定とプロファイル確認
  - bedrock-agentcore-starter-toolkit インストールと設定
  - MCP Server 環境構築（uvx、uv インストール）
  - AWS Documentation MCP Server 動作確認
  - AWS Knowledge MCP Server 動作確認
  - AgentCore CLI（agentcore configure/launch）動作確認
  - _Requirements: AgentCore 基盤、MCP 統合_

- [ ] 3. テスト環境のセットアップ
  - pytest 環境の構築
  - moto（AWS モック）の設定
  - AgentCore ローカルテスト環境の構築
  - MCP Server テスト用モック設定
  - 単体テスト・統合テスト・E2E テスト用ディレクトリ構造の作成
  - 基本的なテスト設定ファイルの作成
  - _Requirements: テスト基盤_

### Phase 2: データ基盤とコア機能

- [ ] 4. データモデルと DynamoDB 基盤の実装

  - DynamoDB テーブル設計の実装とテスト
  - 基本的なデータモデル（Question、Delivery、UserResponse）の実装
  - DynamoDB クライアントとリポジトリパターンの実装
  - 問題データの CRUD 操作実装
  - 単体テストによる動作確認
  - _Requirements: 3.6, 5.6, 6.3_

- [ ] 5. キャッシュシステムの実装
  - DynamoDB TTL ベースキャッシュテーブルの作成
  - Lambda メモリキャッシュクラスの実装
  - ServerlessCacheManager クラスの実装
  - キャッシュ機能の単体テスト作成
  - _Requirements: 3.1, 3.2, 4.4_

### Phase 3: マルチエージェントシステムのコア機能

- [ ] 6. MCP 統合と AWS 情報取得エージェントの実装

  - MCP Client ライブラリの統合（Strands Agents 対応）
  - AWS Documentation MCP Server との連携実装（uvx 起動方式）
  - AWS Knowledge MCP Server との連携実装（uvx 起動方式）
  - AWS 情報取得エージェント（@tool）の実装とテスト
  - ストリーミング対応による処理状況通知機能
  - _Requirements: 3.1, 3.2, 4.2, 4.4, 4.5_

- [ ] 7. 問題生成エージェントの実装

  - 問題生成エージェント（@tool）の基本構造実装
  - LLM クライアント（Amazon Bedrock）の統合
  - Agent-as-Tools パターンによる監督者エージェントとの連携
  - 問題文・選択肢・解説生成ロジックの実装
  - ストリーミング対応による生成状況のリアルタイム配信
  - _Requirements: 3.2, 3.3, 3.4, 3.5_

- [ ] 8. 品質管理エージェントと監督者エージェントの実装
  - 品質管理エージェント（@tool）の実装
  - 監督者エージェントによるマルチエージェント統合
  - キーワードベース類似度チェック機能の実装
  - 品質基準検証ロジックの実装
  - 複数モデル対応による分間クォータ対策
  - 再生成機能とエラーハンドリングの実装
  - _Requirements: 3.7, 5.1, 5.2, 5.3, 5.6, 6.5_

### Phase 4: AgentCore Runtime と API Gateway 連携

- [ ] 9. AgentCore Runtime メインエージェントの実装

  - AgentCore Runtime 用メインエージェント（agent_main.py）作成
  - 監督者エージェントによるマルチエージェント統合
  - ストリーミング対応によるリアルタイム処理状況配信
  - エラーハンドリングとログ出力の実装
  - AgentCore ローカルテスト実行
  - _Requirements: 3.6, 6.4_

- [ ] 10. API Gateway + Lambda による外部連携の実装

  - API Gateway REST API の設定
  - Lambda 関数による AgentCore Runtime 呼び出し
  - Power Automate Webhook 呼び出し機能の実装
  - Teams 投稿データフォーマット機能の実装
  - EventBridge スケジュール連携の実装
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 6.1, 6.2, 6.3, 6.4_

- [ ] 11. 問題配信システムの統合実装
  - EventBridge → API Gateway → AgentCore Runtime → Teams の統合フロー実装
  - 配信結果の記録機能の実装
  - AgentCore オブザーバビリティ + CloudWatch による配信ログ記録
  - 統合テストによる全体フロー確認
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

### Phase 5: ハイブリッドデプロイとインフラ

- [ ] 12. AgentCore Runtime デプロイ設定

  - requirements.txt の作成（strands-agents、bedrock-agentcore、uv）
  - agentcore configure による設定ファイル生成
  - IAM ロールと権限設定の自動作成確認
  - ECR リポジトリの自動作成確認
  - agentcore launch によるデプロイ実行
  - _Requirements: 6.1, 6.4_

- [ ] 13. API Gateway + Lambda インフラとデプロイ設定
  - API Gateway REST API 用 SAM テンプレート作成
  - Lambda 関数と API Gateway の定義
  - DynamoDB テーブル定義の実装
  - EventBridge スケジュール設定の実装
  - IAM ロールと権限設定（AgentCore 呼び出し権限含む）
  - デプロイスクリプト（deploy-hybrid.sh）の作成
  - GitHub Actions ワークフロー（ハイブリッド対応）の実装
  - _Requirements: 6.4_

### Phase 6: Teams 統合と E2E テスト

- [ ] 14. Power Automate フローの設定と連携テスト

  - Power Automate フロー定義の作成
  - Teams 投稿テンプレートの実装
  - リアクション自動追加機能の設定
  - 解答公開フローの実装
  - Teams 連携の動作確認
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 2.4, 2.5_

- [ ] 15. 回答集計と統計分析機能の実装

  - リアクション収集機能の実装
  - 回答統計計算ロジックの実装
  - 参加状況分析機能の実装
  - 統計データの保存と取得機能の実装
  - 統計機能の単体テスト作成
  - _Requirements: 2.1, 2.2, 2.3, 6.3_

- [ ] 16. E2E テストスイートの実装
  - Playwright E2E テスト環境の構築
  - 問題生成から配信までの E2E テスト実装
  - Teams UI 操作のテスト実装
  - 回答収集と統計表示のテスト実装
  - CI/CD パイプラインでの E2E テスト実行設定
  - _Requirements: 全要件の統合テスト_

## Phase 2 拡張機能（将来実装）

以下の機能は、MVP 完了後の Phase 2 で実装を検討します：

- [ ] 17. Amazon Bedrock Citations API 統合

  - Citations API クライアントの実装
  - 引用元情報を含む解説生成機能
  - 品質検証プロセスへの統合
  - _Requirements: 5.2, 5.4_

- [ ] 18. 管理者通知システム

  - 品質基準未達時の通知機能実装
  - 管理者ダッシュボード機能
  - 通知設定管理機能
  - _Requirements: 5.5_

- [ ] 19. 高度な品質管理機能
  - 品質スコア詳細化
  - 品質トレンド分析機能
  - A/B テスト機能
  - _Requirements: 5.1, 5.2, 5.3_

## AgentCore 開発環境セットアップの詳細

### 必要なツール一覧

#### 1. AWS CLI

```bash
# インストール確認
aws --version

# プロファイル設定確認
aws configure list
aws sts get-caller-identity
```

#### 2. bedrock-agentcore-starter-toolkit

```bash
# インストール
pip install bedrock-agentcore-starter-toolkit

# 確認
agentcore --version
```

#### 3. uv と uvx（MCP Server 用）

```bash
# uv インストール（Python パッケージ管理）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 確認
uv --version
uvx --version
```

#### 4. MCP Server 動作確認

```bash
# AWS Documentation MCP Server
uvx awslabs.aws-documentation-mcp-server

# AWS Knowledge MCP Server
uvx awslabs.aws-knowledge-mcp-server
```

#### 5. VS Code 拡張機能

- AWS Toolkit for Visual Studio Code
- Python Extension
- YAML Support

### 設定ファイル例

#### pyproject.toml (AgentCore 対応)

```toml
[project]
name = "aws-exam-agent"
version = "0.1.0"
requires-python = ">=3.12"

dependencies = [
    "strands-agents>=1.0.0",
    "bedrock-agentcore>=1.0.0",
    "boto3>=1.34.0",
    "pydantic>=2.0.0",
]

[tool.uv]
dev-dependencies = [
    "pytest>=7.0.0",
    "moto>=4.0.0",
    "ruff>=0.1.0",
    "bedrock-agentcore-starter-toolkit>=1.0.0",
]
```

#### app/agentcore/docker/requirements.txt

```txt
strands-agents
bedrock-agentcore
uv
```

## 実装時の注意事項

### コーディング規約の遵守

- [Python コーディング規約](../../steering/python-coding-standards.md)に従った実装
- [TypeScript コーディング規約](../../steering/typescript-coding-standards.md)に従った E2E テスト実装

### テスト戦略

- 各タスクで単体テストを先に作成（TDD）
- 統合テストで複数コンポーネントの連携確認
- E2E テストで全体フローの動作確認

### 設計書参照

各タスク実装時は以下の設計書を参照：

- [システム概要](design/01-overview.md)
- [アーキテクチャ](design/02-architecture.md)
- [AI エンジン](design/03-ai-engine.md)
- [Teams 連携](design/04-teams-integration.md)
- [データモデル](design/05-data-models.md)
- [デプロイ](design/06-deployment.md)
- [エラーハンドリング](design/07-error-handling.md)
- [テスト戦略](design/08-testing.md)

### 品質確保

- 各タスク完了時にテスト実行
- コードレビューの実施
- 設計書との整合性確認
- 要件定義との対応確認
