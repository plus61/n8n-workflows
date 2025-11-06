# LINE CRM with Notion Integration

LINE公式アカウントとNotionを連携したリード管理システム

## 🎯 概要

このワークフローシステムは、LINE公式アカウントでの顧客接点を自動化し、Notionで一元管理するためのソリューションです。

### 主要機能

- ✅ 友だち追加時の自動登録
- ✅ LINEプロフィール情報の取得
- ✅ Notionへのリアルタイム同期
- ✅ リッチメニュー連携
- ✅ 段階的な情報配信
- ✅ タグ自動付与

### システム構成

```
LINE公式アカウント
  ↓
Webhook (n8n)
  ↓
ワークフロー処理
  ↓
Notion Database
```

## 📁 ワークフロー一覧

### 1. LINE Lead Pipeline - Notion

**ファイル**: `lead-pipeline.json`

**機能**:
- 友だち追加イベントの処理
- メッセージイベントの処理
- リッチメニューイベントの処理
- Notionへのデータ登録・更新

**Webhook URL**: `https://your-n8n-instance.com/webhook/line-lead-notion`

### 2. LINE Step Delivery System

**ファイル**: `step-delivery.json`

**機能**:
- 段階的な情報配信
- 配信タイミングの自動制御
- Notionステータス更新

**実行頻度**: 1時間ごと

### 3. LINE Rich Menu Integration

**ファイル**: `rich-menu.json`

**機能**:
- リッチメニュータップの検知
- ユーザー関心度の記録
- タグ自動付与

**注意**: 現在は Lead Pipeline ワークフローに統合されています。

## 🚀 セットアップ

### 前提条件

- n8nインスタンス（セルフホストまたはRailway等）
- LINE Developersアカウント
- Notionアカウント
- Notion Integration Token

### 手順

#### 1. Notionデータベース作成

詳細は [notion-database-setup.md](notion-database-setup.md) を参照してください。

#### 2. LINE設定

詳細は [line-setup.md](line-setup.md) を参照してください。

#### 3. n8nワークフローインポート

1. n8n管理画面を開く
2. 「Import from File」を選択
3. 各JSONファイルをインポート
4. 認証情報を設定

#### 4. 環境変数設定

```bash
# LINE
LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token

# Notion
NOTION_API_KEY=your_notion_integration_token
NOTION_DATABASE_ID=your_database_id
```

#### 5. Webhook URL設定

LINE Developers ConsoleでWebhook URLを設定します。

```
https://your-n8n-instance.com/webhook/line-lead-notion
```

## 📊 Notionデータベース構造

| プロパティ名 | タイプ | 用途 |
|------------|--------|------|
| Lead ID | Title | ユニークID |
| User ID | Rich Text | LINE User ID |
| Display Name | Rich Text | 表示名 |
| Picture URL | URL | プロフィール画像 |
| Timestamp JST | Date | 登録日時 |
| Last Message Date | Date | 最終メッセージ日時 |
| Source | Multi-select | 登録元 |
| Status | Multi-select | 処理状態 |
| Step Status | Select | ステップ配信状態 |
| Current Step | Number | 現在のステップ |
| Rich Menu ID | Rich Text | リッチメニューID |
| Tags | Multi-select | タグ |
| Notes | Rich Text | メモ |

## 🔄 データフロー

### 友だち追加フロー

```
1. ユーザーが友だち追加
   ↓
2. LINEがfollowイベントを送信
   ↓
3. n8n Webhookが受信
   ↓
4. LINEプロフィール取得
   ↓
5. Notionに登録
   ↓
6. ウェルカムメッセージ送信
```

### リッチメニュータップフロー

```
1. ユーザーがリッチメニューをタップ
   ↓
2. LINEがmessageイベントを送信
   ↓
3. n8nがメッセージをパース
   ↓
4. Notionでユーザー検索
   ↓
5. Rich Menu ID、Tagsを更新
   ↓
6. 応答メッセージ送信
```

### ステップ配信フロー

```
1. Schedule Trigger (1時間ごと)
   ↓
2. Notion検索 (Step Status = 配信中)
   ↓
3. 配信タイミング判定
   ↓
4. LINEメッセージ送信
   ↓
5. Notion更新 (Current Step, Last Message Date)
```

## 📝 ドキュメント

- [Notionデータベースセットアップ](notion-database-setup.md)
- [LINE設定ガイド](line-setup.md)
- [リッチメニュー設定ガイド](rich-menu-setup.md)
- [Notionダッシュボードガイド](dashboard-setup.md)
- [トラブルシューティング](troubleshooting.md)

## 🧪 テスト

### 友だち追加テスト

1. LINEアプリで公式アカウントを友だち追加
2. n8n実行履歴を確認
3. Notionデータベースにレコードが追加されているか確認
4. ウェルカムメッセージが届くか確認

### リッチメニューテスト

1. リッチメニューをタップ
2. n8n実行履歴を確認
3. NotionでRich Menu IDがTagsが更新されているか確認

### ステップ配信テスト

1. NotionでStep Statusを「配信中」に設定
2. 1時間待つ
3. LINEメッセージが届くか確認
4. NotionでCurrent Stepが更新されているか確認

## 🐛 トラブルシューティング

詳細は [troubleshooting.md](troubleshooting.md) を参照してください。

### よくある問題

#### Webhookが反応しない

- Webhook URLが正しいか確認
- n8nワークフローがアクティブか確認
- LINE Developers ConsoleでWebhook送信が有効か確認

#### Notionにデータが登録されない

- Notion Integration Tokenが有効か確認
- データベースIDが正しいか確認
- データベースにインテグレーションが接続されているか確認

#### ステップ配信が実行されない

- Schedule Triggerが有効か確認
- Step Statusが「配信中」に設定されているか確認
- Last Message Dateが正しく記録されているか確認

## 📊 主要KPI

### システムパフォーマンス

- Webhook応答時間: < 3秒
- ステップ配信精度: 100%
- Notion同期成功率: 100%

### 運用効率

- 日次タスク時間: 5分
- データ確認: 1ページ
- 意思決定速度: 即座

## 🚀 今後の拡張

### Phase 2: 分析強化

- Google Sheetsへの自動エクスポート
- 週次レポート自動生成
- コンバージョン率分析

### Phase 3: 自動化強化

- AIによる自動返信
- セグメント別自動配信
- A/Bテスト機能

### Phase 4: 統合拡張

- Slack通知連携
- Google Analytics連携
- CRM連携

## 📚 参考リンク

- [LINE Messaging API](https://developers.line.biz/ja/docs/messaging-api/)
- [Notion API](https://developers.notion.com/)
- [n8n Documentation](https://docs.n8n.io/)

---

**作成日**: 2025-10-26  
**最終更新**: 2025-10-26  
**ステータス**: ✅ 完全完了
