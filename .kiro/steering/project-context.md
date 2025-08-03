---
inclusion: always
---

# AWS Exam Agent プロジェクトコンテキスト

## AI エージェント向けメタ情報

このファイルは、AI エージェントがプロジェクトの作業継続性を維持するための最小限の情報を提供します。
プロダクトの技術設計は `.kiro/specs/aws-exam-coach/design/` を参照してください。

## プロジェクト識別情報

- **プロジェクト名**: AWS Exam Agent
- **GitHub**: https://github.com/kobank-t/aws-exam-agent
- **目的**: AI エージェント技術学習 + 組織コミュニケーション活性化

## 現在の作業状況

- **開発段階**: Spec 作成ワークフロー - 設計フェーズ完了
- **完了済み**: 要件定義、設計書（9 ファイル分割）、コーディング規約
- **次回予定**: 設計書レビュー → タスクリスト作成

## 開発環境・ツール

- **Python**: 3.12 + uv（仮想環境・依存関係管理）
- **MCP Server**: 7 つ動作確認済み（Git, AWS 系 5 つ, Context7, Playwright）
- **GitHub**: Personal Access Token 設定済み（期限: 2025 年 10 月）

## 作業継続性ルール

- **日本語回答**: 全ての回答・ドキュメントは日本語
- **作業記録更新**: 重要作業完了時は WORK_LOG.md 更新必須
- **フェーズ進行許可制**: 次フェーズ前にユーザー承認必須
- **公式情報源のみ**: AWS 公式ドキュメント + 試験ガイド

## セッション開始時のアクション

1. **WORK_LOG.md 確認** → 前回作業内容・次回予定把握
2. **継続性維持** → 作業記録に基づく適切なタスク継続

## 情報参照先

- **プロダクト設計**: `.kiro/specs/aws-exam-agent/design/`
- **作業履歴**: `WORK_LOG.md`
- **コーディング規約**: `.kiro/steering/*-coding-standards.md`

#[[file:WORK_LOG.md]]
