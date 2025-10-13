# Cloud CoPassAgent コストガイド

Cloud CoPassAgent の運用コストと最適化方法をシンプルに解説します。

## 💰 基本コスト構造

### 主要コスト

- **Amazon Bedrock**: AI モデル推論（メインコスト）
- **その他**: Lambda、S3、CloudWatch（微小）

### 月間コスト目安（1 日 1 問生成）

```
Nova Pro:            $0.14/月  ← コスト重視
Nova Lite:           $0.04/月  ← 最安
Claude 3.5 Sonnet:   $0.63/月  ← 高品質
Claude 3.7 Sonnet:   $0.63/月  ← より高品質
Claude Sonnet 4:     $0.63/月  ← 最高品質
Claude Sonnet 4.5:   $0.63/月  ← 最新・最高品質（推奨）
```

## 🎯 モデル選択ガイド

### Nova Pro（現在使用・推奨）

- **コスト**: $0.14/月
- **品質**: 高品質
- **制約**: なし
- **リリース**: 2024 年 12 月
- **用途**: 日常的な問題生成

### Nova Lite（最安）

- **コスト**: $0.04/月
- **品質**: 標準
- **制約**: なし
- **用途**: テスト・大量生成

### Claude 3.5 Sonnet（高品質）

- **コスト**: $0.63/月
- **品質**: 高品質
- **制約**: なし
- **リリース**: 2024 年 6 月
- **用途**: 重要な試験対策

### Claude 3.7 Sonnet（より高品質）

- **コスト**: $0.63/月
- **品質**: より高品質
- **制約**: ⚠️ **SCP 制限により現在利用不可**
- **リリース**: 2025 年 2 月
- **用途**: 組織の SCP 制限解除後に利用可能

### Claude Sonnet 4（最高品質）

- **コスト**: $0.63/月
- **品質**: 最高品質
- **制約**: なし（US Cross-Region Inference Profile）
- **リリース**: 2025 年 5 月
- **用途**: 高品質な問題生成

### Claude Sonnet 4.5（最新・最高品質・推奨）

- **コスト**: $0.63/月
- **品質**: 最新・最高品質
- **制約**: なし
- **リリース**: 2025 年 9 月
- **特徴**:
  - JP Cross-Region Inference Profile 対応（日本国内限定）
  - US Cross-Region Inference Profile 対応
  - Global Cross-Region Inference Profile 対応（最高スループット）
- **用途**: 最高品質の問題生成、日本国内限定運用

## ⚠️ 現在の制約・課題

### Cross-Region Inference Profile の選択

Claude Sonnet 4.5 では、データ所在地要件に応じて推論プロファイルを選択できます：

**JP Cross-Region Inference Profile（推奨）**:

- **モデル ID**: `jp.anthropic.claude-sonnet-4-5-20250929-v1:0`
- **リージョン**: `ap-northeast-1`（東京）または `ap-northeast-3`（大阪）
- **データ所在地**: 日本国内のみ（東京・大阪）
- **用途**: コンプライアンス要件で日本国内限定が必要な場合

**US Cross-Region Inference Profile**:

- **モデル ID**: `us.anthropic.claude-sonnet-4-5-20250929-v1:0`
- **リージョン**: `us-east-1`、`us-east-2`、`us-west-2`
- **データ所在地**: 米国内のみ
- **用途**: 米国内限定が必要な場合

**Global Cross-Region Inference Profile**:

- **モデル ID**: `global.anthropic.claude-sonnet-4-5-20250929-v1:0`
- **リージョン**: 任意
- **データ所在地**: 全商用リージョン
- **用途**: 最高スループット、約 10%のコスト削減

### 利用可能モデル

```
✅ 利用可能:
   - Nova Pro/Lite/Micro（ON_DEMAND）
   - Claude 3.5 Sonnet（ON_DEMAND）
   - Claude 3.7 Sonnet（US Cross-Region）
   - Claude Sonnet 4（US Cross-Region）
   - Claude Sonnet 4.5（JP/US/Global Cross-Region）← 推奨
   - Claude 3.7 Sonnet
   - Claude 3.5 Sonnet v2
```

### Claude モデル間のコスト

**重要**: Claude 3.5 Sonnet、Claude 3.7 Sonnet、Claude Sonnet 4、Claude Sonnet 4.5 は**同一料金**

- **Input**: $0.003 per 1K tokens
- **Output**: $0.015 per 1K tokens
- **1 問あたり**: $0.021（2K input + 1K output）
- **月 30 問**: $0.63

**Global Cross-Region Inference Profile の場合**: 約 10%のコスト削減

- **月 30 問**: $0.57（$0.06 削減）

## 📊 使用量別コスト

### 1 日 1 問（標準）

```
Nova Pro:            年間 $1.68
Nova Lite:           年間 $0.43
Claude 3.5 Sonnet:   年間 $7.56
Claude 3.7 Sonnet:   年間 $7.56
Claude Sonnet 4:     年間 $7.56
Claude Sonnet 4.5:   年間 $7.56（JP/US）、$6.80（Global、10%削減）
```

### 平日のみ（週 5 問）

```
Nova Pro:            年間 $1.25
Nova Lite:           年間 $0.32
Claude 3.5 Sonnet:   年間 $5.67
Claude 3.7 Sonnet:   年間 $5.67
Claude Sonnet 4:     年間 $5.67
Claude Sonnet 4.5:   年間 $5.67（JP/US）、$5.10（Global、10%削減）
```

### 週 3 回

```
Nova Pro:            年間 $0.73
Nova Lite:           年間 $0.19
Claude 3.5 Sonnet:   年間 $3.31
Claude 3.7 Sonnet:   年間 $3.31
Claude Sonnet 4:     年間 $3.31
Claude Sonnet 4.5:   年間 $3.31（JP/US）、$2.98（Global、10%削減）
```

## 💡 コスト最適化のコツ

### 1. モデル選択

- **開発・テスト**: Nova Lite
- **日常運用（コスト重視）**: Nova Pro
- **高品質**: Claude 3.5 Sonnet
- **より高品質**: Claude 3.7 Sonnet
- **最高品質**: Claude Sonnet 4
- **最新・最高品質（推奨）**: Claude Sonnet 4.5
  - JP Cross-Region: 日本国内限定が必要な場合
  - US Cross-Region: 米国内限定が必要な場合
  - Global: 最高スループット、10%コスト削減

### 2. 実行頻度

- **毎日**: 最大効果、高コスト
- **平日のみ**: バランス良好
- **週 3 回**: 低コスト

### 3. 複数問一括生成

```
1問ずつ生成（現在）: 基準コスト
3問一括生成:         17-19%削減
5問一括生成:         20-24%削減

実際の削減額（1日1問の場合）:
Nova Pro:     年間 $0.3-0.4 削減
Claude 3.5:   年間 $1.3-1.5 削減
```

**結論**: 1 日 1 問の使用量では削減効果は限定的（年間数十セント〜1.5 ドル程度）

### 4. 1 日 1 問での実際の影響

```
現在（Nova Pro）:        月 $0.14
Claude モデル移行:       月 $0.63
差額:                   月 $0.49（年間 $5.88）
```

**結論**: 1 日 1 問の使用量では、コスト差は実質的に無視できるレベル

### 5. Claude モデル間の選択

**コスト面**: Claude 3.5、3.7、Sonnet 4、Sonnet 4.5 は同一料金のため、**品質・機能で選択**

- **Claude 3.5 Sonnet**: 実績あり、安定性重視
- **Claude 3.7 Sonnet**: より高い推論能力
- **Claude Sonnet 4**: 最新機能、最高品質
- **Claude Sonnet 4.5（推奨）**: 最新・最高品質
  - JP Cross-Region: 日本国内限定運用
  - Global: 10%コスト削減

## 🔍 コスト監視

### 簡単な確認方法

1. **AWS コンソール** → **Bedrock** → **使用量**
2. **月次予算アラート**を$5 に設定
3. **異常な増加**があれば設定を確認

### 目安となる警告レベル

- **日次**: $0.10 以上
- **月次**: $3.00 以上
- **年次**: $10.00 以上

## 📈 ROI（費用対効果）

### コスト比較

```
Cloud CoPassAgent:  年間 $2-8
市販問題集:         年間 $50-100
オンライン学習:     年間 $200-500
研修コース:         年間 $1,000-3,000
```

**結論**: 圧倒的にコスト効率が良い

## 🎯 推奨戦略

### 短期（現在）

- **モデル**: Nova Pro（継続使用）
- **理由**: SCP 制限回避、十分な品質、低コスト
- **予算**: $2/月

### 中長期（SCP 制限解除後）

- **選択肢 1**: Nova Pro 継続（コスト重視）
- **選択肢 2**: Claude Sonnet 4 移行（品質重視）
- **判断基準**: 1 日 1 問なら月 49 セントの差額は微小

### Claude モデル選択指針（制限解除後）

- **安定性重視**: Claude 3.5 Sonnet
- **バランス重視**: Claude 3.7 Sonnet
- **最新機能重視**: Claude Sonnet 4

### 複数問一括生成の判断

- **実装推奨**: 将来的な使用量増加を見込む場合
- **現状維持推奨**: 1 日 1 問の現在の使用量では効果限定的

## 🔧 SCP 制限解除について

### 組織管理者への依頼内容

- **対象**: Cross-Region Inference Profile の使用許可
- **必要アクション**: `bedrock:InvokeModelWithResponseStream` の地域間アクセス許可
- **影響範囲**: us-east-1 から us-west-2 等へのモデルアクセス
- **セキュリティ**: US リージョン内に限定可能

### 制限解除のメリット

- **Claude 3.7/Sonnet 4**: より高品質なモデルの利用
- **将来性**: 新しいモデルへの早期アクセス
- **選択肢**: より多くのモデルオプション
- **コスト**: 同一料金で品質向上

## 📞 参考情報

- **AWS Bedrock 料金**: https://aws.amazon.com/bedrock/pricing/
- **料金計算ツール**: https://calculator.aws/
- **関連ドキュメント**: [deployment-guide.md](./deployment-guide.md)

---

**更新**: 2025-08-24 - 複数問一括生成のコスト分析追加
