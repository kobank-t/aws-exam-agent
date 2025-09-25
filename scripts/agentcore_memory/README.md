# AgentCore Memory 管理スクリプト

AgentCore Memory リソースの作成・削除・管理を行うスクリプト群です。

## 📁 ファイル構成

```
scripts/agentcore_memory/
├── README.md                        # このファイル
├── manage.py                        # 統合管理スクリプト
├── create_agentcore_memory.py       # Memory リソース作成
├── list_agentcore_memories.py       # Memory リソース一覧表示
└── delete_old_agentcore_memory.py   # 古い Memory リソース削除
```

## 🚀 使用方法

### 統合管理スクリプト（推奨）

```bash
# Memory リソース作成
python scripts/agentcore_memory/manage.py create

# Memory リソース一覧表示
python scripts/agentcore_memory/manage.py list

# 古い Memory リソース削除
python scripts/agentcore_memory/manage.py delete-old

# Memory 内容表示（bash版）
python scripts/agentcore_memory/manage.py show

# 使用方法表示
python scripts/agentcore_memory/manage.py help
```

### 個別スクリプト実行

```bash
# Memory リソース作成
uv run python scripts/agentcore_memory/create_agentcore_memory.py

# Memory リソース一覧表示
uv run python scripts/agentcore_memory/list_agentcore_memories.py

# 古い Memory リソース削除
uv run python scripts/agentcore_memory/delete_old_agentcore_memory.py
```

### bash 版管理スクリプト

```bash
# AWS_PROFILE 設定が必要
export AWS_PROFILE=sandbox

# Memory 内容表示
./scripts/manage-agentcore-memory.sh show

# 詳細分析
./scripts/manage-agentcore-memory.sh analyze

# クリーンアップ
./scripts/manage-agentcore-memory.sh cleanup
```

## 📋 各スクリプトの説明

### create_agentcore_memory.py

- 新しい AgentCore Memory リソースを作成
- 30 日間自動削除設定（短期記憶のみ）
- 作成された Memory ID を .env ファイルに自動登録

### list_agentcore_memories.py

- 現在の Memory リソース一覧を表示
- 各リソースの詳細情報（ID、名前、ステータス、作成日時）
- 現在使用中のリソースを識別

### delete_old_agentcore_memory.py

- 不要になった古い Memory リソースを削除
- 削除前に確認プロンプト表示
- 安全な削除処理

### manage.py

- 上記スクリプトを統合的に管理
- 簡単なコマンドラインインターフェース
- bash 版スクリプトとの連携

## ⚠️ 注意事項

- AWS_PROFILE=sandbox の設定が必要
- Memory リソースの削除は慎重に行ってください
- .env ファイルの AGENTCORE_MEMORY_ID が正しく設定されていることを確認してください

## 🔗 関連ファイル

- `scripts/manage-agentcore-memory.sh`: bash 版 Memory 管理スクリプト
- `.env`: Memory ID 設定ファイル
- `app/agentcore/domain_memory_client.py`: Memory クライアント実装
