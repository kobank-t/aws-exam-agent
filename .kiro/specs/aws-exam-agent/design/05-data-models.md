# データモデル設計

## サーバーレスデータベース設計 (DynamoDB)

### 1. テーブル設計概要

**単一テーブル設計 (Single Table Design) を採用:**

**設計根拠:**

- **コスト効率**: 複数テーブルより単一テーブルの方が RCU/WCU 効率が良い
- **パフォーマンス**: 関連データを 1 回のクエリで取得可能（JOIN が不要）
- **運用簡素化**: テーブル数削減によるメンテナンス負荷軽減
- **スケーラビリティ**: DynamoDB の特性を最大限活用

**実装方式:**

- 1 つの DynamoDB テーブルで全データを管理
- パーティションキー(PK)とソートキー(SK)でエンティティを識別
- GSI (Global Secondary Index) で効率的なクエリを実現

### 2. メインテーブル: `aws-exam-coach-data`

```json
{
  "TableName": "aws-exam-coach-data",
  "KeySchema": [
    { "AttributeName": "PK", "KeyType": "HASH" },
    { "AttributeName": "SK", "KeyType": "RANGE" }
  ],
  "AttributeDefinitions": [
    { "AttributeName": "PK", "AttributeType": "S" },
    { "AttributeName": "SK", "AttributeType": "S" },
    { "AttributeName": "GSI1PK", "AttributeType": "S" },
    { "AttributeName": "GSI1SK", "AttributeType": "S" },
    { "AttributeName": "GSI2PK", "AttributeType": "S" },
    { "AttributeName": "GSI2SK", "AttributeType": "S" }
  ],
  "GlobalSecondaryIndexes": [
    {
      "IndexName": "GSI1",
      "KeySchema": [
        { "AttributeName": "GSI1PK", "KeyType": "HASH" },
        { "AttributeName": "GSI1SK", "KeyType": "RANGE" }
      ],
      "Projection": {
        "ProjectionType": "ALL"
      }
    },
    {
      "IndexName": "GSI2",
      "KeySchema": [
        { "AttributeName": "GSI2PK", "KeyType": "HASH" },
        { "AttributeName": "GSI2SK", "KeyType": "RANGE" }
      ],
      "Projection": {
        "ProjectionType": "ALL"
      }
    }
  ]
}
```

## 3. データエンティティ設計

### 問題データ (Question)

```json
{
  "PK": "QUESTION#q_20250729_001",
  "SK": "METADATA",
  "EntityType": "Question",
  "question_id": "q_20250729_001",
  "question_text": "VPCに関する問題です？",
  "choices": ["選択肢A", "選択肢B", "選択肢C", "選択肢D"],
  "correct_answer": "B",
  "explanation": "正解はBです。理由は...",
  "service": "EC2",
  "topic": "VPC",
  "difficulty": "Professional",
  "source_documents": ["vpc-user-guide", "exam-guide"],
  "quality_score": 0.85,
  "created_at": "2025-07-29T10:00:00Z",
  "updated_at": "2025-07-29T10:00:00Z",
  "created_by": "system",
  "GSI1PK": "SERVICE#EC2",
  "GSI1SK": "CREATED#2025-07-29T10:00:00Z",
  "GSI2PK": "DIFFICULTY#Professional",
  "GSI2SK": "QUALITY#0.85"
}
```

### 配信履歴 (Delivery)

```json
{
  "PK": "DELIVERY#d_20250729_001",
  "SK": "METADATA",
  "EntityType": "Delivery",
  "delivery_id": "d_20250729_001",
  "question_id": "q_20250729_001",
  "teams_message_id": "teams_msg_12345",
  "teams_channel_id": "19:abc123@thread.tacv2",
  "posted_at": "2025-07-29T10:05:00Z",
  "status": "posted",
  "total_responses": 0,
  "correct_responses": 0,
  "correct_rate": null,
  "response_details": {},
  "error_message": null,
  "answered_at": null,
  "GSI1PK": "QUESTION#q_20250729_001",
  "GSI1SK": "DELIVERY#d_20250729_001",
  "GSI2PK": "STATUS#posted",
  "GSI2SK": "POSTED#2025-07-29T10:05:00Z"
}
```

### ユーザー回答 (UserResponse)

```json
{
  "PK": "DELIVERY#d_20250729_001",
  "SK": "USER#user123",
  "EntityType": "UserResponse",
  "delivery_id": "d_20250729_001",
  "user_id": "user123",
  "user_name": "田中太郎",
  "selected_answer": "B",
  "is_correct": true,
  "responded_at": "2025-07-29T11:30:00Z",
  "reaction_type": "🅱️",
  "GSI1PK": "USER#user123",
  "GSI1SK": "RESPONDED#2025-07-29T11:30:00Z",
  "GSI2PK": "DELIVERY#d_20250729_001",
  "GSI2SK": "RESPONSE#2025-07-29T11:30:00Z"
}
```

### システム設定 (SystemSettings)

```json
{
  "PK": "SETTINGS",
  "SK": "CONFIG",
  "EntityType": "SystemSettings",
  "teams_channel_id": "19:abc123@thread.tacv2",
  "daily_question_time": "10:00",
  "answer_reveal_delay": 24,
  "max_questions_per_day": 1,
  "quality_threshold": 0.8,
  "updated_at": "2025-07-29T09:00:00Z",
  "updated_by": "admin"
}
```

## 4. アクセスパターンとクエリ設計

### 主要なアクセスパターン

#### 1. 問題の取得

```python
# 特定問題の取得
response = dynamodb.get_item(
    Key={'PK': 'QUESTION#q_20250729_001', 'SK': 'METADATA'}
)

# サービス別問題一覧
response = dynamodb.query(
    IndexName='GSI1',
    KeyConditionExpression='GSI1PK = :service',
    ExpressionAttributeValues={':service': 'SERVICE#EC2'}
)
```

#### 2. 配信履歴の管理

```python
# 配信履歴の取得
response = dynamodb.get_item(
    Key={'PK': 'DELIVERY#d_20250729_001', 'SK': 'METADATA'}
)

# 問題に対する配信履歴
response = dynamodb.query(
    IndexName='GSI1',
    KeyConditionExpression='GSI1PK = :question_id',
    ExpressionAttributeValues={':question_id': 'QUESTION#q_20250729_001'}
)
```

#### 3. ユーザー回答の集計

```python
# 特定配信の全回答
response = dynamodb.query(
    KeyConditionExpression='PK = :delivery_id AND begins_with(SK, :user_prefix)',
    ExpressionAttributeValues={
        ':delivery_id': 'DELIVERY#d_20250729_001',
        ':user_prefix': 'USER#'
    }
)

# ユーザーの回答履歴
response = dynamodb.query(
    IndexName='GSI1',
    KeyConditionExpression='GSI1PK = :user_id',
    ExpressionAttributeValues={':user_id': 'USER#user123'}
)
```

## 5. 類似度チェックの簡素化

### 従来のアプローチ (RDB)

- 全問題に対してベクトル類似度計算
- 複雑な SQL 文での類似度検索

### DynamoDB 向け簡素化アプローチ

```python
class SimpleSimilarityChecker:
    def __init__(self):
        self.similarity_threshold = 0.70

    async def check_similarity(self, new_question: Question) -> bool:
        """簡素化された類似度チェック"""
        # 1. サービス・トピックが同じ問題を取得
        similar_questions = await self._get_questions_by_service_topic(
            new_question.service, new_question.topic
        )

        # 2. キーワードベースの簡易類似度計算
        for existing_question in similar_questions:
            similarity = self._calculate_keyword_similarity(
                new_question.question_text,
                existing_question.question_text
            )

            if similarity > self.similarity_threshold:
                return False  # 類似問題が存在

        return True  # 類似問題なし

    def _calculate_keyword_similarity(self, text1: str, text2: str) -> float:
        """キーワードベースの簡易類似度計算"""
        # 形態素解析やTF-IDFの代わりに単純な単語一致率を使用
        words1 = set(text1.split())
        words2 = set(text2.split())

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union) if union else 0.0
```

## サーバーレスキャッシュ設計

### 設計根拠

**キャッシュ導入の理由:**

1. **コスト削減**: Bedrock API ($0.003/1K tokens) + MCP Server 呼び出しコストを削減
2. **レスポンス時間短縮**: 外部 API 呼び出し (3-5 秒) → キャッシュ取得 (50ms)
3. **API 制限回避**: 外部サービスのレート制限・障害時の影響軽減
4. **ユーザー体験向上**: 問題生成待機時間の大幅短縮

**DynamoDB TTL 選択の理由:**

- サーバーレス環境で Redis インスタンス管理が不要
- 自動的なデータ削除でメンテナンスフリー
- Lambda 間でのキャッシュ共有が可能
- AWS 統合による運用コスト削減

### 1. DynamoDB TTL を活用したキャッシュ

**キャッシュ専用テーブル: `aws-exam-coach-cache`**

```json
{
  "TableName": "aws-exam-coach-cache",
  "KeySchema": [{ "AttributeName": "cache_key", "KeyType": "HASH" }],
  "AttributeDefinitions": [
    { "AttributeName": "cache_key", "AttributeType": "S" }
  ],
  "TimeToLiveSpecification": {
    "AttributeName": "ttl",
    "Enabled": true
  }
}
```

**キャッシュデータ構造:**

```json
{
  "cache_key": "aws_doc:EC2:VPC",
  "cache_value": "AWS VPC documentation content...",
  "created_at": "2025-07-29T10:00:00Z",
  "ttl": 1722340800
}
```

### 2. Lambda メモリキャッシュ (短期間)

```python
import time
from typing import Dict, Any, Optional

class LambdaMemoryCache:
    """Lambda実行環境内でのメモリキャッシュ"""

    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            item = self._cache[key]
            if time.time() < item['expires_at']:
                return item['value']
            else:
                del self._cache[key]
        return None

    def set(self, key: str, value: Any, ttl_seconds: int = 300):
        """デフォルト5分間キャッシュ"""
        self._cache[key] = {
            'value': value,
            'expires_at': time.time() + ttl_seconds
        }

    def clear(self):
        self._cache.clear()

# グローバルインスタンス（Lambda実行環境で再利用）
memory_cache = LambdaMemoryCache()
```

### 3. キャッシュ管理クラス

```python
class ServerlessCacheManager:
    def __init__(self, cache_table_name: str = "aws-exam-coach-cache"):
        self.dynamodb = boto3.resource('dynamodb')
        self.cache_table = self.dynamodb.Table(cache_table_name)
        self.memory_cache = memory_cache

    async def get_aws_doc(self, service: str, topic: str) -> Optional[str]:
        cache_key = f"aws_doc:{service}:{topic}"

        # 1. メモリキャッシュから確認
        cached_value = self.memory_cache.get(cache_key)
        if cached_value:
            return cached_value

        # 2. DynamoDBキャッシュから確認
        try:
            response = self.cache_table.get_item(Key={'cache_key': cache_key})
            if 'Item' in response:
                value = response['Item']['cache_value']
                # メモリキャッシュにも保存（5分間）
                self.memory_cache.set(cache_key, value, 300)
                return value
        except Exception as e:
            logger.warning(f"キャッシュ取得エラー: {e}")

        return None

    async def cache_aws_doc(self, service: str, topic: str, content: str, ttl_hours: int = 24):
        cache_key = f"aws_doc:{service}:{topic}"

        # TTL設定（24時間後）
        ttl = int(time.time()) + (ttl_hours * 3600)

        # DynamoDBに保存
        try:
            self.cache_table.put_item(
                Item={
                    'cache_key': cache_key,
                    'cache_value': content,
                    'created_at': datetime.now().isoformat(),
                    'ttl': ttl
                }
            )

            # メモリキャッシュにも保存
            self.memory_cache.set(cache_key, content, 300)

        except Exception as e:
            logger.error(f"キャッシュ保存エラー: {e}")
```
