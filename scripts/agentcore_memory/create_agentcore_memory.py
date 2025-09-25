#!/usr/bin/env python3
"""
AgentCore Memory リソース作成スクリプト

AWS Bedrock AgentCore Memory を作成します（短期記憶のみ使用）。
作成された Memory ID を .env ファイルに自動登録します。
"""

import time
from pathlib import Path

from bedrock_agentcore.memory import MemoryClient
from dotenv import load_dotenv

# .env ファイルの読み込み（AWS_PROFILE=sandbox設定を反映）
load_dotenv()


def create_memory_resource() -> str:
    """AgentCore Memory リソースを作成"""

    # Memory Client の初期化
    client = MemoryClient(region_name="us-east-1")

    # 長期記憶（strategies）は使用しない - 短期記憶のみでシンプルに運用
    # 将来必要になった場合に追加可能

    print("🚀 AgentCore Memory 作成中...")
    print("📝 設定内容:")
    print("   - Event Expiry Duration: 30日間（AWS側で自動削除）")
    print("   - Memory Type: 短期記憶のみ（長期記憶は未使用）")
    print("   - 用途: 問題生成の学習分野偏り解消")
    print("   - 実装: sessionId = exam_type (例: AWS-SAP)")
    print("   - 利点: シンプルな構成、クライアント側フィルタリング不要")

    # タイムスタンプ付きの名前を生成
    timestamp = int(time.time())
    memory_name = f"CloudCoPassAgentMemory_{timestamp}"

    # Memory リソース作成（30日間自動削除設定、短期記憶のみ）
    memory = client.create_memory(
        name=memory_name,
        description="Cloud CoPassAgent用メモリ（30日間自動削除、短期記憶のみ）",
        event_expiry_days=30,  # 30日間で自動削除
        # strategies は指定しない（短期記憶のみ使用）
    )

    memory_id: str = memory["id"]
    print("\n✅ Memory 作成完了！")
    print(f"   Memory ID: {memory_id}")
    print(f"   Status: {memory['status']}")

    return memory_id


def update_env_file(memory_id: str) -> None:
    """作成された Memory ID を .env ファイルに登録"""
    env_file_path = Path(".env")

    if not env_file_path.exists():
        print("❌ .env ファイルが見つかりません")
        return

    # .env ファイルを読み込み
    with open(env_file_path, encoding="utf-8") as f:
        lines = f.readlines()

    # AGENTCORE_MEMORY_ID の行を探して更新
    updated = False
    for i, line in enumerate(lines):
        if line.startswith("AGENTCORE_MEMORY_ID="):
            lines[i] = f"AGENTCORE_MEMORY_ID={memory_id}\n"
            updated = True
            break

    # 存在しない場合は追加
    if not updated:
        lines.append(f"AGENTCORE_MEMORY_ID={memory_id}\n")

    # .env ファイルに書き戻し
    with open(env_file_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"✅ .env ファイルに Memory ID を登録しました: {memory_id}")


if __name__ == "__main__":
    memory_id = create_memory_resource()
    print(f"\n🎉 作成された Memory ID: {memory_id}")

    # .env ファイルに Memory ID を登録
    update_env_file(memory_id)

    print("\n� 次次のステップ:")
    print(f"1. .env ファイルの AGENTCORE_MEMORY_ID が '{memory_id}' に設定されました")
    print("2. uv run python app/agentcore/agent_main.py --test で動作確認")
    print("3. 必要に応じて長期記憶機能を将来追加可能")
