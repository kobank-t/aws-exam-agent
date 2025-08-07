# Implementation Plan

## 概要

この実装計画は、Strands Agents フレームワークと AWS Bedrock AgentCore を活用した AWS Exam Agent の設計書に基づいて、テスト駆動開発（TDD）アプローチで段階的に機能を実装するためのタスクリストです。各タスクは独立して実行可能で、前のタスクの成果物を活用して次のタスクに進む構成になっています。

## 実装方針

- **AgentCore 中心**: メイン処理を AgentCore Runtime で実行
- **マルチエージェント**: Agent-as-Tools パターンによる専門エージェント連携
- **MCP 統合**: Model Context Protocol による標準化されたコンテキスト提供
- **受け入れテスト駆動開発**: 各タスクに受け入れテスト必須、100%通過で完了
- **段階的実装**: 小さな単位で機能を実装し、早期に動作確認
- **技術的負債ゼロ**: 受け入れテスト未通過での次タスク進行禁止
- **ストリーミング対応**: リアルタイム処理状況監視
- **品質管理統一**: 全タスクで `uv run ruff check app/ tests/` + `uv run mypy app/ tests/` + IDE エラー表示ゼロを必須とする

## 現在の状況

- **完了済み**: 要件定義、設計書（9 ファイル分割）、コーディング規約
- **更新完了**: Strands & AgentCore ハンズオン知見の反映
- **現在フェーズ**: 実装フェーズ開始準備完了
- **コードベース**: 未実装（README.md、WORK_LOG.md、設計書のみ存在）
- **次回開始**: タスク 1（Python 開発環境セットアップ）から実装開始

## タスクリスト

### Phase 1: 環境セットアップ

- [x] 1. Python 開発環境のセットアップ

  **完了基準**:

  - `uv run python --version` で Python 3.12 確認
  - `uv run pytest tests/unit/test_shared/ -v` で共通モジュールテスト通過
  - `uv run ruff check app/ tests/` でリンターエラー 0 件
  - `uv run mypy app/ tests/` で型チェックエラー 0 件
  - IDE 上でエラー表示ゼロ（精神衛生上必須）
  - VS Code 設定の品質保証（廃止設定削除、新形式対応）

  **サブタスク**:

  - [x] 1.1 プロジェクト構造の作成（AgentCore 中心設計）
  - [x] 1.2 uv 環境と pyproject.toml の設定
  - [x] 1.3 依存関係の定義（利用可能なパッケージのみ）
  - [x] 1.4 開発ツール設定（Ruff、Mypy、pre-commit、VS Code 設定品質保証）
  - [x] 1.5 共通モジュール（config, constants, exceptions）の実装
  - [x] 1.6 共通モジュールの単体テスト作成・実行

  _Requirements: 全体の基盤_

- [ ] 2. AgentCore 開発環境のセットアップ

  **完了基準**:

  - `aws sts get-caller-identity` で AWS 認証確認
  - `agentcore --version` で AgentCore CLI 動作確認
  - `uvx awslabs.aws-documentation-mcp-server --help` で MCP Server 動作確認
  - `agentcore configure` で設定ファイル生成成功
  - `uv run python app/agentcore/docker/agent_main.py` で strands_agents 動作確認
  - `uv run pytest tests/unit/test_agentcore_config/ -v` で AgentCore 設定テスト通過
  - pyproject.toml に strands_agents、bedrock-agentcore 依存関係追加完了

  **サブタスク**:

  - [ ] 2.1 AWS CLI 設定とプロファイル確認
  - [ ] 2.2 bedrock-agentcore-starter-toolkit インストールと設定
  - [ ] 2.3 strands_agents の正しいインストール方法確認・実行
  - [ ] 2.4 pyproject.toml に AgentCore 関連依存関係追加
  - [ ] 2.5 MCP Server 環境構築（uvx、uv インストール）
  - [ ] 2.6 AWS Documentation MCP Server 動作確認
  - [ ] 2.7 AWS Knowledge MCP Server 動作確認
  - [ ] 2.8 agent_main.py の動作確認（strands_agents インポート成功）
  - [ ] 2.9 AgentCore 設定クラスの実装・テスト作成

  _Requirements: AgentCore 基盤、MCP 統合_

- [ ] 3. テスト環境のセットアップ

  **完了基準**:

  - `uv run pytest tests/unit/ -v` で全単体テスト通過
  - `uv run pytest tests/integration/ -v` で統合テスト通過
  - moto を使用した AWS モックテストの動作確認
  - `uv run python app/agentcore/docker/agent_main.py --test` で AgentCore ローカル実行成功

  **サブタスク**:

  - [ ] 3.1 pytest 環境の構築（conftest.py, pytest.ini 設定）
  - [ ] 3.2 moto（AWS モック）の設定・テスト作成
  - [ ] 3.3 AgentCore ローカルテスト環境の構築
  - [ ] 3.4 基本的な統合テストの作成・実行

  _Requirements: テスト基盤_

### Phase 2: データ基盤とコア機能

- [ ] 4. データモデルと DynamoDB 基盤の実装

  **完了基準**:

  - `uv run pytest tests/unit/test_models/ -v` でデータモデルテスト通過
  - `uv run pytest tests/unit/test_repositories/ -v` でリポジトリテスト通過
  - `uv run pytest tests/integration/test_dynamodb/ -v` で DynamoDB 統合テスト通過
  - moto 使用の DynamoDB モックテストで全 CRUD 操作確認

  **サブタスク**:

  - [ ] 4.1 DynamoDB テーブル設計の実装（SAM テンプレート）
  - [ ] 4.2 Pydantic データモデル（Question、Delivery、UserResponse）の実装
  - [ ] 4.3 DynamoDB クライアントとリポジトリパターンの実装
  - [ ] 4.4 データモデル・リポジトリの単体テスト作成
  - [ ] 4.5 DynamoDB 統合テスト作成（moto 使用）

  _Requirements: 3.6, 5.6, 6.3_

- [ ] 5. キャッシュシステムの実装

  **完了基準**:

  - `uv run pytest tests/unit/test_cache/ -v` でキャッシュクラステスト通過
  - `uv run pytest tests/integration/test_cache_system/ -v` で 2 層キャッシュ統合テスト通過
  - moto 使用の DynamoDB TTL テーブル動作確認
  - メモリキャッシュの期限切れ・LRU 動作確認

  **サブタスク**:

  - [ ] 5.1 DynamoDB TTL ベースキャッシュテーブル設計・実装
  - [ ] 5.2 Lambda メモリキャッシュクラスの実装
  - [ ] 5.3 ServerlessCacheManager クラスの実装
  - [ ] 5.4 キャッシュシステムの単体・統合テスト作成

  _Requirements: 3.1, 3.2, 4.4_

### Phase 3: マルチエージェントシステムのコア機能

- [ ] 6. MCP 統合と AWS 情報取得エージェントの実装

  **完了基準**:

  - `uvx awslabs.aws-documentation-mcp-server --help` で MCP Server 動作確認
  - `uv run pytest tests/unit/test_mcp/ -v` で MCP 統合テスト通過
  - `uv run pytest tests/unit/test_agents/test_aws_info_agent.py -v` でエージェントテスト通過
  - 実際の MCP Server 接続・データ取得の動作確認

  **サブタスク**:

  - [ ] 6.1 MCP Client ライブラリの統合（Strands Agents 対応）
  - [ ] 6.2 AWS Documentation MCP Server との連携実装（uvx 起動方式）
  - [ ] 6.3 AWS Knowledge MCP Server との連携実装（uvx 起動方式）
  - [ ] 6.4 AWS 情報取得エージェント（@tool）の実装
  - [ ] 6.5 MCP 統合・エージェントの単体テスト作成
  - [ ] 6.6 ストリーミング対応による処理状況通知機能

  _Requirements: 3.1, 3.2, 4.2, 4.4, 4.5_

- [ ] 7. 問題生成エージェントの実装

  **完了基準**:

  - `uv run pytest tests/unit/test_agents/test_question_gen_agent.py -v` でエージェントテスト通過
  - `uv run pytest tests/unit/test_bedrock/ -v` で Bedrock 統合テスト通過
  - moto 使用の Bedrock API モックテストで問題生成確認
  - 実際の Claude API での問題生成動作確認（手動テスト）

  **サブタスク**:

  - [ ] 7.1 Bedrock Claude モデルとの統合実装
  - [ ] 7.2 問題生成プロンプトエンジニアリング
  - [ ] 7.3 問題生成エージェント（@tool）の実装
  - [ ] 7.4 Bedrock 統合・エージェントの単体テスト作成
  - [ ] 7.5 ストリーミング生成対応の実装

  _Requirements: 3.2, 3.3, 3.4, 3.5_

- [ ] 8. 品質管理エージェントと監督者エージェントの実装

  **完了基準**:

  - `uv run pytest tests/unit/test_agents/ -v` で全エージェントテスト通過
  - `uv run pytest tests/integration/test_multi_agent/ -v` でマルチエージェント統合テスト通過
  - `uv run python app/agentcore/docker/agent_main.py` でローカル実行成功
  - 品質評価・類似度チェック・再生成機能の動作確認

  **サブタスク**:

  - [ ] 8.1 品質管理エージェント（@tool）の実装
  - [ ] 8.2 監督者エージェントによるマルチエージェント統合
  - [ ] 8.3 キーワードベース類似度チェック機能の実装
  - [ ] 8.4 品質基準検証ロジックの実装
  - [ ] 8.5 複数モデル対応による分間クォータ対策
  - [ ] 8.6 再生成機能とエラーハンドリングの実装
  - [ ] 8.7 全エージェントの単体・統合テスト作成

  _Requirements: 3.7, 5.1, 5.2, 5.3, 5.6, 6.5_

### Phase 4: AgentCore Runtime と API Gateway 連携

- [ ] 9. AgentCore Runtime メインエージェントの実装

  **完了基準**:

  - `uv run python app/agentcore/docker/agent_main.py` でローカル実行成功
  - `agentcore configure` で設定ファイル生成成功
  - `agentcore launch` で AWS 環境デプロイ成功（手動確認）
  - AgentCore エンドポイントでの問題生成 API 動作確認

  **サブタスク**:

  - [ ] 9.1 AgentCore Runtime 用メインエージェント（agent_main.py）完成
  - [ ] 9.2 監督者エージェントによるマルチエージェント統合
  - [ ] 9.3 ストリーミング対応によるリアルタイム処理状況配信
  - [ ] 9.4 エラーハンドリングとログ出力の実装
  - [ ] 9.5 AgentCore 設定ファイル・requirements.txt 作成
  - [ ] 9.6 ローカル・AWS 環境での動作確認

  _Requirements: 3.6, 6.4_

- [ ] 10. API Gateway + Lambda による外部連携の実装

  **完了基準**:

  - `sam build && sam deploy` でインフラデプロイ成功
  - `curl <API Gateway URL>` で API 動作確認
  - `uv run pytest tests/unit/test_lambda/ -v` で Lambda 関数テスト通過
  - EventBridge スケジュール実行の動作確認（手動テスト）

  **サブタスク**:

  - [ ] 10.1 SAM テンプレートで API Gateway REST API 設定
  - [ ] 10.2 Lambda 関数による AgentCore Runtime 呼び出し実装
  - [ ] 10.3 Power Automate Webhook 呼び出し機能の実装
  - [ ] 10.4 Teams 投稿データフォーマット機能の実装
  - [ ] 10.5 EventBridge スケジュール連携の実装
  - [ ] 10.6 Lambda 関数の単体テスト作成

  _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 6.1, 6.2, 6.3, 6.4_

- [ ] 11. 問題配信システムの統合実装

  **完了基準**:

  - EventBridge → API Gateway → AgentCore → Teams の全フロー動作確認（手動テスト）
  - `uv run pytest tests/integration/test_delivery_system/ -v` で統合テスト通過
  - CloudWatch Logs で配信ログ記録確認
  - 実際の Teams チャネルでの問題投稿・リアクション確認

  **サブタスク**:

  - [ ] 11.1 EventBridge → API Gateway → AgentCore Runtime → Teams の統合フロー実装
  - [ ] 11.2 配信結果の記録機能の実装（CloudWatch Logs）
  - [ ] 11.3 エンドツーエンド統合テスト作成
  - [ ] 11.4 全体フローの手動テスト・動作確認

  _Requirements: 6.1, 6.2, 6.3, 6.4_

### Phase 5: ハイブリッドデプロイとインフラ

- [ ] 12. AgentCore Runtime デプロイ設定

  **完了基準**:

  - `agentcore configure` で設定ファイル生成成功
  - `agentcore launch` で AWS 環境デプロイ成功
  - `aws iam list-roles | grep agentcore` で IAM ロール作成確認
  - `aws ecr describe-repositories` で ECR リポジトリ作成確認
  - AgentCore エンドポイントでの API 動作確認

  **サブタスク**:

  - [ ] 12.1 requirements.txt の作成（実際に利用可能な依存関係）
  - [ ] 12.2 agentcore configure による設定ファイル生成・確認
  - [ ] 12.3 agentcore launch によるデプロイ実行
  - [ ] 12.4 IAM ロールと権限設定の自動作成確認
  - [ ] 12.5 ECR リポジトリの自動作成確認
  - [ ] 12.6 デプロイ後の動作確認・テスト

  _Requirements: 6.1, 6.4_

- [ ] 13. API Gateway + Lambda インフラとデプロイ設定

  **完了基準**:

  - `sam validate` で SAM テンプレート構文確認
  - `sam build && sam deploy` でインフラデプロイ成功
  - `./scripts/deploy-hybrid.sh` でハイブリッドデプロイ成功
  - GitHub Actions ワークフローで CI/CD 実行成功
  - 全インフラリソースの作成・動作確認

  **サブタスク**:

  - [ ] 13.1 API Gateway REST API 用 SAM テンプレート作成
  - [ ] 13.2 Lambda 関数と API Gateway の定義
  - [ ] 13.3 DynamoDB テーブル定義の実装
  - [ ] 13.4 EventBridge スケジュール設定の実装
  - [ ] 13.5 IAM ロールと権限設定（AgentCore 呼び出し権限含む）
  - [ ] 13.6 デプロイスクリプト（deploy-hybrid.sh）の作成
  - [ ] 13.7 GitHub Actions ワークフロー（ハイブリッド対応）の実装

  _Requirements: 6.4_

### Phase 6: Teams 統合と E2E テスト

- [ ] 14. Power Automate フローの設定と連携テスト

  **完了基準**:

  - Power Automate フローの作成・実行成功（手動確認）
  - 実際の Teams チャネルでの問題投稿確認
  - リアクション絵文字（🅰️🅱️🇨🇩）の自動追加確認
  - 解答公開フローの動作確認
  - Teams Webhook URL での投稿・レスポンス確認

  **サブタスク**:

  - [ ] 14.1 Power Automate フロー定義の作成
  - [ ] 14.2 Teams 投稿テンプレートの実装
  - [ ] 14.3 リアクション自動追加機能の設定
  - [ ] 14.4 解答公開フローの実装
  - [ ] 14.5 実際の Teams チャネルでの動作確認・テスト

  _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 2.4, 2.5_

- [ ] 15. 回答集計と統計分析機能の実装

  **完了基準**:

  - `uv run pytest tests/unit/test_analytics/ -v` で統計分析テスト通過
  - `uv run pytest tests/integration/test_reaction_collection/ -v` で統合テスト通過
  - 実際の Teams リアクションデータでの集計動作確認
  - 統計 API エンドポイントでのデータ取得確認

  **サブタスク**:

  - [ ] 15.1 リアクション収集機能の実装
  - [ ] 15.2 回答統計計算ロジックの実装
  - [ ] 15.3 参加状況分析機能の実装
  - [ ] 15.4 統計データの保存と取得 API 実装
  - [ ] 15.5 統計分析機能の単体・統合テスト作成

  _Requirements: 2.1, 2.2, 2.3, 6.3_

- [ ] 16. E2E テストスイートの実装

  **完了基準**: `tests/acceptance/test_task_16_completion.py` の全テストが通ること

  **サブタスク**:

  - [ ] 16.1 Playwright E2E テスト環境の構築
    - 検証: E2E テスト環境セットアップ・実行テスト成功
  - [ ] 16.2 問題生成から配信までの E2E テスト実装
    - 検証: 全体フローの自動テスト成功
  - [ ] 16.3 Teams UI 操作のテスト実装
    - 検証: Teams インターフェース操作テスト成功
  - [ ] 16.4 回答収集と統計表示のテスト実装
    - 検証: 回答処理・統計表示の自動テスト成功
  - [ ] 16.5 CI/CD パイプラインでの E2E テスト実行設定
    - 検証: 自動化パイプラインでのテスト実行成功

  _Requirements: 全要件の統合テスト_

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

#### 3. strands_agents の正しいインストール

```bash
# 方法1: PyPI からのインストール（推奨）
uv add strands-agents

# 方法2: 開発版インストール（必要に応じて）
uv add git+https://github.com/strands-ai/strands-agents.git

# 方法3: bedrock-agentcore-starter-toolkit に含まれる場合
# agentcore configure 実行時に自動インストールされる可能性を確認

# インストール確認
uv run python -c "from strands_agents import Agent; print('strands_agents installed successfully')"
```

#### 4. pyproject.toml 依存関係更新

```toml
# 追加すべき依存関係
dependencies = [
    # 既存の依存関係...

    # AgentCore 関連
    "strands-agents>=1.0.0",
    "bedrock-agentcore>=1.0.0",

    # MCP 関連（必要に応じて）
    "mcp-client>=1.0.0",
]
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

#### agent_main.py 動作確認手順

```bash
# 1. strands_agents インポート確認
uv run python -c "from strands_agents import Agent, tool; print('Import successful')"

# 2. agent_main.py 基本動作確認
uv run python app/agentcore/docker/agent_main.py

# 3. 期待される出力例
# INFO:__main__:Initializing Supervisor Agent
# INFO:__main__:Supervisor Agent initialized successfully
# INFO:__main__:Starting question generation flow: topic=EC2, difficulty=intermediate
# INFO:__main__:Execution result: {'status': 'success', ...}

# 4. エラーが発生した場合の対処
# - ImportError: strands_agents が見つからない → インストール方法を再確認
# - ModuleNotFoundError: bedrock_agentcore → bedrock-agentcore-starter-toolkit の再インストール
# - その他のエラー → 依存関係の不足を確認
```

## 実装時の注意事項

### 品質管理の継続性保証

**全タスク共通の必須チェック項目**（セッション継続時の漏れ防止）:

- [ ] `uv run ruff check app/ tests/` でエラー 0 件
- [ ] `uv run mypy app/ tests/` でエラー 0 件
- [ ] IDE 上でエラー表示ゼロ（精神衛生上必須）
- [ ] VS Code 設定の品質保証（廃止設定なし、新形式対応）
- [ ] テストコードも本番コードと同等の型チェック基準適用
- [ ] 外部ライブラリの型チェック無視設定が適切に設定済み

**品質劣化の防止策**:

- 新しいセッション開始時は必ず上記チェック項目を確認
- タスク完了時は必ず品質メトリクス 100%達成を確認
- 「テストだから緩くても良い」という考えを排除

### コーディング規約の遵守

- [Python コーディング規約](../../steering/python-coding-standards.md)に従った実装
- [TypeScript コーディング規約](../../steering/typescript-coding-standards.md)に従った E2E テスト実装
- [開発環境設定規約](../../steering/development-environment-standards.md)の厳格な遵守

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
