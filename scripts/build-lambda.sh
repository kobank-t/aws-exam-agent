#!/bin/bash

# Lambda関数ローカルビルドスクリプト
# buildspec.ymlと同じ処理をローカルで実行

set -e

# 設定
LAMBDA_DIR="app/lambda/trigger"
BUILD_DIR="$LAMBDA_DIR/build"
PACKAGE_NAME="trigger-function.zip"

echo "🚀 Lambda関数ビルド開始"
echo "Lambda Directory: $LAMBDA_DIR"

# 1. ビルドディレクトリの準備
echo "📁 ビルドディレクトリ準備中..."
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# 2. Lambda関数ファイルのコピー
echo "📄 Lambda関数ファイルコピー中..."
cp "$LAMBDA_DIR/lambda_function.py" "$BUILD_DIR/"

# 3. 依存関係のインストール
echo "📦 依存関係インストール中..."
pip install -r "$LAMBDA_DIR/requirements.txt" -t "$BUILD_DIR/"

# 4. boto3バージョンとbedrock-agentcoreサポートの確認
echo "🔍 boto3バージョンとbedrock-agentcoreサポート確認中..."
cd "$BUILD_DIR"
python3 -c "
import boto3
print(f'boto3 version: {boto3.__version__}')
session = boto3.Session()
services = session.get_available_services()
bedrock_agentcore_supported = 'bedrock-agentcore' in services
print(f'bedrock-agentcore supported: {bedrock_agentcore_supported}')
if bedrock_agentcore_supported:
    print('✅ bedrock-agentcore is supported!')
else:
    print('❌ bedrock-agentcore is not supported')
    exit(1)
"
cd - > /dev/null

# 5. ZIPパッケージの作成
echo "📦 ZIPパッケージ作成中..."
cd "$BUILD_DIR"
zip -r "../$PACKAGE_NAME" . -x "*.pyc" "*/__pycache__/*" > /dev/null
cd - > /dev/null

# 6. パッケージサイズの確認
PACKAGE_PATH="$LAMBDA_DIR/$PACKAGE_NAME"
PACKAGE_SIZE=$(du -h "$PACKAGE_PATH" | cut -f1)
echo "📊 パッケージサイズ: $PACKAGE_SIZE"
ls -la "$PACKAGE_PATH"

# 7. クリーンアップ
echo "🧹 ビルドディレクトリクリーンアップ中..."
rm -rf "$BUILD_DIR"

echo "✅ Lambda関数ビルド完了"
echo "📍 パッケージ場所: $PACKAGE_PATH"
echo ""
echo "🎯 次のステップ:"
echo "1. S3にアップロード:"
echo "   aws s3 cp $PACKAGE_PATH s3://YOUR-BUCKET/lambda-packages/"
echo ""
echo "2. CloudFormationでデプロイ:"
echo "   ./scripts/deploy-eventbridge-scheduler.sh"
echo ""
echo "💡 ヒント:"
echo "   デプロイ後にZIPファイルを削除する場合:"
echo "   rm $PACKAGE_PATH"
