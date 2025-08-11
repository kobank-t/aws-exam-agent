"""
基底データモデルの単体テスト

DynamoDBBaseModelとTimestampMixinの機能をテスト
"""

from datetime import datetime

import pytest

from app.models.base import DynamoDBBaseModel, TimestampMixin


class TestDynamoDBBaseModel:
    """DynamoDBBaseModelのテストクラス"""

    def test_to_dynamodb_item(self) -> None:
        """DynamoDB用のアイテム形式への変換をテスト"""

        # テスト用のモデルクラスを作成
        class TestModel(DynamoDBBaseModel):
            test_field: str = "test_value"

        model = TestModel()
        item = model.to_dynamodb_item()

        # datetime が ISO 文字列に変換されることを確認
        assert isinstance(item["created_at"], str)
        assert isinstance(item["updated_at"], str)
        assert item["created_by"] == "system"
        assert item["test_field"] == "test_value"

    def test_from_dynamodb_item(self) -> None:
        """DynamoDBアイテムからモデルの作成をテスト"""

        # テスト用のモデルクラスを作成
        class TestModel(DynamoDBBaseModel):
            test_field: str = "default"

        # DynamoDBアイテム形式のデータ
        item_data = {
            "test_field": "test_value",
            "created_at": "2025-08-10T10:00:00",
            "updated_at": "2025-08-10T11:00:00",
            "created_by": "test_user",
        }

        model: TestModel = TestModel.from_dynamodb_item(item_data)

        # datetime が正しく変換されることを確認
        assert isinstance(model.created_at, datetime)
        assert isinstance(model.updated_at, datetime)
        assert model.created_by == "test_user"
        # TestModelクラスで定義されたフィールドなので直接アクセス可能
        assert model.test_field == "test_value"

    def test_from_dynamodb_item_with_z_suffix(self) -> None:
        """Z接尾辞付きISO文字列の変換をテスト"""

        class TestModel(DynamoDBBaseModel):
            test_field: str = "default"

        item_data = {
            "test_field": "test_value",
            "created_at": "2025-08-10T10:00:00Z",  # Z接尾辞付き
            "updated_at": "2025-08-10T11:00:00Z",
            "created_by": "test_user",
        }

        model: TestModel = TestModel.from_dynamodb_item(item_data)

        # Z接尾辞が正しく処理されることを確認
        assert isinstance(model.created_at, datetime)
        assert isinstance(model.updated_at, datetime)

    def test_from_dynamodb_item_invalid_datetime(self) -> None:
        """不正なdatetime文字列の処理をテスト"""

        class TestModel(DynamoDBBaseModel):
            test_field: str = "default"

        item_data = {
            "test_field": "test_value",
            "created_at": "invalid_datetime",  # 不正な形式
            "updated_at": "2025-08-10T11:00:00",
            "created_by": "test_user",
        }

        # Pydanticのバリデーションエラーが発生することを確認
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            TestModel.from_dynamodb_item(item_data)


class TestTimestampMixin:
    """TimestampMixinのテストクラス"""

    def test_update_timestamp(self) -> None:
        """タイムスタンプ更新機能をテスト"""

        class TestModel(DynamoDBBaseModel, TimestampMixin):
            test_field: str = "test"

        model = TestModel()
        original_updated_at = model.updated_at

        # 少し待ってからタイムスタンプを更新
        import time

        time.sleep(0.01)
        model.update_timestamp()

        # updated_at が更新されることを確認
        assert model.updated_at > original_updated_at

    def test_model_config(self) -> None:
        """モデル設定が正しく適用されることをテスト"""

        class TestModel(DynamoDBBaseModel):
            test_field: str = "test"

        model = TestModel()

        # populate_by_name が設定されていることを確認
        assert model.model_config.get("populate_by_name") is True
        assert model.model_config.get("extra") == "allow"
