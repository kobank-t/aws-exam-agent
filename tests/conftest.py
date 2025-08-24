#!/usr/bin/env python3
"""
pytest 設定ファイル

AgentCore Runtime (agent_main.py) 用の最小限のテスト設定。
シンプル化されたアーキテクチャに対応。
"""

import asyncio
import os
import sys
from collections.abc import Generator
from pathlib import Path

import pytest

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# AgentCore Runtime環境での相対インポート対応
# テスト環境でagentcoreディレクトリをPythonパスに追加
agentcore_path = Path(__file__).parent.parent / "app" / "agentcore"
if agentcore_path.exists():
    sys.path.insert(0, str(agentcore_path))


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """セッション全体で使用するイベントループ"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# 現在のテストは自己完結しており、共通フィクスチャは不要
# test_agent_main.py は契約による設計に基づいて独立したテストを実装


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """テスト環境の自動セットアップ"""
    # 基本的なテスト用環境変数
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    # AWS設定
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    monkeypatch.setenv("BEDROCK_REGION", "us-east-1")
