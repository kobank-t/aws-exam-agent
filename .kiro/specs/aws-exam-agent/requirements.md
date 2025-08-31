# Cloud CoPassAgent 要件定義書

## Introduction

**Cloud CoPassAgent** は、クラウド資格学習を通じて組織内のコミュニケーション(Co)を促し、合格とスキルの橋渡し(Pass)を支援する AI エージェントです。

初回ローンチ時点では、MVP（Minimum Viable Product）として、AWS SAP を題材に、問題の生成から投稿までの最小限の流れを提供し、組織メンバーの反応を伺いながら改善を進めています。

### 主要目的

- **AI エージェント技術のスキルアップ**（開発側）
- **組織内コミュニケーション活性化、クラウド用語の習慣化**（利用側）
- **強強メンバから経験の浅いメンバへのスキルトランスファー**（きっとおそらくたぶん）

### 対象組織・環境

- **対象**: エンジニア中心の 200 名組織
- **利用環境**: Microsoft Teams チャネル
- **デバイス**: 会社支給 PC・iPhone
- **戦略**: 段階的リリースでフィードバック収集

### 技術スタック（実装済み）

- **AI 基盤**: Amazon Bedrock（Claude 3.5 Sonnet） + Amazon Bedrock AgentCore + Strands Agents + MCP 統合
- **バックエンド**: Lambda + EventBridge Scheduler
- **フロントエンド**: Power Automate + Teams + Microsoft Lists（SharePoint）
- **言語**: Python 3.12 + uv

### MVP 戦略

**実装済み**: 問題生成 → Teams 投稿の垂直スライス
**現在**: 組織展開中、フィードバック収集期間（1 週間）

## 実装済み MVP 要件

### Requirement 1: AI 問題生成機能

**User Story:** As a システム管理者, I want AI エージェントが自動的に AWS SAP Professional レベルの問題を生成する機能, so that 組織メンバーに継続的で質の高い学習コンテンツを提供できる

#### Acceptance Criteria

1. WHEN システムが問題生成を開始する THEN AgentCore Runtime SHALL MCP 統合により AWS 公式ドキュメントから最新情報を取得する
2. WHEN AWS 情報を取得する THEN システム SHALL AWS Documentation MCP Server を活用する
3. WHEN 問題を生成する THEN システム SHALL Claude 3.5 Sonnet を使用して Professional レベルの技術問題を作成する
4. WHEN 問題を作成する THEN システム SHALL 実際のビジネスシナリオを想定した複雑な問題文を生成する
5. WHEN 選択肢を生成する THEN システム SHALL 1 つの正解と 4 つ以上の説得力のある不正解選択肢を作成する
6. WHEN 解説を生成する THEN システム SHALL 正解理由と各選択肢の詳細な説明を含む充実した解説を作成する
7. WHEN 参考資料を追加する THEN システム SHALL AWS 公式ドキュメントへのリンクを自動的に含める

### Requirement 2: Teams 投稿・データ登録機能

**User Story:** As a 組織メンバー, I want Teams チャネルに見やすい形式で AWS 問題が投稿され、同時に問題データが記録される機能, so that 馴染みのある Teams 環境で気軽に学習に参加でき、問題履歴も管理できる

#### Acceptance Criteria

1. WHEN 問題生成が完了する THEN システム SHALL Power Automate を通じて Teams チャネルに投稿する
2. WHEN Teams 投稿を実行する THEN システム SHALL Adaptive Card 形式で構造化された見やすい表示を提供する
3. WHEN 問題カードを表示する THEN システム SHALL 問題文、4 つ以上の選択肢（A-D 以上）、問題番号を含める
4. WHEN 問題カードを表示する THEN システム SHALL 「回答を見る」ボタンによる段階的な情報提示を提供する
5. WHEN 回答ボタンが押される THEN システム SHALL 正解と詳細な解説を表示する
6. WHEN 解説を表示する THEN システム SHALL AWS 公式ドキュメントへのリンクを含める
7. WHEN Teams 投稿が完了する THEN システム SHALL Power Automate を通じて Microsoft Lists（SharePoint リスト）に問題データを自動登録する
8. WHEN Microsoft Lists に登録する THEN システム SHALL 問題文、選択肢、正解、解説、投稿日時等の詳細情報を記録する
9. IF Teams 投稿でエラーが発生する THEN システム SHALL エラーログを記録し、処理を継続する

### Requirement 3: 定期実行機能

**User Story:** As a システム管理者, I want 定期的に新しい問題が自動配信される機能, so that 継続的な学習機会を組織に提供できる

#### Acceptance Criteria

1. WHEN 定期実行スケジュールが設定される THEN EventBridge Scheduler SHALL 指定された時間に Lambda 関数を呼び出す
2. WHEN Lambda 関数が呼び出される THEN システム SHALL AgentCore Runtime を起動して問題生成プロセスを開始する
3. WHEN 問題生成プロセスが完了する THEN システム SHALL 自動的に Teams 投稿まで実行する
4. WHEN 定期実行が完了する THEN システム SHALL CloudWatch Logs に実行ログを記録する
5. IF 定期実行でエラーが発生する THEN システム SHALL エラー内容をログに記録し、次回実行に影響しないよう処理する

## 非機能要件

### 性能要件

- **問題生成時間**: 60 秒以内での問題生成完了
- **Teams 投稿**: 5 秒以内での投稿完了
- **可用性**: 99%以上の稼働率（EventBridge Scheduler + Lambda + AgentCore）

### セキュリティ要件

- **AWS 環境**: 統括部の砂場環境での安全な実行
- **Teams 連携**: Power Automate による認証済み連携
- **データ保護**: 組織内データの適切な管理

### 運用要件

- **監視**: CloudWatch Logs による実行状況監視
- **エラーハンドリング**: 障害時の適切なログ記録と継続実行
- **スケーラビリティ**: 組織規模拡大への対応可能性

---

**作成日**: 2025 年 8 月 26 日  
**ベース**: 実装済み MVP（Cloud CoPassAgent）から逆算  
**対象**: 現在組織展開中のサービス
