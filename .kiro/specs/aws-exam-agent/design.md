# AWS Exam Coach 設計書

## 📚 設計書構成

### 基本設計

- [01. システム概要・設計原則](./design/01-overview.md) - システム概要・設計原則・プロジェクト目的
- [02. アーキテクチャ](./design/02-architecture.md) - 全体構成・主要コンポーネント・技術スタック

### 詳細設計

- [03. AI 問題生成エンジン](./design/03-ai-engine.md) - Bedrock AgentCore・Strands Agents・問題生成アルゴリズム
- [04. Teams 連携システム](./design/04-teams-integration.md) - Power Automate・メッセージ配信・リアクション分析
- [05. データモデル](./design/05-data-models.md) - DynamoDB 設計・キャッシュ戦略・アクセスパターン

### 運用・品質

- [06. デプロイメント](./design/06-deployment.md) - SAM・CI/CD・AgentCore デプロイ・トリガー設計
- [07. エラーハンドリング](./design/07-error-handling.md) - エラー分類・対応戦略・監視・復旧手順
- [08. テスト戦略](./design/08-testing.md) - テスト自動化・品質保証・性能テスト

### 記録

- [09. 技術選択記録](./design/09-decisions.md) - 設計判断・見送り理由・学習重視の判断基準

## 🎯 設計書の特徴

### 学習重視のアプローチ

- **単一環境**: 環境分離は不要（学習用途のため）
- **シンプル設計**: 複雑な機能より理解しやすい実装を優先
- **段階的実装**: MVP → 機能拡張の順次開発
- **公式ツール活用**: AWS 公式ツール・サービスの積極的利用

### app 配下集約の構成

```
aws-exam-coach/
├── app/                          # 全ソースコード集約
│   ├── lambda/                   # Lambda関数
│   ├── agent/                    # AgentCore用
│   └── shared/                   # 共通モジュール
├── tests/                        # テストコード
├── infrastructure/               # インフラ定義
└── scripts/                      # デプロイ・運用スクリプト
```

### 技術スタック概要

- **AI 基盤**: Bedrock AgentCore + Strands Agents
- **バックエンド**: Python 3.12 + API Gateway + Lambda
- **データベース**: DynamoDB (単一テーブル設計)
- **Teams 統合**: Power Automate + HTTP API
- **デプロイ**: AWS SAM + GitHub Actions

## 📖 設計書の使い方

### 実装時の参照順序

1. **[システム概要](./design/01-overview.md)** でプロジェクト全体を把握
2. **[アーキテクチャ](./design/02-architecture.md)** で技術構成を理解
3. 実装する機能に応じて詳細設計を参照
4. **[デプロイメント](./design/06-deployment.md)** でデプロイ手順を確認

### 分割による利点

- **高速アクセス**: 必要な情報に直接アクセス
- **並行作業**: 複数人での同時編集可能
- **メンテナンス性**: 部分的な更新が容易
- **レビュー効率**: セクション別の集中レビュー

### 更新時の注意事項

- 関連するセクション間の整合性を保つ
- 技術選択の変更は [09. 技術選択記録](./design/09-decisions.md) に記録
- 新しい設計判断は適切なセクションに追加

## 🚀 次のステップ

設計承認後、[実装タスクリスト](./tasks.md)の作成に進みます。
