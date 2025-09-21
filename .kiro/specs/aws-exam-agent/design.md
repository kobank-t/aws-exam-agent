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
    options: List[str]      # 選択肢（A-D以上、太字記法使用）
    correct_answer: str     # 正解（A, B, C, D...のラベルのみ）
    explanation: str        # 詳細解説
    source: List[str]       # AWS公式ドキュメントURL（MCP Server検証済み）

    # 新機能: 試験ガイド活用による問題分類表示
    learning_domain: str    # 学習分野分類（汎用的な命名）
    primary_technologies: List[str]  # 主要技術要素リスト（最大3つ）
    learning_insights: str  # 試験ガイドに基づく学習戦略と試験対策ポイント（explanationとは独立した学習支援情報）

class AgentOutput:
    questions: List[Question]  # 生成された問題のリスト（複数問題対応）

class AgentInput:
    exam_type: str          # 試験の種類（現在: "SAP"、新機能で"AWS-SAP-C02"等のファイル名ベースに変更予定）
    category: List[str]     # 試験ガイド記載のカテゴリ（現状は限定的活用、新機能で自動判定に移行予定）
    question_count: int     # 生成する問題数（1-5問）
```

### Teams 投稿処理

```python
# 実際の実装では、AgentOutputを直接Power Automate Webhookに送信
# 専用のTeamsPostモデルは使用せず、シンプルな構成を採用

class TeamsClient:
    async def send(self, agent_output: AgentOutput) -> None:
        # AgentOutputをそのままPower Automate Webhookに送信
        # Power Automate側でAdaptive Card形式に変換・Teams投稿・Microsoft Lists登録を実行
```

## AI エンジン設計

### 問題生成プロセス

1. **試験ガイド読み込み**: `AgentInput.exam_type` に基づく動的ガイド選択
2. **コンテキスト統合**: 試験ガイド + MCP Server からの AWS 公式情報統合
3. **問題生成**: Claude 3.5 Sonnet による Professional レベル問題作成
4. **分類情報生成**: 学習分野・主要技術・ガイド参照の自動判定
5. **品質検証**: AWS 公式ドキュメント参照による正確性確認
6. **構造化**: 問題・選択肢・解説・分類情報の適切な構造化

### 試験ガイド統合設計

#### 動的ガイド選択機能

- **ファイル構造**: `data/exam_guides/{exam_type}.md`
- **選択ロジック**: `AgentInput.exam_type` による動的選択
- **フォールバック**: 存在しない場合はデフォルトガイド（AWS-SAP-C02.md）使用
- **拡張性**: 他クラウドプロバイダー（Azure、GCP、OCI 等）対応可能
- **既存フィールドの扱い**:
  - `AgentInput.exam_type`: 現在"SAP"デフォルト → 新機能で"AWS-SAP-C02"デフォルトに変更（ファイル名と一致、他クラウド対応）
  - `AgentInput.category`: 現状維持、将来的に試験ガイドからの自動判定に移行検討
- **汎用性確保**: Azure（"AZ-104"）、GCP（"ACE"）、OCI（"1Z0-1085"）等の将来対応を考慮した命名規則

#### 段階的実装アプローチ

**基本実装: シンプルなファイル読み込み + プロンプト統合**

- **狙い**: 最小限の実装で機能検証
- **方法**: 試験ガイド全体をシステムプロンプトに含める
- **実装**: ファイル読み込み → プロンプトコンテキスト統合
- **課題**: トークン制限に引っかかる可能性

**拡張実装: 必要に応じて圧縮機能追加**

- **狙い**: トークン制限対応とコンテキスト最適化
- **方法**: LLMLingua 等による試験ガイド圧縮
- **効果**: コンテキストサイズを約 1/3 に削減
- **実装**: 圧縮ライブラリ統合 → 動的圧縮処理

**最適化実装: 動的コンテキスト選択で最適化**

- **狙い**: トークン効率と問題品質の両立
- **方法**: カテゴリに基づく関連セクションの動的抽出
- **効果**: 必要な情報のみでコンテキストサイズを最小化
- **実装**: セクション解析 → 関連度計算 → 動的選択

#### 実装判断基準

- **基本実装 → 拡張実装**: トークン制限エラーが発生した場合
- **拡張実装 → 最適化実装**: より精密なコンテキスト制御が必要な場合
- **各フェーズで機能検証**: 問題品質・分類精度・システム安定性を評価

#### 分類情報生成ロジック

```python
# 学習分野判定
learning_domain: str = "試験ガイドで定義されたコンテンツ分野から自動判定"

# 主要技術要素抽出（最大3つ）
primary_technologies: List[str] = [
    "問題で扱われる主要な技術・サービス",
    "クラウドプロバイダー非依存の汎用的命名",
    "最大3つまでの重要度順"
]

# 学習戦略生成
learning_insights: str = "試験ガイドに基づく学習戦略と試験対策ポイント（出題傾向、学習優先度、よくある間違い、実務経験による有利/不利、効果的な学習方法を含む構造化された学習支援情報）"
```

#### プロンプト設計方針

**システムプロンプト（固定）**:

- 既存の問題生成品質要件を維持
- 汎用的な役割定義・品質チェック項目
- 分類情報生成の基本指示を追加

**実行時プロンプト（動的）**:

- 試験ガイド内容の動的統合（ファイル読み込み）
- exam_type に基づく試験固有のコンテキスト提供
- 分類情報（learning_domain, primary_technologies, learning_insights）の具体的生成指示

**コンテキスト統合方式**:

- 実行時プロンプトに試験ガイド内容を含める
- MCP Server 情報との適切なバランス
- トークン制限を考慮した段階的アプローチ

**品質保証**:

- 既存の技術的正確性要件を継続
- 分類情報の一貫性・正確性を追加
- 試験ガイドとの整合性確保

### 学習戦略支援機能設計

**learning_insights フィールドの設計思想**:

- **差別化**: `explanation`（問題解説）と`learning_insights`（学習戦略）の明確な役割分担
- **試験特化**: 試験合格のための戦略的学習支援に特化
- **構造化**: 【】区切りによる情報の整理と視認性向上

**生成内容の構造**:

```
【試験対策】出題頻度★評価、学習優先度
【よくある間違い】受験者が陥りやすいミス・混同
【学習戦略】推奨学習順序・効果的な学習方法
【実務経験差】実務経験による有利/不利・補強方法
【関連項目】他の試験分野との関連性
【効果的な学習方法】ハンズオン・ユースケース研究等
```

**学習効果の最大化**:

- **効率的学習**: 重要度に基づく優先学習の支援
- **ミス防止**: よくある間違いの事前把握
- **経験活用**: 実務経験の効果的な活用方法
- **体系的学習**: 関連分野との繋がりを意識した学習

### MCP 統合

- **AWS Documentation MCP Server**: `uvx awslabs.aws-documentation-mcp-server`
- **技術的正確性**: 最新の AWS 公式ドキュメント参照
- **標準化**: Model Context Protocol による統一的なコンテキスト提供

## ジャンル分散機能設計（実装完了）

### 問題の背景

従来の実装では、AI エージェントが試験ガイド全体を参照して問題を生成するため、特定のジャンル（例：「複雑な組織に対応するソリューションの設計」）に偏る傾向がありました。これにより、試験ガイドの全領域をバランス良く学習できない問題が発生していました。

### 実装完了機能

**✅ 完了した機能**:

- AgentCore Memory による学習分野履歴管理
- プロンプトレベルでの分散指示生成
- 最近使用分野の自動取得・除外指示
- Memory 管理スクリプト（`scripts/manage-agentcore-memory.sh`）

### 設計方針

- **AgentCore Memory 活用**: AWS マネージドサービスによる履歴管理
- **プロンプトレベル制御**: 除外指示による分散実現
- **短期メモリ活用**: 最近使用された学習分野の記録・参照（7 日間）
- **汎用性**: 異なる試験ガイド構造に対応可能な設計

### アーキテクチャ

#### AgentCore Memory 統合

```mermaid
graph TB
    A[問題生成開始] --> B[AgentCore Memory]
    B --> C[最近の分野履歴取得]
    C --> D[プロンプト生成]
    D --> E[AI エージェント]
    E --> F[問題生成]
    F --> G[使用分野記録]
    G --> B
```

#### メモリ管理設計

**短期メモリ活用**:

- **イベント記録**: 使用した学習分野情報を `CreateEvent` で記録
- **履歴参照**: `ListEvents` で最近の分野使用履歴を取得
- **自動管理**: AgentCore Memory による自動的な履歴管理

#### Namespace 設計ポリシー

**基本原則**:

- **階層構造**: AgentCore Memory の公式推奨に従った `/` 区切りの階層構造
- **機能明確化**: namespace 名から記録内容が明確に理解できる命名
- **段階的拡張**: 現在の実装から将来の拡張まで対応可能な設計
- **データモデル一貫性**: `Question` モデルのフィールド名と一貫した命名

**AgentCore Memory の公式構造**:

```
/strategy/{strategyId}/actor/{actorId}/session/{sessionId}
```

**Memory 作成時の namespace template**:

```python
"namespaces": ["{sessionId}"]  # session_idをそのまま使用
```

**実際の namespace 例**:

```
/strategy/semantic-12345/actor/cloud-copass-agent/session/learning-domains/AWS-SAP
```

**現在の実装**:

```python
actor_id = "cloud-copass-agent"
session_id = f"learning-domains/{exam_type}"  # learning-domains/AWS-SAP
```

**設計の整合性**:

- Memory 作成時: `{sessionId}` template
- 実装時: `session_id = "learning-domains/AWS-SAP"`
- 結果: `/session/learning-domains/AWS-SAP` (重複なし、意図通り)

**将来の拡張パターン**:

```python
# 問題統計分析機能追加時
session_id = "question-analytics/{exam_type}"  # question-analytics/AWS-SAP

# ユーザー進捗管理機能追加時
session_id = "user-progress/{user_id}/{exam_type}"  # user-progress/user123/AWS-SAP
```

**環境管理**:

- **Memory ID**: 環境変数 `AGENTCORE_MEMORY_ID` で管理
- **設定管理**: `.env` ファイルによる環境変数管理

**実装済みデータ構造**:

```python
# DomainMemoryClient 実装
class DomainMemoryClient:
    def __init__(self, memory_id: str, region_name: str):
        self.memory_client = MemoryClient(region_name=region_name)
        self.memory_id = memory_id
        self.actor_id = "cloud-copass-agent"

    async def record_domain_usage(self, learning_domain: str, exam_type: str) -> None:
        """学習分野の使用履歴を記録"""
        session_id = f"{exam_type}"  # "AWS-SAP"
        messages = [("user", learning_domain)]

        await self.memory_client.create_event(
            memory_id=self.memory_id,
            actor_id=self.actor_id,
            session_id=session_id,
            messages=messages
        )

    async def get_recent_domains(self, exam_type: str, days_back: int = 7) -> List[str]:
        """最近使用された学習分野を取得（重複除去済み）"""
        session_id = f"{exam_type}"
        cutoff_time = datetime.now() - timedelta(days=days_back)

        events = await self.memory_client.list_events(
            memory_id=self.memory_id,
            actor_id=self.actor_id,
            session_id=session_id,
            start_time=cutoff_time
        )

        # payloadから学習分野を抽出・重複除去
        domains = []
        for event in events:
            for message in event.payload:
                if message.conversational.role == "USER":
                    domains.append(message.conversational.content.text)

        return list(dict.fromkeys(domains))  # 順序保持で重複除去
```

#### 実装済みプロンプト制御ロジック

**統計ベース分散指示アプローチ**:

```python
# agent_main.py での実装
async def invoke(payload: dict[str, Any]) -> dict[str, Any]:
    # 最近使用された分野を取得（ジャンル分散機能）
    recent_domains = []
    if memory_client is not None:
        try:
            recent_domains = await memory_client.get_recent_domains(
                exam_type=input.exam_type, days_back=7
            )
        except Exception as e:
            logger.warning(f"最近の分野取得に失敗（処理継続）: {e}")

    # ジャンル分散指示の作成
    diversity_instruction = ""
    if recent_domains:
        from collections import Counter
        domain_counts = Counter(recent_domains)
        most_used_domains = [
            domain for domain, count in domain_counts.most_common(2)
        ]

        diversity_instruction = f"""
        # ジャンル分散指示（偏り防止）
        - 最近使用された学習分野の使用状況: {dict(domain_counts)}
        - 特に使用頻度の高い分野: {", ".join(most_used_domains) if most_used_domains else "なし"}
        - 学習効果を高めるため、使用頻度の低い分野を優先して問題を生成してください
        - 全ての学習分野をバランス良く出題することを重視してください
        - 適切な問題が作成できる範囲で、多様性を最優先してください
        """

    # 問題生成後の分野履歴記録
    if memory_client is not None:
        try:
            for question in agent_output.questions:
                await memory_client.record_domain_usage(
                    learning_domain=question.learning_domain,
                    exam_type=input.exam_type,
                )
        except Exception as e:
            logger.warning(f"分野履歴記録に失敗（処理継続）: {e}")
```

**設計方針**:

- **シンプル性**: learning_domain レベルでの分散制御に特化
- **段階的改善**: まず大分類レベルでの効果を検証
- **品質優先**: 分散よりも問題品質を優先する安全弁を設置
- **将来拡張**: 必要に応じて技術要素レベルの制御を追加可能

### Memory 管理機能（実装完了）

**管理スクリプト**: `scripts/manage-agentcore-memory.sh`

```bash
# Memory内容確認
./scripts/manage-agentcore-memory.sh show

# 詳細分析（ジャンル分散効果測定）
./scripts/manage-agentcore-memory.sh analyze

# 最新イベント以外削除
./scripts/manage-agentcore-memory.sh cleanup

# 全イベント削除（初期化）
./scripts/manage-agentcore-memory.sh clear
```

**分析機能**:

- 学習分野別使用統計
- 多様性比率計算（1.0 が最高）
- 使用頻度の偏り比率（最大/最小）
- 分散効果評価（良好/普通/要改善）
- 推奨アクション提示

**運用統合**:

- 日次確認: Memory 状況確認
- 週次分析: ジャンル分散効果測定
- 月次メンテナンス: 古いイベントクリーンアップ

詳細な運用方法は [運用ガイド](../../../docs/operations-guide.md#-agentcore-memory-管理) を参照。

## Teams 統合設計

### Power Automate フロー

1. **Webhook 受信**: AgentCore からの HTTP POST 受信
2. **Teams 投稿**: Adaptive Card 形式での問題投稿
3. **データ登録**: Microsoft Lists への問題データ保存

### Adaptive Card 設計

- **問題表示**: 問題文・選択肢の構造化表示
- **学習分野表示**: タイトル部分に「[絵文字 分野名] 問題タイトル」形式で表示
- **インタラクション**: 「回答を見る」ボタン
- **段階的表示**: 回答・解説の段階的な情報提示
- **学習戦略表示**: 問題解説とは別セクションでの学習支援情報表示
- **参考資料**: AWS 公式ドキュメントリンク
- **分類情報**: 主要技術要素・学習戦略の表示（解説部分）

**表示構成例**:

```
🎯 [複雑な組織に対応するソリューションの設計] AWS SAP問題

【問題】...
【選択肢】**A.** ... **B.** ...

【💡 学習戦略】
出題頻度★★★★☆、学習優先度最高
よくある間違い: OrganizationsとControl Towerの混同注意
学習順序: Control Tower → Organizations → IAM

【🔧 主要技術】
AWS Control Tower, AWS Organizations, AWS IAM

【解答・解説】（ボタンクリックで表示）
```

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
**最終更新**: 2025 年 9 月 22 日（ジャンル分散機能実装完了・Memory 管理機能追加）
