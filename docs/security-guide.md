# Cloud CoPassAgent セキュリティガイド

Cloud CoPassAgent のセキュリティ機能と運用上のセキュリティ考慮事項について説明します。

## 🔒 セキュリティ機能概要

### 多層防御アーキテクチャ

```
┌─────────────────────────────────────────────────────────────┐
│ 1. AWS IAM Role ベース認証 (AgentCore ↔ AWS Services)      │
├─────────────────────────────────────────────────────────────┤
│ 2. セキュリティトークン認証 (AgentCore ↔ Power Automate)   │
├─────────────────────────────────────────────────────────────┤
│ 3. 環境変数による機密情報管理 (.env ファイル)               │
├─────────────────────────────────────────────────────────────┤
│ 4. Git 管理からの機密情報除外 (.gitignore)                 │
└─────────────────────────────────────────────────────────────┘
```

## 🛡️ セキュリティトークン認証システム

### 概要

Power Automate Webhook URL の漏洩対策として、セキュリティトークン認証を実装しています。

### 認証フロー

```
AWS AgentCore → Power Automate → セキュリティトークン検証 → Teams投稿
                                      ↓
                                 不正なトークン → 投稿拒否
```

### トークン仕様

- **長さ**: 64 文字（256 ビット相当）
- **形式**: 16 進数文字列
- **生成方法**: `openssl rand -hex 32`
- **有効期限**: 設定なし（手動更新推奨）

### 実装詳細

#### AgentCore 側

```python
# teams_client.py での実装
class TeamsClient:
    def __init__(self, webhook_url: str, security_token: str):
        # 事前条件: セキュリティトークンは64文字
        if len(security_token) != 64:
            raise ValueError("Security token must be 64 characters")

        self.webhook_url = webhook_url
        self.security_token = security_token

    def send(self, questions: List[Question]) -> requests.Response:
        payload = {
            "security_token": self.security_token,
            "questions": [q.dict() for q in questions]
        }
        return requests.post(self.webhook_url, json=payload)
```

#### Power Automate 側

```
条件: @equals(triggerBody()?['security_token'], 'CONFIGURED_TOKEN_VALUE')
├─ はい: Teams投稿実行
└─ いいえ: 処理終了（ログなし）
```

## 🔐 機密情報管理

### 環境変数による管理

機密情報は全て環境変数として管理し、コードへのハードコードを防止：

```bash
# .env ファイル例
POWER_AUTOMATE_WEBHOOK_URL=https://prod-XX.japaneast.logic.azure.com/workflows/...
POWER_AUTOMATE_SECURITY_TOKEN=<64文字のランダム文字列>
```

### Git 管理からの除外

```gitignore
# .gitignore での設定
.env
.env.*
!.env.example
```

### セキュリティトークンの生成

```bash
# 新しいセキュリティトークンの生成
SECURITY_TOKEN=$(openssl rand -hex 32)
echo "生成されたセキュリティトークン: $SECURITY_TOKEN"

# .env ファイルへの設定
echo "POWER_AUTOMATE_SECURITY_TOKEN=$SECURITY_TOKEN" >> .env
```

## 🔑 AWS IAM セキュリティ

### 最小権限の原則

AgentCore 実行ロールは必要最小限の権限のみを付与：

#### Bedrock 権限

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": [
        "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-5-sonnet-20240620-v1:0"
      ]
    }
  ]
}
```

#### CloudWatch Logs 権限

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:log-group:/aws/bedrock-agentcore/*"
    }
  ]
}
```

## 🚨 セキュリティインシデント対応

### セキュリティトークン漏洩時の対応

#### 即座に実行すべき対応

1. **新しいセキュリティトークンの生成**

   ```bash
   # 新しいトークンを生成
   NEW_TOKEN=$(openssl rand -hex 32)
   echo "新しいセキュリティトークン: $NEW_TOKEN"
   ```

2. **環境変数の更新**

   ```bash
   # .env ファイルの更新
   sed -i '' "s/POWER_AUTOMATE_SECURITY_TOKEN=.*/POWER_AUTOMATE_SECURITY_TOKEN=$NEW_TOKEN/" .env
   ```

3. **Power Automate フローの更新**

   - Power Automate フローの条件設定を新しいトークンに更新
   - フローを保存して有効化

4. **AgentCore の再デプロイ**
   ```bash
   ./scripts/deploy-agentcore.sh
   ```

### Webhook URL 漏洩時の対応

1. **Power Automate フローの無効化**
2. **新しいフローの作成**（新しい Webhook URL）
3. **環境変数の更新**
4. **AgentCore の再デプロイ**
5. **古いフローの削除**

## 🔍 セキュリティ監査

### 定期的な監査項目

#### 月次監査

- [ ] 環境変数の確認（`.env` ファイルの存在と内容）
- [ ] IAM ロールの権限確認
- [ ] ログの監査（異常なアクセスパターンの検出）

#### 四半期監査

- [ ] セキュリティトークンの更新
- [ ] 依存関係の脆弱性スキャン（`uv run pip-audit`）
- [ ] AWS リソースの棚卸し

### 自動化された監視

#### CloudWatch アラーム例

```bash
# 異常な実行頻度の検出
aws cloudwatch put-metric-alarm \
  --alarm-name "AgentCore-HighExecutionRate" \
  --alarm-description "AgentCore execution rate is too high" \
  --metric-name "Invocations" \
  --namespace "AWS/BedrockAgentCore" \
  --statistic "Sum" \
  --period 3600 \
  --threshold 10 \
  --comparison-operator "GreaterThanThreshold"
```

## 📋 セキュリティチェックリスト

### デプロイ前チェックリスト

- [ ] `.env` ファイルが適切に設定されている
- [ ] セキュリティトークンが 64 文字の 16 進数文字列である
- [ ] Webhook URL が正しい形式である
- [ ] `.gitignore` に `.env` が含まれている
- [ ] Power Automate フローでセキュリティトークン認証が設定されている

### 運用中チェックリスト（月次）

- [ ] AgentCore ログにエラーがない
- [ ] Teams 投稿が正常に動作している
- [ ] 不正なアクセスの痕跡がない
- [ ] IAM ロールの権限が適切である
- [ ] 環境変数が漏洩していない

### セキュリティインシデント対応チェックリスト

- [ ] インシデントの影響範囲を特定した
- [ ] 漏洩した認証情報を無効化した
- [ ] 新しい認証情報を生成・設定した
- [ ] システムを再デプロイした
- [ ] 動作確認を完了した
- [ ] インシデント報告書を作成した

## 🚀 セキュリティ強化の推奨事項

### 短期的な改善

1. **セキュリティトークンの定期ローテーション**

   - 3-6 ヶ月での手動更新
   - 更新手順の自動化スクリプト作成

2. **ログ監視の強化**
   - CloudWatch Insights による異常検知
   - SNS 通知による即座のアラート

### 長期的な改善

1. **OAuth 2.0 認証の導入**

   - より堅牢な認証メカニズムへの移行
   - トークンの自動更新機能

2. **エンドツーエンド暗号化**
   - ペイロードの暗号化
   - 証明書ベースの認証

## 🔄 継続的なセキュリティ改善

### セキュリティ文化の醸成

1. **定期的なセキュリティレビュー**
2. **セキュリティ意識の向上**
3. **インシデント対応訓練**

### 技術的な改善

1. **自動化されたセキュリティテスト**
2. **継続的な脆弱性スキャン**
3. **セキュリティメトリクスの監視**

## 📞 セキュリティサポート

### セキュリティ関連リソース

- **AWS セキュリティベストプラクティス**: https://aws.amazon.com/security/
- **Power Automate セキュリティ**: Microsoft 公式ドキュメント
- **OWASP セキュリティガイド**: https://owasp.org/
