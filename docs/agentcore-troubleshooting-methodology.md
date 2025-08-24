# AgentCore 調査・トラブルシューティング手法

AgentCore の問題解決や新機能発見のための系統的な調査手法とベストプラクティスです。

## 📋 目次

- [基本的な調査アプローチ](#基本的な調査アプローチ)
- [情報源の優先順位](#情報源の優先順位)
- [具体的な調査手順](#具体的な調査手順)
- [問題解決のパターン](#問題解決のパターン)
- [ケーススタディ](#ケーススタディ)
- [調査ツールとコマンド](#調査ツールとコマンド)

## 🔍 基本的な調査アプローチ

### 系統的調査の4ステップ

1. **問題の特定と仮説立案**
2. **情報収集と検証**
3. **解決策の実装**
4. **結果の確認と文書化**

### 調査の心構え

- **仮定を疑う**: 「動作するはず」ではなく「実際に動作するか」を確認
- **段階的アプローチ**: 複雑な問題を小さな部分に分解
- **記録を残す**: 調査過程と結果を必ず記録
- **再現性を重視**: 他の人が同じ手順で同じ結果を得られるように

## 📊 情報源の優先順位

### 1. 公式ドキュメント（信頼度: ★★★★★）

```bash
# AWS 公式ドキュメント
https://docs.aws.amazon.com/bedrock/

# AgentCore 関連ドキュメント
https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html
```

**特徴**:
- 最も信頼できる情報源
- ただし、最新機能が反映されていない場合がある
- 基本的な使用方法に重点

### 2. CLI ヘルプ（信頼度: ★★★★★）

```bash
# 基本ヘルプ
agentcore --help

# サブコマンドヘルプ
agentcore launch --help
agentcore configure --help
agentcore status --help
agentcore invoke --help

# 特定オプションの検索
agentcore launch --help | grep -i env
agentcore launch --help | grep -i region
```

**特徴**:
- 実装と完全に一致
- 最新の機能とオプションを反映
- 使用例やフォーマットが明記

### 3. ソースコード（信頼度: ★★★★☆）

```bash
# AgentCore CLI の実装確認
find /Users/$(whoami)/.pyenv/versions/*/lib/python*/site-packages/bedrock_agentcore_starter_toolkit -name "*.py" | head -10

# 特定機能の検索
grep -r "env" /Users/$(whoami)/.pyenv/versions/*/lib/python*/site-packages/bedrock_agentcore_starter_toolkit/cli/

# 設定ファイルの構造確認
find /Users/$(whoami)/.pyenv/versions/*/lib/python*/site-packages/bedrock_agentcore_starter_toolkit -name "*schema*" -o -name "*config*"
```

**特徴**:
- 実装の詳細を理解可能
- 隠れた機能やオプションを発見
- エラーハンドリングの仕組みを把握

### 4. CloudWatch ログ（信頼度: ★★★★☆）

```bash
# リアルタイムログ監視
aws logs tail /aws/bedrock-agentcore/runtimes/agent_main-4h7OvMAtVL-DEFAULT --follow

# 特定期間のログ検索
aws logs filter-log-events \
  --log-group-name "/aws/bedrock-agentcore/runtimes/agent_main-4h7OvMAtVL-DEFAULT" \
  --start-time $(date -v-1H +%s)000 \
  --region us-east-1

# エラーログの抽出
aws logs filter-log-events \
  --log-group-name "/aws/bedrock-agentcore/runtimes/agent_main-4h7OvMAtVL-DEFAULT" \
  --filter-pattern "ERROR" \
  --start-time $(date -v-1H +%s)000 \
  --region us-east-1
```

**特徴**:
- 実際の動作状況を確認
- エラーの詳細情報を取得
- パフォーマンス情報の分析

### 5. コミュニティ・フォーラム（信頼度: ★★★☆☆）

- AWS re:Post
- Stack Overflow
- GitHub Issues
- Reddit (r/aws)

**特徴**:
- 実際の使用例と問題解決事例
- 非公式だが実用的な情報
- 情報の正確性は要検証

## 🔧 具体的な調査手順

### 新機能・オプションの発見

#### 1. CLI ヘルプの系統的確認

```bash
# 全体構造の把握
agentcore --help

# 各サブコマンドの詳細確認
for cmd in configure launch status invoke; do
  echo "=== $cmd ==="
  agentcore $cmd --help
  echo
done

# 特定キーワードの検索
agentcore launch --help | grep -E "(env|environment|variable|config)"
```

#### 2. 設定ファイルの構造分析

```bash
# 設定ファイルの場所確認
find . -name ".bedrock_agentcore.yaml" -o -name "*.yaml" | grep -v node_modules

# 設定ファイルの内容確認
cat app/agentcore/.bedrock_agentcore.yaml

# スキーマファイルの確認（可能な設定項目を把握）
find /Users/$(whoami)/.pyenv/versions/*/lib/python*/site-packages/bedrock_agentcore_starter_toolkit -name "*schema*"
```

#### 3. 実装コードの調査

```bash
# 環境変数関連の実装確認
grep -r "env" /Users/$(whoami)/.pyenv/versions/*/lib/python*/site-packages/bedrock_agentcore_starter_toolkit/cli/ | head -10

# 設定処理の実装確認
grep -r "config" /Users/$(whoami)/.pyenv/versions/*/lib/python*/site-packages/bedrock_agentcore_starter_toolkit/operations/ | head -10

# エラーハンドリングの確認
grep -r "error\|exception" /Users/$(whoami)/.pyenv/versions/*/lib/python*/site-packages/bedrock_agentcore_starter_toolkit/cli/ | head -5
```

### 問題の診断手順

#### 1. 症状の特定

```bash
# 基本状態の確認
agentcore status

# 最近のログ確認
aws logs tail /aws/bedrock-agentcore/runtimes/agent_main-4h7OvMAtVL-DEFAULT --since 10m

# エラーの有無確認
aws logs filter-log-events \
  --log-group-name "/aws/bedrock-agentcore/runtimes/agent_main-4h7OvMAtVL-DEFAULT" \
  --filter-pattern "ERROR" \
  --start-time $(date -v-30M +%s)000 \
  --region us-east-1
```

#### 2. 環境の確認

```bash
# ローカル環境変数の確認
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
for key in ['AWS_DEFAULT_REGION', 'POWER_AUTOMATE_WEBHOOK_URL']:
    value = os.getenv(key)
    print(f'{key}: {\"SET\" if value else \"NOT SET\"}')
"

# AWS 認証情報の確認
aws sts get-caller-identity

# AgentCore 設定の確認
cat app/agentcore/.bedrock_agentcore.yaml | grep -E "(name|region|execution_role)"
```

#### 3. 段階的テスト

```bash
# 1. 基本的な接続テスト
agentcore invoke '{"prompt": "Hello"}'

# 2. 環境変数依存機能のテスト
agentcore invoke '{"prompt": "AWS SAP試験問題を1問生成してください"}'

# 3. ログでの動作確認
aws logs filter-log-events \
  --log-group-name "/aws/bedrock-agentcore/runtimes/agent_main-4h7OvMAtVL-DEFAULT" \
  --filter-pattern "Teams" \
  --start-time $(date -v-5M +%s)000 \
  --region us-east-1
```

## 🎯 問題解決のパターン

### パターン1: 設定関連の問題

**症状**: 機能が動作しない、設定が反映されない

**調査手順**:
1. 設定ファイルの確認
2. 環境変数の確認
3. CLI オプションの確認
4. ログでの設定値確認

**例**: 環境変数設定問題
```bash
# 問題: POWER_AUTOMATE_WEBHOOK_URL が設定されていない
# 調査: CLI ヘルプで --env オプションを発見
agentcore launch --help | grep env

# 解決: --env オプションで環境変数を設定
agentcore launch --env POWER_AUTOMATE_WEBHOOK_URL="<url>" --auto-update-on-conflict
```

### パターン2: 権限関連の問題

**症状**: アクセス拒否、認証エラー

**調査手順**:
1. IAM ロールの確認
2. ポリシーの確認
3. リソースの存在確認
4. CloudTrail ログの確認

**例**: ECR アクセス権限問題
```bash
# 問題: ECR へのプッシュが失敗
# 調査: IAM ロールの権限確認
aws iam list-attached-role-policies --role-name BedrockAgentCoreExecutionRole-development

# 解決: 必要な権限の追加
```

### パターン3: ネットワーク関連の問題

**症状**: 接続タイムアウト、DNS 解決失敗

**調査手順**:
1. ネットワーク設定の確認
2. セキュリティグループの確認
3. VPC 設定の確認
4. DNS 設定の確認

### パターン4: リソース不足の問題

**症状**: メモリ不足、CPU 使用率高騰

**調査手順**:
1. CloudWatch メトリクスの確認
2. ログでのリソース使用状況確認
3. 設定値の最適化
4. スケーリング設定の確認

## 📚 ケーススタディ

### ケース1: 環境変数設定方法の発見

**背景**: 
- ローカル環境では `.env` ファイルで環境変数が動作
- AgentCore Runtime では環境変数が設定されていない
- 公式ドキュメントに明確な記載なし

**調査プロセス**:

1. **問題の特定**
```bash
# CloudWatch ログでエラー確認
aws logs filter-log-events \
  --log-group-name "/aws/bedrock-agentcore/runtimes/agent_main-4h7OvMAtVL-DEFAULT" \
  --filter-pattern "POWER_AUTOMATE_WEBHOOK_URL" \
  --start-time $(date -v-1H +%s)000 \
  --region us-east-1

# 結果: "POWER_AUTOMATE_WEBHOOK_URL が設定されていません"
```

2. **仮説の立案**
- AgentCore デプロイ時に環境変数を指定する方法があるはず
- Docker や Kubernetes と同様のパターンが存在する可能性

3. **CLI ヘルプの確認**
```bash
agentcore launch --help | grep -i env
# 発見: --env オプションの存在
```

4. **実装の詳細確認**
```bash
grep -r "env" /Users/$(whoami)/.pyenv/versions/*/lib/python*/site-packages/bedrock_agentcore_starter_toolkit/cli/runtime/commands.py
# 確認: KEY=VALUE フォーマットの実装
```

5. **実際のテスト**
```bash
agentcore launch --env POWER_AUTOMATE_WEBHOOK_URL="<url>" --auto-update-on-conflict
```

6. **動作確認**
```bash
aws logs filter-log-events \
  --log-group-name "/aws/bedrock-agentcore/runtimes/agent_main-4h7OvMAtVL-DEFAULT" \
  --filter-pattern "Teams投稿完了" \
  --start-time $(date -v-5M +%s)000 \
  --region us-east-1
# 結果: "Teams投稿完了 (HTTP 202)"
```

**学んだこと**:
- CLI ヘルプは最も信頼できる情報源
- 既存の知識（Docker等）を活用した仮説立案が有効
- 段階的な検証が重要

### ケース2: インポートパス問題の解決

**背景**:
- ローカル開発では動作するコード
- AgentCore Runtime でインポートエラー

**調査プロセス**:

1. **エラーログの確認**
```bash
aws logs filter-log-events \
  --log-group-name "/aws/bedrock-agentcore/runtimes/agent_main-4h7OvMAtVL-DEFAULT" \
  --filter-pattern "ModuleNotFoundError" \
  --start-time $(date -v-1H +%s)000 \
  --region us-east-1
```

2. **環境の違いを分析**
- ローカル: Python パッケージとして認識
- AgentCore: コンテナ内で直接実行

3. **解決策の実装**
```python
# 変更前
from app.agentcore.teams_client import TeamsClient

# 変更後
from .teams_client import TeamsClient
```

## 🛠️ 調査ツールとコマンド

### 基本的な調査コマンド

#### AgentCore 関連

```bash
# 基本情報
agentcore --version
agentcore --help
agentcore status

# 設定確認
cat app/agentcore/.bedrock_agentcore.yaml
ls -la app/agentcore/

# ログ確認
aws logs describe-log-groups --log-group-name-prefix "/aws/bedrock-agentcore"
aws logs tail /aws/bedrock-agentcore/runtimes/agent_main-4h7OvMAtVL-DEFAULT --since 1h
```

#### AWS リソース確認

```bash
# 認証情報
aws sts get-caller-identity

# Bedrock 関連
aws bedrock list-foundation-models --region us-east-1
aws bedrock get-model-invocation-logging-configuration --region us-east-1

# ECR 関連
aws ecr describe-repositories --region us-east-1
aws ecr list-images --repository-name aws-exam-agent-runtime-development --region us-east-1

# IAM 関連
aws iam get-role --role-name BedrockAgentCoreExecutionRole-development
aws iam list-attached-role-policies --role-name BedrockAgentCoreExecutionRole-development
```

### 高度な調査テクニック

#### 1. ログの構造化検索

```bash
# JSON ログの解析
aws logs filter-log-events \
  --log-group-name "/aws/bedrock-agentcore/runtimes/agent_main-4h7OvMAtVL-DEFAULT" \
  --start-time $(date -v-1H +%s)000 \
  --region us-east-1 \
  --query 'events[*].message' \
  --output text | jq -r 'select(type == "object") | .body'

# 特定パターンの抽出
aws logs filter-log-events \
  --log-group-name "/aws/bedrock-agentcore/runtimes/agent_main-4h7OvMAtVL-DEFAULT" \
  --filter-pattern "[timestamp, request_id, level, message]" \
  --start-time $(date -v-1H +%s)000 \
  --region us-east-1
```

#### 2. パフォーマンス分析

```bash
# 応答時間の分析
aws logs filter-log-events \
  --log-group-name "/aws/bedrock-agentcore/runtimes/agent_main-4h7OvMAtVL-DEFAULT" \
  --filter-pattern "Invocation completed successfully" \
  --start-time $(date -v-1H +%s)000 \
  --region us-east-1 \
  --query 'events[*].message' \
  --output text | grep -o '[0-9]*\.[0-9]*s' | sed 's/s//' | awk '{sum+=$1; count++} END {print "Average:", sum/count, "seconds"}'

# エラー率の計算
SUCCESS=$(aws logs filter-log-events \
  --log-group-name "/aws/bedrock-agentcore/runtimes/agent_main-4h7OvMAtVL-DEFAULT" \
  --filter-pattern "Invocation completed successfully" \
  --start-time $(date -v-1H +%s)000 \
  --region us-east-1 \
  --query 'length(events)')

ERROR=$(aws logs filter-log-events \
  --log-group-name "/aws/bedrock-agentcore/runtimes/agent_main-4h7OvMAtVL-DEFAULT" \
  --filter-pattern "ERROR" \
  --start-time $(date -v-1H +%s)000 \
  --region us-east-1 \
  --query 'length(events)')

echo "Success: $SUCCESS, Error: $ERROR, Error Rate: $(echo "scale=2; $ERROR / ($SUCCESS + $ERROR) * 100" | bc)%"
```

#### 3. 設定の差分確認

```bash
# 設定ファイルのバックアップと比較
cp app/agentcore/.bedrock_agentcore.yaml /tmp/current_config.yaml
# 変更後
diff /tmp/current_config.yaml app/agentcore/.bedrock_agentcore.yaml

# 環境変数の比較
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
local_vars = {k: v for k, v in os.environ.items() if k.startswith(('AWS_', 'POWER_', 'BEDROCK_'))}
print('Local environment variables:')
for k, v in local_vars.items():
    print(f'  {k}: {v[:20]}...' if len(v) > 20 else f'  {k}: {v}')
"
```

## 📝 調査結果の文書化

### 調査レポートのテンプレート

```markdown
# 調査レポート: [問題の概要]

## 問題の概要
- **発生日時**: 
- **症状**: 
- **影響範囲**: 

## 調査プロセス
1. **初期確認**
   - 実行したコマンド
   - 確認した結果

2. **詳細調査**
   - 調査した情報源
   - 発見した事実

3. **解決策の検討**
   - 検討した選択肢
   - 選択した理由

## 解決策
- **実装内容**: 
- **実行コマンド**: 
- **確認方法**: 

## 学んだこと
- **技術的な学び**: 
- **プロセスの改善点**: 
- **今後の予防策**: 

## 関連リソース
- 参考にしたドキュメント
- 関連する設定ファイル
- 有用なコマンド
```

### ナレッジベースの構築

```bash
# 調査結果の保存
mkdir -p docs/investigations
echo "# 調査履歴" > docs/investigations/README.md

# 個別の調査レポート
cat > docs/investigations/$(date +%Y%m%d)_environment_variables.md << 'EOF'
# 環境変数設定方法の調査

## 問題
AgentCore Runtime で環境変数が設定されない

## 解決策
`agentcore launch --env KEY=VALUE` オプションの使用

## 詳細
[調査内容を記載]
EOF
```

## 🎯 ベストプラクティス

### 効率的な調査のコツ

1. **仮説駆動型アプローチ**
   - 問題の原因について仮説を立てる
   - 仮説を検証する最小限の実験を設計
   - 結果に基づいて仮説を修正

2. **段階的な検証**
   - 複雑な問題を小さな部分に分解
   - 各部分を個別に検証
   - 動作する部分から順次組み立て

3. **記録の重要性**
   - 実行したコマンドと結果を記録
   - 失敗した試行も含めて文書化
   - 他の人が再現できる形で記録

4. **知識の共有**
   - 調査結果をチームで共有
   - 類似問題の予防策を検討
   - ドキュメントの継続的な更新

### 避けるべき落とし穴

1. **思い込みによる調査**
   - 「こうあるべき」ではなく「実際はどうか」を確認
   - 公式ドキュメントの記載を鵜呑みにしない

2. **表面的な解決**
   - 症状だけでなく根本原因を特定
   - 一時的な回避策と恒久的な解決策を区別

3. **孤立した調査**
   - チームメンバーとの情報共有を怠らない
   - 既存の知識やドキュメントを活用

---

**最終更新**: 2025-08-17  
**バージョン**: 1.0.0
