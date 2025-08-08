#!/bin/bash
# Infrastructure品質チェックスクリプト
# 使用方法: 
#   ./scripts/infrastructure-quality-check.sh <file>     # 単一ファイル
#   ./scripts/infrastructure-quality-check.sh            # 全体チェック

set -e

# 引数処理
TARGET_FILE="$1"
PROJECT_ROOT="$(pwd)"

# 設定
YAML_TARGETS="infrastructure/ app/agentcore/.bedrock_agentcore.yaml"

if [[ -n "$TARGET_FILE" ]]; then
    echo "🚀 Infrastructure品質チェック開始: $(basename "$TARGET_FILE")"
    
    # 単一ファイルモード
    if [[ "$TARGET_FILE" == *.yaml || "$TARGET_FILE" == *.yml ]]; then
        echo "📝 YAML品質チェック..."
        uv run yamllint "$TARGET_FILE"
        echo "✅ yamllint完了"
        
        # CloudFormation/SAMテンプレートの場合
        if [[ "$TARGET_FILE" == infrastructure/* ]]; then
            echo "🔍 CloudFormation構文チェック..."
            uv run cfn-lint "$TARGET_FILE"
            echo "✅ cfn-lint完了"
        fi
    else
        echo "ℹ️  YAMLファイルではありません: $TARGET_FILE"
    fi
    
else
    echo "🚀 Infrastructure品質チェック開始: 全体"
    
    # 全体チェックモード
    echo "📝 YAML品質チェック..."
    uv run yamllint $YAML_TARGETS
    echo "✅ yamllint完了"
    
    echo "🔍 CloudFormation構文チェック..."
    if [[ -d "infrastructure" ]]; then
        uv run cfn-lint infrastructure/*.yaml infrastructure/*.yml 2>/dev/null || true
        echo "✅ cfn-lint完了"
    fi
fi

echo "🎉 Infrastructure品質チェック完了"