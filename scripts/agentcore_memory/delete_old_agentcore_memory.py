#!/usr/bin/env python3
"""
古いAgentCore Memory リソース削除スクリプト

不要になった古いMemoryリソースを削除します。
"""

from bedrock_agentcore.memory import MemoryClient
from dotenv import load_dotenv

# .env ファイルの読み込み（AWS_PROFILE=sandbox設定を反映）
load_dotenv()


def delete_old_memory_resource(old_memory_id: str) -> None:
    """古いAgentCore Memory リソースを削除"""

    # Memory Client の初期化
    client = MemoryClient(region_name="us-east-1")

    print("🗑️  古いAgentCore Memory削除中...")
    print("📝 削除対象:")
    print(f"   Memory ID: {old_memory_id}")
    print("   理由: 新しいMemoryリソース（短期記憶のみ）に移行済み")

    try:
        # Memory リソース削除
        client.delete_memory(memory_id=old_memory_id)

        print("\n✅ Memory 削除完了！")
        print(f"   削除されたMemory ID: {old_memory_id}")

    except Exception as e:
        print(f"\n❌ Memory削除に失敗しました: {e}")
        print("   - Memory IDが存在しない可能性があります")
        print("   - 既に削除済みの可能性があります")
        print("   - AWS認証を確認してください")


if __name__ == "__main__":
    # 古いMemory ID（長期記憶設定付き）
    old_memory_id = "CloudCoPassAgentMemory_1758470667-YvBRIT3DdL"

    print("⚠️  古いAgentCore Memory削除確認")
    print("=" * 50)
    print(f"削除対象Memory ID: {old_memory_id}")
    print("削除理由: 長期記憶機能を削除し、短期記憶のみの新しいMemoryに移行")
    print("")

    confirm = input("本当に削除しますか？ (yes/no): ")

    if confirm.lower() == "yes":
        delete_old_memory_resource(old_memory_id)
    else:
        print("削除をキャンセルしました")
