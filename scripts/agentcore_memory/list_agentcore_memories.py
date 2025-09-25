#!/usr/bin/env python3
"""
AgentCore Memory リソース一覧表示スクリプト

現在のMemoryリソースを一覧表示します。
"""

from bedrock_agentcore.memory import MemoryClient
from dotenv import load_dotenv

# .env ファイルの読み込み（AWS_PROFILE=sandbox設定を反映）
load_dotenv()


def list_memory_resources() -> None:
    """AgentCore Memory リソース一覧を表示"""

    # Memory Client の初期化
    client = MemoryClient(region_name="us-east-1")

    print("📋 AgentCore Memory リソース一覧")
    print("=" * 50)

    try:
        # Memory リソース一覧取得
        memories = client.list_memories()

        if not memories:
            print("❌ Memoryリソースが見つかりません")
            return

        print(f"📊 総数: {len(memories)}件")
        print("")

        for i, memory in enumerate(memories, 1):
            memory_id = memory.get("id", "不明")
            name = memory.get("name", "不明")
            status = memory.get("status", "不明")
            created_at = memory.get("createdAt", "不明")
            description = memory.get("description", "説明なし")

            print(f"🔹 Memory {i}:")
            print(f"   ID: {memory_id}")
            print(f"   名前: {name}")
            print(f"   ステータス: {status}")
            print(f"   作成日時: {created_at}")
            print(f"   説明: {description}")

            # 現在使用中のMemoryかチェック
            from pathlib import Path
            env_file = Path(".env")
            if env_file.exists():
                with open(env_file) as f:
                    env_content = f.read()
                    if memory_id in env_content:
                        print("   🎯 現在使用中")

            print("")

    except Exception as e:
        print(f"❌ Memory一覧取得に失敗しました: {e}")
        print("   - AWS認証を確認してください")
        print("   - リージョン設定を確認してください")


if __name__ == "__main__":
    list_memory_resources()
