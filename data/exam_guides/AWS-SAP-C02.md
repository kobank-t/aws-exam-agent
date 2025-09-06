# AWS Certified Solutions Architect - Professional (SAP-C02) 試験ガイド

**出典**: https://d1.awsstatic.com/ja_JP/training-and-certification/docs-sa-pro/AWS-Certified-Solutions-Architect-Professional_Exam-Guide.pdf

## はじめに

AWS Certified Solutions Architect - Professional (SAP-C02) 試験は、ソリューションアーキテクトの役割を担う個人を対象としています。この試験では、AWS Well-Architected フレームワークに基づいて AWS ソリューションを設計し、最適化することを課題とし、受験者の高度な技術スキルと経験を検証します。

この試験では、受験者が AWS Well-Architected フレームワークの範囲内で次のタスクを完了する能力も検証されます。

- 複雑な組織に対応する設計
- 新しいソリューションのための設計
- 既存ソリューションの継続的な改善
- ワークロードの移行とモダナイゼーションの加速

## 受験対象者について

AWS のサービスを使用してクラウドソリューションを設計し、実装した経験が 2 年以上ある人が受験対象者となります。クラウドアプリケーションの要件を評価し、アプリケーションのデプロイについてアーキテクチャに関するレコメンデーションを行う能力が求められます。また、複雑な組織内で複数のアプリケーションやプロジェクトにまたがるアーキテクチャを設計する際に、エキスパートとしてガイダンスを提供できる能力も必要です。

### 受験対象者として範囲外の職務と知識

受験対象者に対して想定されていない職務と知識は、以下のリストのとおりです。このリストはすべてを網羅しているわけではありません。以下の職務と知識は、本試験の範囲外です。

- モバイルアプリケーションのフロントエンド開発
- Twelve-Factor App 方法論
- オペレーティングシステムに関する詳細な知識

試験に出題される可能性のあるテクノロジーと概念のリスト、試験対象の AWS
サービスと機能のリスト、試験対象外の AWS サービスと機能のリストについては、
付録を参照してください。

## 試験内容

### 解答タイプ

試験には、次の出題形式が 1 つ以上含まれています。

- **択一選択問題**: 正しい選択肢が 1 つ、誤った選択肢 (不正解) が 3 つ提示される。
- **複数選択問題**: 5 つ以上の選択肢のうち、正解が 2 つ以上ある。設問に対する点数を得るには、正解をすべて選択する必要がある。

未解答の設問は不正解とみなされます。推測による解答にペナルティはありません。試験には、スコアに影響する設問が 65 問含まれています。

### 採点対象外の設問

試験には、スコアに影響しない採点対象外の設問が 10 問含まれています。AWS では、こういった採点対象外の設問でのパフォーマンス情報を収集し、今後、採点対象の設問として使用できるかどうかを評価します。試験では、どの設問が採点対象外かは受験者にわからないようになっています。

### 試験の結果

AWS Certified Solutions Architect - Professional (SAP-C02) 試験は、合否判定方式です。試験の採点は、認定業界のベストプラクティスおよびガイドラインに基づいた、AWS の専門家によって定められる最低基準に照らして行われます。

試験の結果は、100 ～ 1,000 の換算スコアとして報告されます。合格スコアは 750 です。このスコアにより、試験全体の成績と合否がわかります。複数の試験間で難易度がわずかに異なる可能性があるため、スコアを均等化するために換算スコアが使用されます。

スコアレポートには、各セクションのパフォーマンスを示す分類表が含まれる場合があります。試験には補整スコアリングモデルが使用されるため、セクションごとに合否ラインは設定されておらず、試験全体のスコアで合否が判定されます。

試験の各セクションには特定の重みが設定されているため、各セクションに割り当てられる設問数が異なる場合があります。分類表には、受験者の得意分野と不得意分野を示す全般的な情報が含まれます。セクションごとのフィードバックを解釈する際は注意してください。

## 試験内容の概要

この試験ガイドには、試験に設定された重み、コンテンツ分野、タスクについての説明が含まれています。本ガイドは、試験内容の包括的なリストを提供するものではありません。ただし、各タスクの追加情報が含まれており、試験の準備に役立てることができます。

### 本試験のコンテンツ分野と重み設定

- **コンテンツ分野 1**: 複雑な組織に対応するソリューションの設計 (採点対象コンテンツの 26%)
- **コンテンツ分野 2**: 新しいソリューションのための設計 (採点対象コンテンツの 29%)
- **コンテンツ分野 3**: 既存のソリューションの継続的な改善 (採点対象コンテンツの 25%)
- **コンテンツ分野 4**: ワークロードの移行とモダナイゼーションの加速 (採点対象コンテンツの 20%)

---

## コンテンツ分野 1: 複雑な組織に対応するソリューションの設計

### タスク 1.1: ネットワーク接続戦略を設計する

**対象知識:**

- AWS グローバルインフラストラクチャ
- AWS ネットワークの概念 [Amazon Virtual Private Cloud (Amazon VPC)、AWS Direct Connect、AWS VPN、推移的ルーティング、AWS コンテナサービスなど]
- ハイブリッド DNS の概念 (Amazon Route 53 Resolver、オンプレミス DNS 統合など)
- ネットワークセグメンテーション (サブネット、IP アドレス指定、VPC 間の接続など)
- ネットワークトラフィックモニタリング

**対象スキル:**

- 複数の VPC の接続オプションを評価する。
- オンプレミス、コロケーション、クラウド統合の接続オプションを評価する。
- ネットワークとレイテンシーの要件に基づいて AWS リージョンとアベイラビリティーゾーンを選択する。
- AWS ツールを使用してトラフィックフローの問題を解決する。
- サービス統合のためのサービスエンドポイントを使用する。

### タスク 1.2: セキュリティコントロールを規定する

**対象知識:**

- AWS Identity and Access Management (IAM) と AWS IAM アイデンティティセンター
- ルートテーブル、セキュリティグループ、ネットワーク ACL
- 暗号化キーと証明書管理 [AWS Key Management Service (AWS KMS)、AWS Certificate Manager (ACM) など]
- AWS のセキュリティ、アイデンティティ、コンプライアンスのツール (AWS CloudTrail、AWS Identity and Access Management Access Analyzer、AWS Security Hub、Amazon Inspector など)

**対象スキル:**

- クロスアカウントアクセス管理を評価する。
- サードパーティー ID プロバイダーと統合する。
- 保存中のデータと転送中のデータに対する暗号化戦略をデプロイする。
- セキュリティイベントの通知と監査を一元化するための戦略を策定する。

### タスク 1.3: 信頼性と耐障害性に優れたアーキテクチャを設計する

**対象知識:**

- 目標復旧時間 (RTO) と目標復旧時点 (RPO)
- ディザスタリカバリ戦略 (AWS Elastic Disaster Recovery、パイロットライト、ウォームスタンバイ、マルチサイトの使用など)
- データのバックアップと復元

**対象スキル:**

- RTO および RPO 要件に基づいてディザスタリカバリソリューションを設計する。
- 障害から自動的に復旧するアーキテクチャを実装する。
- スケールアップとスケールアウトのオプションを考慮し、最適なアーキテクチャを策定する。
- 効果的なバックアップ/復元の戦略を設計する。

### タスク 1.4: マルチアカウント AWS 環境を設計する

**対象知識:**

- AWS Organizations と AWS Control Tower
- マルチアカウントイベント通知
- 環境間の AWS リソース共有

**対象スキル:**

- 組織の要件に最も適したアカウント構造を評価する。
- 一元的なログ記録とイベント通知の戦略を推奨する。
- マルチアカウントガバナンスモデルを開発する。

### タスク 1.5: コスト最適化と可視化の戦略を決定する

**対象知識:**

- AWS のコストおよび使用状況のモニタリングツール (AWS Trusted Advisor、AWS 料金見積りツール、AWS Cost Explorer、AWS Budgets など)
- AWS 購入オプション (リザーブドインスタンス、Savings Plans、スポットインスタンスなど)
- サイズ適正化のための AWS 可視化ツール [AWS Compute Optimizer、Amazon Simple Storage Service (Amazon S3) Storage Lens など]

**対象スキル:**

- AWS ツールでコストと使用量をモニタリングする。
- コストを事業単位にマッピングする効果的なタグ付け戦略を策定する。
- 購入オプションがコストとパフォーマンスに与える影響を理解する。

---

## コンテンツ分野 2: 新しいソリューションのための設計

### タスク 2.1: ビジネス要件を満たすデプロイ戦略を設計する

**対象知識:**

- Infrastructure as Code (IaC) (AWS CloudFormation など)
- 継続的インテグレーションおよび継続的デリバリー (CI/CD)
- 変更管理プロセス
- 構成管理ツール (AWS Systems Manager など)

**対象スキル:**

- 新しいサービスや機能のためのアプリケーションまたはアップグレードパスを決定する。
- デプロイ戦略を策定し、適切なロールバックメカニズムを実装するためのサービスを選定する。
- 必要に応じてマネージドサービスを採用し、インフラストラクチャのプロビジョニングやパッチ適用のオーバーヘッドを削減する。
- 複雑な開発タスクとデプロイタスクを AWS にまかせ、高度なテクノロジーを利用できるようにする。

### タスク 2.2: 事業の継続性を確保するソリューションを設計する

**対象知識:**

- AWS グローバルインフラストラクチャ
- AWS ネットワークの概念 (Route 53、ルーティングメソッドなど)
- RTO と RPO
- ディザスタリカバリシナリオ (バックアップと復元、パイロットライト、ウォームスタンバイ、マルチサイトなど)
- AWS のディザスタリカバリソリューション

**対象スキル:**

- ディザスタリカバリソリューションを構成する。
- データとデータベースのレプリケーションを構成する。
- ディザスタリカバリテストを実行する。
- 自動化され、費用対効果が高く、複数のアベイラビリティーゾーンまたは AWS リージョンをまたいで事業継続性をサポートするバックアップソリューションのアーキテクチャを設計する。
- 障害時もアプリケーションとインフラストラクチャの可用性を維持するアーキテクチャを設計する。
- プロセスとコンポーネントを使用して一元的なモニタリングを行い、システム障害からプロアクティブに復旧する。

### タスク 2.3: 要件に基づいてセキュリティコントロールを決定する

**対象知識:**

- IAM
- ルートテーブル、セキュリティグループ、ネットワーク ACL
- 保管中のデータと転送中のデータの暗号化オプション
- AWS サービスエンドポイント
- 認証情報管理サービス
- AWS マネージドセキュリティサービス (AWS Shield、AWS WAF、Amazon GuardDuty、AWS Security Hub など)

**対象スキル:**

- 最小権限アクセスの原則に従った IAM ユーザーと IAM ロールを指定する。
- セキュリティグループルールとネットワーク ACL ルールを使用したインバウンドおよびアウトバウンドのネットワークフローを指定する。
- 大規模なウェブアプリケーションの攻撃対策戦略を策定する。
- 保管中のデータと転送中のデータの暗号化戦略を策定する。
- サービス統合のサービスエンドポイントを指定する。
- 組織の規格への準拠を維持するためのパッチ管理戦略を策定する。

### タスク 2.4: 信頼性の要件を満たす戦略を策定する

**対象知識:**

- AWS グローバルインフラストラクチャ
- AWS ストレージサービスとレプリケーション戦略 [Amazon S3、Amazon Relational Database Service (Amazon RDS)、Amazon ElastiCache など]
- マルチ AZ およびマルチリージョンアーキテクチャ
- オートスケーリングのポリシーとイベント
- アプリケーション統合 [Amazon Simple Notification Service (Amazon SNS)、Amazon Simple Queue Service (Amazon SQS)、AWS Step Functions など]
- サービスクォータと上限

**対象スキル:**

- ビジネス要件に基づいて可用性の高いアプリケーション環境を設計する。
- 高度な技術を使用して障害に備えて設計し、シームレスなシステム回復性を確保する。
- 疎結合依存関係を実装する。
- 高可用性アーキテクチャを運用、保守する (アプリケーションのフェイルオーバー、データベースのフェイルオーバーなど)。
- AWS マネージドサービスを使用して高可用性を実現する。
- DNS ルーティングポリシーを実装する (Route 53 のレイテンシールーティングポリシー、位置情報ルーティング、シンプルルーティングなど)。

### タスク 2.5: パフォーマンス目標を満たすソリューションを設計する

**対象知識:**

- パフォーマンスモニタリングテクノロジー
- AWS のストレージオプション
- インスタンスファミリーとユースケース
- 目的別データベース

**対象スキル:**

- さまざまなアクセスパターンに対応した大規模アプリケーションアーキテクチャを設計する。
- ビジネス目標に合わせて伸縮自在なアーキテクチャを設計する。
- キャッシュ、バッファリング、レプリカでパフォーマンス目標を達成するための設計パターンを適用する。
- 必要なタスクに特化したサービスを選択するためのプロセス方法論を策定する。
- サイズ適正化戦略を設計する。

### タスク 2.6: ソリューションの目標と目的を達成するためのコスト最適化戦略を決定する

**対象知識:**

- AWS のコストおよび使用状況のモニタリングツール (Cost Explorer、Trusted Advisor、AWS 料金見積りツールなど)
- 料金モデル (リザーブドインスタンス、Savings Plans など)
- ストレージ階層化
- データ転送コスト
- AWS が提供するマネージドサービス

**対象スキル:**

- インフラストラクチャを選択し適切なサイズにする機会を特定して、リソースの費用対効果を上げる。
- 適切な価格モデルを特定する。
- データ転送のモデル化とサービスの選択を行い、データ転送コストを削減する。
- 経費支出と使用状況を認識するための戦略を策定し、制御を実装する。

---

## コンテンツ分野 3: 既存のソリューションの継続的な改善

### タスク 3.1: 全体的な運用上の優秀性を高めるための戦略を作成する

**対象知識:**

- アラートと自動修復の戦略
- ディザスタリカバリ計画
- モニタリングとログ記録のソリューション (Amazon CloudWatch など)
- CI/CD パイプラインとデプロイ戦略 (ブルー/グリーン、1 回にすべて、ローリングなど)
- 構成管理ツール (Systems Manager など)

**対象スキル:**

- 最も適したログ記録とモニタリング戦略を決定する。
- 改善の機会を特定する目的で現在のデプロイプロセスを評価する。
- ソリューションスタック内のオートメーションの機会に優先順位を付ける。
- 構成管理オートメーションを可能にするために適切な AWS ソリューションを提案する。
- 復旧アクションの理解をサポートし、演習するための障害シナリオアクティビティを設計する。

### タスク 3.2: セキュリティを向上させるための戦略を決定する

**対象知識:**

- データ保持、データ機密性、データ規制要件
- モニタリングと修正の自動化戦略 (AWS Config ルールなど)
- シークレット管理 (Systems Manager、AWS Secrets Manager など)
- 最小権限アクセスの原則
- セキュリティ固有の AWS ソリューション
- パッチ適用のプラクティス
- バックアップのプラクティスと方法

**対象スキル:**

- シークレットと認証情報を安全に管理するための戦略を評価する。
- 最小権限アクセスについて環境を監査する。
- 実装されたソリューションを見直し、すべてのレイヤーでセキュリティを確保する。
- ユーザーとサービスの包括的なトレーサビリティを見直す。
- 脆弱性の検出に対する自動対応に優先順位を付ける。
- パッチと更新のプロセスを設計し、実装する。
- バックアッププロセスを設計し、実装する。
- 修復手法を採用する。

### タスク 3.3: パフォーマンスを改善するための戦略を決定する

**対象知識:**

- 高パフォーマンスのシステムアーキテクチャ (オートスケーリング、インスタンスフリート、プレイスメントグループなど)
- グローバルサービス (AWS Global Accelerator、Amazon CloudFront、エッジコンピューティングサービスなど)
- モニタリングツールのセットとサービス (CloudWatch など)
- サービスレベルアグリーメント (SLA) と重要業績評価指標 (KPI)

**対象スキル:**

- ビジネス要件を測定可能なメトリクスに変換する。
- 修復ソリューション候補をテストし、レコメンデーションを行う。
- 新しいテクノロジーとマネージドサービスを導入する機会を提案する。
- ソリューションを評価し、要件に基づいてサイズの適正化を行う。
- パフォーマンスのボトルネックを特定し、調査する。

### タスク 3.4: 信頼性を向上させるための戦略を決定する

**対象知識:**

- AWS グローバルインフラストラクチャ
- データレプリケーション方法
- スケーリング方法論 (ロードバランシング、オートスケーリングなど)
- 高可用性と回復力
- ディザスタリカバリの方法とツール
- サービスクォータと上限

**対象スキル:**

- アプリケーションの利用増加と使用傾向を把握する。
- 既存のアーキテクチャを評価し、信頼性が不十分な領域を特定する。
- 単一障害点を修正する。
- データレプリケーション、自己修復、伸縮自在な機能とサービスを実現する。

### タスク 3.5: コスト最適化の機会を特定する

**対象知識:**

- コスト意識の高いアーキテクチャの選択 (スポットインスタンスの使用、スケーリングポリシー、リソースのサイズ適正化など)
- 価格モデルの採用 (リザーブドインスタンス、Savings Plans など)
- ネットワークとデータ転送のコスト
- コスト管理、アラート、レポート作成

**対象スキル:**

- 使用状況レポートを分析し、使用率の低いリソースと使用率の高いリソースを特定する。
- AWS ソリューションを使用し、使用されていないリソースを特定する。
- 予想される使用パターンに基づいて課金アラームを設計する。
- AWS Cost and Usage Report をきめ細かく調査する。
- コスト配分とレポート作成にタグ付けを使用する。

---

## コンテンツ分野 4: ワークロードの移行とモダナイゼーションの加速

### タスク 4.1: 移行が可能な既存のワークロードとプロセスを選択する

**対象知識:**

- 移行アセスメントおよび追跡ツール (AWS Migration Hub など)
- ポートフォリオアセスメント
- アセットプランニング
- ワークロードの優先順位付けと移行 (ウェーブプランニングなど)

**対象スキル:**

- アプリケーション移行アセスメントを実施する。
- 7 つの一般的な移行戦略 (7R) に従ってアプリケーションを評価する。
- 総保有コスト (TCO) を評価する。

### タスク 4.2: 既存ワークロードの最適な移行アプローチを決定する

**対象知識:**

- データ移行のオプションとツール (AWS DataSync、AWS Transfer Family、AWS Snow Family、S3 Transfer Acceleration など)
- アプリケーション移行ツール (AWS Application Discovery Service、AWS Application Migration Service など)
- AWS ネットワークサービスと DNS (Direct Connect、AWS Site-to-Site VPN、Route 53 など)
- アイデンティティサービス (IAM Identity Center、AWS Directory Service など)
- データベース移行ツール [AWS Database Migration Service (AWS DMS)、AWS Schema Conversion Tool (AWS SCT) など]
- ガバナンスツール (AWS Control Tower、Organizations など)

**対象スキル:**

- 適切なデータベース転送メカニズムを選択する。
- 適切なアプリケーション転送メカニズムを選択する。
- 適切なデータ転送サービスと移行戦略を選択する。
- 移行ツールに適したセキュリティ方法を適用する。
- 適切なガバナンスモデルを選択する。

### タスク 4.3: 既存ワークロードの新しいアーキテクチャを決定する

**対象知識:**

- コンピューティングサービス [Amazon Elastic Compute Cloud (Amazon EC2)、AWS Elastic Beanstalk など]
- コンテナ [Amazon Elastic Container Service (Amazon ECS)、Amazon Elastic Kubernetes Service (Amazon EKS)、AWS Fargate, Amazon Elastic Container Registry (Amazon ECR) など]
- AWS ストレージサービス [Amazon Elastic Block Store (Amazon EBS)、Amazon Elastic File System (Amazon EFS)、Amazon FSx、Amazon S3、ボリュームゲートウェイなど]
- データベース (Amazon DynamoDB、Amazon OpenSearch Service、Amazon RDS、Amazon EC2 のセルフマネージド型データベースなど)

**対象スキル:**

- 適切なコンピューティングプラットフォームを選択する。
- 適切なコンテナホスティングプラットフォームを選択する。
- 適切なストレージサービスを選択する。
- 適切なデータベースプラットフォームを選択する。

### タスク 4.4: モダナイゼーションと機能強化の機会を決定する

**対象知識:**

- サーバーレスコンピューティングサービス (AWS Lambda など)
- コンテナ (Amazon ECS、Amazon EKS、Fargate など)
- AWS ストレージサービス (Amazon S3、Amazon EFS など)
- 目的別データベース (DynamoDB, Amazon Aurora Serverless、ElastiCache など)
- 統合サービス (Amazon SQS、Amazon SNS、Amazon EventBridge、Step Functions など)

**対象スキル:**

- アプリケーションコンポーネントを切り離す機会を特定する。
- サーバーレスソリューションの機会を特定する。
- コンテナに適したサービスを選択する。
- 目的別データベースの機会を特定する。
- 適切なアプリケーション統合サービスを選択する。

---

## 付録

### 試験に出題される可能性のあるテクノロジーと概念

以下は、試験に出題される可能性のあるテクノロジーと概念のリストです。このリストはすべてを網羅しているわけではなく、また、変更される場合があります。このリストにおける項目の掲載順序や配置は、その項目の相対的な重みや試験における重要性を示すものではありません。

- コンピューティング
- コスト管理
- データベース
- ディザスタリカバリ
- 高可用性
- マネジメントとガバナンス
- マイクロサービスとコンポーネントのデカップリング
- 移行とデータの転送
- ネットワーク、接続、コンテンツ配信
- セキュリティ
- サーバーレスの設計原則
- ストレージ

### 試験での AWS サービスへの言及

AWS 認定では、略語や括弧付きの情報を含む周知の AWS サービス名に正式な短縮名を使用して、この試験を容易に読めるようにしています。例えば、試験では、Amazon Simple Notification Service (Amazon SNS) が Amazon SNS と記載されます。

試験のヘルプ機能 (すべての問題に用意されています) には、短い AWS サービス名と、それに対応する正式名のリストが含まれています。

試験に短縮名で表示されるサービスのリストについては、AWS 認定ウェブサイトの「AWS サービス名」を参照してください。リストに含まれているサービスのうち、試験の範囲外のものは試験に記載されていません。

**注**: 略語には、試験に正式名が記述されていないものや、ヘルプ機能に含まれていないものがあります。一部の AWS サービスの正式名 (Amazon API Gateway、Amazon EMR など) には、常に略語のまま記載される略語が含まれています。また、試験には、受験者が知っていると想定される他の略語が含まれる場合もあります。

### 範囲内の AWS のサービスと機能

以下に、試験範囲の AWS のサービスと機能のリストを示します。このリストはすべてを網羅しているわけではなく、また、変更される場合があります。各 AWS のサービスは、サービスの主な機能に応じたカテゴリに分けられています。

#### 分析

- Amazon Athena
- AWS Data Exchange
- Amazon Data Firehose
- Amazon EMR
- AWS Glue
- Amazon Kinesis Data Streams
- AWS Lake Formation
- Amazon Managed Service for Apache Flink
- Amazon Managed Streaming for Apache Kafka (Amazon MSK)
- Amazon OpenSearch Service
- Amazon QuickSight

#### アプリケーション統合

- Amazon AppFlow
- AWS AppSync
- Amazon EventBridge
- Amazon MQ
- Amazon Simple Notification Service (Amazon SNS)
- Amazon Simple Queue Service (Amazon SQS)
- AWS Step Functions

#### ブロックチェーン

- Amazon Managed Blockchain

#### ビジネスアプリケーション

- Amazon Simple Email Service (Amazon SES)

#### クラウド財務管理

- AWS Budgets
- AWS Cost and Usage Report
- AWS Cost Explorer
- Savings Plans

#### コンピューティング

- AWS App Runner
- AWS Auto Scaling
- AWS Batch
- AWS Elastic Beanstalk
- Amazon Elastic Compute Cloud (Amazon EC2)
- Amazon EC2 Auto Scaling
- AWS Fargate
- AWS Lambda
- Amazon Lightsail
- AWS Outposts
- AWS Wavelength

#### コンテナ

- Amazon Elastic Container Registry (Amazon ECR)
- Amazon Elastic Container Service (Amazon ECS)
- Amazon ECS Anywhere
- Amazon Elastic Kubernetes Service (Amazon EKS)
- Amazon EKS Anywhere
- Amazon EKS Distro

#### データベース

- Amazon Aurora
- Amazon Aurora Serverless
- Amazon DocumentDB (MongoDB 互換)
- Amazon DynamoDB
- Amazon ElastiCache
- Amazon Keyspaces (Apache Cassandra 向け)
- Amazon Neptune
- Amazon Relational Database Service (Amazon RDS)
- Amazon Redshift
- Amazon Timestream

#### デベロッパーツール

- AWS CodeArtifact
- AWS CodeBuild
- AWS CodeDeploy
- Amazon CodeGuru
- AWS CodePipeline
- AWS X-Ray

#### エンドユーザーコンピューティング

- Amazon AppStream 2.0
- Amazon WorkSpaces

#### フロントエンドのウェブとモバイル

- AWS Amplify
- Amazon API Gateway
- AWS Device Farm
- Amazon Pinpoint

#### IoT

- AWS IoT Core
- AWS IoT Device Defender
- AWS IoT Device Management
- AWS IoT Events
- AWS IoT Greengrass
- AWS IoT SiteWise
- AWS IoT Things Graph
- AWS IoT 1-Click

#### 機械学習

- Amazon Comprehend
- Amazon Fraud Detector
- Amazon Kendra
- Amazon Lex
- Amazon Personalize
- Amazon Polly
- Amazon Rekognition
- Amazon SageMaker AI (旧名 Amazon SageMaker)
- Amazon Textract
- Amazon Transcribe
- Amazon Translate

#### マネジメントとガバナンス

- AWS CloudFormation
- AWS CloudTrail
- Amazon CloudWatch
- Amazon CloudWatch Logs
- AWS コマンドラインインターフェイス (AWS CLI)
- AWS Compute Optimizer
- AWS Config
- AWS Control Tower
- AWS Health Dashboard
- AWS License Manager
- Amazon Managed Grafana
- Amazon Managed Service for Prometheus
- AWS マネジメントコンソール
- AWS Organizations
- AWS Proton
- AWS Service Catalog
- Service Quotas
- AWS Systems Manager
- AWS Trusted Advisor
- AWS Well-Architected Tool

#### メディアサービス

- Amazon Elastic Transcoder
- Amazon Kinesis Video Streams

#### 移行と転送

- AWS Application Discovery Service
- AWS Application Migration Service
- AWS Database Migration Service (AWS DMS)
- AWS DataSync
- AWS Migration Hub
- AWS Schema Conversion Tool (AWS SCT)
- AWS Snow Family
- AWS Transfer Family

#### ネットワークとコンテンツ配信

- Amazon CloudFront
- AWS Direct Connect
- Elastic Load Balancing (ELB)
- AWS Global Accelerator
- AWS PrivateLink
- Amazon Route 53
- AWS Transit Gateway
- Amazon Virtual Private Cloud (Amazon VPC)
- AWS VPN

#### セキュリティ、アイデンティティ、コンプライアンス

- AWS Artifact
- AWS Audit Manager
- AWS Certificate Manager (ACM)
- AWS CloudHSM
- Amazon Cognito
- Amazon Detective
- AWS Directory Service
- AWS Firewall Manager
- Amazon GuardDuty
- AWS IAM アイデンティティセンター
- AWS Identity and Access Management (IAM)
- Amazon Inspector
- AWS Key Management Service (AWS KMS)
- Amazon Macie
- AWS Network Firewall
- AWS Resource Access Manager (AWS RAM)
- AWS Secrets Manager
- AWS Security Hub
- AWS Security Token Service (AWS STS)
- AWS Shield
- AWS WAF

#### ストレージ

- AWS Backup
- Amazon Elastic Block Store (Amazon EBS)
- AWS Elastic Disaster Recovery
- Amazon Elastic File System (Amazon EFS)
- Amazon FSx (すべてのタイプに対応)
- Amazon Simple Storage Service (Amazon S3)
- Amazon S3 Glacier
- AWS Storage Gateway

### 範囲外の AWS のサービスと機能

以下に、試験対象外の AWS のサービスと機能のリストを示します。このリストはすべてを網羅しているわけではなく、また、変更される場合があります。試験の対象となる職務内容に完全に関係のない AWS のサービスは、このリストから除外されています。

#### ゲーム関連テクノロジー

- Amazon GameLift

---

## アンケート

この試験ガイドはどの程度役に立ちましたか？ アンケートに答えてお知らせください。

---

**バージョン 1.2 SAP-C02**
