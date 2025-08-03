# エラーハンドリング設計

## エラー分類と対応戦略

### 1. システムレベルエラー

#### DynamoDB エラー

```python
class DynamoDBError(Exception):
    """DynamoDB関連エラー"""
    pass

class DynamoDBThrottlingError(DynamoDBError):
    """DynamoDB スロットリングエラー"""
    def __init__(self, message: str, retry_count: int = 0):
        self.message = message
        self.retry_count = retry_count
        super().__init__(f"DynamoDB スロットリング (試行回数: {retry_count}): {message}")

class DynamoDBCapacityError(DynamoDBError):
    """DynamoDB 容量不足エラー"""
    def __init__(self, message: str, table_name: str):
        self.table_name = table_name
        super().__init__(f"DynamoDB 容量不足 [{table_name}]: {message}")

# 対応戦略: 指数バックオフによる再試行 + ジッター
import random
import asyncio

async def execute_with_retry(operation, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await operation()
        except DynamoDBThrottlingError as e:
            if attempt == max_retries - 1:
                raise
            # 指数バックオフ + ジッター
            base_wait = 2 ** attempt
            jitter = random.uniform(0, 0.1 * base_wait)
            wait_time = base_wait + jitter
            await asyncio.sleep(wait_time)
        except DynamoDBCapacityError as e:
            # 容量不足は即座に失敗
            logger.error(f"DynamoDB容量不足: {e.table_name}")
            raise
```

#### 外部 API エラー (Bedrock, Teams)

```python
class ExternalAPIError(Exception):
    """外部API関連エラー"""
    pass

class BedrockAPIError(ExternalAPIError):
    """Bedrock API エラー"""
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"Bedrock API エラー [{status_code}]: {message}")

class TeamsAPIError(ExternalAPIError):
    """Teams API エラー"""
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"Teams API エラー [{status_code}]: {message}")

# 対応戦略: サーキットブレーカーパターン
import time

class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    async def call(self, operation):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
            else:
                raise ExternalAPIError("サーキットブレーカーが開いています")

        try:
            result = await operation()
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"

            raise
```

### 2. ビジネスロジックエラー

#### 問題生成エラー

```python
class QuestionGenerationError(Exception):
    """問題生成関連エラー"""
    pass

class QualityCheckFailedError(QuestionGenerationError):
    """品質チェック失敗エラー"""
    def __init__(self, reason: str, quality_score: float):
        self.reason = reason
        self.quality_score = quality_score
        super().__init__(f"品質チェック失敗 (スコア: {quality_score}): {reason}")

class SimilarityCheckFailedError(QuestionGenerationError):
    """類似度チェック失敗エラー"""
    def __init__(self, similarity_score: float, similar_question_id: str):
        self.similarity_score = similarity_score
        self.similar_question_id = similar_question_id
        super().__init__(f"類似問題検出 (類似度: {similarity_score}, 問題ID: {similar_question_id})")

# 対応戦略: 再生成ロジック
class QuestionGenerationService:
    async def generate_with_quality_check(self, request: GenerationRequest, max_retries: int = 3):
        for attempt in range(max_retries):
            try:
                # 問題生成
                question = await self._generate_raw_question(request)

                # 品質チェック
                quality_result = await self.quality_service.validate_question(question)
                if not quality_result.is_valid:
                    raise QualityCheckFailedError(quality_result.reason, quality_result.score)

                # 類似度チェック
                similarity_result = await self.similarity_service.check_similarity(question)
                if not similarity_result.is_unique:
                    raise SimilarityCheckFailedError(
                        similarity_result.score,
                        similarity_result.similar_question_id
                    )

                return question

            except (QualityCheckFailedError, SimilarityCheckFailedError) as e:
                logger.warning(f"問題生成失敗 (試行 {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    raise QuestionGenerationError(f"最大試行回数に達しました: {e}")

                # プロンプト調整して再試行
                request = self._adjust_generation_request(request, e)
```

#### 配信エラー

```python
class DeliveryError(Exception):
    """配信関連エラー"""
    pass

class TeamsChannelNotFoundError(DeliveryError):
    """Teams チャネル未発見エラー"""
    def __init__(self, channel_id: str):
        self.channel_id = channel_id
        super().__init__(f"Teams チャネルが見つかりません: {channel_id}")

class MessagePostFailedError(DeliveryError):
    """メッセージ投稿失敗エラー"""
    def __init__(self, reason: str, retry_count: int = 0):
        self.reason = reason
        self.retry_count = retry_count
        super().__init__(f"メッセージ投稿失敗 (試行回数: {retry_count}): {reason}")

# 対応戦略: フォールバック配信
class TeamsDeliveryService:
    async def deliver_with_fallback(self, question: Question, primary_channel: str, fallback_channel: str):
        try:
            # プライマリチャネルに配信
            return await self._deliver_to_channel(question, primary_channel)
        except TeamsChannelNotFoundError:
            logger.warning(f"プライマリチャネル配信失敗、フォールバックに切り替え: {fallback_channel}")
            return await self._deliver_to_channel(question, fallback_channel)
        except MessagePostFailedError as e:
            if e.retry_count < 3:
                # 短時間待機後に再試行
                await asyncio.sleep(5)
                return await self._deliver_to_channel(question, primary_channel, e.retry_count + 1)
            else:
                # 最終的にフォールバックチャネルに配信
                logger.error(f"プライマリチャネル配信最終失敗、フォールバックに切り替え")
                return await self._deliver_to_channel(question, fallback_channel)
```

### 3. 統合エラーハンドリング

#### Lambda 関数レベルのエラーハンドリング

```python
import structlog
from typing import Dict, Any

logger = structlog.get_logger()

def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """統合エラーハンドリングを含むLambdaハンドラー"""

    # リクエストID設定
    request_id = context.aws_request_id
    logger = logger.bind(request_id=request_id)

    try:
        # リクエスト解析
        request = parse_request(event)
        logger.info("リクエスト受信", request=request)

        # ビジネスロジック実行
        result = await process_request(request)

        logger.info("処理完了", result=result)
        return create_success_response(result)

    except ValidationError as e:
        logger.warning("バリデーションエラー", error=str(e))
        return create_error_response(400, "リクエストが無効です", str(e))

    except QuestionGenerationError as e:
        logger.error("問題生成エラー", error=str(e))
        return create_error_response(500, "問題生成に失敗しました", str(e))

    except DeliveryError as e:
        logger.error("配信エラー", error=str(e))
        return create_error_response(500, "配信に失敗しました", str(e))

    except ExternalAPIError as e:
        logger.error("外部API エラー", error=str(e))
        return create_error_response(502, "外部サービスエラー", "一時的な問題が発生しています")

    except DynamoDBError as e:
        logger.error("データベースエラー", error=str(e))
        return create_error_response(500, "データベースエラー", "データ処理に失敗しました")

    except Exception as e:
        logger.exception("予期しないエラー", error=str(e))
        return create_error_response(500, "内部サーバーエラー", "予期しないエラーが発生しました")

def create_error_response(status_code: int, message: str, detail: str = None) -> Dict[str, Any]:
    """統一されたエラーレスポンス形式"""
    body = {
        "error": True,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }

    if detail:
        body["detail"] = detail

    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(body, ensure_ascii=False)
    }

def create_success_response(data: Any) -> Dict[str, Any]:
    """統一された成功レスポンス形式"""
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({
            "success": True,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }, ensure_ascii=False, default=str)
    }
```

## 監視・アラート設計

### CloudWatch メトリクス

```python
import boto3

cloudwatch = boto3.client('cloudwatch')

class MetricsCollector:
    def __init__(self, namespace: str = "AWS/ExamCoach"):
        self.namespace = namespace
        self.cloudwatch = cloudwatch

    async def record_question_generation_success(self, service: str, duration: float):
        """問題生成成功メトリクス"""
        await self._put_metric(
            metric_name="QuestionGenerationSuccess",
            value=1,
            unit="Count",
            dimensions=[
                {"Name": "Service", "Value": service}
            ]
        )

        await self._put_metric(
            metric_name="QuestionGenerationDuration",
            value=duration,
            unit="Seconds",
            dimensions=[
                {"Name": "Service", "Value": service}
            ]
        )

    async def record_question_generation_failure(self, service: str, error_type: str):
        """問題生成失敗メトリクス"""
        await self._put_metric(
            metric_name="QuestionGenerationFailure",
            value=1,
            unit="Count",
            dimensions=[
                {"Name": "Service", "Value": service},
                {"Name": "ErrorType", "Value": error_type}
            ]
        )

    async def record_delivery_metrics(self, status: str, channel_id: str):
        """配信メトリクス"""
        await self._put_metric(
            metric_name="DeliveryAttempt",
            value=1,
            unit="Count",
            dimensions=[
                {"Name": "Status", "Value": status},
                {"Name": "Channel", "Value": channel_id}
            ]
        )

    async def _put_metric(self, metric_name: str, value: float, unit: str, dimensions: list):
        """CloudWatch メトリクス送信"""
        try:
            self.cloudwatch.put_metric_data(
                Namespace=self.namespace,
                MetricData=[
                    {
                        'MetricName': metric_name,
                        'Dimensions': dimensions,
                        'Value': value,
                        'Unit': unit,
                        'Timestamp': datetime.now()
                    }
                ]
            )
        except Exception as e:
            logger.warning(f"メトリクス送信失敗: {e}")
```

### アラーム設定

```yaml
# CloudWatch Alarms (SAMテンプレートに追加)
Resources:
  QuestionGenerationFailureAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: aws-exam-coach-question-generation-failures
      AlarmDescription: 問題生成失敗率が高い
      MetricName: QuestionGenerationFailure
      Namespace: AWS/ExamCoach
      Statistic: Sum
      Period: 300
      EvaluationPeriods: 2
      Threshold: 3
      ComparisonOperator: GreaterThanThreshold
      AlarmActions:
        - !Ref SNSAlarmTopic

  DeliveryFailureAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: aws-exam-coach-delivery-failures
      AlarmDescription: Teams配信失敗率が高い
      MetricName: DeliveryAttempt
      Namespace: AWS/ExamCoach
      Dimensions:
        - Name: Status
          Value: failure
      Statistic: Sum
      Period: 300
      EvaluationPeriods: 2
      Threshold: 2
      ComparisonOperator: GreaterThanThreshold
      AlarmActions:
        - !Ref SNSAlarmTopic

  LambdaErrorAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: aws-exam-coach-lambda-errors
      AlarmDescription: Lambda関数エラー率が高い
      MetricName: Errors
      Namespace: AWS/Lambda
      Dimensions:
        - Name: FunctionName
          Value: !Ref QuestionGeneratorFunction
      Statistic: Sum
      Period: 300
      EvaluationPeriods: 2
      Threshold: 5
      ComparisonOperator: GreaterThanThreshold
      AlarmActions:
        - !Ref SNSAlarmTopic

  SNSAlarmTopic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: aws-exam-coach-alerts
      DisplayName: AWS Exam Coach Alerts
```

## 復旧手順

### 自動復旧

```python
class AutoRecoveryService:
    async def handle_delivery_failure(self, question_id: str, original_error: DeliveryError):
        """配信失敗時の自動復旧"""
        try:
            # 1. 問題データの再取得
            question = await self.question_repo.get_question(question_id)

            # 2. フォールバックチャネルに配信
            fallback_channel = await self.get_fallback_channel()
            delivery_result = await self.delivery_service.deliver_to_channel(
                question, fallback_channel
            )

            # 3. 復旧ログ記録
            logger.info(f"自動復旧成功: {question_id} -> {fallback_channel}")

            return delivery_result

        except Exception as recovery_error:
            # 復旧失敗時は管理者に通知
            await self.notify_admin_recovery_failure(question_id, original_error, recovery_error)
            raise

    async def handle_generation_failure(self, request: GenerationRequest, original_error: QuestionGenerationError):
        """問題生成失敗時の自動復旧"""
        try:
            # 1. 過去の類似問題から選択
            fallback_question = await self.get_fallback_question(request.service, request.topic)

            if fallback_question:
                # 2. フォールバック問題を配信
                delivery_result = await self.delivery_service.deliver_question(fallback_question)

                # 3. フォールバック使用ログ
                logger.info(f"フォールバック問題使用: {fallback_question.question_id}")

                return delivery_result
            else:
                # フォールバック問題もない場合は管理者に通知
                await self.notify_admin_no_fallback(request, original_error)

        except Exception as recovery_error:
            await self.notify_admin_recovery_failure(request, original_error, recovery_error)
            raise
```
