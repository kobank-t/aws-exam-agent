# Implementation Plan

## 概要

この実装計画は、Strands Agents フレームワークと AWS Bedrock AgentCore を活用した AWS Exam Agent の設計書に基づいて、テスト駆動開発（TDD）アプローチで段階的に機能を実装するためのタスクリストです。各タスクは独立して実行可能で、前のタスクの成果物を活用して次のタスクに進む構成になっています。

## 実装方針

### 🎯 アジャイル開発原則（2025 年 8 月 11 日更新）

- **垂直スライス開発**: 水平レイヤー（データ層 → ビジネス層 →UI 層）ではなく、垂直機能（問題生成 →Teams 投稿 → 回答収集の完全フロー）を優先
- **動く価値の早期提供**: 各イテレーションで実際に使える完全な機能を実装
- **短いフィードバックサイクル**: 1-2 週間での価値提供とユーザーフィードバック収集
- **品質を保つ仕組み**: 品質基準維持（100%テスト通過、型チェック等）、CI/CD パイプライン、小さなコミット
- **継続的価値検証**: 動く機能の実装 → 実際のユーザーでの動作確認 → フィードバック収集 → 次イテレーションへの反映
- **既存実装の最大活用**: タスク 1-5 で実装済みの基盤（MCP 統合、AgentCore、データモデル、問題生成機能）を有効活用

### 🔧 技術実装原則

- **AgentCore 中心**: メイン処理を AgentCore Runtime で実行
- **マルチエージェント**: Agent-as-Tools パターンによる専門エージェント連携
- **MCP 統合**: Model Context Protocol による標準化されたコンテキスト提供
- **受け入れテスト駆動開発**: 各タスクに受け入れテスト必須、100%通過で完了
- **段階的実装**: 小さな単位で機能を実装し、早期に動作確認
- **技術的負債ゼロ**: 受け入れテスト未通過での次タスク進行禁止
- **ストリーミング対応**: リアルタイム処理状況監視
- **品質管理統一**: 全タスクで `./scripts/python-quality-check.sh` による統合品質チェック必須
- **インフラ品質管理**: CloudFormation テンプレート作成タスクで `./scripts/infrastructure-quality-check.sh` による統合品質チェック必須

## 現在の状況

- **完了済み**: 要件定義、設計書（9 ファイル分割）、コーディング規約、タスク 1-4（環境セットアップ・データ基盤）
- **実装済み基盤**: MCP 統合、AgentCore 基盤、データモデル、品質チェック体制（100%通過済み）
- **現在フェーズ**: 問題生成機能の先行実装・動作確認フェーズ
- **開発方針転換**: 2025 年 8 月 11 日にコア価値優先アプローチに変更
- **次回開始**: タスク 5（問題生成エージェントの先行実装・動作確認）から継続

## タスクリスト

### Phase 1: 環境セットアップ

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

- [x] 3. テスト環境のセットアップ

  **完了基準**:

  - `uv run pytest tests/unit/ -v` で全単体テスト通過（全テスト PASSED、エラー 0 件）
  - `uv run pytest tests/integration/ -v` で統合テスト通過（全テスト PASSED、エラー 0 件）
  - `uv run pytest -m unit` で単体テストのみ実行（マーカー分離確認）
  - `uv run pytest -m integration` で統合テストのみ実行（マーカー分離確認）
  - `uv run python app/agentcore/agent_main.py` で SupervisorAgent 実行（exit code 0）
  - `uv run ruff check app/ tests/` でリンターエラー 0 件
  - `uv run mypy app/ tests/` で型チェックエラー 0 件

  **サブタスク**:

  - [x] 3.1 pytest 環境の最適化（統合テスト用フィクスチャ・マーカー分離設定）
  - [x] 3.2 テスト戦略の最適化（不適切な aws_mock テスト削除、適切なタスクでの統合テスト実装計画）
  - [x] 3.3 AgentCore ローカルテスト環境の構築（Strands Agents + MCP 統合）
  - [x] 3.4 基本的な統合テストの作成・実行（コンポーネント連携テスト）

  _Requirements: テスト基盤_

### Phase 2: データ基盤とコア機能

- [x] 4. データモデルと DynamoDB 基盤の実装

  **完了基準**:

  - `./scripts/python-quality-check.sh` で全 Python 品質チェック通過（エラー 0 件）
  - `./scripts/infrastructure-quality-check.sh infrastructure/dynamodb-tables.yaml` でインフラ品質チェック通過（エラー 0 件）
  - `uv run pytest tests/unit/models/ tests/unit/repositories/ tests/integration/test_data_access.py -v` で全関連テスト通過（全テスト PASSED）
  - DynamoDB 単一テーブル設計での全 CRUD 操作確認

  **サブタスク**:

  - [x] 4.1 DynamoDB テーブル設計の実装（SAM テンプレート）
    - `./scripts/infrastructure-quality-check.sh infrastructure/dynamodb-tables.yaml` でインフラ品質チェック通過（エラー 0 件）
  - [x] 4.2 Pydantic データモデル（Question、Delivery、UserResponse）の実装
  - [x] 4.3 DynamoDB クライアントとリポジトリパターンの実装
  - [x] 4.4 データモデル・リポジトリの単体テスト作成
  - [x] 4.5 DynamoDB 統合テスト作成（tests/integration/test_data_access.py、moto 使用）

  _Requirements: 3.6, 5.6, 6.3_

- [x] 5. 問題生成エージェントの先行実装・動作確認（コア機能検証優先）

  **完了基準**:

  - `./scripts/python-quality-check.sh` で全 Python 品質チェック通過（エラー 0 件）
  - `uv run python app/agentcore/agent_main.py --topic EC2` で実際の問題生成実行（exit code 0 + 問題 JSON 出力）
  - 生成された問題の品質確認（Professional レベル、技術的正確性、実際のビジネスシナリオ）
  - MCP 統合による最新 AWS 情報取得の動作確認（AWS Documentation + AWS Knowledge）
  - 実際の問題例を複数生成して内容検証（EC2、S3、VPC 等で各 3 問以上）
  - `uv run pytest tests/unit/agents/ tests/integration/test_question_generation/ -v` で全関連テスト通過（全テスト PASSED）

  **サブタスク**:

  - [ ] 5.1 MCP 統合と AWS 情報取得エージェントの拡張実装（既存 MCP クライアント活用）
  - [ ] 5.2 Bedrock Claude モデルとの統合実装（boto3 + 非同期処理）
  - [ ] 5.3 問題生成エージェント（@tool）のコア機能実装
  - [ ] 5.4 品質管理エージェント（@tool）による自動検証機能実装
  - [ ] 5.5 監督者エージェントによるマルチエージェント統合（既存 agent_main.py 拡張）
  - [ ] 5.6 実際の問題生成・品質確認（手動テスト + 生成問題例の評価・改善）

  _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5（問題生成のコア価値検証を最優先）_

### Phase 3: 周辺機能とシステム統合

- [ ] 6. 問題生成 →Teams 投稿の完全フロー実装（垂直スライス第 1 イテレーション）

  **完了基準**:

  - `./scripts/python-quality-check.sh` で全 Python 品質チェック通過（エラー 0 件）
  - 実際の Teams チャネルに問題が投稿される（手動操作含む）
  - 問題生成から Teams 投稿までの完全フローが動作
  - `uv run pytest tests/integration/test_complete_flow_v1/ -v` で統合テスト通過（全テスト PASSED）
  - 実際のユーザーでの動作確認とフィードバック収集

  **サブタスク**:

  - [ ] 6.1 Power Automate フロー設定（基本的な Teams 投稿機能）
  - [ ] 6.2 問題生成 →Webhook 呼び出しの統合実装
  - [ ] 6.3 Teams 投稿テンプレートの実装
  - [ ] 6.4 実際の Teams チャネルでの動作確認・フィードバック収集
  - [ ] 6.5 完全フローの統合テスト作成

  _Requirements: 問題生成 →Teams 投稿の完全な価値提供_

- [ ] 7. 回答収集 → 統計表示の完全フロー実装（垂直スライス第 2 イテレーション）

  **完了基準**:

  - `./scripts/python-quality-check.sh` で全 Python 品質チェック通過（エラー 0 件）
  - Teams リアクション（🅰️🅱️🇨🇩）による回答収集が動作
  - 回答統計の計算・表示が動作
  - `uv run pytest tests/integration/test_complete_flow_v2/ -v` で統合テスト通過（全テスト PASSED）
  - 実際のユーザーでの動作確認とフィードバック収集

  **サブタスク**:

  - [ ] 7.1 Teams リアクション自動追加機能の実装
  - [ ] 7.2 リアクション収集機能の実装
  - [ ] 7.3 回答統計計算ロジックの実装
  - [ ] 7.4 統計表示機能の実装（Teams 投稿）
  - [ ] 7.5 実際のユーザーでの動作確認・フィードバック収集
  - [ ] 7.6 完全フローの統合テスト作成

  _Requirements: 問題投稿 → 回答収集 → 統計表示の完全な価値提供_

- [ ] 8. 自動スケジュール実行の完全フロー実装（垂直スライス第 3 イテレーション）

  **完了基準**:

  - `./scripts/python-quality-check.sh` で全 Python 品質チェック通過（エラー 0 件）
  - EventBridge スケジュールによる自動実行が動作
  - 問題生成 →Teams 投稿 → 回答収集 → 統計表示の全自動フローが動作
  - `uv run pytest tests/integration/test_complete_flow_v3/ -v` で統合テスト通過（全テスト PASSED）
  - 実際のユーザーでの動作確認とフィードバック収集

  **サブタスク**:

  - [ ] 8.1 EventBridge スケジュール設定の実装
  - [ ] 8.2 Lambda 関数による自動実行機能の実装
  - [ ] 8.3 API Gateway + Lambda インフラの実装
  - [ ] 8.4 全自動フローの統合実装
  - [ ] 8.5 実際のユーザーでの動作確認・フィードバック収集
  - [ ] 8.6 完全フローの統合テスト作成

  _Requirements: 全自動での問題配信 → 回答収集 → 統計表示の完全な価値提供_

- [ ] 9. 高品質問題生成の完全フロー実装（垂直スライス第 4 イテレーション）

  **完了基準**:

  - `./scripts/python-quality-check.sh` で全 Python 品質チェック通過（エラー 0 件）
  - 品質管理エージェントによる自動検証が動作
  - Professional レベルの高品質問題が安定して生成される
  - `uv run pytest tests/integration/test_complete_flow_v4/ -v` で統合テスト通過（全テスト PASSED）
  - 実際のユーザーでの動作確認とフィードバック収集

  **サブタスク**:

  - [ ] 9.1 品質管理エージェント（@tool）の高度化実装
  - [ ] 9.2 キーワードベース類似度チェック機能の実装
  - [ ] 9.3 品質基準検証ロジックの実装
  - [ ] 9.4 再生成機能とエラーハンドリングの実装
  - [ ] 9.5 実際のユーザーでの動作確認・フィードバック収集
  - [ ] 9.6 完全フローの統合テスト作成

  _Requirements: 高品質問題生成の完全な価値提供_

### Phase 4: AgentCore Runtime と API Gateway 連携

- [ ] 10. AgentCore Runtime メインエージェントの実装

  **完了基準**:

  - `./scripts/python-quality-check.sh` で全 Python 品質チェック通過（エラー 0 件）
  - `uv run python app/agentcore/agent_main.py` で SupervisorAgent 実行（exit code 0 + 期待ログ出力）
  - `agentcore configure` で設定ファイル生成（agentcore.yaml ファイル存在確認）
  - `agentcore launch` で AWS 環境デプロイ（デプロイ完了ログ出力確認）
  - `curl -X POST <AgentCore Endpoint>/invoke -d '{"topic":"EC2"}' -H "Content-Type: application/json"` で API 動作確認（HTTP 200 レスポンス）

  **サブタスク**:

  - [ ] 9.1 AgentCore Runtime 用メインエージェント（agent_main.py）完成
  - [ ] 9.2 監督者エージェントによるマルチエージェント統合
  - [ ] 9.3 ストリーミング対応によるリアルタイム処理状況配信
  - [ ] 9.4 エラーハンドリングとログ出力の実装
  - [ ] 9.5 AgentCore 設定ファイル・requirements.txt 作成
  - [ ] 9.6 ローカル・AWS 環境での動作確認

  _Requirements: 3.6, 6.4_

- [ ] 11. API Gateway + Lambda による外部連携の実装

  **完了基準**:

  - `./scripts/python-quality-check.sh` で全 Python 品質チェック通過（エラー 0 件）
  - `./scripts/infrastructure-quality-check.sh` で全インフラテンプレート品質チェック通過（エラー 0 件）
  - `sam build && sam deploy` でインフラデプロイ（デプロイ完了ログ出力確認）
  - `curl -X POST <API Gateway URL>/generate -d '{"topic":"EC2"}' -H "Content-Type: application/json"` で API 動作確認（HTTP 200 レスポンス）
  - `uv run pytest tests/unit/lambda/ tests/integration/test_compute_services.py -v` で全 Lambda 関連テスト通過（全テスト PASSED）
  - `aws events list-rules --name-prefix aws-exam-agent` で EventBridge ルール作成確認（JSON レスポンス取得）

  **サブタスク**:

  - [ ] 10.1 SAM テンプレートで API Gateway REST API 設定
    - `./scripts/infrastructure-quality-check.sh infrastructure/api-gateway.yaml` でインフラ品質チェック通過（エラー 0 件）
  - [ ] 10.2 Lambda 関数による AgentCore Runtime 呼び出し実装
  - [ ] 10.3 Power Automate Webhook 呼び出し機能の実装
  - [ ] 10.4 Teams 投稿データフォーマット機能の実装
  - [ ] 10.5 EventBridge スケジュール連携の実装
  - [ ] 10.6 Lambda 関数の単体テスト作成
  - [ ] 10.7 Lambda 統合テスト作成（tests/integration/test_compute_services.py、moto 使用）

  _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 6.1, 6.2, 6.3, 6.4_

- [ ] 12. 問題配信システムの統合実装

  **完了基準**:

  - `./scripts/python-quality-check.sh` で全 Python 品質チェック通過（エラー 0 件）
  - `uv run pytest tests/integration/test_delivery_system/ tests/e2e/test_full_flow/ -v` で全統合・E2E テスト通過（全テスト PASSED）
  - `aws logs describe-log-groups --log-group-name-prefix /aws/lambda/aws-exam-agent` で CloudWatch Logs 確認（JSON レスポンス取得）
  - `curl -X POST <Power Automate Webhook URL> -d '{"question":"test"}' -H "Content-Type: application/json"` で Teams 投稿確認（HTTP 200 レスポンス）

  **サブタスク**:

  - [ ] 11.1 EventBridge → API Gateway → AgentCore Runtime → Teams の統合フロー実装
  - [ ] 11.2 配信結果の記録機能の実装（CloudWatch Logs）
  - [ ] 11.3 エンドツーエンド統合テスト作成
  - [ ] 11.4 全体フローの手動テスト・動作確認

  _Requirements: 6.1, 6.2, 6.3, 6.4_

### Phase 5: ハイブリッドデプロイとインフラ

- [ ] 13. AgentCore Runtime デプロイ設定

  **完了基準**:

  - `agentcore configure` で設定ファイル生成（agentcore.yaml ファイル存在確認）
  - `agentcore launch` で AWS 環境デプロイ（デプロイ完了ログ出力確認）
  - `aws iam list-roles --query 'Roles[?contains(RoleName, \`agentcore\`)].RoleName' --output text` で IAM ロール作成確認（ロール名出力）
  - `aws ecr describe-repositories --query 'repositories[?contains(repositoryName, \`agentcore\`)].repositoryName' --output text` で ECR リポジトリ作成確認（リポジトリ名出力）
  - `curl -X POST <AgentCore Endpoint>/invoke -d '{"topic":"EC2"}' -H "Content-Type: application/json"` で API 動作確認（HTTP 200 レスポンス）

  **サブタスク**:

  - [ ] 12.1 requirements.txt の作成（実際に利用可能な依存関係）
  - [ ] 12.2 agentcore configure による設定ファイル生成・確認
  - [ ] 12.3 agentcore launch によるデプロイ実行
  - [ ] 12.4 IAM ロールと権限設定の自動作成確認
  - [ ] 12.5 ECR リポジトリの自動作成確認
  - [ ] 12.6 デプロイ後の動作確認・テスト

  _Requirements: 6.1, 6.4_

- [ ] 14. API Gateway + Lambda インフラとデプロイ設定

  **完了基準**:

  - `sam validate` で SAM テンプレート構文確認
  - `./scripts/infrastructure-quality-check.sh` で全インフラテンプレート品質チェック通過（エラー 0 件）
  - `sam build && sam deploy` でインフラデプロイ成功
  - `./scripts/deploy-hybrid.sh` でハイブリッドデプロイ成功
  - GitHub Actions ワークフローで CI/CD 実行成功
  - 全インフラリソースの作成・動作確認

  **サブタスク**:

  - [ ] 13.1 API Gateway REST API 用 SAM テンプレート作成
    - `./scripts/infrastructure-quality-check.sh infrastructure/main-template.yaml` でインフラ品質チェック通過（エラー 0 件）
  - [ ] 13.2 Lambda 関数と API Gateway の定義
    - `./scripts/infrastructure-quality-check.sh infrastructure/lambda-functions.yaml` でインフラ品質チェック通過（エラー 0 件）
  - [ ] 13.3 DynamoDB テーブル定義の実装
    - `./scripts/infrastructure-quality-check.sh infrastructure/dynamodb-tables.yaml` でインフラ品質チェック通過（エラー 0 件）
  - [ ] 13.4 EventBridge スケジュール設定の実装
    - `./scripts/infrastructure-quality-check.sh infrastructure/eventbridge-schedules.yaml` でインフラ品質チェック通過（エラー 0 件）
  - [ ] 13.5 IAM ロールと権限設定（AgentCore 呼び出し権限含む）
  - [ ] 13.6 デプロイスクリプト（deploy-hybrid.sh）の作成
  - [ ] 13.7 GitHub Actions ワークフロー（ハイブリッド対応）の実装

  _Requirements: 6.4_

### Phase 6: Teams 統合と E2E テスト

- [ ] 15. Power Automate フローの設定と連携テスト

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

- [ ] 16. 回答集計と統計分析機能の実装

  **完了基準**:

  - `./scripts/python-quality-check.sh` で全 Python 品質チェック通過（エラー 0 件）
  - `uv run pytest tests/unit/analytics/ tests/integration/test_reaction_collection/ -v` で全統計分析テスト通過（全テスト PASSED）
  - 実際の Teams リアクションデータでの集計動作確認
  - 統計 API エンドポイントでのデータ取得確認

  **サブタスク**:

  - [ ] 15.1 リアクション収集機能の実装
  - [ ] 15.2 回答統計計算ロジックの実装
  - [ ] 15.3 参加状況分析機能の実装
  - [ ] 15.4 統計データの保存と取得 API 実装
  - [ ] 15.5 統計分析機能の単体・統合テスト作成

  _Requirements: 2.1, 2.2, 2.3, 6.3_

- [ ] 17. E2E テストスイートの実装

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

- [ ] 18. Amazon Bedrock Citations API 統合

  - Citations API クライアントの実装
  - 引用元情報を含む解説生成機能
  - 品質検証プロセスへの統合
  - _Requirements: 5.2, 5.4_

- [ ] 19. 管理者通知システム

  - 品質基準未達時の通知機能実装
  - 管理者ダッシュボード機能
  - 通知設定管理機能
  - _Requirements: 5.5_

- [ ] 20. 高度な品質管理機能
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

#### 3. strands の正しいインストール

```bash
# 方法1: PyPI からのインストール（推奨）
uv add strands-agents

# 方法2: 開発版インストール（必要に応じて）
uv add git+https://github.com/strands-ai/strands-agents.git

# 方法3: bedrock-agentcore-starter-toolkit に含まれる場合
# agentcore configure 実行時に自動インストールされる可能性を確認

# インストール確認（正しいインポート方法）
uv run python -c "from strands import Agent; print('strands imported successfully')"

# 注意: 正しいインポートは "from strands import Agent" です
# 間違い: "from strands_agents import Agent"
# 正解: "from strands import Agent"
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

#### app/agentcore/requirements.txt

```txt
strands-agents
bedrock-agentcore
uv
```

#### agent_main.py 動作確認手順

```bash
# 1. strands インポート確認（正しいインポート方法）
uv run python -c "from strands import Agent, tool; print('Import successful')"

# 2. agent_main.py 基本動作確認
uv run python app/agentcore/agent_main.py

# 3. 期待される出力例
# INFO:__main__:Initializing Supervisor Agent
# INFO:__main__:Supervisor Agent initialized successfully
# INFO:__main__:Starting question generation flow: topic=EC2, difficulty=intermediate
# INFO:__main__:Execution result: {'status': 'success', ...}

# 4. エラーが発生した場合の対処
# - ImportError: strands が見つからない → インストール方法を再確認
# - ModuleNotFoundError: bedrock_agentcore → bedrock-agentcore-starter-toolkit の再インストール
# - その他のエラー → 依存関係の不足を確認
```

## 実装時の注意事項

### 品質管理の継続性保証

**全タスク共通の必須チェック項目**（セッション継続時の漏れ防止）:

- [ ] `./scripts/python-quality-check.sh` で全 Python 品質チェック通過（エラー 0 件）
- [ ] IDE 上でエラー表示ゼロ（精神衛生上必須）
- [ ] VS Code 設定の品質保証（廃止設定なし、新形式対応）
- [ ] テストコードも本番コードと同等の型チェック基準適用
- [ ] 外部ライブラリの型チェック無視設定が適切に設定済み

**CloudFormation テンプレート作成タスクの追加チェック項目**:

- [ ] `./scripts/infrastructure-quality-check.sh` で統合インフラ品質チェック通過（エラー 0 件）

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
