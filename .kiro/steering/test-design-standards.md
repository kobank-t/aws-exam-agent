---
inclusion: always
---

# テスト設計標準ルール

## 🎯 基本原則

**全ての単体テストは契約による設計（Design by Contract）に基づき、事前条件・事後条件・不変条件を明確に検証する**

### 契約による設計の必須実装

- **事前条件（Preconditions）**: 入力データの妥当性検証
- **事後条件（Postconditions）**: 出力データの妥当性検証
- **不変条件（Invariants）**: システム状態の一貫性検証

## 📋 テスト実装の必須要件

### 1. テストクラス・メソッド命名規則

#### **テストクラス命名**

```python
class TestModelName:
    """ModelName の契約検証"""

class TestFunctionName:
    """function_name 関数の契約検証"""
```

#### **テストメソッド命名**

```python
def test_valid_input_contract(self) -> None:
    """
    事前条件: 有効な入力データ
    事後条件: 期待される出力データが返される
    不変条件: データ型・構造の一貫性が保たれる
    """

def test_invalid_input_precondition(self) -> None:
    """
    事前条件: 無効な入力データ
    事後条件: ValidationError が発生する
    """

def test_business_logic_invariant(self) -> None:
    """
    不変条件: ビジネスロジックの一貫性が保たれる
    """
```

### 2. テストコード構造の標準化

#### **AAA パターンの必須適用**

```python
def test_example_contract(self) -> None:
    """
    事前条件: 具体的な入力条件
    事後条件: 具体的な期待結果
    不変条件: 保持されるべき条件
    """
    # Arrange - 事前条件設定
    input_data = {"key": "value"}
    expected_result = {"expected": "output"}

    # Act - 実行
    result = target_function(input_data)

    # Assert - 事後条件検証
    assert result == expected_result

    # 不変条件検証
    assert isinstance(result, dict)
    assert "required_field" in result
```

### 3. 契約検証の具体的実装

#### **事前条件検証パターン**

```python
def test_invalid_input_precondition(self) -> None:
    """事前条件違反時の適切なエラーハンドリング検証"""
    # Arrange - 事前条件違反: 無効なデータ
    invalid_data = {"invalid": "data"}

    # Act & Assert - 事前条件検証
    with pytest.raises(ValidationError):
        TargetModel(**invalid_data)
```

#### **事後条件検証パターン**

```python
def test_successful_operation_contract(self) -> None:
    """正常処理時の事後条件検証"""
    # Arrange - 事前条件設定
    valid_input = create_valid_input()

    # Act
    result = target_function(valid_input)

    # Assert - 事後条件検証
    assert result.status == "success"
    assert isinstance(result.data, list)
    assert len(result.data) > 0

    # 事後条件: 必須フィールドの存在確認
    for item in result.data:
        assert "id" in item
        assert "name" in item
```

#### **不変条件検証パターン**

```python
def test_data_integrity_invariant(self) -> None:
    """データ整合性の不変条件検証"""
    # Arrange
    model = create_test_model()

    # Act - 複数の操作を実行
    model.update_field1("new_value1")
    model.update_field2("new_value2")

    # Assert - 不変条件検証
    assert model.is_valid()  # 常に有効な状態を保持
    assert model.field1 != model.field2  # 異なるフィールドは異なる値
    assert len(model.history) > 0  # 操作履歴が記録される
```

### 4. 意図的エラーテストの実装

#### **型安全性テスト**

```python
def test_type_validation_invariant(self) -> None:
    """
    不変条件: 型バリデーションが正しく動作する
    """
    # 不変条件検証: 型エラーでValidationErrorが発生
    with pytest.raises(ValidationError):
        TargetModel(
            string_field=123,  # type: ignore  # 意図的な型エラーのテスト
            list_field="not_a_list",  # type: ignore  # 意図的な型エラーのテスト
        )
```

#### **ビジネスルール違反テスト**

```python
def test_business_rule_violation_precondition(self) -> None:
    """
    事前条件違反: ビジネスルール違反時の適切なエラーハンドリング
    """
    # 事前条件違反: 範囲外の値
    with pytest.raises(ValueError, match="値は1-100の範囲である必要があります"):
        create_model(value=150)  # 範囲外の値
```

## 🔧 テスト品質の必須要件

### 1. カバレッジ要件

- **単体テスト**: 新規作成コードの 90%以上
- **契約検証**: 全パブリックメソッド・プロパティの契約を検証
- **エラーパス**: 全例外処理パスをテスト

### 2. テストの独立性

```python
def test_independent_contract(self) -> None:
    """各テストは他のテストに依存しない"""
    # ❌ 悪い例: 他のテストの結果に依存
    # assert global_state.previous_test_result == "success"

    # ✅ 良い例: 自己完結したテスト
    input_data = create_fresh_test_data()
    result = target_function(input_data)
    assert result.is_valid()
```

### 3. モックの適切な使用

```python
@patch("module.external_service")
def test_external_dependency_contract(self, mock_service: MagicMock) -> None:
    """外部依存を持つ機能の契約検証"""
    # Arrange - モックの設定
    mock_service.return_value = create_mock_response()

    # Act
    result = function_with_external_dependency()

    # Assert - 事後条件検証
    assert result.status == "success"
    mock_service.assert_called_once_with(expected_params)
```

## 🚫 禁止事項

### テスト実装の禁止パターン

- **❌ 曖昧なテスト名**: `test_function()` → `test_valid_input_contract()`
- **❌ 契約の未記載**: docstring での契約明記必須
- **❌ 複数責任テスト**: 1 つのテストで複数の契約を検証
- **❌ 外部依存テスト**: 単体テストでの実際の API 呼び出し
- **❌ 手動確認依存**: 自動化できない検証方法

### type: ignore の適切な使用

```python
# ✅ 適切: 意図的な型エラーテスト
model = Model(field=123)  # type: ignore  # 意図的な型エラーのテスト

# ✅ 適切: 外部ライブラリの型定義不備
result = external_lib.function()  # type: ignore  # ライブラリの型定義不完全

# ❌ 不適切: 面倒だから無視
data = some_function()  # type: ignore  # 面倒だから無視
```

## ✅ 品質チェックリスト

### テスト作成時の必須確認項目

- [ ] **契約の明記**: docstring で事前条件・事後条件・不変条件を記載
- [ ] **AAA パターン**: Arrange・Act・Assert の明確な分離
- [ ] **独立性**: 他のテストに依存しない自己完結したテスト
- [ ] **命名規則**: `test_*_contract` または `test_*_precondition` 形式
- [ ] **型安全性**: 意図的な型エラーテストでの `type: ignore` 使用
- [ ] **エラーハンドリング**: 例外処理パスの適切なテスト
- [ ] **モック使用**: 外部依存の適切な分離

### 品質メトリクス

- [ ] **pytest**: 全テスト通過（100%）
- [ ] **mypy**: 型エラー 0 件（type: ignore は適切な理由付きのみ）
- [ ] **ruff**: リンターエラー 0 件
- [ ] **カバレッジ**: 新規コードの 90%以上

## 📖 参考実装例

### 完全な契約検証テストの例

```python
class TestUserModel:
    """User モデルの契約検証"""

    def test_valid_user_creation_contract(self) -> None:
        """
        事前条件: 有効なユーザーデータ
        事後条件: 正しいUserモデルが作成される
        不変条件: 必須フィールドが全て設定される
        """
        # Arrange - 事前条件設定
        user_data = {
            "name": "テストユーザー",
            "email": "test@example.com",
            "age": 25
        }

        # Act
        user = User(**user_data)

        # Assert - 事後条件検証
        assert user.name == "テストユーザー"
        assert user.email == "test@example.com"
        assert user.age == 25

        # 不変条件検証
        assert isinstance(user.name, str)
        assert len(user.name) > 0
        assert "@" in user.email
        assert user.age > 0

    def test_invalid_email_precondition(self) -> None:
        """
        事前条件違反: 無効なメールアドレス
        事後条件: ValidationError が発生する
        """
        # Arrange - 事前条件違反
        invalid_data = {
            "name": "テストユーザー",
            "email": "invalid-email",  # 無効なメール形式
            "age": 25
        }

        # Act & Assert - 事前条件検証
        with pytest.raises(ValidationError, match="email"):
            User(**invalid_data)

    def test_age_validation_invariant(self) -> None:
        """
        不変条件: 年齢は常に正の整数である
        """
        # 不変条件検証: 負の年齢でエラー
        with pytest.raises(ValidationError):
            User(name="テスト", email="test@example.com", age=-1)

        # 不変条件検証: 型エラー
        with pytest.raises(ValidationError):
            User(
                name="テスト",
                email="test@example.com",
                age="文字列"  # type: ignore  # 意図的な型エラーのテスト
            )
```

---

**制定日**: 2025 年 8 月 15 日  
**適用対象**: 全単体テスト  
**更新履歴**: 初版制定（契約による設計の標準化）
