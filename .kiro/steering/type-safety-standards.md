# 型安全性管理規約

## 概要

AWS Exam Agent プロジェクトにおける型安全性の管理規約です。
`# type: ignore` の使用を最小限に抑え、健全で保守性の高いコードベースを維持します。

**関連ドキュメント**: 一般的な Python コーディング規約は `python-coding-standards.md` を参照してください。

## 基本原則

### 1. `# type: ignore` 使用の原則禁止

- **基本方針**: `# type: ignore` は原則として使用禁止
- **例外条件**: 以下の条件を全て満たす場合のみ使用可能
  1. 他の解決策（型ガード、cast、型注釈）では解決不可能
  2. 使用理由を詳細なコメントで説明
  3. コードレビューでの承認取得
  4. 将来的な解決策の検討・記録

### 2. 型安全性の段階的向上

- **Phase 1**: 既存の `# type: ignore` を適切な手法で置き換え
- **Phase 2**: 新規コードでの型安全性確保
- **Phase 3**: 外部ライブラリとの境界での型安全性強化

### 3. 教育的価値の重視

- 型安全性の学習機会として活用
- 適切な解決策の蓄積・共有
- チーム全体での型安全性意識向上

## 適切な解決策

### 1. 型ガード（isinstance）の使用

**Union 型の安全な処理**:

```python
# ❌ 不適切
result = some_function()  # type: ignore[assignment]

# ✅ 適切
if isinstance(result, Exception):
    # エラー処理
    error_info = {"error": str(result)}
else:
    # 正常処理（型が自動的に絞り込まれる）
    success_info = result
```

### 2. cast 関数の活用

**型推論が困難な場合の明示的キャスト**:

```python
from typing import cast

# ❌ 不適切
data = complex_operation()  # type: ignore[assignment]

# ✅ 適切
if isinstance(results[0], Exception):
    data = {"error": str(results[0])}
else:
    # 理由を明記したcast
    # asyncio.gatherの結果は正常時にdict[str, Any]を返すことが保証されている
    data = cast(dict[str, Any], results[0])
```

### 3. 適切な型注釈の追加

**変数・関数の型を明確化**:

```python
# ❌ 不適切
def process_data(data):  # type: ignore
    return data

# ✅ 適切
def process_data(data: dict[str, Any]) -> dict[str, Any]:
    return data
```

### 4. 外部ライブラリの型チェック無視

**pyproject.toml での設定**:

```toml
[[tool.mypy.overrides]]
module = [
    "moto.*",                    # テスト用AWSモック（型スタブなし）
    "aws_lambda_powertools.*",   # AWS Lambda用ユーティリティ（型スタブ不完全）
    "strands_agents.*",          # エージェントフレームワーク（型スタブなし）
    "boto3.*",                   # AWS SDK（型スタブは別パッケージで複雑）
]
ignore_missing_imports = true
```

## 非同期プログラミングの型安全性

### 1. 非同期関数の適切なテスト

**asyncio.Future を使った非同期モック**:

```python
# ❌ 不適切
mock_async_func.return_value = {"result": "data"}  # 同期的な戻り値

# ✅ 適切
import asyncio
from typing import Any

future: asyncio.Future[Any] = asyncio.Future()
future.set_result({"result": "data"})
mock_async_func.return_value = future
```

### 2. asyncio.gather の型安全な処理

**例外処理を含む並行処理**:

```python
# ❌ 不適切
results = await asyncio.gather(task1, task2, return_exceptions=True)
data1 = results[0]  # type: ignore[assignment]
data2 = results[1]  # type: ignore[assignment]

# ✅ 適切
results = await asyncio.gather(task1, task2, return_exceptions=True)

if isinstance(results[0], Exception):
    data1 = {"error": str(results[0])}
else:
    data1 = cast(dict[str, Any], results[0])

if isinstance(results[1], Exception):
    data2 = {"error": str(results[1])}
else:
    data2 = cast(dict[str, Any], results[1])
```

## テストコードの型安全性

### 1. テストコードも本番コード同等の品質

**基本方針**:

- テストコードも本番コードと同等の型チェック基準を適用
- 「テストだから緩くても良い」という考えを排除
- 長期的な保守性を重視

### 2. 適切なテスト関数の型注釈

```python
# ❌ 不適切
def test_example():
    pass

# ✅ 適切
def test_example(self) -> None:
    pass

async def test_async_example(self) -> None:
    pass
```

### 3. モックオブジェクトの型安全な使用

```python
from unittest.mock import Mock
import pytest

# ✅ 適切
def test_with_mock(self, mock_service: Mock) -> None:
    mock_service.return_value = {"expected": "result"}
    result = service_function()
    assert result["expected"] == "result"
```

## 品質保証チェックリスト

### 開発時の必須チェック

- [ ] `uv run mypy app/ tests/` でエラー 0 件
- [ ] `uv run ruff check app/ tests/` でエラー 0 件
- [ ] IDE 上でエラー表示がない
- [ ] `# type: ignore` の使用がない（または適切な理由付き）

### コードレビュー時の確認事項

- [ ] 型ガード（isinstance）で解決できる箇所がないか
- [ ] cast 関数で適切に解決できる箇所がないか
- [ ] 型注釈の追加で解決できる箇所がないか
- [ ] `# type: ignore` 使用時の理由が明確か

### CI/CD パイプラインでの自動チェック

```bash
# 型チェック
uv run mypy app/ tests/ --show-error-codes

# リンターチェック
uv run ruff check app/ tests/

# type: ignore の使用チェック
if grep -r "# type: ignore" app/ tests/; then
    echo "ERROR: # type: ignore found. Please use proper type safety techniques."
    exit 1
fi
```

## トラブルシューティング

### 1. Union 型の処理エラー

**症状**: `Union[T, Exception]` 型での assignment エラー

**解決策**:

```python
# isinstance による型ガード使用
if isinstance(result, Exception):
    # Exception の場合の処理
else:
    # T 型の場合の処理（型が自動的に絞り込まれる）
```

### 2. asyncio.gather の型エラー

**症状**: `asyncio.gather` の戻り値での型エラー

**解決策**:

```python
# cast関数を使用した明示的キャスト
if isinstance(results[0], Exception):
    data = {"error": str(results[0])}
else:
    data = cast(ExpectedType, results[0])
```

### 3. 外部ライブラリの型エラー

**症状**: boto3、moto 等の外部ライブラリでの型エラー

**解決策**:

```toml
# pyproject.toml での設定
[[tool.mypy.overrides]]
module = ["problematic_library.*"]
ignore_missing_imports = true
```

## 成功事例

### プロジェクト実績（2025 年 8 月 10 日）

**削除前の状況**:

- `# type: ignore` 使用箇所: 5 箇所
- 型安全性の問題: 実行時エラーのリスク
- 保守性の問題: 意図不明なコード

**削除後の成果**:

- `# type: ignore` 使用箇所: 0 箇所（完全削除）
- Mypy エラー: 0 件
- Ruff エラー: 0 件
- テスト通過率: 100%

**学習効果**:

- 適切な型ガード手法の習得
- cast 関数の効果的な活用
- 非同期プログラミングの型安全性向上
- テストコードの品質向上

## まとめ

型安全性の向上により、以下の効果を実現します：

1. **実行時エラーの削減**: 型チェックによる事前エラー検出
2. **保守性の向上**: 意図が明確なコード
3. **開発効率の向上**: IDE での型チェック支援
4. **学習効果の最大化**: 適切な型安全性手法の習得

これらの規約により、**健全で保守性の高いコードベース**を維持し、長期的な開発効率向上を実現します。

---

**策定日**: 2025 年 8 月 10 日  
**適用範囲**: AWS Exam Agent プロジェクト全体  
**必須遵守事項**: `# type: ignore` の原則使用禁止、適切な型安全性手法の使用
