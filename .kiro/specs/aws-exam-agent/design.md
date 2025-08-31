# Cloud CoPassAgent 設計書

## 概要

**Cloud CoPassAgent**は、クラウド資格学習を通じて組織内のコミュニケーション(Co)を促し、合格とスキルの橋渡し(Pass)を支援する AI エージェントです。

### 設計原則

- **垂直スライス開発**: 水平レイヤーより完全な価値提供フローを優先
- **シンプル化**: 複雑な基盤構築を避け、動く価値の早期提供
- **品質とスピード両立**: 品質を妥協せず、効率的な開発プロセス
- **技術的正確性**: MCP 統合による AWS 公式ドキュメント参照

## 技術選択の記録

### なぜ AgentCore Runtime を選んだか

**選択理由**:

- **AWS 公式**: Bedrock AgentCore は AWS 公式のエージェント実行環境
- **MCP 統合**: Model Context Protocol の標準的な統合サポート
- **運用・監視**: CloudWatch との自動統合による運用の容易さ
- **学習効果**: 最新の AI エージェント技術の実践的習得

**代替案との比較**:

- Lambda 単体: MCP 統合の複雑さ、エージェント機能の制限
- ECS/Fargate: 運用コストの高さ、オーバーエンジニアリング
- 自前実装: 開発コストの高さ、品質リスク

### なぜシンプル化したか

**背景**:

- 当初設計: DynamoDB + 複雑なサービス層 + リアクション収集機能
- 実装判断: AgentCore 中心のシンプル構成に変更

**シンプル化の価値**:

- **早期価値提供**: 1 週間での Teams 投稿実現
- **品質向上**: 複雑性削減による品質管理の容易さ
- **学習効果**: 垂直スライス開発の実践的習得
- **フィードバック収集**: 実際のユーザー体験による改善点発見

**削除した機能と判断理由**:

- DynamoDB: MVP では永続化不要、Power Automate で十分
- リアクション収集: 次イテレーションで実装予定
- 複雑なサービス層: AgentCore で直接実装が効率的

## システムアーキテクチャ

### 実装済みシステム構成

```mermaid
graph LR
    A[EventBridge Scheduler] --> B[Lambda Function]
    B --> C[AgentCore Runtime]
    C --> D[MCP Server]
    D --> E[AWS Documentation]

    C --> F[Claude 3.5 Sonnet]
    F --> G[問題生成]
    G --> H[Power Automate]
    H --> I[Teams チャネル]
    H --> J[Microsoft Lists]

    I --> K[組織メンバー]
    K --> L[Adaptive Card]
    L --> M[回答・学習]
```

### 主要コンポーネント

#### 1. 問題生成システム（AgentCore Runtime）

- **実行環境**: AWS Bedrock AgentCore Runtime
- **AI モデル**: Claude 3.5 Sonnet
- **MCP 統合**: AWS Documentation MCP Server による技術的正確性確保
- **品質保証**: AWS 公式ドキュメント参照による正確性確保

#### 2. 配信システム（Power Automate + Teams）

- **自動投稿**: Adaptive Card 形式での構造化表示
- **データ登録**: Microsoft Lists（SharePoint）への問題履歴保存
- **ユーザー体験**: 「回答を見る」ボタンによる段階的情報提示

#### 3. 定期実行システム（EventBridge Scheduler）

- **自動実行**: 指定時間での問題生成・配信
- **監視**: CloudWatch Logs による実行状況記録
- **エラーハンドリング**: 障害時の適切なログ記録

## 技術スタック

### AI エージェント基盤

- **エージェントフレームワーク**: Strands Agents
- **実行環境**: AWS Bedrock AgentCore Runtime
- **LLM**: Amazon Bedrock Claude 3.5 Sonnet
- **MCP 統合**: AWS Documentation MCP Server

### バックエンド・インフラ

- **言語**: Python 3.12
- **パッケージ管理**: uv（高速・信頼性の高い依存関係管理）
- **定期実行**: EventBridge Scheduler → Lambda → AgentCore Runtime
- **監視**: CloudWatch Logs + X-Ray トレーシング

### 外部連携

- **Teams 統合**: Power Automate（Webhook → Teams 投稿 → Microsoft Lists 登録）
- **データ保存**: Microsoft Lists（SharePoint）による問題履歴管理
- **表示形式**: Adaptive Card による構造化表示

### デプロイ・運用

- **デプロイツール**: bedrock-agentcore-starter-toolkit
- **設定管理**: agentcore configure
- **品質管理**: Ruff（リンター・フォーマッター）+ Mypy（型チェック）+ pytest

## データモデル

### 問題データ構造

```python
class Question:
    question: str           # 問題文
    options: List[str]      # 選択肢（A-D以上）
    correct_answer: str     # 正解（A, B, C, D...）
    explanation: str        # 詳細解説
    service: str           # 対象AWSサービス
    quality_score: float   # 品質スコア
    reference_links: List[str]  # AWS公式ドキュメントリンク
```

### Teams 投稿データ

```python
class TeamsPost:
    question_data: Question
    post_time: datetime
    channel_id: str
    adaptive_card: dict    # Adaptive Card JSON
```

## AI エンジン設計

### 問題生成プロセス

1. **コンテキスト取得**: MCP Server から AWS 公式情報取得
2. **問題生成**: Claude 3.5 Sonnet による Professional レベル問題作成
3. **品質検証**: AWS 公式ドキュメント参照による正確性確認
4. **構造化**: 問題・選択肢・解説の適切な構造化

### MCP 統合

- **AWS Documentation MCP Server**: `uvx awslabs.aws-documentation-mcp-server`
- **技術的正確性**: 最新の AWS 公式ドキュメント参照
- **標準化**: Model Context Protocol による統一的なコンテキスト提供

## Teams 統合設計

### Power Automate フロー

1. **Webhook 受信**: AgentCore からの HTTP POST 受信
2. **Teams 投稿**: Adaptive Card 形式での問題投稿
3. **データ登録**: Microsoft Lists への問題データ保存

### Adaptive Card 設計

- **問題表示**: 問題文・選択肢の構造化表示
- **インタラクション**: 「回答を見る」ボタン
- **段階的表示**: 回答・解説の段階的な情報提示
- **参考資料**: AWS 公式ドキュメントリンク

## エラーハンドリング

### エラー分類

- **MCP 接続エラー**: AWS Documentation MCP Server 接続失敗
- **AI 生成エラー**: Claude 3.5 Sonnet 応答エラー
- **Teams 投稿エラー**: Power Automate 連携エラー

### エラー対応

- **ログ記録**: CloudWatch Logs への詳細エラー記録
- **処理継続**: エラー発生時の適切な処理継続
- **透明性**: エラー内容の明確な表示（フォールバック機能なし）

## テスト戦略

### 単体テスト

- **契約による設計**: 事前条件・事後条件・不変条件の検証
- **100% カバレッジ**: 新規作成コードの完全テスト
- **型安全性**: mypy による型チェック

### 統合テスト

- **エンドツーエンド**: 問題生成から Teams 投稿までの完全フロー
- **MCP 統合**: 実際の MCP Server との統合テスト
- **Power Automate**: 実際の Teams 環境での動作確認

## デプロイメント

### デプロイ手順

1. **環境準備**: `agentcore configure` による設定
2. **デプロイ実行**: `agentcore launch` による AWS 環境デプロイ
3. **動作確認**: 実際の問題生成・Teams 投稿確認

### 監視・運用

- **CloudWatch Logs**: 実行ログの監視
- **X-Ray トレーシング**: パフォーマンス監視
- **エラーアラート**: 障害時の通知

## 技術選択の判断理由

### なぜ AgentCore Runtime？

- **AWS 公式サポート**: 安定性・信頼性の確保
- **運用・監視**: CloudWatch Logs、X-Ray による容易な監視
- **スケーラビリティ**: サーバーレスアーキテクチャによる自動スケーリング

### なぜ MCP 統合？

- **標準化**: Model Context Protocol による統一的なコンテキスト提供
- **技術的正確性**: AWS 公式ドキュメント参照による正確性確保
- **保守性**: uvx による統一的なサーバー起動・管理

### なぜ Power Automate？

- **ノーコード/ローコード**: 迅速な Teams 連携実現
- **Adaptive Card**: 構造化された見やすい表示
- **Microsoft Lists 統合**: 問題履歴の自動管理

### なぜシンプル化？

- **開発速度**: 複雑な基盤構築を回避して価値提供に集中
- **保守性**: 理解しやすく変更しやすいコード
- **品質**: シンプルなコードによるバグ削減

## プロジェクト構成

詳細なディレクトリ構成とセットアップ手順については、プロジェクト直下の `README.md` を参照してください。

### 構成の設計原則

- **AgentCore 中心**: 全機能を agent_main.py に集約
- **シンプル構造**: 不要な複雑性を排除
- **品質保証**: 100% テスト通過、型安全性確保
- **3 層アーキテクチャ**: docs/（汎用ガイド）、specs/（プロジェクト固有）、steering/（汎用ノウハウ）

---

**作成日**: 2025 年 8 月 26 日  
**基準**: requirements.md の実装済み MVP 要件に基づく統合設計書  
**更新方針**: 要件変更時のみ更新、実装詳細は docs/ 配下のガイドを参照
