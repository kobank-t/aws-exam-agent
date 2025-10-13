#!/bin/bash

# AgentCore Memory 管理スクリプト
# メモリの確認・削除・分析を行います
# Memory設定: 30日間自動削除（eventExpiryDuration=30）

set -e

# 設定
# .envファイルから設定を読み込み
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

REGION="${AWS_DEFAULT_REGION:-us-east-1}"
MEMORY_ID="${AGENTCORE_MEMORY_ID:-CloudCoPassAgentMemory_1758807000-VM286QEJaJ}"
SESSION_ID="AWS-SAP"
ACTOR_ID="cloud-copass-agent"

# 色付きログ関数
log_info() {
    echo -e "\033[34m[INFO]\033[0m $1"
}

log_success() {
    echo -e "\033[32m[SUCCESS]\033[0m $1"
}

log_warning() {
    echo -e "\033[33m[WARNING]\033[0m $1"
}

log_error() {
    echo -e "\033[31m[ERROR]\033[0m $1"
}

# AWS認証確認
check_aws_auth() {
    log_info "AWS認証確認中..."
    if ! aws sts get-caller-identity --region $REGION > /dev/null 2>&1; then
        log_error "AWS認証に失敗しました。AWS_PROFILEを設定してください。"
        exit 1
    fi
    log_success "AWS認証成功"
}

# 現在のイベント一覧取得
get_events() {
    local include_payloads="${1:-false}"
    local events_output
    
    if [ "$include_payloads" = "true" ]; then
        # payloadを含めて取得
        events_output=$(aws bedrock-agentcore list-events \
            --memory-id "$MEMORY_ID" \
            --session-id "$SESSION_ID" \
            --actor-id "$ACTOR_ID" \
            --region "$REGION" 2>&1)
    else
        # payloadを含めずに取得
        events_output=$(aws bedrock-agentcore list-events \
            --memory-id "$MEMORY_ID" \
            --session-id "$SESSION_ID" \
            --actor-id "$ACTOR_ID" \
            --region "$REGION" \
            --no-include-payloads 2>&1)
    fi
    
    if [ $? -eq 0 ]; then
        
        # JSONの妥当性を確認
        if echo "$events_output" | jq . > /dev/null 2>&1; then
            echo "$events_output"
        else
            log_error "取得したデータがJSONではありません" >&2
            echo "Raw output: $events_output" >&2
            return 1
        fi
    else
        log_error "Memory内容取得に失敗しました" >&2
        echo "$events_output" >&2
        return 1
    fi
}

# メモリ内容の表示
show_memory_contents() {
    log_info "AgentCore Memory内容を取得中..."
    
    local events_json
    if ! events_json=$(get_events true); then
        return 1
    fi
    
    # 一時ファイルに保存
    local temp_file=$(mktemp)
    echo "$events_json" > "$temp_file"
    
    # 総イベント数を確認
    local total_events=$(jq '.events | length' "$temp_file" 2>/dev/null)
    if [ -z "$total_events" ] || [ "$total_events" = "null" ]; then
        log_error "イベント数の取得に失敗しました"
        rm "$temp_file"
        return 1
    fi
    
    echo ""
    echo "📊 AgentCore Memory 内容"
    echo "========================="
    echo "📋 基本情報:"
    echo "   Memory ID: $MEMORY_ID"
    echo "   Session ID: $SESSION_ID"
    echo "   Actor ID: $ACTOR_ID"
    echo "   総イベント数: $total_events"
    echo ""
    
    if [ "$total_events" -eq 0 ]; then
        log_info "記録されたイベントがありません"
        rm "$temp_file"
        return 0
    fi
    
    # 学習分野別統計
    echo "📈 学習分野別統計:"
    echo "┌─────────────────────────────────────────────────────────┬───────┐"
    echo "│ 学習分野                                                │ 回数  │"
    echo "├─────────────────────────────────────────────────────────┼───────┤"
    
    # payloadから学習分野を抽出して統計
    local domains=$(jq -r '.events[] | .payload[]?.conversational?.content?.text // empty' "$temp_file" | sort | uniq -c | sort -nr)
    
    if [ -n "$domains" ]; then
        echo "$domains" | while read count domain; do
            printf "│ %-55s │ %5s │\\n" "$domain" "$count"
        done
    else
        printf "│ %-55s │ %5s │\\n" "データなし" "0"
    fi
    
    echo "└─────────────────────────────────────────────────────────┴───────┘"
    echo ""
    
    # 時系列表示（最新10件）
    echo "⏰ 最新イベント（最新10件）:"
    echo "┌──────────────────────┬─────────────────────────────────────────────┐"
    echo "│ 日時                 │ 学習分野                                    │"
    echo "├──────────────────────┼─────────────────────────────────────────────┤"
    
    jq -r '.events[] | "\(.eventTimestamp) \(.payload[]?.conversational?.content?.text // "不明")"' "$temp_file" | \
    sort -r | head -10 | \
    while IFS=' ' read -r timestamp domain; do
        # タイムスタンプを読みやすい形式に変換
        local readable_time=$(date -d "$timestamp" '+%Y-%m-%d %H:%M' 2>/dev/null || echo "$timestamp")
        printf "│ %-20s │ %-43s │\\n" "$readable_time" "$domain"
    done
    
    echo "└──────────────────────┴─────────────────────────────────────────────┘"
    echo ""
    
    rm "$temp_file"
}

# 全イベント削除
delete_all_events() {
    log_warning "⚠️  AgentCore Memory内容を全削除します"
    echo "この操作により、学習分野の履歴がすべて削除されます。"
    echo "削除後は、ジャンル分散機能が初期状態に戻ります。"
    echo ""
    read -p "本当に削除しますか？ (yes/no): " confirm
    
    if [ "$confirm" != "yes" ]; then
        log_info "削除をキャンセルしました"
        return 0
    fi
    
    log_info "Memory内容削除中..."
    
    # まず現在のイベントを取得
    local events_json
    if events_json=$(get_events false); then
        local event_ids=$(echo "$events_json" | jq -r '.events[].eventId')
        
        if [ -z "$event_ids" ]; then
            log_info "削除するイベントがありません"
            return 0
        fi
        
        # 各イベントを削除
        local deleted_count=0
        while IFS= read -r event_id; do
            if [ -n "$event_id" ]; then
                log_info "イベント削除中: $event_id"
                if aws bedrock-agentcore delete-event \
                    --memory-id "$MEMORY_ID" \
                    --session-id "$SESSION_ID" \
                    --actor-id "$ACTOR_ID" \
                    --event-id "$event_id" \
                    --region "$REGION" > /dev/null 2>&1; then
                    ((deleted_count++))
                else
                    log_warning "イベント削除失敗: $event_id"
                fi
            fi
        done <<< "$event_ids"
        
        log_success "Memory内容削除完了: $deleted_count 件のイベントを削除しました"
        
    else
        log_error "Memory内容取得に失敗しました"
        return 1
    fi
}

# 最新イベント以外を削除
cleanup_old_events() {
    log_info "最新イベント以外の削除を開始します..."
    
    # イベント一覧を取得
    log_info "AgentCore Memory内容を取得中..."
    local events_json
    if ! events_json=$(get_events false); then
        return 1
    fi
    
    # 一時ファイルに保存
    local temp_file=$(mktemp)
    echo "$events_json" > "$temp_file"
    
    # 総イベント数を確認
    local total_events=$(jq '.events | length' "$temp_file" 2>/dev/null)
    if [ -z "$total_events" ] || [ "$total_events" = "null" ]; then
        log_error "イベント数の取得に失敗しました"
        rm "$temp_file"
        return 1
    fi
    
    log_info "総イベント数: $total_events"
    
    if [ "$total_events" -eq 0 ]; then
        log_info "削除するイベントがありません"
        rm "$temp_file"
        return 0
    fi
    
    if [ "$total_events" -eq 1 ]; then
        log_info "イベントが1件のみです。削除対象はありません。"
        rm "$temp_file"
        return 0
    fi
    
    # 最新のイベントを特定（タイムスタンプでソート）
    local latest_event_id=$(jq -r '.events | sort_by(.eventTimestamp) | reverse | .[0].eventId' "$temp_file")
    log_info "最新イベント（保持対象）: $latest_event_id"
    
    # 削除対象のイベントIDを取得（最新以外）
    local old_event_ids=$(jq -r --arg latest "$latest_event_id" '.events[] | select(.eventId != $latest) | .eventId' "$temp_file")
    
    if [ -z "$old_event_ids" ]; then
        log_info "削除対象のイベントがありません"
        rm "$temp_file"
        return 0
    fi
    
    local delete_count=$(echo "$old_event_ids" | wc -l)
    log_warning "⚠️  最新イベント以外の $delete_count 件を削除します"
    echo "最新イベント（保持）: $latest_event_id"
    echo "削除対象イベント:"
    echo "$old_event_ids" | while read event_id; do
        echo "  - $event_id"
    done
    echo ""
    
    read -p "削除を実行しますか？ (yes/no): " confirm
    
    if [ "$confirm" != "yes" ]; then
        log_info "削除をキャンセルしました"
        rm "$temp_file"
        return 0
    fi
    
    # 各イベントを削除
    echo "$old_event_ids" | while IFS= read -r event_id; do
        if [ -n "$event_id" ]; then
            log_info "イベント削除中: $event_id"
            if aws bedrock-agentcore delete-event \
                --memory-id "$MEMORY_ID" \
                --session-id "$SESSION_ID" \
                --actor-id "$ACTOR_ID" \
                --event-id "$event_id" \
                --region "$REGION" > /dev/null 2>&1; then
                echo "✅ 削除成功: $event_id"
            else
                echo "❌ 削除失敗: $event_id"
            fi
        fi
    done
    
    log_success "クリーンアップ完了"
    
    # 結果確認
    log_info "クリーンアップ後の状態を確認中..."
    local final_events_json
    if final_events_json=$(get_events false); then
        local final_count=$(echo "$final_events_json" | jq '.events | length')
        log_success "残存イベント数: $final_count"
        
        if [ "$final_count" -eq 1 ]; then
            local remaining_event_id=$(echo "$final_events_json" | jq -r '.events[0].eventId')
            log_success "残存イベント: $remaining_event_id"
        fi
    fi
    
    rm "$temp_file"
}

# 詳細分析
analyze_memory() {
    log_info "AgentCore Memory使用状況を分析中..."
    
    # イベント取得
    local events_json
    if ! events_json=$(get_events true); then
        return 1
    fi
    
    # 一時ファイルに保存
    local temp_file=$(mktemp)
    echo "$events_json" > "$temp_file"
    
    # 基本統計
    local total_events=$(jq '.events | length' "$temp_file")
    
    echo ""
    echo "📊 AgentCore Memory 詳細分析"
    echo "============================="
    echo "📋 基本情報:"
    echo "   Memory ID: $MEMORY_ID"
    echo "   Session ID: $SESSION_ID"
    echo "   総イベント数: $total_events"
    echo ""
    
    if [ "$total_events" -eq 0 ]; then
        log_warning "記録されたイベントがありません"
        rm "$temp_file"
        return 0
    fi
    
    # 学習分野の多様性分析
    local unique_domains=$(jq -r '.events[] | .payload[]?.conversational?.content?.text // empty' "$temp_file" | sort | uniq | wc -l)
    local diversity_ratio=$(echo "scale=2; $unique_domains / $total_events" | bc -l 2>/dev/null || echo "N/A")
    
    echo "🎯 ジャンル分散効果分析:"
    echo "   📋 総学習分野数: $unique_domains"
    echo "   📊 多様性比率: $diversity_ratio (1.0が最高)"
    
    # 最近の使用パターンを分析
    local recent_domains=$(jq -r '.events[] | .payload[]?.conversational?.content?.text // empty' "$temp_file" | tail -5)
    local unique_recent=$(echo "$recent_domains" | sort | uniq | wc -l)
    local total_recent=$(echo "$recent_domains" | wc -l)
    
    if [ "$total_recent" -gt 0 ]; then
        echo "   📋 最近5回の学習分野多様性: $unique_recent/$total_recent 分野"
    fi
    
    # 偏りの計算
    local domain_stats=$(jq -r '.events[] | .payload[]?.conversational?.content?.text // empty' "$temp_file" | sort | uniq -c | sort -nr)
    if [ -n "$domain_stats" ]; then
        local max_usage=$(echo "$domain_stats" | head -1 | awk '{print $1}')
        local min_usage=$(echo "$domain_stats" | tail -1 | awk '{print $1}')
        local bias_ratio=$(echo "scale=2; $max_usage / $min_usage" | bc -l 2>/dev/null || echo "N/A")
        
        echo "   📊 使用頻度の偏り比率: $bias_ratio (最大/最小)"
        
        if (( $(echo "$bias_ratio <= 2.0" | bc -l 2>/dev/null || echo 0) )); then
            echo "   ✅ 分散効果: 良好（偏りが少ない）"
        elif (( $(echo "$bias_ratio <= 3.0" | bc -l 2>/dev/null || echo 0) )); then
            echo "   ⚠️  分散効果: 普通（やや偏りあり）"
        else
            echo "   ❌ 分散効果: 要改善（偏りが大きい）"
        fi
    fi
    
    echo ""
    
    # 推奨アクション
    echo "💡 推奨アクション:"
    
    if [ "$unique_domains" -lt 4 ]; then
        echo "   📚 より多様な学習分野での問題生成を推奨します"
    fi
    
    if (( $(echo "$bias_ratio > 3.0" | bc -l 2>/dev/null || echo 0) )); then
        echo "   ⚖️  特定分野の使用頻度が高すぎます。分散機能の調整を検討してください"
    fi
    
    if [ "$total_events" -lt 10 ]; then
        echo "   📈 より多くの学習データ蓄積により、分散効果が向上します"
    fi
    
    # 一時ファイル削除
    rm "$temp_file"
    
    log_success "分析完了"
}

# 使用方法表示
show_usage() {
    echo "🧹 AgentCore Memory 管理スクリプト"
    echo "=================================="
    echo ""
    echo "AgentCore Memoryの内容確認・削除・分析を行います。"
    echo ""
    echo "使用方法:"
    echo "  export AWS_PROFILE=sandbox"
    echo "  $0 <command>"
    echo ""
    echo "コマンド:"
    echo "  show        Memory内容を表示"
    echo "  analyze     Memory使用状況を詳細分析"
    echo "  cleanup     最新イベント以外を削除"
    echo "  clear       全イベントを削除"
    echo "  help        このヘルプを表示"
    echo ""
    echo "例:"
    echo "  $0 show     # Memory内容確認"
    echo "  $0 analyze  # 詳細分析"
    echo "  $0 cleanup  # 最新以外削除"
    echo "  $0 clear    # 全削除"
    echo ""
}

# メイン処理
main() {
    local command="${1:-help}"
    
    case "$command" in
        "show")
            echo "🔍 AgentCore Memory 内容表示"
            echo "============================"
            check_aws_auth
            show_memory_contents
            ;;
        "analyze")
            echo "📊 AgentCore Memory 詳細分析"
            echo "============================"
            check_aws_auth
            analyze_memory
            ;;
        "cleanup")
            echo "🧹 AgentCore Memory クリーンアップ（最新以外削除）"
            echo "=============================================="
            echo ""
            echo "📋 設定情報:"
            echo "   Memory ID: $MEMORY_ID"
            echo "   Session ID: $SESSION_ID"
            echo "   Actor ID: $ACTOR_ID"
            echo "   Region: $REGION"
            echo ""
            check_aws_auth
            cleanup_old_events
            ;;
        "clear")
            echo "🗑️  AgentCore Memory 全削除"
            echo "=========================="
            echo ""
            echo "📋 設定情報:"
            echo "   Memory ID: $MEMORY_ID"
            echo "   Session ID: $SESSION_ID"
            echo "   Actor ID: $ACTOR_ID"
            echo "   Region: $REGION"
            echo ""
            check_aws_auth
            delete_all_events
            ;;
        "help"|"-h"|"--help")
            show_usage
            ;;
        *)
            log_error "不正なコマンド: $command"
            echo ""
            show_usage
            exit 1
            ;;
    esac
}

# スクリプト実行
main "$@"