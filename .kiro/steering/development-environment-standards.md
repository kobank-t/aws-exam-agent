---
inclusion: fileMatch
fileMatchPattern: "{.vscode/settings.json,pyproject.toml}"
---

# 開発環境設定規約

## 概要

Cloud CoPassAgent プロジェクトにおける開発環境設定の標準化規約です。
VS Code 設定、Mypy 設定、Ruff 設定の最適化により、チーム全体で一貫した開発体験を提供します。

## 基本原則

### 1. IDE 上でのエラー表示ゼロ

- **精神衛生上の重要性**: チームメンバー全員がクリーンな開発環境で作業
- **品質保証**: エラー表示がない = 高品質なコードベース
- **生産性向上**: エラー修正に時間を取られない

### 2. 本番コードとテストコードの品質統一

- テストコードも本番コードと同等の型チェック基準を適用
- 「テストだから緩くても良い」という考えを排除
- 長期的な保守性を重視

### 3. 自動化による品質保証

- 手動チェックに依存しない自動化された品質管理
- CI/CD パイプラインでの品質ゲート
- 開発者の認知負荷軽減

## VS Code 設定 (.vscode/settings.json)

### 推奨設定

```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "[python]": {
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": "explicit",
      "source.fixAll": "explicit"
    },
    "editor.rulers": [88],
    "editor.defaultFormatter": "charliermarsh.ruff"
  },
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"],
  "python.testing.unittestEnabled": false
}
```

### 重要な設定項目

#### 1. Ruff フォーマッター設定

```json
"editor.defaultFormatter": "charliermarsh.ruff"
```

**理由**:

- Ruff 拡張機能の正しい設定
- 古い Python 拡張機能設定との競合回避

#### 2. 型チェックの設定

**注意**: `python.analysis.typeCheckingMode`は廃止されました。

**現在の型チェック方法**:

- **Mypy 設定**: `pyproject.toml`での厳格な設定
- **コマンドライン**: `uv run mypy app/ tests/`
- **CI/CD**: パイプラインでの自動チェック

**効果**:

- コマンドラインでの確実な型エラー検出
- CI/CD での品質保証

#### 3. 自動修正の有効化

```json
"editor.codeActionsOnSave": {
  "source.organizeImports": "explicit",
  "source.fixAll": "explicit"
}
```

**効果**:

- 保存時の自動 import 整理
- 自動的なコードスタイル修正

**設定値の説明**:

- `"explicit"`: 明示的に有効化（推奨）
- `"always"`: 常に実行
- `"never"`: 無効化

### 避けるべき設定

#### ❌ 廃止された設定

```json
// これらの設定は使用しない（Python拡張機能の新バージョンで廃止）
"python.linting.enabled": true,
"python.linting.ruffEnabled": true,
"python.formatting.provider": "none"
```

## Mypy 設定 (pyproject.toml)

### 厳格な型チェック設定

```toml
[tool.mypy]
python_version = "3.12"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = false  # @toolデコレータ対応
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true
```

### 外部ライブラリの型チェック無視

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

**理由と品質保証戦略**:

- **型スタブ不足への対応**: 多くの Python ライブラリは型スタブ（.pyi）を提供していない
- **依存関係の簡素化**: 型スタブパッケージ（types-boto3 等）は 100+の追加依存関係が必要
- **学習プロジェクトに適した実用性**: 商用レベルの完璧な型安全性より開発効率を重視
- **品質劣化の防止策**:
  - 自分のコード（app/, tests/）は 100%厳格な型チェック維持
  - 外部ライブラリとの境界で明示的な型注釈を使用
  - Pydantic モデルによる実行時データ検証
  - moto + pytest による包括的なテストカバレッジ

### ❌ 避けるべき設定

```toml
# テストファイルの型チェック緩和は行わない
# [[tool.mypy.overrides]]
# module = "tests.*"
# disallow_untyped_defs = false
# disallow_incomplete_defs = false
```

**理由**:

- テストコードも本番コードと同等の品質を維持
- IDE 上でのエラー表示を回避
- チーム開発の精神衛生上重要

## Ruff 設定

### 基本設定

```toml
[tool.ruff]
line-length = 88
target-version = "py312"
src = ["app", "tests"]

[tool.ruff.lint]
select = [
    "E",  # pycodestyle errors
    "W",  # pycodestyle warnings
    "F",  # pyflakes
    "I",  # isort
    "B",  # flake8-bugbear
    "C4", # flake8-comprehensions
    "UP", # pyupgrade
    "N",  # pep8-naming
]
ignore = [
    "E501",  # line too long, handled by formatter
    "B008",  # do not perform function calls in argument defaults
]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
line-ending = "auto"
# skip-string-normalization は廃止済み（削除必要）
```

### 重要な注意点

#### 1. 廃止された設定の削除

```toml
# ❌ 削除が必要
skip-string-normalization = false
```

**理由**: Ruff の新バージョンで廃止され、`quote-style`に統合

#### 2. Python 3.12 対応

```toml
target-version = "py312"
```

**効果**: 最新の Python 機能を活用したコード変換

## トラブルシューティング

### 1. VS Code 設定がグレーアウトされる

**原因**: 古い Python 拡張機能設定の使用

**解決策**:

```json
// 削除する設定（廃止済み）
"python.linting.enabled": true,
"python.linting.ruffEnabled": true,
"python.formatting.provider": "none",
"python.analysis.typeCheckingMode": "strict"

// 追加する設定
"[python]": {
  "editor.defaultFormatter": "charliermarsh.ruff",
  "editor.codeActionsOnSave": {
    "source.organizeImports": "explicit",
    "source.fixAll": "explicit"
  }
}
```

### 2. Mypy エラーが大量に表示される

**原因**: テストファイルの型注釈不足

**解決策**:

```python
# 全てのテスト関数に型注釈を追加
def test_example(self) -> None:
    pass

def test_with_fixture(self, monkeypatch: pytest.MonkeyPatch) -> None:
    pass
```

### 3. Ruff エラー「unknown field」

**原因**: 廃止された設定の使用

**解決策**:

```toml
# pyproject.tomlから削除
# skip-string-normalization = false
```

### 4. VS Code 設定で「型が正しくありません」エラー

**原因**: `editor.codeActionsOnSave`の設定値が古い形式

**解決策**:

```json
// ❌ 古い形式（boolean値）
"editor.codeActionsOnSave": {
  "source.organizeImports": true,
  "source.fixAll": true
}

// ✅ 新しい形式（文字列値）
"editor.codeActionsOnSave": {
  "source.organizeImports": "explicit",
  "source.fixAll": "explicit"
}
```

### 5. 「不明な構成設定」警告

**原因**: 廃止された Python 拡張機能設定の使用

**解決策**:

```json
// ❌ 削除が必要（廃止済み設定）
"python.analysis.typeCheckingMode": "strict"
```

**代替手段**: pyproject.toml での Mypy 設定を使用

### 6. Mypy キャッシュエラー

**解決策**:

```bash
# キャッシュクリア
rm -rf .mypy_cache
uv run mypy app/ tests/
```

## 品質保証チェックリスト

### 開発環境セットアップ時

- [ ] VS Code 設定に廃止された項目がない
- [ ] Ruff 設定に廃止された項目がない
- [ ] Mypy 設定でテストファイル緩和を行っていない
- [ ] `uv run mypy app/ tests/` でエラー 0 件
- [ ] `uv run ruff check app/ tests/` でエラー 0 件
- [ ] IDE 上でエラー表示がない

### コード作成時

- [ ] 全ての関数に適切な型注釈
- [ ] テスト関数も`-> None`を明記
- [ ] Python 3.12+の新しい型注釈を使用
- [ ] 外部ライブラリの型エラーは適切に無視設定

### CI/CD 設定時

- [ ] Mypy、Ruff チェックをパイプラインに組み込み
- [ ] 品質ゲートでエラー 0 件を必須条件に設定
- [ ] 型チェック失敗時のビルド停止設定

## エージェントフック

### Python 品質チェックフック

Python ファイル編集時にエージェントが自動実行する包括的品質チェックフックです。

#### 動作方式

- **トリガー**: Python ファイル（`*.py`）の編集時
- **実行方式**: エージェントへのプロンプト送信（`type: "askAgent"`）
- **実行場所**: `.kiro/hooks/python-quality-check.kiro.hook`

#### 自動実行内容

1. **Ruff 自動修正とフォーマット**

   - `uv run ruff check --fix` でコードスタイル自動修正
   - `uv run ruff format` でフォーマット統一

2. **Mypy 型チェック**

   - `uv run mypy --show-error-codes` で型エラー検出
   - エラー詳細の報告

3. **関連テスト実行**

   - ファイルパスに基づく関連テスト自動検出
   - 対応関係に基づいたテスト実行

4. **結果サマリー**
   - 各ステップの実行結果を簡潔に報告
   - エラーがあっても処理継続

#### ファイル対応関係

- `app/shared/config.py` → `tests/unit/shared/test_config.py`
- `app/shared/exceptions.py` → `tests/unit/shared/test_exceptions.py`
- `app/shared/constants.py` → `tests/unit/shared/test_constants.py`
- `app/agentcore/agent_main.py` → `tests/unit/agentcore/test_agent_main.py`
- `tests/unit/*/test_*.py` → そのテストファイル自体

#### フック設定の確認・変更

```bash
# フック一覧確認
ls -la .kiro/hooks/

# フック設定確認
cat .kiro/hooks/python-quality-check.kiro.hook

# フック無効化（一時的）
# .kiro/hooks/python-quality-check.kiro.hook の "enabled": false に変更
```

#### 手動品質チェック

フックと同等の品質チェックを手動実行する場合：

```bash
# 特定ファイルの品質チェック（フックと同じロジック）
./scripts/python-quality-check.sh app/shared/config.py

# 全体品質チェック（CI/CDと同じロジック）
./scripts/python-quality-check.sh

# 個別コマンド実行
uv run ruff check --fix app/shared/config.py
uv run ruff format app/shared/config.py
uv run mypy app/shared/config.py --show-error-codes
uv run pytest tests/unit/shared/test_config.py -v
```

#### トラブルシューティング

- **フックが動作しない**: AGENT HOOKS エリアでフック状態を確認
- **実行時間が長い**: エージェントが効率的に実行するため、通常 6-10 秒で完了
- **エラー発生時**: ファイル保存は成功、エラー詳細はエージェント応答で確認
- **手動確認**: 上記の手動品質チェックコマンドで個別確認可能

## 型安全性向上の実践例

### `# type: ignore` の完全削除

**2025 年 8 月 10 日実施**: プロジェクト全体から `# type: ignore` を完全削除し、健全な型安全性を実現

#### 削除前の問題

- **5 箇所の `# type: ignore` 使用**: 根拠不明な型チェック無視
- **型安全性の低下**: 実行時エラーのリスク増加
- **保守性の問題**: 将来の開発者にとって意図不明

#### 適切な解決策の実装

**1. 型ガードと cast の使用**

```python
# 修正前（不健全）
documentation = documentation_result  # type: ignore[assignment]

# 修正後（型安全）
if isinstance(results[0], Exception):
    documentation = {"error": str(results[0])}
else:
    # asyncio.gatherの結果は正常時にdict[str, Any]を返すことが保証されている
    documentation = cast(dict[str, Any], results[0])
```

**2. 非同期テストの適切な実装**

```python
# 修正前（到達不可能コード）
doc_result = await mcp_client.get_aws_documentation("EC2", "overview")  # type: ignore[unreachable]

# 修正後（適切な条件）
doc_result = await mcp_client.get_aws_documentation("EC2", "overview")
```

#### 成果

- **型チェックエラー**: 0 件（`uv run mypy app/ tests/`）
- **リンターエラー**: 0 件（`uv run ruff check app/ tests/`）
- **テスト通過率**: 100%（統合テスト 10/10、単体テスト 15/15）
- **`# type: ignore` 使用**: 0 件（完全削除）

#### 学習効果

- **適切な型ガード**: `isinstance` による安全な型絞り込み
- **cast 関数の活用**: 型推論が困難な場合の明示的キャスト
- **非同期モック**: `asyncio.Future` を使った適切なテスト実装
- **コメントによる説明**: 型キャストの理由を明記

## まとめ

開発環境設定の標準化により、以下の効果を実現します：

1. **チーム全体での一貫した開発体験**
2. **IDE 上でのエラー表示ゼロによる精神衛生の向上**
3. **自動化による品質保証**（エージェントフック含む）
4. **長期的な保守性の確保**
5. **型安全性の向上**（`# type: ignore` 完全削除による健全なコード）

これらの設定は、プロジェクトの成功と開発者の生産性向上に直結する重要な要素です。

---

**更新日**: 2025 年 8 月 10 日  
**適用範囲**: Cloud CoPassAgent プロジェクト全体  
**必須遵守事項**: IDE 上でのエラー表示ゼロ、`# type: ignore` の使用禁止
