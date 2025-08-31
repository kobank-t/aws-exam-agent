# 環境変数設定ガイド

Cloud CoPassAgent の環境変数設定について説明します。

## 🔧 必須環境変数

| 変数名                          | 説明                                       | 例                                                                 | 設定場所      |
| ------------------------------- | ------------------------------------------ | ------------------------------------------------------------------ | ------------- |
| `POWER_AUTOMATE_WEBHOOK_URL`    | Teams 連携用 Webhook URL                   | `https://prod-XX.japaneast.logic.azure.com/workflows/...`          | .env ファイル |
| `POWER_AUTOMATE_SECURITY_TOKEN` | Webhook URL 漏洩対策用セキュリティトークン | `cef26f0de574983a475345f2e3518abbd6472d102b5254384ef6912931f8a68f` | .env ファイル |

## 💻 環境変数の設定

### .env ファイルの作成

プロジェクトルートに `.env` ファイルを作成：

```bash
# セキュリティトークンの生成（64文字のランダム文字列）
SECURITY_TOKEN=$(openssl rand -hex 32)

# .envファイルの作成
cat > .env << EOF
# Teams 連携（必須）
POWER_AUTOMATE_WEBHOOK_URL=https://prod-XX.japaneast.logic.azure.com/workflows/YOUR-WORKFLOW-ID/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=YOUR-SIGNATURE

# セキュリティトークン（必須）
POWER_AUTOMATE_SECURITY_TOKEN=$SECURITY_TOKEN
EOF
```

### Power Automate Webhook URL の取得方法

1. **Microsoft Teams** で Power Automate フローを作成
2. **HTTP 要求の受信時** トリガーを設定
3. **Teams にメッセージを投稿** アクションを追加
4. 生成された **HTTP POST URL** をコピー

### Power Automate セキュリティトークン設定

セキュリティトークンによる Webhook URL 漏洩対策を設定：

1. **Power Automate フロー** で「HTTP 要求の受信時」トリガーを選択
2. **条件** アクションを追加
3. **条件式** を以下のように設定：
   ```
   @equals(triggerBody()?['security_token'], 'YOUR_SECURITY_TOKEN_HERE')
   ```
4. **「はい」の場合** に Teams 投稿アクションを配置
5. **「いいえ」の場合** は何もしない（不正なリクエストを無視）

**重要**: `YOUR_SECURITY_TOKEN_HERE` を `.env` ファイルで生成したセキュリティトークンに置き換えてください。

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
- **セキュリティトークン**: Webhook URL 漏洩時の不正利用を防ぐため、64 文字のランダムトークンで認証
- **二重認証**: Power Automate 側でセキュリティトークンを検証し、正しいトークンの場合のみ Teams 投稿を実行

## 🔍 トラブルシューティング

### よくある問題

1. **Webhook URL 未設定エラー**:

   ```
   ❌ POWER_AUTOMATE_WEBHOOK_URL が .env ファイルに設定されていません
   ```

   → `.env` ファイルに正しい Webhook URL を設定

2. **セキュリティトークン未設定エラー**:

   ```
   ❌ POWER_AUTOMATE_SECURITY_TOKEN が .env ファイルに設定されていません
   ```

   → `.env` ファイルに 64 文字のセキュリティトークンを設定

3. **Teams 投稿失敗（認証エラー）**:

   ```
   Teams投稿完了 (HTTP 202) だが、実際にはTeamsに投稿されない
   ```

   → Power Automate フローのセキュリティトークン条件が正しく設定されているか確認

4. **Teams 投稿失敗（一般エラー）**:

   ```
   Teams投稿に失敗しました: HTTP 400/401/403
   ```

   → Power Automate フローが有効か、Webhook URL が正しいか確認

5. **環境変数読み込み失敗**:
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
