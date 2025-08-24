#!/bin/bash

# 移行元リソース削除スクリプト（最終版）
# 注意: このスクリプトは移行完了後にのみ実行してください

set -e

echo "🚨 移行元リソース削除スクリプト"
echo "================================"
echo "⚠️  このスクリプトは現在接続中のアカウントのAWS Exam Agentリソースを削除します"

# プロファイル指定の確認
if [ -z "$AWS_PROFILE" ]; then
    echo "⚠️  AWS_PROFILE 環境変数が設定されていません"
    echo "💡 移行元アカウントのプロファイルを指定してください"
    echo "💡 使用例: export AWS_PROFILE=default && ./scripts/cleanup-source-resources.sh"
    exit 1
fi

# アカウント確認
echo ""
echo "🔍 接続先アカウント確認..."
ACCOUNT_INFO=$(aws sts get-caller-identity --profile "$AWS_PROFILE")
CURRENT_ACCOUNT=$(echo "$ACCOUNT_INFO" | jq -r '.Account')
CURRENT_USER=$(echo "$ACCOUNT_INFO" | jq -r '.Arn')

echo "📋 削除対象アカウント: $CURRENT_ACCOUNT"
echo "📋 実行ユーザー: $CURRENT_USER"

# 移行先アカウントでないことの確認
echo ""
echo "⚠️  移行元アカウントであることを確認してください"
echo "💡 現在接続中のアカウントが移行元（削除対象）であることを確認してから続行してください"
echo ""
read -p "このアカウント ($CURRENT_ACCOUNT) が移行元アカウントで間違いありませんか？ (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 削除をキャンセルしました"
    echo "💡 正しい移行元アカウントのプロファイルに切り替えてから再実行してください"
    exit 1
fi

echo "✅ 移行先アカウントではありません"

# リソース確認
echo ""
echo "🔍 削除対象リソースの確認..."

# CloudFormationスタック確認
STACKS=$(aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE DELETE_FAILED --profile "$AWS_PROFILE" --query 'StackSummaries[?contains(StackName, `aws-exam-agent`)].StackName' --output text 2>/dev/null || echo "")
if [ -n "$STACKS" ]; then
    echo "📋 CloudFormationスタック:"
    for STACK in $STACKS; do
        STACK_STATUS=$(aws cloudformation describe-stacks --stack-name "$STACK" --profile "$AWS_PROFILE" --query 'Stacks[0].StackStatus' --output text)
        echo "  - $STACK ($STACK_STATUS)"
    done
fi

# ECRリポジトリ確認
ECR_REPOS=$(aws ecr describe-repositories --profile "$AWS_PROFILE" --query 'repositories[?contains(repositoryName, `aws-exam-agent`) || contains(repositoryName, `bedrock-agentcore`)].repositoryName' --output text 2>/dev/null || echo "")
if [ -n "$ECR_REPOS" ]; then
    echo "📋 ECRリポジトリ:"
    for REPO in $ECR_REPOS; do
        IMAGE_COUNT=$(aws ecr list-images --repository-name "$REPO" --profile "$AWS_PROFILE" --query 'length(imageIds)' --output text 2>/dev/null || echo "0")
        echo "  - $REPO (イメージ数: $IMAGE_COUNT)"
    done
fi

# 最終確認
echo ""
echo "🚨 最終確認"
echo "==========="
echo "アカウント $CURRENT_ACCOUNT の以下のリソースを削除します:"
echo ""
echo "【削除手順】"
echo "1. ECRリポジトリ強制削除（イメージ含む）"
echo "2. CloudFormationスタック削除"
echo "3. 残存リソース個別削除"
echo ""
echo "【削除されるリソース】"
echo "- ECRリポジトリ（全イメージ含む）"
echo "- EventBridge Schedule"
echo "- Lambda 関数"
echo "- IAMロール"
echo "- S3バケット"
echo "- CodeBuildプロジェクト"
echo ""
echo "⚠️  この操作は取り消せません！"
echo ""
read -p "本当に削除しますか？ (DELETE と入力してください): " CONFIRMATION

if [ "$CONFIRMATION" != "DELETE" ]; then
    echo "❌ 削除をキャンセルしました"
    exit 1
fi

echo ""
echo "🗑️  リソース削除を開始します..."

# 1. ECRリポジトリの強制削除（CloudFormation削除失敗を防ぐため）
echo ""
echo "🐳 ECR リポジトリの強制削除..."
if [ -n "$ECR_REPOS" ]; then
    for REPO in $ECR_REPOS; do
        echo "  削除中: $REPO"
        IMAGE_COUNT=$(aws ecr list-images --repository-name "$REPO" --profile "$AWS_PROFILE" --query 'length(imageIds)' --output text 2>/dev/null || echo "0")
        echo "    イメージ数: $IMAGE_COUNT（全て削除されます）"
        aws ecr delete-repository --repository-name "$REPO" --force --profile "$AWS_PROFILE" || echo "  ⚠️  削除失敗: $REPO"
        echo "  ✅ 削除完了: $REPO"
    done
else
    echo "  ℹ️  ECR リポジトリが見つかりません"
fi

# 2. CloudFormation スタックの削除
echo ""
echo "☁️  CloudFormation スタックの削除..."
if [ -n "$STACKS" ]; then
    for STACK in $STACKS; do
        STACK_STATUS=$(aws cloudformation describe-stacks --stack-name "$STACK" --profile "$AWS_PROFILE" --query 'Stacks[0].StackStatus' --output text 2>/dev/null || echo "NOT_FOUND")
        
        if [ "$STACK_STATUS" = "DELETE_FAILED" ]; then
            echo "  削除失敗状態のスタックを再削除: $STACK"
        elif [ "$STACK_STATUS" != "NOT_FOUND" ]; then
            echo "  削除中: $STACK"
        else
            echo "  スキップ: $STACK (既に削除済み)"
            continue
        fi
        
        aws cloudformation delete-stack --stack-name "$STACK" --profile "$AWS_PROFILE"
        echo "    待機中: $STACK の削除完了まで..."
        aws cloudformation wait stack-delete-complete --stack-name "$STACK" --profile "$AWS_PROFILE" || echo "    ⚠️  削除待機タイムアウト: $STACK"
        
        # 削除結果確認
        FINAL_STATUS=$(aws cloudformation describe-stacks --stack-name "$STACK" --profile "$AWS_PROFILE" --query 'Stacks[0].StackStatus' --output text 2>/dev/null || echo "DELETED")
        if [ "$FINAL_STATUS" = "DELETED" ]; then
            echo "  ✅ 削除完了: $STACK"
        else
            echo "  ⚠️  削除未完了: $STACK ($FINAL_STATUS)"
        fi
    done
else
    echo "  ℹ️  CloudFormation スタックが見つかりません"
fi

# 3. 残存リソースの個別削除
echo ""
echo "🔍 残存リソースの個別削除..."

# 残存Lambda関数
REMAINING_FUNCTIONS=$(aws lambda list-functions --profile "$AWS_PROFILE" --query 'Functions[?contains(FunctionName, `aws-exam-agent`)].FunctionName' --output text 2>/dev/null || echo "")
if [ -n "$REMAINING_FUNCTIONS" ]; then
    echo "  ⚠️  残存Lambda関数:"
    for FUNCTION in $REMAINING_FUNCTIONS; do
        echo "    削除中: $FUNCTION"
        aws lambda delete-function --function-name "$FUNCTION" --profile "$AWS_PROFILE" || echo "    ❌ 削除失敗: $FUNCTION"
    done
fi

# 残存CodeBuildプロジェクト
REMAINING_BUILDS=$(aws codebuild list-projects --profile "$AWS_PROFILE" --query 'projects[?contains(@, `bedrock-agentcore`) || contains(@, `aws-exam-agent`)]' --output text 2>/dev/null || echo "")
if [ -n "$REMAINING_BUILDS" ]; then
    echo "  ⚠️  残存CodeBuildプロジェクト:"
    for PROJECT in $REMAINING_BUILDS; do
        echo "    削除中: $PROJECT"
        aws codebuild delete-project --name "$PROJECT" --profile "$AWS_PROFILE" || echo "    ❌ 削除失敗: $PROJECT"
    done
fi

# 残存S3バケット
REMAINING_BUCKETS=$(aws s3api list-buckets --profile "$AWS_PROFILE" --query 'Buckets[?contains(Name, `aws-exam-agent`) || contains(Name, `bedrock-agentcore`)].Name' --output text 2>/dev/null || echo "")
if [ -n "$REMAINING_BUCKETS" ]; then
    echo "  ⚠️  残存S3バケット:"
    for BUCKET in $REMAINING_BUCKETS; do
        echo "    削除中: $BUCKET"
        aws s3 rm "s3://$BUCKET" --recursive --profile "$AWS_PROFILE" 2>/dev/null || echo "    ⚠️  オブジェクト削除失敗: $BUCKET"
        aws s3api delete-bucket --bucket "$BUCKET" --profile "$AWS_PROFILE" || echo "    ❌ バケット削除失敗: $BUCKET"
    done
fi

# 残存IAMロール
REMAINING_ROLES=$(aws iam list-roles --profile "$AWS_PROFILE" --query 'Roles[?contains(RoleName, `AmazonBedrockAgentCore`) || contains(RoleName, `LambdaTriggerFunction`) || contains(RoleName, `EventBridgeScheduler`)].RoleName' --output text 2>/dev/null || echo "")
if [ -n "$REMAINING_ROLES" ]; then
    echo "  ⚠️  残存IAMロール:"
    for ROLE in $REMAINING_ROLES; do
        echo "    削除中: $ROLE"
        
        # アタッチされたポリシーを削除
        ATTACHED_POLICIES=$(aws iam list-attached-role-policies --role-name "$ROLE" --profile "$AWS_PROFILE" --query 'AttachedPolicies[].PolicyArn' --output text 2>/dev/null || echo "")
        for POLICY in $ATTACHED_POLICIES; do
            aws iam detach-role-policy --role-name "$ROLE" --policy-arn "$POLICY" --profile "$AWS_PROFILE" 2>/dev/null || echo "      ⚠️  ポリシーデタッチ失敗: $POLICY"
        done
        
        # インラインポリシーを削除
        INLINE_POLICIES=$(aws iam list-role-policies --role-name "$ROLE" --profile "$AWS_PROFILE" --query 'PolicyNames' --output text 2>/dev/null || echo "")
        for POLICY in $INLINE_POLICIES; do
            aws iam delete-role-policy --role-name "$ROLE" --policy-name "$POLICY" --profile "$AWS_PROFILE" 2>/dev/null || echo "      ⚠️  インラインポリシー削除失敗: $POLICY"
        done
        
        # ロールを削除
        aws iam delete-role --role-name "$ROLE" --profile "$AWS_PROFILE" || echo "    ❌ ロール削除失敗: $ROLE"
    done
fi

echo ""
echo "✅ 移行元リソース削除完了"
echo "========================"
echo "📋 削除対象アカウント: $CURRENT_ACCOUNT"
echo ""
echo "💡 削除手順:"
echo "1. ECRリポジトリ強制削除（イメージ含む）"
echo "2. CloudFormationスタック削除"
echo "3. 残存リソース個別削除"
echo ""
echo "🎯 移行先での動作確認:"
echo "   AWS_PROFILE=sandbox ./scripts/test-agentcore.sh"
echo "   AWS_PROFILE=sandbox ./scripts/test-lambda.sh"
echo ""
echo "🧹 次のステップ（手動実行）:"
echo "   移行元バックアップファイルの削除:"
echo "   rm -f app/agentcore/.bedrock_agentcore.yaml.backup"
echo "   rm -f app/agentcore/Dockerfile.backup"
echo "   rm -f app/agentcore/.dockerignore.backup"
