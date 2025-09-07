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
6. WHEN 選択肢を表示する THEN システム SHALL 選択肢ラベル（A、B、C、D 等）を太字で強調表示する
7. WHEN 解説を生成する THEN システム SHALL 正解理由と各選択肢の詳細な説明を含む充実した解説を作成する
8. WHEN 参考資料を追加する THEN システム SHALL AWS 公式ドキュメントへのリンクを自動的に含める

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

## フィードバック収集段階での改善要求

### Requirement 4: 選択肢表示の視認性向上

**User Story:** As a 組織メンバー, I want 選択肢のラベル（A、B、C、D 等）が太字で強調表示される機能, so that 問題を読む際に選択肢を素早く識別でき、学習効率を向上できる

#### Acceptance Criteria

1. WHEN 問題の選択肢を生成する THEN システム SHALL 選択肢ラベル（A、B、C、D 等）を Markdown 太字記法（**A.**、**B.**等）で表現する
2. WHEN Teams 投稿を実行する THEN システム SHALL Adaptive Card 内で選択肢ラベルが太字で表示されることを確認する
3. WHEN 選択肢を表示する THEN システム SHALL 各選択肢の内容と太字ラベルが明確に区別できる形式で表示する
4. WHEN 問題生成プロンプトを実行する THEN システム SHALL AI エージェントに対して太字記法の使用を明確に指示する

#### 技術的実装要件

- **対象ファイル**: `app/agentcore/agent_main.py` の `Question` モデル
- **修正箇所**: `options` フィールドの `description` 属性
- **期待される改善**: AI エージェントが太字記法を確実に使用するよう、より具体的で効果的な指示文に変更

### Requirement 5: 試験ガイド活用による問題分類表示機能

**User Story:** As a 組織メンバー, I want 問題がどの学習分野から出題されているかが分かる機能, so that 体系的で効率的な学習ができる

#### Acceptance Criteria

1. WHEN 問題生成を開始する THEN システム SHALL `AgentInput.exam_type` に基づいて対応する試験ガイドファイル（`data/exam_guides/{exam_type}.md`）を読み込む
2. WHEN 試験ガイドファイルが存在しない場合 THEN システム SHALL デフォルトガイド（AWS-SAP-C02.md）を使用する
3. WHEN 試験ガイドを読み込む THEN システム SHALL ガイド内容をプロンプトコンテキストとして AI エージェントに提供する
4. WHEN 問題を生成する THEN システム SHALL 読み込んだ試験ガイドに基づいて以下の情報を自動判定・出力する：
   - **学習分野**: 試験ガイドで定義されたコンテンツ分野
   - **主要技術要素**: 問題で扱われる主要な技術・サービス（最大 3 つ）
   - **学習戦略**: 試験ガイドに基づく学習戦略と試験対策ポイント（出題傾向、学習優先度、よくある間違い、実務経験による有利/不利、効果的な学習方法を含む）
5. WHEN Teams 投稿を実行する THEN システム SHALL 問題タイトル部分に学習分野情報を表示する
6. WHEN 学習分野情報を表示する THEN システム SHALL 絵文字付き分野名で視認性を向上させる
7. WHEN 複数分野にまたがる問題の場合 THEN システム SHALL 主要な分野 1 つを選択して表示する
8. WHEN 分野判定が困難な場合 THEN システム SHALL デフォルト分野として最初の分野を選択する

#### 技術的実装要件

- **対象ファイル**: `app/agentcore/agent_main.py` の `Question` モデル
- **追加フィールド**:
  - `learning_domain`: 学習分野分類（汎用的な命名）
  - `primary_technologies`: 主要技術要素リスト（クラウドプロバイダー非依存）
  - `learning_insights`: 試験ガイドに基づく学習戦略と試験対策ポイント（explanation とは異なり、問題解説ではなく試験合格のための学習支援に特化）
- **エージェントインプット活用**: 既存の `AgentInput.exam_type` フィールドを活用した動的試験ガイド選択
- **試験ガイド統合**:
  - インプットに基づく動的ガイド選択機能
  - ファイル読み込み機能の実装（`data/exam_guides/` 配下対応）
  - システムプロンプトへのコンテキスト統合
  - 必要に応じた圧縮機能（LLMLingua 等）
- **表示形式**: Teams Adaptive Card のタイトル部分に「[絵文字 分野名] 問題タイトル」形式で表示
- **段階的実装**:
  - **基本実装**: シンプルなファイル読み込み + プロンプト統合
    - 狙い: 最小限の実装で機能検証
    - 方法: 試験ガイド全体をシステムプロンプトに含める
    - 課題: トークン制限に引っかかる可能性
  - **拡張実装**: 必要に応じて圧縮機能追加
    - 狙い: トークン制限対応とコンテキスト最適化
    - 方法: LLMLingua 等による試験ガイド圧縮
    - 効果: コンテキストサイズを約 1/3 に削減
  - **最適化実装**: 動的コンテキスト選択で最適化
    - 狙い: トークン効率と問題品質の両立
    - 方法: カテゴリに基づく関連セクションの動的抽出
    - 効果: 必要な情報のみでコンテキストサイズを最小化
- **実装判断基準**:
  - 基本実装 → 拡張実装: トークン制限エラーが発生した場合
  - 拡張実装 → 最適化実装: より精密なコンテキスト制御が必要な場合
  - 各フェーズで機能検証を行い、必要に応じて次フェーズに進む
- **MVP 検証**: AWS SAP を題材とした初期検証、将来的に他クラウドプロバイダーに拡張
- **将来拡張性**: Azure、GCP、OCI 等の試験ガイドにも対応可能な汎用的設計

### Requirement 6: 学習戦略支援機能の強化

**User Story:** As a 組織メンバー, I want 問題の解説とは別に、その分野の効果的な学習戦略を知りたい, so that 試験合格に向けた効率的な学習計画を立てることができる

#### Acceptance Criteria

1. WHEN 問題を生成する THEN システム SHALL 問題解説（explanation）とは独立した学習戦略情報（learning_insights）を生成する
2. WHEN 学習戦略を生成する THEN システム SHALL 試験ガイドに基づく以下の情報を含める：
   - **出題傾度**: ★ 評価による重要度の視覚化
   - **学習優先度**: 試験合格における重要度レベル
   - **よくある間違い**: 受験者が陥りやすいミスや混同しやすい概念
   - **学習戦略**: 推奨する学習順序や効果的な学習方法
   - **実務経験差**: 実務経験による有利/不利と補強方法
   - **関連項目**: 他の試験分野との関連性
3. WHEN 学習戦略を表示する THEN システム SHALL 構造化された形式（【】区切り）で情報を整理する
4. WHEN Teams 投稿を実行する THEN システム SHALL 学習戦略情報を問題解説とは別セクションで表示する
5. WHEN 学習戦略を生成する THEN システム SHALL 試験合格のための実用的な情報に特化し、問題解説の重複を避ける

#### 技術的実装要件

- **対象フィールド**: `learning_insights`（旧 `guide_reference` から変更）
- **情報源**: 試験ガイドファイルの内容と構造
- **差別化**: `explanation`（問題解説）と`learning_insights`（学習戦略）の明確な役割分担
- **表示形式**: 構造化された学習支援情報（【試験対策】【学習戦略】【よくある間違い】等）
- **学習効果**: 単なる問題解説から戦略的学習支援ツールへの進化

---

**作成日**: 2025 年 8 月 26 日  
**ベース**: 実装済み MVP（Cloud CoPassAgent）から逆算  
**対象**: 現在組織展開中のサービス  
**最終更新**: 2025 年 9 月 7 日（学習戦略支援機能強化・learning_insights フィールド仕様変更）
