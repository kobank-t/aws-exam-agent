# Implementation Plan - シンプル化版

## 概要

この実装計画は、実証済みの `agent_main.py` を起点として、最小限の機能で動く価値を早期提供することを目的としています。複雑な基盤構築は後回しにし、問題生成 → Teams 投稿の直線的なフローを最優先で実装します。

## 実装方針

### 🎯 シンプル化原則（2025 年 8 月 13 日更新）

- **実証済み機能の活用**: `agent_main.py` で動作確認済みの問題生成機能を中心に構築
- **最小限の実装**: DynamoDB、キャッシュ、品質検証システムは後回し
- **直線的フロー**: 問題生成 → Teams 投稿の単純な流れ
- **手動運用許容**: 最初は手動トリガーや手動操作を許容
- **早期価値提供**: 1 週間以内に実際の Teams で問題配信を実現

### 🔧 技術実装原則

- **AgentCore 中心**: 実証済みの BedrockAgentCore アプリケーション活用
- **MCP 統合**: AWS Documentation MCP Server による技術的正確性確保
- **品質維持**: 基本的な品質チェック（ruff, mypy）は継続
- **段階的拡張**: 動く基盤ができてから機能追加

## 現在の状況

- **実証完了**: `agent_main.py` で AWS Professional レベル問題生成確認済み
- **次のステップ**: シンプル化と AgentCore デプロイ
- **目標**: 1 週間以内に Teams 投稿まで実現

## タスクリスト

### Phase 0: 完了済み環境セットアップ

- [x] 1. Python 開発環境のセットアップ

  **完了基準**:

  - `uv run python --version` で Python 3.12 確認
  - `uv run pytest tests/unit/shared/ -v` で共通モジュールテスト通過
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

- [x] 2. AgentCore 開発環境のセットアップ

  **完了基準**:

  - `aws sts get-caller-identity` で AWS 認証確認（JSON レスポンス取得）
  - `sam deploy` で AgentCore 事前リソースデプロイ成功（CloudFormation スタック作成確認）
  - `uv run yamllint infrastructure/agentcore-resources.yaml` で YAML 品質チェック通過（エラー 0 件）
  - `uv run cfn-lint infrastructure/agentcore-resources.yaml` で CloudFormation 構文チェック通過（エラー 0 件）
  - `agentcore configure list` で設定ファイル認識確認（エージェント設定表示）
  - `uv run python -c "from strands import Agent; print('strands imported successfully')"` で strands インポート確認（出力文字列一致）
  - `uv run python app/agentcore/agent_main.py` で SupervisorAgent 実行（exit code 0 + 期待ログ出力）
  - `uv run pytest tests/unit/agentcore/test_agent_main.py -v` で AgentCore エージェントテスト通過（全テスト PASSED）
  - `uv run ruff check app/ tests/` でリンターエラー 0 件
  - `uv run mypy app/ tests/` で型チェックエラー 0 件

  **サブタスク**:

  - [x] 2.1 AWS CLI 設定とプロファイル確認
  - [x] 2.2 bedrock-agentcore-starter-toolkit インストールと設定
  - [x] 2.3 strands の正しいインポート方法確認・実行（from strands import Agent）
  - [x] 2.4 pyproject.toml に AgentCore 関連依存関係追加（MCP 関連含む）
  - [x] 2.5 基本的なエージェント実装（agent_main.py の作成）
  - [x] 2.6 AgentCore 設定クラスの実装・テスト作成
  - [x] 2.7 AgentCore 事前リソースの作成（IAM ロール・ECR リポジトリ）
  - [x] 2.8 AgentCore configure による設定ファイル生成確認

  _Requirements: AgentCore 基盤、MCP 統合_

### Phase 1: シンプル化とリファクタリング

- [x] 3. 不要コードの削除とシンプル化

  **完了基準**:

  - 複雑な DynamoDB 関連コード削除完了
  - キャッシュシステム関連コード削除完了
  - 品質検証システム関連コード削除完了
  - `agent_sample.py` ベースの最小限構成に整理完了
  - `uv run ruff check app/ tests/` でリンターエラー 0 件
  - `uv run mypy app/ tests/` で型チェックエラー 0 件

  **サブタスク**:

  - [x] 3.1 不要なファイル・ディレクトリの特定と削除
  - [x] 3.2 `agent_sample.py` を `app/agentcore/agent_main.py` にリファクタリング
  - [x] 3.3 最小限の依存関係に整理（pyproject.toml 更新）
  - [x] 3.4 不要なテストファイルの削除
  - [x] 3.5 品質チェック実行・修正

  _Requirements: シンプル化による保守性向上_

- [ ] 4. AgentCore デプロイ設定

  **完了基準**:

  - `app/agentcore/requirements.txt` 作成完了（最小限の依存関係）
  - `agentcore configure` で設定ファイル生成（agentcore.yaml 存在確認）
  - `agentcore launch` で AWS 環境デプロイ（デプロイ完了ログ出力確認）
  - `curl -X POST <AgentCore Endpoint>/invoke` で API 動作確認（HTTP 200 レスポンス）
  - 実際の問題生成が AWS 環境で動作

  **サブタスク**:

  - [x] 4.1 requirements.txt の最小化（agent_main.py で使用する依存関係のみ）
  - [ ] 4.2 agentcore configure による設定ファイル生成
  - [ ] 4.3 agentcore launch によるデプロイ実行
  - [ ] 4.4 AWS 環境での動作確認・テスト
  - [ ] 4.5 エラー修正・再デプロイ

  _Requirements: AgentCore Runtime での問題生成機能_

- [ ] 5. Teams 連携の基本実装

  **完了基準**:

  - Power Automate フロー作成完了（Webhook 受信 → Teams 投稿）
  - AgentCore → Webhook 呼び出し機能実装完了
  - 実際の Teams チャネルに問題が投稿される
  - 手動トリガーでの完全フロー動作確認
  - 実際のユーザーでの動作確認とフィードバック収集

  **サブタスク**:

  - [ ] 5.1 Power Automate フロー設定（基本的な Webhook → Teams 投稿）
  - [ ] 5.2 AgentCore エンドポイントからの Webhook 呼び出し実装
  - [ ] 5.3 Teams 投稿テンプレートの実装（問題・選択肢・解説の整形）
  - [ ] 5.4 実際の Teams チャネルでの動作確認
  - [ ] 5.5 ユーザーフィードバック収集・改善

  _Requirements: 問題生成 → Teams 投稿の完全な価値提供_

## 将来実装（Phase 2）

以下の機能は、基本フローが動作してからの拡張として実装：

- [ ] 6. 自動スケジュール実行
- [ ] 7. 回答収集・統計分析
- [ ] 8. DynamoDB データ永続化
- [ ] 9. 高度な品質管理機能

_Requirements: 問題投稿 → 回答収集 → 統計表示の完全な価値提供_
