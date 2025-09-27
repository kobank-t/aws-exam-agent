# Implementation Plan

## 概要

この実装計画は、Cloud CoPassAgent の問題生成から Teams 投稿までの完全なフローを実装することを目的としています。垂直スライス開発により、最小限の機能で動く価値を早期提供し、段階的に機能を拡張していきます。

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

### Phase 0: 環境セットアップ

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

### Phase 1: シンプル化とリファクタリング（MVP として、まずは AWS SAP を題材に、問題の生成から投稿までの最小限の流れを開発）

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

### Phase 2: フィードバック収集段階での改善

- [x] 6. 選択肢表示の視認性向上

  **完了基準**:

  - `Question` モデルの `options` フィールド description 更新完了
  - AI エージェントが太字記法（**A.**、**B.** 等）を確実に使用
  - `uv run python app/agentcore/agent_main.py --test` で太字記法確認
  - 実際の Teams 投稿で選択肢ラベルが太字表示される
  - `uv run pytest tests/unit/agentcore/ -v` で全テスト通過
  - `uv run ruff check app/ tests/` でリンターエラー 0 件
  - `uv run mypy app/ tests/` で型チェックエラー 0 件

  **実装内容**:

  - Question モデルの options フィールド description の改善
  - AI エージェントへの指示文の最適化
  - 太字記法の確実な適用を促すプロンプト改善

  **サブタスク**:

  - [x] 6.1 現在の選択肢生成パターンの分析と問題点特定
  - [x] 6.2 効果的な太字記法指示文の設計・実装
  - [x] 6.3 AI エージェントのシステムプロンプト改善（必要に応じて）
  - [x] 6.4 実際の問題生成での太字記法確認・検証
  - [x] 6.5 Teams 投稿での表示確認・品質チェック実行

  _Requirements: Requirement 4 (選択肢表示の視認性向上)_

### Phase 3: 試験ガイド活用による問題分類表示機能

- [x] 7. 基本実装: シンプルなファイル読み込み + プロンプト統合

  **完了基準**:

  - `data/exam_guides/AWS-SAP-C02.md` ファイル読み込み機能実装完了
  - `AgentInput.exam_type` による動的ガイド選択機能実装完了
  - 実行時プロンプトに試験ガイド内容統合完了
  - `Question` モデルに新フィールド（learning_domain, primary_technologies, guide_reference）追加完了
  - `uv run python app/agentcore/agent_main.py --test` で新フィールド生成確認
  - `uv run pytest tests/unit/agentcore/ -v` で全テスト通過
  - `uv run ruff check app/ tests/` でリンターエラー 0 件
  - `uv run mypy app/ tests/` で型チェックエラー 0 件

  **実装内容**:

  - 試験ガイドファイル読み込み機能の実装
  - AgentInput.exam_type による動的ガイド選択
  - Question モデルの拡張（新分類フィールド追加）
  - 実行時プロンプトへの試験ガイド統合
  - 分類情報生成のプロンプト指示追加

  **サブタスク**:

  - [x] 7.1 Question モデルに新フィールド追加（learning_domain, primary_technologies, guide_reference）
  - [x] 7.2 試験ガイドファイル読み込み機能実装（data/exam_guides/{exam_type}.md）
  - [x] 7.3 AgentInput.exam_type による動的ガイド選択ロジック実装
  - [x] 7.4 実行時プロンプトに試験ガイド内容統合機能実装
  - [x] 7.5 分類情報生成のプロンプト指示追加・テスト実行

  _Requirements: Requirement 5 (試験ガイド活用による問題分類表示機能) - 基本実装_

- [x] 8. AgentInput.exam_type デフォルト値変更と汎用性向上

  **完了基準**:

  - `AgentInput.exam_type` デフォルト値を "AWS-SAP" に変更完了
  - `EXAM_TYPES` 辞書の更新完了（ファイル名ベース対応）
  - 既存機能の動作確認完了（後方互換性確保）
  - `uv run python app/agentcore/agent_main.py --test` で新デフォルト値動作確認
  - `uv run pytest tests/unit/agentcore/ -v` で全テスト通過
  - 実際の Teams 投稿で学習分野情報表示確認

  **実装内容**:

  - AgentInput.exam_type デフォルト値の変更
  - EXAM_TYPES 辞書の汎用化
  - 後方互換性の確保
  - 汎用的な命名規則への移行

  **サブタスク**:

  - [x] 8.1 AgentInput.exam_type デフォルト値を "AWS-SAP" に変更
  - [x] 8.2 EXAM_TYPES 辞書をファイル名ベースに更新
  - [x] 8.3 既存機能の動作確認・後方互換性テスト
  - [x] 8.4 Teams 投稿での学習分野情報表示実装
  - [x] 8.5 汎用性確保のための最終調整・品質チェック

  _Requirements: Requirement 5 (試験ガイド活用による問題分類表示機能) - 汎用性向上_

- [ ] 9. 拡張実装: 必要に応じて圧縮機能追加（条件付き実装）

  **完了基準**:

  - 基本実装でトークン制限エラーが発生した場合のみ実装
  - LLMLingua 等による試験ガイド圧縮機能実装完了
  - コンテキストサイズ約 1/3 削減確認
  - 問題品質の維持確認（圧縮前後比較）
  - `uv run pytest tests/unit/agentcore/ -v` で全テスト通過

  **実装内容**:

  - トークン制限エラーの検出・対応
  - LLMLingua 等の圧縮ライブラリ統合
  - 動的圧縮処理の実装
  - 圧縮効果の測定・検証

  **サブタスク**:

  - [ ] 9.1 基本実装でのトークン制限エラー発生確認
  - [ ] 9.2 LLMLingua 等の圧縮ライブラリ調査・選定
  - [ ] 9.3 試験ガイド圧縮機能実装
  - [ ] 9.4 圧縮効果測定・問題品質検証
  - [ ] 9.5 圧縮機能の統合・最終テスト

  _Requirements: Requirement 5 (試験ガイド活用による問題分類表示機能) - 拡張実装（条件付き）_

- [ ] 10. 最適化実装: 動的コンテキスト選択で最適化（条件付き実装）

  **完了基準**:

  - 拡張実装でより精密なコンテキスト制御が必要な場合のみ実装
  - カテゴリに基づく関連セクション動的抽出機能実装完了
  - 必要な情報のみでコンテキストサイズ最小化確認
  - 問題品質とトークン効率の両立確認
  - `uv run pytest tests/unit/agentcore/ -v` で全テスト通過

  **実装内容**:

  - セクション解析機能の実装
  - 関連度計算アルゴリズムの実装
  - 動的選択機能の実装
  - 最適化効果の測定・検証

  **サブタスク**:

  - [ ] 10.1 拡張実装でのコンテキスト制御需要確認
  - [ ] 10.2 試験ガイドセクション解析機能実装
  - [ ] 10.3 関連度計算・動的選択アルゴリズム実装
  - [ ] 10.4 最適化効果測定・問題品質検証
  - [ ] 10.5 動的選択機能の統合・最終テスト

  _Requirements: Requirement 5 (試験ガイド活用による問題分類表示機能) - 最適化実装（条件付き）_

### Phase 4: ジャンル分散機能実装

- [x] 11. AgentCore Memory を活用したジャンル分散機能実装

  **完了基準**:

  - AgentCore Memory への分野履歴記録機能実装完了
  - 最近使用された分野の取得機能実装完了
  - プロンプトレベルでの除外指示機能実装完了
  - 実際の問題生成で異なる分野からの問題生成確認
  - `uv run pytest tests/unit/agentcore/ -v` で全テスト通過
  - `uv run ruff check app/ tests/` でリンターエラー 0 件
  - `uv run mypy app/ tests/` で型チェックエラー 0 件

  **実装内容**:

  - AgentCore Memory API（CreateEvent/ListEvents）の統合
  - 学習分野履歴の記録・参照機能
  - プロンプト生成時の除外指示ロジック
  - 既存の問題生成フローへの統合

  **サブタスク**:

  - [x] 11.1 AgentCore Memory クライアント実装
  - [x] 11.2 分野履歴記録機能実装（record_domain_usage）
  - [x] 11.3 分野履歴取得機能実装（get_recent_domains_from_memory）
  - [x] 11.4 分散プロンプト生成機能実装（create_diversified_prompt）
  - [x] 11.5 既存問題生成フローへの統合・動作確認

  _Requirements: Requirement 6 (ジャンル分散機能)_

### Phase 5: 問題品質評価・改善機能実装（Strands Agents カスタムツール）

- [ ] 12. 品質評価カスタムツールの実装

  **完了基準**:

  - `evaluate_question_quality` カスタムツール実装完了
  - 4 軸評価システム（技術的正確性・難易度・構造・準拠性）実装完了
  - 重み付き総合スコア算出機能実装完了
  - `uv run python app/agentcore/agent_main.py --test-quality` で品質評価ツール動作確認
  - `uv run pytest tests/unit/agentcore/test_quality_tools.py -v` で全テスト通過
  - `uv run ruff check app/ tests/` でリンターエラー 0 件
  - `uv run mypy app/ tests/` で型チェックエラー 0 件

  **実装内容**:

  - Strands Agents `@tool` デコレータによるカスタムツール実装
  - 4 軸評価ロジックの実装
  - LLM による品質判定機能（モデル非依存）
  - 公式サンプル問題との比較分析機能（クラウドプロバイダー非依存）

  **サブタスク**:

  - [x] 12.1 試験リソース管理の改善（exam_resources 統合・命名ルール適用）
  - [ ] 12.2 品質評価カスタムツール基盤実装（@tool デコレータ活用）
  - [ ] 12.3 サンプル問題管理機能実装（load_sample_questions 関数）
  - [ ] 12.4 技術的正確性評価機能実装（MCP 統合による検証）
  - [ ] 12.5 難易度・構造品質評価機能実装（サンプル問題との比較）

  _Requirements: Requirement 8 (問題品質評価・改善機能) - カスタムツール基盤_

- [ ] 13. 品質改善カスタムツールの実装

  **完了基準**:

  - `improve_question_quality` カスタムツール実装完了
  - 品質フィードバックに基づく自動改善機能実装完了
  - 改善提案の具体的適用機能実装完了
  - `uv run python app/agentcore/agent_main.py --test-improvement` で品質改善ツール動作確認
  - `uv run pytest tests/unit/agentcore/test_improvement_tools.py -v` で全テスト通過
  - `uv run ruff check app/ tests/` でリンターエラー 0 件
  - `uv run mypy app/ tests/` で型チェックエラー 0 件

  **実装内容**:

  - Strands Agents `@tool` デコレータによる改善ツール実装
  - 品質フィードバック解析機能
  - 自動改善ロジックの実装
  - 改善効果の検証機能

  **サブタスク**:

  - [ ] 13.1 品質改善カスタムツール基盤実装（@tool デコレータ活用）
  - [ ] 13.2 技術的正確性改善機能実装（公式ドキュメント参照強化）
  - [ ] 13.3 選択肢妥当性改善機能実装（説得力のある不正解生成）
  - [ ] 13.4 解説充実化機能実装（学習効果向上）
  - [ ] 13.5 構造最適化機能実装（問題文・選択肢の構造改善）

  _Requirements: Requirement 8 (問題品質評価・改善機能) - 改善ツール_

- [ ] 14. エージェント自律品質管理統合

  **完了基準**:

  - エージェントへの品質評価・改善ツール統合完了
  - システムプロンプトによる自律的品質管理指示実装完了
  - 品質基準達成まで自動改善サイクル実装完了
  - 実際の問題生成で品質評価 → 改善 → 再評価サイクル動作確認
  - 最大改善回数制限（3 回）による無限ループ防止実装完了
  - `uv run pytest tests/unit/agentcore/test_autonomous_quality.py -v` で全テスト通過

  **実装内容**:

  - エージェントツール統合
  - 自律的品質管理システムプロンプト
  - 品質改善サイクルの実装
  - 無限ループ防止機能

  **サブタスク**:

  - [ ] 14.1 エージェントへのカスタムツール統合（tools リストに追加）
  - [ ] 14.2 自律的品質管理システムプロンプト実装
  - [ ] 14.3 品質基準達成まで自動改善サイクル実装
  - [ ] 14.4 最大改善回数制限・無限ループ防止機能実装
  - [ ] 14.5 既存問題生成フローへの統合・エンドツーエンド動作確認

  _Requirements: Requirement 8 (問題品質評価・改善機能) - エージェント統合_

---

**作成日**: 2025 年 8 月 3 日  
**最終更新**: 2025 年 9 月 27 日  
**ステータス**: 問題品質評価・改善機能のタスクリスト作成完了
