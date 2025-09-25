#!/usr/bin/env python3
"""
AgentCore Memory 統合管理スクリプト

Memory関連の操作を統合的に管理します。
"""

import subprocess
import sys
from pathlib import Path


def show_usage() -> None:
    """使用方法を表示"""
    print("🧠 AgentCore Memory 統合管理")
    print("=" * 40)
    print("")
    print("使用方法:")
    print("  python scripts/agentcore_memory/manage.py <command>")
    print("")
    print("コマンド:")
    print("  create      新しいMemoryリソースを作成")
    print("  list        Memoryリソース一覧を表示")
    print("  delete-old  古いMemoryリソースを削除")
    print("  show        Memory内容を表示（bash版）")
    print("  analyze     Memory使用状況を詳細分析（bash版）")
    print("  cleanup     最新イベント以外を削除（bash版）")
    print("  clear       全イベントを削除（bash版）")
    print("  help        このヘルプを表示")
    print("")
    print("例:")
    print("  python scripts/agentcore_memory/manage.py create")
    print("  python scripts/agentcore_memory/manage.py list")
    print("  ./scripts/manage-agentcore-memory.sh show")
    print("")

def run_script(script_name: str, args: list[str] | None = None) -> int:
    """指定されたスクリプトを実行"""
    script_path = Path(__file__).parent / script_name
    if not script_path.exists():
        print(f"❌ スクリプトが見つかりません: {script_path}")
        return 1

    cmd = ["python", str(script_path)]
    if args:
        cmd.extend(args)

    try:
        result = subprocess.run(cmd, check=True)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"❌ スクリプト実行に失敗しました: {e}")
        return e.returncode

def run_bash_script(command: str) -> int:
    """bash版管理スクリプトを実行"""
    bash_script = Path(__file__).parent.parent / "manage-agentcore-memory.sh"
    if not bash_script.exists():
        print(f"❌ bash管理スクリプトが見つかりません: {bash_script}")
        return 1

    try:
        result = subprocess.run([str(bash_script), command], check=True)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"❌ bash スクリプト実行に失敗しました: {e}")
        return e.returncode

def main() -> int:
    if len(sys.argv) < 2:
        show_usage()
        return 1

    command = sys.argv[1].lower()

    if command == "help" or command == "-h" or command == "--help":
        show_usage()
        return 0
    elif command == "create":
        return run_script("create_agentcore_memory.py")
    elif command == "list":
        return run_script("list_agentcore_memories.py")
    elif command == "delete-old":
        return run_script("delete_old_agentcore_memory.py")
    elif command in ["show", "analyze", "cleanup", "clear"]:
        print(f"🔄 bash版管理スクリプトを実行中: {command}")
        return run_bash_script(command)
    else:
        print(f"❌ 不明なコマンド: {command}")
        show_usage()
        return 1

if __name__ == "__main__":
    sys.exit(main())
