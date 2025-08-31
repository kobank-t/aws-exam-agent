# Implementation Plan

## 概要

この実装計画は、AWS Exam Agent の問題生成から Teams 投稿までの完全なフローを実装することを目的としています。垂直スライス開発により、最小限の機能で動く価値を早期提供し、段階的に機能を拡張していきます。

> **📍 プロジェクト構造**: [README.md - プロジェクト構造](../../../README.md#-プロジェクト構造) を参照

## 実装方針

### アジャイル開発アプローチ

- **価値優先**: 技術的完璧性より、ユーザー価値の早期提供を重視
- **反復改善**: 小さなリリースを繰り返し、フィードバックを基に改善
- **品質とスピード**: 品質を妥協せず、効率的な開発プロセスを追求
- **チーム協働**: 透明性の高いコミュニケーションと知識共有

### 技術選択の基準

- **AWS ネイティブ**: AWS サービスとの親和性を重視
- **運用性**: 監視、ログ、デバッグの容易さを考慮
- **拡張性**: 将来の機能追加に対応できる柔軟な設計
- **コスト効率**: 開発・運用コストの最適化

## タスクリスト

### Phase 0: 完了済み環境セットアップ

- [x] 1. Python 開発環境のセットアップ

  **完了基準**:

  - `uv run python --version` で Python 3.12 確認
  - `uv run pytest tests/unit/shared/ -v` で共通モジュールテスト通過
  - `uv run ruff check app/ tests/` でリンターエラー 0 件
  - `uv run mypy app/ tests/` で型チェックエラー 0 件
  - IDE 上でエラー表示ゼロ（精神衛生上必須）

  **実装内容**:

  - Python 3.12 環境の構築
  - uv パッケージマネージャーの導入
  - 開発ツール（Ruff, Mypy）の設定
  - VS Code 設定の最適化

  **サブタスク**:

  - [x] 1.1 プロジェクト構造の作成（AgentCore 中心設計）
  - [x] 1.2 uv 環境と pyproject.toml の設定
  - [x] 1.3 依存関係の定義（利用可能なパッケージのみ）
  - [x] 1.4 開発ツール設定（Ruff、Mypy、pre-commit、VS Code 設定品質保証）

  _Requirements: Requirement 1, 2, 3 の基盤_

- [x] 2. AgentCore 開発環境のセットアップ

  **完了基準**:

  - `aws sts get-caller-identity` で AWS 認証確認（JSON レスポンス取得）
  - `agentcore configure list` で設定ファイル認識確認（エージェント設定表示）
  - `uv run python -c "from strands import Agent; print('strands imported successfully')"` で strands インポート確認
  - `uv run python app/agentcore/agent_main.py` で SupervisorAgent 実行（exit code 0 + 期待ログ出力）
  - `uv run pytest tests/unit/agentcore/test_agent_main.py -v` で AgentCore エージェントテスト通過

  **実装内容**:

  - AWS CLI の設定とプロファイル確認
  - bedrock-agentcore-starter-toolkit のインストール
  - Strands Agents フレームワークの統合
  - MCP（Model Context Protocol）統合基盤の構築

  **サブタスク**:

  - [x] 2.1 AWS CLI 設定とプロファイル確認
  - [x] 2.2 bedrock-agentcore-starter-toolkit インストールと設定
  - [x] 2.3 strands の正しいインポート方法確認・実行（from strands import Agent）
  - [x] 2.4 pyproject.toml に AgentCore 関連依存関係追加（MCP 関連含む）
  - [x] 2.5 基本的なエージェント実装（agent_main.py の作成）

  _Requirements: Requirement 1 (AI 問題生成機能)_

### Phase 1: シンプル化とリファクタリング

- [x] 3. 不要コードの削除とシンプル化

  **完了基準**:

  - 不要なコードとファイルの削除完了
  - コード構造の簡素化完了
  - `uv run ruff check app/ tests/` でリンターエラー 0 件
  - `uv run mypy app/ tests/` で型チェックエラー 0 件

  **実装内容**:

  - 不要なコードとファイルの削除
  - コード構造の簡素化
  - 依存関係の最適化
  - テストカバレッジの向上

  **サブタスク**:

  - [x] 3.1 不要なファイル・ディレクトリの特定と削除
  - [x] 3.2 `agent_sample.py` を `app/agentcore/agent_main.py` にリファクタリング
  - [x] 3.3 最小限の依存関係に整理（pyproject.toml 更新）
  - [x] 3.4 不要なテストファイルの削除
  - [x] 3.5 品質チェック実行・修正

  _Requirements: 全要件の実装効率化_

- [x] 4. AgentCore デプロイ設定

  **完了基準**:

  - `app/agentcore/requirements.txt` 作成完了（最小限の依存関係）
  - `agentcore configure` で設定ファイル生成（agentcore.yaml 存在確認）
  - `agentcore launch` で AWS 環境デプロイ（デプロイ完了ログ出力確認）
  - `curl -X POST <AgentCore Endpoint>/invoke` で API 動作確認（HTTP 200 レスポンス）
  - 実際の問題生成が AWS 環境で動作

  **実装内容**:

  - requirements.txt の最小化
  - agentcore configure による設定ファイル生成
  - AWS 環境でのデプロイと動作確認

  **サブタスク**:

  - [x] 4.1 requirements.txt の最小化（agent_main.py で使用する依存関係のみ）
  - [x] 4.2 agentcore configure による設定ファイル生成
  - [x] 4.3 agentcore launch によるデプロイ実行
  - [x] 4.4 AWS 環境での動作確認・テスト

  _Requirements: Requirement 1 (AI 問題生成機能)_

- [x] 5. Teams 連携の基本実装

  **完了基準**:

  - Power Automate フロー作成完了（Webhook 受信 → Teams 投稿）
  - AgentCore → Webhook 呼び出し機能実装完了
  - 実際の Teams チャネルに問題が投稿される
  - 手動トリガーでの完全フロー動作確認
  - 実際のユーザーでの動作確認とフィードバック収集

  **実装内容**:

  - Power Automate フローの作成
  - Teams チャネルとの連携設定
  - Adaptive Card による問題表示の実装
  - エラーハンドリングの追加

  **サブタスク**:

  - [x] 5.1 Power Automate フロー設定（基本的な Webhook → Teams 投稿）
  - [x] 5.2 AgentCore エンドポイントからの Webhook 呼び出し実装
  - [x] 5.3 Teams 投稿テンプレートの実装（問題・選択肢・解説の整形）
  - [x] 5.4 実際の Teams チャネルでの動作確認
  - [x] 5.5 EventBridge Scheduler 定期実行機能の実装

  _Requirements: Requirement 2 (Teams 投稿・データ登録機能), Requirement 3 (定期実行機能)_

---

**作成日**: 2025 年 8 月 3 日  
**最終更新**: 2025 年 8 月 26 日  
**ステータス**: 進行中
