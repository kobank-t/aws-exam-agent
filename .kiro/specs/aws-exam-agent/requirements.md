# Requirements Document

## Introduction

AWS Exam Agent は、Strands Agents フレームワークと AWS Bedrock AgentCore を活用した AI エージェントによる自動問題生成を核とした組織内コラボレーション学習プラットフォームの MVP（Minimum Viable Product）です。200 名のエンジニア組織において、AWS Certified Solutions Architect - Professional の学習を通じてコミュニケーション活性化とスキルトランスファーを促進します。

**主要目的:**

- AI エージェント技術のスキルアップ（開発側）
- 組織内コミュニケーション活性化（利用側）
- 強強メンバから経験の浅いメンバへのスキルトランスファー

**対象組織:** エンジニア中心の 200 名組織
**利用環境:** 社内、会社支給 PC・iPhone、Microsoft Teams チャネル
**技術方式:** AgentCore Runtime + API Gateway + Power Automate + HTTP リクエスト + Teams リアクション
**戦略:** 段階的リリースでフィードバック収集、注目集まったら専用画面開発

**AI エージェント基盤:**

- **フレームワーク**: Strands Agents (AWS 製オープンソース)
- **実行環境**: AWS Bedrock AgentCore Runtime (Preview) + API Gateway ハイブリッド構成
- **MCP 統合**: Model Context Protocol による標準化されたコンテキスト提供
- **マルチエージェント**: Agent-as-Tools パターンによる専門エージェント連携
- **外部連携**: API Gateway + Lambda による Power Automate・スケジュール連携

**MVP 情報源:** AWS 公式ドキュメント、Solutions Architect - Professional 試験ガイド
**将来拡張予定:** FAQ、What's New、Well-Architected Framework、ベストプラクティスガイド、他の AWS 認定資格への対応

## Requirements

### Requirement 1

**User Story:** As a 組織メンバー, I want Teams チャネルに投稿される AWS 試験問題にリアクションで回答できる機能, so that 馴染みのある Teams 環境で気軽に学習に参加できる

#### Acceptance Criteria

1. WHEN システムが問題を配信する THEN システム SHALL Power Automate を通じて Teams チャネルに問題カードを投稿する
2. WHEN 問題カードが投稿される THEN システム SHALL 問題文、4 つの選択肢（A、B、C、D）、問題番号を含む見やすい形式で表示する
3. WHEN 組織メンバーが問題を見る THEN システム SHALL A、B、C、D の絵文字リアクションを自動的に追加する
4. WHEN メンバーがリアクションで回答する THEN システム SHALL そのリアクションを回答として記録する
5. IF 設定された時間が経過する THEN システム SHALL 正解と解説をスレッドに自動投稿する

### Requirement 2

**User Story:** As a 組織メンバー, I want 問題のスレッドで他のメンバーと議論できる機能, so that ワイガヤを通じて知識を共有し、スキルトランスファーを促進できる

#### Acceptance Criteria

1. WHEN 正解と解説がスレッドに投稿される THEN システム SHALL 各選択肢の詳細な説明と関連 AWS サービスの情報を含める
2. WHEN メンバーがスレッドで質問や補足をする THEN システム SHALL そのコメントを問題に関連付けて保存する
3. WHEN 経験豊富なメンバーが追加解説を投稿する THEN システム SHALL @メンション機能を活用して知識共有を促進する
4. WHEN スレッド内で活発な議論が発生する THEN システム SHALL 議論の内容を今後の問題生成の参考情報として活用する
5. IF 間違った情報が投稿される THEN システム SHALL 他のメンバーが訂正できる環境を提供する

### Requirement 3

**User Story:** As a システム管理者, I want Strands Agents フレームワークによるマルチエージェントシステムが自動的に試験問題を生成する機能, so that 常に最新で質の高い練習問題を学習者に提供することができる

#### Acceptance Criteria

1. WHEN システムが問題生成を開始する THEN 監督者エージェント SHALL Agent-as-Tools パターンで専門エージェントを呼び出す
2. WHEN AWS 情報取得エージェントが呼び出される THEN システム SHALL MCP (Model Context Protocol) を通じて AWS Documentation MCP Server および AWS Knowledge MCP Server から最新情報を取得する
3. WHEN 問題生成エージェントが呼び出される THEN システム SHALL 取得した情報を基に実際のビジネスシナリオを想定した複雑な問題文を生成する
4. WHEN 問題生成エージェントが選択肢を生成する THEN システム SHALL 1 つの正解と 3 つの説得力のある不正解選択肢を Professional レベルで生成する
5. WHEN 品質管理エージェントが呼び出される THEN システム SHALL 生成された問題の技術的正確性と適切な難易度を検証する
6. WHEN エージェント間の連携が発生する THEN システム SHALL ストリーミング対応により各エージェントの処理状況をリアルタイムで監視する
7. IF 生成された問題が品質基準を満たす THEN システム SHALL 問題をデータベースに保存し、学習者に提供する
8. IF 生成された問題が品質基準を満たさない THEN システム SHALL 問題を破棄し、再生成を試行する

### Requirement 4

**User Story:** As a システム管理者, I want MCP 統合により特定の AWS サービスやトピックに基づいて問題を生成できる機能, so that 体系的で網羅的な学習コンテンツを提供することができる

#### Acceptance Criteria

1. WHEN システム管理者が問題生成を指示する THEN システム SHALL 特定の AWS サービス（EC2、S3、VPC 等）またはトピック（セキュリティ、コスト最適化等）を指定できる
2. WHEN 特定のサービスが指定される THEN AWS 情報取得エージェント SHALL MCP Server を通じてそのサービスの高度な機能、制限事項、ベストプラクティスに関する最新情報を取得する
3. WHEN 特定のトピックが指定される THEN システム SHALL そのトピックに関連する複数の AWS サービスを組み合わせた統合的な問題を生成する
4. IF 指定されたサービスまたはトピックの情報が不足している THEN システム SHALL MCP Client を通じて AWS Documentation MCP Server から追加情報を自動取得する
5. WHEN MCP Server との通信が発生する THEN システム SHALL uvx コマンドによる標準化されたサーバー起動方式を使用する

### Requirement 5

**User Story:** As a システム管理者, I want AI エージェントが生成した問題の品質を管理できる機能, so that 学習者に正確で適切な難易度の問題を提供することができる

#### Acceptance Criteria

1. WHEN AI エージェントが問題を生成する THEN システム SHALL Amazon Bedrock Citations API を使用して AWS 公式ドキュメントとの整合性を自動検証する
2. WHEN 品質検証を実行する THEN システム SHALL LLM による技術的正確性チェックと引用元情報を取得する
3. WHEN 問題の品質に問題がある THEN システム SHALL 具体的な問題点と参照すべき公式ドキュメントを示して自動修正または再生成する
4. WHEN 解説を生成する THEN システム SHALL Citations API を活用して引用元（ページ番号、具体的な文章）を含む詳細な解説を作成する
5. IF 複数回の再生成でも品質基準を満たさない THEN システム SHALL エラーログと引用元情報を記録し、管理者に通知する
6. IF 生成された問題が既存の問題と類似度が高い THEN システム SHALL 重複を避けるため問題を再生成する

### Requirement 6

**User Story:** As a システム管理者, I want AgentCore Runtime 上で動作するエージェントが定期的に新しい問題を配信できる機能, so that 継続的な学習機会を組織に提供できる

#### Acceptance Criteria

1. WHEN システム管理者が配信スケジュールを設定する THEN システム SHALL EventBridge スケジュールから AgentCore Runtime を呼び出して自動的に新しい問題を Teams チャネルに投稿する
2. WHEN 新しい問題が投稿される THEN システム SHALL 前回の問題の参加状況（参加者数、正答率等）を簡潔に表示する
3. WHEN 問題配信が完了する THEN システム SHALL AgentCore のオブザーバビリティ機能により配信ログを記録し、参加状況を分析できるデータを蓄積する
4. WHEN エージェント処理中にエラーが発生する THEN システム SHALL CloudWatch Logs および AgentCore トレース機能によりエラー内容を記録し、管理者に通知する
5. IF Bedrock の分間クォータに達する THEN システム SHALL 複数のモデル（Claude Opus 4、Claude Sonnet 4、Claude 3.7 Sonnet、Claude 3 Haiku）を使い分けてリトライを実行する
