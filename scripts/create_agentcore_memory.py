#!/usr/bin/env python3
"""
AgentCore Memory リソース作成スクリプト

AWS Bedrock AgentCore Memory を作成し、ジャンル分散機能用の設定を行います。
作成された Memory ID を .env ファイルに自動登録します。
"""

import time
from pathlib import Path

from bedrock_agentcore.memory import MemoryClient
from bedrock_agentcore.memory.constants import StrategyType
from dotenv import load_dotenv

# .env ファイルの読み込み（AWS_PROFILE=sandbox設定を反映）
load_dotenv()


def create_memory_resource() -> str:
    """AgentCore Memory リソースを作成"""

    # Memory Client の初期化
    client = MemoryClient(region_name="us-east-1")

    # Memory Strategies の定義（ジャンル分散機能用）
    strategies = [
        {
            # 学習分野の記録用（ジャンル分散機能で使用）
            StrategyType.SEMANTIC.value: {
                "name": "LearningDomainTracker",
                "description": "クラウド認定試験の学習分野を記録・追跡してジャンル分散を実現",
                "namespaces": [
                    "learning-domains/{sessionId}",  # Short-Term Memory利用のためシンプル構成
                ],
            }
        }
    ]

    print("🚀 AgentCore Memory 作成中...")
    print("📝 設定内容:")
    print("   - Semantic Strategy: クラウド認定試験の学習分野記録・追跡")
    print("   - Namespace Template: learning-domains/{sessionId}")
    print("   - 用途: Short-Term Memory による問題生成偏り解消")
    print("   - 実装: sessionId = exam_type (例: AWS-SAP)")
    print("   - 実際の namespace: learning-domains/AWS-SAP")

    # タイムスタンプ付きの名前を生成
    timestamp = int(time.time())
    memory_name = f"CloudCoPassAgentMemory_{timestamp}"

    # Memory リソース作成
    memory = client.create_memory(
        name=memory_name,
        strategies=strategies,
        description="Cloud CoPassAgent用メモリ（クラウド認定試験のジャンル分散機能対応）",
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

    print("\n📝 次のステップ:")
    print("1. agent_main.py の MEMORY_CONFIG を環境変数から読み込むように修正")
    print("2. Memory 機能を有効化（enabled: True）")

    print("\n📋 次のステップ:")
    print(f"1. agent_main.py の MEMORY_CONFIG['memory_id'] を '{memory_id}' に更新")
    print("2. uv run python app/agentcore/agent_main.py --test で動作確認")
