# 技術選択記録

## Amazon S3 Vectors の検討結果 (2025 年 7 月 29 日)

### 検討背景

問題類似度チェックの高度化を目的として、Amazon S3 Vectors の適用可能性を検討しました。

### S3 Vectors の特徴

- **目的**: ベクトルデータの専用ストレージ・検索サービス
- **コスト**: 従来比最大 90%のコスト削減
- **性能**: サブ秒クエリ性能、数十億ベクトルまでスケール
- **統合**: Amazon Bedrock Knowledge Bases、OpenSearch Service との連携
- **状態**: プレビュー段階（2025 年 7 月時点）

### 適用可能箇所の検討

1. **問題類似度チェックの高度化**: 現在のキーワードベース手法をセマンティック検索に置換
2. **知識ベース検索の強化**: AWS 公式ドキュメントのベクトル化・検索

### 見送り理由

1. **プレビュー段階のリスク**: 本番利用には時期尚早、API 仕様変更の可能性
2. **MVP 原則との整合性**: シンプル・迅速な実装を優先する設計方針に反する
3. **十分な精度**: 現在のキーワードベース簡素化アプローチでも実用的
4. **開発工数**: ベクトル化処理の実装により複雑性が増加
5. **コスト**: 小規模利用では従来手法の方が安価

### 将来的な導入検討タイミング

- S3 Vectors が GA（一般提供）になった時点
- 問題データベースが 1000 問以上に拡大した時点
- より高精度な類似度チェックが必要になった時点

### 結論

現在の設計は実用的でシンプルであり、MVP 段階では最適な選択。S3 Vectors は将来の拡張オプションとして継続検討。

## Playwright MCP Server の選択 (2025 年 8 月 1 日)

### 検討背景

E2E テスト自動化と AI エージェント連携を目的として、Playwright MCP Server の導入を検討しました。

### 検討した選択肢

1. **Microsoft 公式版**: `microsoft.playwright-mcp@latest`
2. **Execute Automation 版**: `executeautomation.mcp-playwright@latest`
3. **@playwright/mcp 版**: `@playwright/mcp@latest`

### 選択結果: @playwright/mcp@latest

#### 選択理由

- **パッケージ存在確認**: npm レジストリに実在するパッケージ
- **適切なコマンド**: Node.js/TypeScript ベースのため `npx` が適切
- **標準的な命名**: `@playwright/` スコープは公式に近い信頼性
- **動作確認済み**: uvx/npx 両方での接続エラーが解消

#### 他選択肢の問題点

- **Microsoft 公式版**: パッケージレジストリに存在せず接続エラー
- **Execute Automation 版**: Trust Score 8.5、サードパーティ依存

### 技術的利点

#### MCP 統合による機能

- **AI エージェント連携**: AI が直接ブラウザ操作を実行可能
- **リアルタイム検証**: 開発中の機能を即座にテスト実行
- **自動デバッグ**: テスト失敗時の原因分析・修正提案
- **学習効率向上**: AI がテストパターンを学習・提案

#### 具体的な活用例

```typescript
// AI エージェントが自動実行するテストパターン
test("AI支援による問題配信フロー検証", async ({ page, request }) => {
  // 1. API経由での問題生成
  const response = await request.post("/api/generate", {
    data: { service: "EC2", topic: "VPC" },
  });

  // 2. Teams UIでの問題表示確認
  await page.goto("https://teams.microsoft.com/...");
  await expect(page.locator('[data-testid="question"]')).toBeVisible();

  // 3. AIが問題内容の妥当性を自動判定
  const questionText = await page
    .locator('[data-testid="question-text"]')
    .textContent();
  // AI エージェントが問題品質を評価・レポート
});
```

### 学習効果

- **Playwright API**: モダンな E2E テストフレームワーク
- **MCP 統合**: Model Context Protocol を通じた AI 連携
- **TypeScript**: 型安全なテストコード作成
- **AI 協調開発**: AI エージェントとの協調によるテスト自動化

### 設定詳細

```json
{
  "playwright": {
    "command": "npx",
    "args": ["@playwright/mcp@latest"],
    "env": {
      "FASTMCP_LOG_LEVEL": "ERROR"
    },
    "disabled": false,
    "autoApprove": []
  }
}
```

## その他の技術選択記録

### 1. データベース選択: DynamoDB vs RDS

#### 検討した選択肢

- **DynamoDB**: NoSQL、サーバーレス、単一テーブル設計
- **RDS (PostgreSQL)**: リレーショナル、正規化設計

#### 選択結果: DynamoDB

**理由:**

- **サーバーレス統合**: Lambda + API Gateway との親和性
- **コスト効率**: 従量課金、アイドル時コスト 0
- **運用負荷**: インフラ管理不要
- **スケーラビリティ**: 自動スケーリング

**トレードオフ:**

- **学習コスト**: 単一テーブル設計の習得が必要
- **クエリ制限**: 複雑な JOIN クエリが困難

### 2. AI エージェント基盤: Bedrock AgentCore vs 自前実装

#### 検討した選択肢

- **Bedrock AgentCore + Strands Agents**: AWS マネージドサービス
- **自前実装**: LangChain + Lambda

#### 選択結果: Bedrock AgentCore + Strands Agents

**理由:**

- **最新技術学習**: プレビュー段階の最新サービス体験
- **統合性**: AWS エコシステムとの親和性
- **MCP 統合**: 標準化されたプロトコル対応
- **運用性**: マネージドサービスによる安定性

**トレードオフ:**

- **プレビューリスク**: 仕様変更の可能性
- **学習コスト**: 新しいフレームワークの習得

### 3. Teams 統合: Teams App vs Power Automate

#### 検討した選択肢

- **Teams App**: カスタムアプリケーション開発
- **Power Automate**: ローコード統合

#### 選択結果: Power Automate

**理由:**

- **開発速度**: ローコード開発による迅速な実装
- **運用コスト**: サーバーレス、従量課金
- **メンテナンス性**: GUI ベースの設定変更
- **学習目的**: 複雑な開発より理解しやすい実装

**トレードオフ:**

- **機能制限**: カスタム UI の実装困難
- **依存性**: Microsoft 365 環境への依存

### 4. 環境構成: 複数環境 vs 単一環境

#### 検討した選択肢

- **複数環境**: dev/staging/prod の 3 環境構成
- **単一環境**: production のみ

#### 選択結果: 単一環境

**理由:**

- **学習目的**: 環境管理の複雑性を避けて本質的な学習に集中
- **コスト効率**: 不要なリソース重複を回避
- **シンプル性**: 運用負荷の軽減

**トレードオフ:**

- **リスク**: 本番環境での直接テスト
- **学習機会**: 環境分離のベストプラクティス学習機会の減少

### 5. CI/CD ツール: GitHub Actions vs AWS CodePipeline

#### 検討した選択肢

- **GitHub Actions**: GitHub 統合 CI/CD
- **AWS CodePipeline**: AWS ネイティブ CI/CD

#### 選択結果: GitHub Actions

**理由:**

- **統合性**: GitHub リポジトリとの親和性
- **学習効果**: 広く使われているツールの習得
- **コスト**: パブリックリポジトリでは無料
- **柔軟性**: 豊富なアクションエコシステム

**トレードオフ:**

- **AWS 統合**: CodePipeline ほどの AWS 統合度はない
- **学習機会**: AWS ネイティブツールの学習機会減少

## 設計判断の記録

### 1. プロジェクト構成: app 配下集約

#### 判断内容

全ソースコードを `app` ディレクトリ配下に集約する構成を採用

#### 理由

- **明確な構造**: 全ソースコードが一箇所に集約
- **モジュール共有**: `shared` ディレクトリで共通コード管理
- **テスト効率**: `app` 配下のみをテスト対象に指定
- **デプロイ簡素化**: パス指定が明確

### 2. 設計書分割: 単一ファイル vs 複数ファイル

#### 判断内容

3,275 行の単一ファイルを 9 つのファイルに分割

#### 理由

- **可読性向上**: セクション別の集中レビュー
- **保守性向上**: 部分的な更新が容易
- **並行作業**: 複数人での同時編集可能
- **実装効率**: 必要な設計情報の迅速な特定

#### 分割構成

1. `01-overview.md` - システム概要・設計原則
2. `02-architecture.md` - 全体アーキテクチャ
3. `03-ai-engine.md` - AI 問題生成エンジン
4. `04-teams-integration.md` - Teams 連携システム
5. `05-data-models.md` - データモデル・DynamoDB
6. `06-deployment.md` - デプロイ・CI/CD
7. `07-error-handling.md` - エラーハンドリング
8. `08-testing.md` - テスト戦略
9. `09-decisions.md` - 技術選択記録（このファイル）

### 3. 類似度チェック: ベクトル検索 vs キーワードマッチング

#### 判断内容

複雑なベクトル類似度計算ではなく、シンプルなキーワードベース手法を採用

#### 理由

- **MVP 原則**: シンプルで早期リリース可能
- **十分な精度**: 実用的なレベルでの重複検出
- **開発効率**: 複雑な実装を避けて迅速な開発
- **学習重視**: 本質的な機能に集中

#### 実装方式

```python
def _calculate_keyword_similarity(self, text1: str, text2: str) -> float:
    words1 = set(text1.split())
    words2 = set(text2.split())
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    return len(intersection) / len(union) if union else 0.0
```

## 学習重視の判断基準

### 基本方針

このプロジェクトは**スキルアップを目的とした学習用途**であり、以下の判断基準を適用：

1. **シンプル性優先**: 複雑な実装より理解しやすい設計
2. **学習効果重視**: 新しい技術の実践的な習得
3. **早期リリース**: MVP から開始して段階的に機能拡張
4. **公式ツール活用**: AWS 公式サービス・ツールの積極的利用

### 今後の判断指針

- **技術選択**: 学習効果と実用性のバランス
- **複雑性管理**: 必要最小限の機能から開始
- **品質確保**: テスト自動化による品質担保
- **継続改善**: フィードバックに基づく段階的改善

### 今後の展開

- **E2E テスト実装**: TypeScript + Playwright による自動テスト作成
- **AI 支援テスト**: MCP を通じた AI エージェントによるテスト実行
- **継続的品質確保**: CI/CD パイプラインでの自動テスト統合
