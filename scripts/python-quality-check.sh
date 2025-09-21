#!/bin/bash
# Python品質チェックスクリプト - CI/CD & フック共通版
# 使用方法: 
#   ./scripts/python-quality-check.sh <file>     # 単一ファイル
#   ./scripts/python-quality-check.sh            # 全体チェック
#   ./scripts/python-quality-check.sh --fast     # 高速テスト（開発時用）

set -e

# 引数処理
TARGET_FILE="$1"
PROJECT_ROOT="$(pwd)"

# 設定
RUFF_TARGETS="app/ tests/"
MYPY_TARGETS="app/ tests/"
PYTEST_TARGETS="tests/"

# 高速テスト用設定（重いagent_main.pyテストを除外）
FAST_PYTEST_TARGETS="tests/unit/agentcore/test_domain_memory_client.py tests/unit/agentcore/test_teams_client.py tests/unit/trigger/test_lambda_function.py"

if [[ "$TARGET_FILE" == "--fast" ]]; then
    echo "🚀 Python品質チェック開始: 高速モード（開発時用）"
    
    # 高速モード（重いテストを除外）
    echo "📝 Ruff チェック..."
    uv run ruff check $RUFF_TARGETS
    echo "✅ Ruff完了"
    
    echo "🔍 Mypy型チェック..."
    uv run mypy $MYPY_TARGETS
    echo "✅ Mypy完了"
    
    echo "🧪 高速テスト実行（agent_main.pyの重いテストを除外）..."
    uv run pytest $FAST_PYTEST_TARGETS --cov=app --cov-report=term-missing
    echo "✅ テスト完了"
    
elif [[ -n "$TARGET_FILE" ]]; then
    echo "🚀 Python品質チェック開始: $(basename "$TARGET_FILE")"
    
    # 単一ファイルモード
    echo "📝 Ruff自動修正..."
    uv run ruff check --fix "$TARGET_FILE"
    uv run ruff format "$TARGET_FILE"
    echo "✅ Ruff完了"
    
    echo "🔍 Mypy型チェック..."
    uv run mypy "$TARGET_FILE" --show-error-codes
    echo "✅ Mypy完了"
    
    # 関連テスト検出・実行
    RELATED_TEST=""
    if [[ "$TARGET_FILE" == app/shared/* ]]; then
        MODULE_NAME=$(basename "$TARGET_FILE" .py)
        RELATED_TEST="tests/unit/shared/test_${MODULE_NAME}.py"
    elif [[ "$TARGET_FILE" == app/agentcore/* ]]; then
        REL_PATH=${TARGET_FILE#app/agentcore/}
        MODULE_NAME=$(basename "$REL_PATH" .py)
        RELATED_TEST="tests/unit/agentcore/test_${MODULE_NAME}.py"
    elif [[ "$TARGET_FILE" == tests/* ]]; then
        RELATED_TEST="$TARGET_FILE"
    fi
    
    if [[ -n "$RELATED_TEST" && -f "$RELATED_TEST" ]]; then
        echo "🧪 関連テスト実行: $(basename "$RELATED_TEST")"
        uv run pytest "$RELATED_TEST" -v
        echo "✅ テスト完了"
    else
        echo "ℹ️  関連テストなし"
    fi
    
else
    echo "🚀 Python品質チェック開始: 全体（CI/CD用）"
    
    # 全体チェックモード（CI用）
    echo "📝 Ruff チェック..."
    uv run ruff check $RUFF_TARGETS
    echo "✅ Ruff完了"
    
    echo "🔍 Mypy型チェック..."
    uv run mypy $MYPY_TARGETS
    echo "✅ Mypy完了"
    
    echo "🧪 全テスト実行..."
    uv run pytest $PYTEST_TARGETS
    echo "✅ テスト完了"
fi

echo "🎉 品質チェック完了"