# Implementation Plan

## 概要

この実装計画は、AWS Exam Agent の設計書に基づいて、テスト駆動開発（TDD）アプローチで段階的に機能を実装するためのタスクリストです。各タスクは独立して実行可能で、前のタスクの成果物を活用して次のタスクに進む構成になっています。

## 実装方針

- **テスト駆動開発**: 各機能の実装前にテストを作成
- **段階的実装**: 小さな単位で機能を実装し、早期に動作確認
- **統合重視**: 各コンポーネントを段階的に統合
- **品質確保**: 各段階でのテスト実行と品質チェック

## タスクリスト

### Phase 1: 環境セットアップ

- [ ] 1. Python 開発環境のセットアップ

  - プロジェクト構造の作成（app/配下集約）
  - uv 環境と pyproject.toml の設定
  - 依存関係の定義（boto3、pydantic、pytest 等）
  - 開発ツール設定（Ruff、pre-commit、VS Code 設定）
  - 基本的なディレクトリ構造とファイル作成
  - _Requirements: 全体の基盤_

- [ ] 2. AWS 開発環境のセットアップ

  - AWS CLI 設定とプロファイル確認
  - AWS SAM CLI インストールと設定
  - bedrock-agentcore-starter-toolkit インストール
  - CloudFormation/SAM 用の linter・formatter 設定（cfn-lint、cfn-format）
  - AWS 認証情報とリージョン設定の確認
  - _Requirements: AWS インフラ基盤_

- [ ] 3. TypeScript/E2E テスト環境のセットアップ
  - Playwright 環境の構築
  - TypeScript コーディング規約の適用
  - E2E テスト用ディレクトリ構造の作成
  - 基本的なテスト設定ファイルの作成
  - _Requirements: E2E テスト基盤_

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

### Phase 3: 問題生成エージェントのコア機能

- [ ] 6. MCP 統合と AWS 情報取得サービスの実装

  - MCP Client ライブラリの統合
  - AWS Documentation MCP Server との連携実装
  - AWS Knowledge MCP Server との連携実装
  - 情報取得サービスクラスの実装とテスト
  - _Requirements: 3.1, 3.2, 4.2, 4.4_

- [ ] 7. 問題生成サービスのコア機能実装

  - QuestionGenerationService クラスの基本構造実装
  - LLM クライアント（Amazon Bedrock）の統合
  - 問題文生成ロジックの実装
  - 選択肢生成ロジックの実装
  - 解説生成ロジックの実装
  - _Requirements: 3.2, 3.3, 3.4, 3.5_

- [ ] 8. 品質管理システムの実装
  - QualityControlService クラスの実装
  - キーワードベース類似度チェック機能の実装
  - 品質基準検証ロジックの実装
  - 再生成機能の実装
  - 品質管理の単体テスト作成
  - _Requirements: 3.7, 5.1, 5.2, 5.3, 5.6_

### Phase 4: API 層と Teams 連携

- [ ] 9. Lambda 関数のメインハンドラー実装

  - API Gateway 統合用の Lambda 関数作成
  - リクエスト処理とレスポンス生成の実装
  - エラーハンドリングとログ出力の実装
  - 非同期処理対応の実装
  - Lambda 関数の統合テスト作成
  - _Requirements: 3.6, 6.4_

- [ ] 10. Teams 連携サービスの実装

  - TeamsIntegrationService クラスの実装
  - Power Automate Webhook 呼び出し機能の実装
  - Teams 投稿データフォーマット機能の実装
  - 配信結果の記録機能の実装
  - Teams 連携の単体テスト作成
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 6.1, 6.2, 6.3_

- [ ] 11. 問題配信システムの統合実装
  - 問題生成から配信までの統合フロー実装
  - EventBridge スケジュール連携の実装
  - 配信ログとエラーハンドリングの実装
  - 統合テストによる全体フロー確認
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

### Phase 5: インフラとデプロイ

- [ ] 12. AWS SAM テンプレートとインフラ定義

  - SAM テンプレート（template.yaml）の作成
  - DynamoDB テーブル定義の実装
  - Lambda 関数と API Gateway の定義
  - IAM ロールと権限設定の実装
  - EventBridge スケジュール設定の実装
  - _Requirements: 6.1, 6.4_

- [ ] 13. デプロイスクリプトと CI/CD 設定
  - デプロイスクリプト（deploy-agent.sh）の作成
  - GitHub Actions ワークフローの実装
  - 環境変数とシークレット管理の設定
  - 自動テスト実行の設定
  - デプロイメントテストの実行
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

## AWS 開発環境セットアップの詳細

### 必要なツール一覧

#### 1. AWS CLI

```bash
# インストール確認
aws --version

# プロファイル設定確認
aws configure list
aws sts get-caller-identity
```

#### 2. AWS SAM CLI

```bash
# インストール
brew install aws-sam-cli

# 確認
sam --version
```

#### 3. bedrock-agentcore-starter-toolkit

```bash
# インストール
pip install bedrock-agentcore-starter-toolkit

# 確認
agentcore --version
```

#### 4. CloudFormation/SAM 用ツール

```bash
# cfn-lint (CloudFormationテンプレートのlinter)
pip install cfn-lint

# cfn-format (CloudFormationテンプレートのformatter)
npm install -g cfn-format

# 確認
cfn-lint --version
cfn-format --version
```

#### 5. VS Code 拡張機能

- AWS Toolkit for Visual Studio Code
- CloudFormation Linter
- YAML Support

### 設定ファイル例

#### .vscode/settings.json (CloudFormation 用)

```json
{
  "yaml.schemas": {
    "https://raw.githubusercontent.com/awslabs/goformation/master/schema/sam.schema.json": "template.yaml"
  },
  "cfnLint.validateUsingJsonSchema": true,
  "cfnLint.format.enable": true
}
```

#### pyproject.toml (開発依存関係)

```toml
[tool.uv]
dev-dependencies = [
    "boto3>=1.34.0",
    "bedrock-agentcore-starter-toolkit>=1.0.0",
    "cfn-lint>=0.83.0",
    "aws-sam-cli>=1.100.0"
]
```

## 実装時の注意事項

### コーディング規約の遵守

- [Python コーディング規約](../../steering/python-coding-standards.md) に従った実装
- [TypeScript コーディング規約](../../steering/typescript-coding-standards.md) に従った E2E テスト実装

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
