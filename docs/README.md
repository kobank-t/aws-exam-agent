# AWS Exam Agent ドキュメント

AWS Exam Agent プロジェクトの包括的なドキュメント集です。

## 📚 ドキュメント構成

### 🚀 セットアップ・デプロイ

| ドキュメント | 用途 | 対象者 | 更新日 |
|-------------|------|--------|--------|
| [**デプロイガイド**](./deployment-guide.md) | 新規環境への完全デプロイ手順 | 開発者・運用者 | 2025-08-26 |

### 🔧 運用・保守

| ドキュメント | 用途 | 対象者 | 更新日 |
|-------------|------|--------|--------|
| [**運用ガイド**](./operations-guide.md) | 日常運用・監視・メンテナンス | 運用者 | 2025-08-24 |
| [**トラブルシューティング**](./troubleshooting-guide.md) | 問題解決・調査手法 | 開発者・運用者 | 2025-08-24 |

### 🧪 開発・品質管理

| ドキュメント | 用途 | 対象者 | 更新日 |
|-------------|------|--------|--------|
| [**テストガイド**](./testing-guide.md) | テスト戦略・実装手順・品質基準 | 開発者 | 2025-08-26 |
| [**セキュリティガイド**](./security-guide.md) | セキュリティ機能・運用考慮事項 | 開発者・運用者 | 2025-08-26 |

### 📖 リファレンス

| ドキュメント | 用途 | 対象者 | 更新日 |
|-------------|------|--------|--------|
| [**環境変数リファレンス**](./environment-variables-guide.md) | 環境変数設定の詳細 | 開発者 | 2025-08-24 |

## 🎯 用途別クイックガイド

### 新しい環境にデプロイしたい
→ [**デプロイガイド**](./deployment-guide.md)

**含まれる内容:**
- AWS SSO の設定方法
- AgentCore のデプロイ手順
- Lambda + EventBridge Scheduler のデプロイ
- 動作確認・テスト手順
- 利用可能なスクリプト一覧

### 既存環境の運用・監視をしたい  
→ [**運用ガイド**](./operations-guide.md)

**含まれる内容:**
- 監視・ログ確認方法
- 日常的なメンテナンス
- 設定変更手順
- アラート・通知設定
- コスト管理

### テストを実装・品質管理をしたい
→ [**テストガイド**](./testing-guide.md)

**含まれる内容:**
- 契約による設計アプローチ
- Given-When-Thenパターン
- テストコメント統一フォーマット
- 品質チェック自動化
- カバレッジ基準・実装手順

### セキュリティを確保したい
→ [**セキュリティガイド**](./security-guide.md)

**含まれる内容:**
- 認証・認可機能
- データ保護・暗号化
- ネットワークセキュリティ
- 監査・ログ管理
- セキュリティベストプラクティス

### 問題が発生した・調査したい
→ [**トラブルシューティング**](./troubleshooting-guide.md)

**含まれる内容:**
- 問題の分類と診断フロー
- 認証・権限関連の問題
- AgentCore・Lambda・EventBridge の問題
- ネットワーク・接続関連の問題
- 高度なトラブルシューティング手法

### 環境変数の設定を確認したい
→ [**環境変数リファレンス**](./environment-variables-guide.md)

**含まれる内容:**
- 環境変数の詳細説明
- 設定例とベストプラクティス

## 🏗️ システム構成

```
EventBridge Scheduler → Lambda Function → AgentCore Runtime → Bedrock Models
     (定期実行)         (トリガー関数)      (問題生成AI)        (Claude等)
        ↓                    ↓                  ↓
   CloudWatch Events    CloudWatch Logs   CloudWatch Logs
```

## 🛠️ 利用可能なスクリプト

### デプロイ関連

| スクリプト | 用途 |
|------------|------|
| `./scripts/deploy-agentcore.sh` | AgentCore のデプロイ |
| `./scripts/deploy-eventbridge-scheduler.sh` | EventBridge Scheduler のデプロイ |
| `./scripts/build-lambda.sh` | Lambda関数のビルド |

### 確認・テスト関連

| スクリプト | 用途 |
|------------|------|
| `./scripts/get-agentcore-arn.sh` | AgentCore ARN確認 |
| `./scripts/show-agentcore-logs.sh` | AgentCore ログ確認 |

### 削除・クリーンアップ関連

| スクリプト | 用途 |
|------------|------|
| `./scripts/cleanup-source-resources.sh` | 移行元リソース削除 |

### 開発・品質管理関連

| スクリプト | 用途 |
|------------|------|
| `./scripts/setup-dev.sh` | 開発環境セットアップ |
| `./scripts/python-quality-check.sh` | Python品質チェック・テスト実行 |
| `./scripts/infrastructure-quality-check.sh` | インフラ品質チェック |

## 🚨 既知の制限事項

### Bedrock モデルアクセス制限

**現象**: AgentCore でのモデル呼び出し時に AccessDeniedException が発生

**原因**: 
- Service Control Policy (SCP) による制限
- クロスリージョン推論による意図しないリージョンへのアクセス

**対応**: 組織管理者にSCP制限の解除を依頼

詳細は [トラブルシューティングガイド](./troubleshooting-guide.md) を参照してください。

## 🔄 ドキュメント更新履歴

### 2025-08-26
- **テストガイドを新規作成**: 契約による設計・Given-When-Thenパターン・コメント統一フォーマット
- **セキュリティガイドを新規作成**: 包括的なセキュリティ機能と運用考慮事項
- **デプロイガイドを更新**: 最新の手順とスクリプトを反映
- **品質管理基盤を強化**: 自動化された品質チェック・テストカバレッジ基準

### 2025-08-24
- **docs構成を整理・統合**: 重複情報を排除し、4つの主要ドキュメントに統合
- **デプロイガイドを完全版に更新**: 最新の移行手順を反映、手動ARN入力方式を採用
- **EventBridge Scheduler実行確認を追加**: 実際のテスト実行手順を追加
- **運用ガイドを新規作成**: 日常運用に必要な情報を体系化
- **トラブルシューティングガイドを新規作成**: 問題解決の体系的なアプローチを提供

## 📞 サポート

### 問題報告・機能要望
- **GitHub Issues**: バグ報告・機能要望の投稿

### 開発・運用記録
- **作業記録**: [WORK_LOG.md](../WORK_LOG.md) - 日々の作業記録
- **設計判断記録**: [技術選択記録](../.kiro/specs/aws-exam-agent/design/09-decisions.md) - アーキテクチャ決定の記録

### 関連リソース
- **プロジェクト仕様書**: [.kiro/specs/aws-exam-agent/](../.kiro/specs/aws-exam-agent/) - 詳細な設計書・仕様書
- **スクリプト集**: [scripts/](../scripts/) - 自動化スクリプト
- **インフラ定義**: [infrastructure/](../infrastructure/) - CloudFormation テンプレート

## 🎯 次のステップ

1. **新規デプロイの場合**: [デプロイガイド](./deployment-guide.md) から開始
2. **既存環境の運用**: [運用ガイド](./operations-guide.md) を参照
3. **問題が発生した場合**: [トラブルシューティング](./troubleshooting-guide.md) で解決方法を確認
