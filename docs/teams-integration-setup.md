# Teams 連携セットアップガイド

## 概要

このドキュメントでは、AWS Exam Agent と Microsoft Teams を連携させるための Power Automate フロー設定手順を説明します。

## 前提条件

- Microsoft 365 アカウント（Power Automate ライセンス含む）
- Teams チャネルへの投稿権限
- AWS AgentCore デプロイ済み環境

## Power Automate フロー作成手順

### 1. 新しいフローの作成

1. [Power Automate](https://make.powerautomate.com/) にアクセス
2. 「作成」→「自動化されたクラウドフロー」を選択
3. フロー名: `AWS Exam Agent - Teams 投稿`
4. トリガー: `HTTP 要求の受信時` を選択

### 2. HTTP トリガーの設定

**要求本文の JSON スキーマ:**

```json
{
  "type": "object",
  "properties": {
    "question_id": {
      "type": "string",
      "description": "問題の一意識別子"
    },
    "question": {
      "type": "string",
      "description": "問題文"
    },
    "options": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "選択肢の配列"
    },
    "correct_answer": {
      "type": "string",
      "description": "正解の選択肢（A, B, C, D等）"
    },
    "explanation": {
      "type": "string",
      "description": "解説文"
    },
    "source": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "参考ドキュメントのURL配列"
    },
    "api_key": {
      "type": "string",
      "description": "認証用APIキー"
    }
  },
  "required": ["question", "options", "correct_answer", "explanation"]
}
```

### 3. 認証チェックの追加

1. 「新しいステップ」→「条件」を追加
2. 条件式: `triggerBody()?['api_key']` が `parameters('API_KEY')` と等しい
3. パラメータ `API_KEY` を環境変数として設定

### 4. Teams メッセージ投稿の設定

**「はい」の分岐に以下のアクションを追加:**

1. 「新しいステップ」→「Microsoft Teams」→「チャネルにメッセージを投稿する」
2. チーム: 対象の Teams チームを選択
3. チャネル: 問題投稿用チャネルを選択
4. メッセージ: 以下の HTML テンプレートを使用

**メッセージテンプレート:**

```html
<h3>🎯 AWS Solutions Architect Professional 練習問題</h3>

<div
  style="background-color: #f0f8ff; padding: 15px; border-left: 4px solid #0078d4; margin: 10px 0;"
>
  <p><strong>問題:</strong></p>
  <p>@{triggerBody()?['question']}</p>
</div>

<p><strong>選択肢:</strong></p>
<p>🅰️ @{triggerBody()?['options'][0]}</p>
<p>🅱️ @{triggerBody()?['options'][1]}</p>
<p>🅲️ @{triggerBody()?['options'][2]}</p>
<p>🅳️ @{triggerBody()?['options'][3]}</p>

<p>
  💡
  <strong>回答方法:</strong>
  正解だと思う選択肢のリアクション（🅰️🅱️🅲️🅳️）をクリックしてください
</p>
<p>📝 <strong>議論歓迎:</strong> スレッドで解法や考え方をシェアしましょう！</p>

<p><em>問題ID: @{triggerBody()?['question_id']}</em></p>
```

### 5. 自動リアクション追加

1. 「新しいステップ」→「Microsoft Teams」→「メッセージにリアクションを追加する」
2. メッセージ ID: `@{outputs('Post_message_in_a_chat_or_channel')?['body/id']}`
3. リアクション: 🅰️, 🅱️, 🅲️, 🅳️ を順次追加（複数のアクションが必要）

### 6. エラーハンドリング

**「いいえ」の分岐に以下のアクションを追加:**

1. 「HTTP 応答」アクション
2. 状態コード: 401
3. 本文: `{"error": "Unauthorized: Invalid API key"}`

### 7. 成功レスポンス

**「はい」の分岐の最後に以下のアクションを追加:**

1. 「HTTP 応答」アクション
2. 状態コード: 200
3. 本文:

```json
{
  "status": "success",
  "message_id": "@{outputs('Post_message_in_a_chat_or_channel')?['body/id']}",
  "posted_at": "@{utcNow()}"
}
```

## 設定完了後の確認事項

### Webhook URL の取得

1. フローを保存
2. HTTP トリガーの「HTTP POST の URL」をコピー
3. この URL を AgentCore の環境変数として設定

### テスト実行

以下の curl コマンドでテスト実行:

```bash
curl -X POST "YOUR_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "question_id": "test_001",
    "question": "テスト問題です。正しい選択肢はどれですか？",
    "options": ["選択肢A", "選択肢B", "選択肢C", "選択肢D"],
    "correct_answer": "B",
    "explanation": "正解はBです。理由は...",
    "api_key": "YOUR_API_KEY"
  }'
```

## セキュリティ考慮事項

1. **API キー管理**: 環境変数として安全に管理
2. **HTTPS 通信**: Power Automate は自動的に HTTPS を使用
3. **アクセス制限**: 必要最小限の権限でフローを実行
4. **ログ監視**: Power Automate の実行履歴を定期的に確認

## トラブルシューティング

### よくある問題と解決方法

1. **メッセージが投稿されない**

   - チーム・チャネルの選択を確認
   - Teams アプリの権限を確認

2. **リアクションが追加されない**

   - メッセージ ID の参照を確認
   - 絵文字の形式を確認

3. **認証エラー**
   - API キーの設定を確認
   - 条件式の記述を確認

## 次のステップ

1. AgentCore からの Webhook 呼び出し実装
2. 解答公開フローの作成（24 時間後）
3. 統計分析機能の追加
