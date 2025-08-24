# 環境変数設定ガイド

AWS Exam Agent の環境変数設定について説明します。

## 🔧 必須環境変数

| 変数名 | 説明 | 例 | 設定場所 |
|--------|------|----|----------|
| `POWER_AUTOMATE_WEBHOOK_URL` | Teams 連携用 Webhook URL | `https://prod-XX.japaneast.logic.azure.com/workflows/...` | .env ファイル |

## 💻 環境変数の設定

### .env ファイルの作成

プロジェクトルートに `.env` ファイルを作成：

```bash
# Teams 連携（必須）
POWER_AUTOMATE_WEBHOOK_URL=https://prod-XX.japaneast.logic.azure.com/workflows/YOUR-WORKFLOW-ID/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=YOUR-SIGNATURE
```

### Power Automate Webhook URL の取得方法

1. **Microsoft Teams** で Power Automate フローを作成
2. **HTTP要求の受信時** トリガーを設定
3. **Teams にメッセージを投稿** アクションを追加
4. 生成された **HTTP POST URL** をコピー

## 🚀 AgentCore での環境変数

AgentCore デプロイ時に、`.env` ファイルから自動的に読み込まれます：

```bash
# デプロイスクリプトが自動実行
./scripts/deploy-agentcore.sh
```

デプロイスクリプトは以下を自動実行：
1. `.env` ファイルから `POWER_AUTOMATE_WEBHOOK_URL` を読み込み
2. AgentCore に環境変数として設定
3. Teams 連携機能を有効化

## 🔒 セキュリティ考慮事項

- **Git 管理**: `.env` ファイルは `.gitignore` に含まれており、Git にコミットされません
- **最小権限**: Webhook URL のみを設定し、不要な認証情報は含めません
- **AWS 認証**: AgentCore では IAM Role による認証を使用（認証情報のハードコード不要）

## 🔍 トラブルシューティング

### よくある問題

1. **Webhook URL 未設定エラー**:
   ```
   ❌ POWER_AUTOMATE_WEBHOOK_URL が .env ファイルに設定されていません
   ```
   → `.env` ファイルに正しい Webhook URL を設定

2. **Teams 投稿失敗**:
   ```
   Teams投稿に失敗しました: HTTP 400/401/403
   ```
   → Power Automate フローが有効か、Webhook URL が正しいか確認

3. **環境変数読み込み失敗**:
   ```
   ⚠️ .env ファイルが見つかりません
   ```
   → プロジェクトルートに `.env` ファイルが存在するか確認

### デバッグ方法

```bash
# .env ファイルの確認
cat .env

# AgentCore ログでの確認
aws logs tail /aws/bedrock-agentcore/runtimes/agent_main-XXXXX-DEFAULT --since 1h | grep -i teams
```

## 📝 その他の設定

以下の設定は環境変数として設定する必要はありません：

- **AWS 認証情報**: IAM Role で自動認証
- **AWS リージョン**: `us-east-1` で固定
- **Bedrock モデル**: `amazon.nova-pro-v1:0` で固定（コスト最適化済み）
- **トークン数・温度**: Strands Agents で最適化済み
