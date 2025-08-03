# システム概要・設計原則

## Overview

AWS Exam Agent は、Power Automate と Microsoft Teams を活用した組織内コラボレーション学習プラットフォームです。AI エージェントが自動生成する AWS Certified Solutions Architect - Professional の試験問題を Teams チャネルに配信し、リアクションによる回答とスレッドでの議論を通じて、組織内のコミュニケーション活性化とスキルトランスファーを促進します。

## 設計原則

1. **シンプルさ優先**: 複雑な Teams App 開発を避け、Power Automate + HTTP リクエストで実装
2. **段階的リリース**: MVP から開始し、フィードバックに基づいて機能拡張
3. **既存環境活用**: Teams の標準機能（リアクション、スレッド）を最大限活用
4. **信頼性重視**: AWS 公式情報源のみを使用し、品質の高い問題を生成

## プロジェクト目的

### 真の目的

- **開発側**: AI エージェント技術のスキルアップ
- **利用側**: 200 名エンジニア組織のコミュニケーション活性化
- **共通**: ワイガヤを通じたスキルトランスファー促進

### 対象試験

- **AWS Certified Solutions Architect - Professional**
- **利用環境**: 社内、Teams チャネル、会社支給 PC・iPhone
- **情報源**: AWS 公式ドキュメント + 試験ガイド（MVP）
- **拡張予定**: FAQ、What's New、Well-Architected Framework

## 学習重視のアプローチ

このプロジェクトは**スキルアップを目的とした学習用途**であり、以下の学習効果を重視します：

### 技術学習ポイント

- **AWS SAM**: Infrastructure as Code
- **Bedrock AgentCore**: 最新の AI エージェント実行環境
- **Power Automate**: ローコード開発・Teams 統合
- **DynamoDB**: NoSQL データベース設計
- **API Gateway + Lambda**: サーバーレスアーキテクチャ
- **GitHub Actions**: CI/CD パイプライン

### 開発方針

- **単一環境**: 環境分離は不要（学習用途のため）
- **シンプル設計**: 複雑な機能より理解しやすい実装を優先
- **段階的実装**: MVP → 機能拡張の順次開発
- **公式ツール活用**: AWS 公式ツール・サービスの積極的利用
