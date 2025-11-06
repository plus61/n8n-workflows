# WF7 Notion移行ガイド

**Google Sheets → Notion Database 移行版**

## 📋 概要

WF7の状態管理をGoogle SheetsからNotion Databaseに移行します。

## 🗄️ Notionデータベース構造

### データベース名: 「WF7 動画管理マスタ」

#### プロパティ定義

| プロパティ名 | Notion型 | 説明 | 必須 |
|-------------|----------|------|------|
| **タイトル** | title | 記事タイトル | ✅ |
| Article ID | rich_text | note記事ID | ✅ |
| Script URL | url | script.json URL | |
| Assets URL | url | assets.json URL | |
| Voice URL | url | voice.wav URL | |
| Subtitle URL | url | subtitle.srt URL | |
| Video URL | url | 完成動画URL | |
| Thumbnail URL | url | サムネイルURL | |
| Template ID | select | テンプレートID（default, hook01など） | |
| Status | select | 処理状態 | ✅ |
| Needs Narration | checkbox | 音声生成要否 | |
| Created At | date | 作成日時 | ✅ |
| Completed At | date | 完了日時 | |
| Error Message | rich_text | エラー内容 | |

#### Statusセレクトオプション

- 🟡 Pending - 待機中
- 🔵 Processing - 台本生成中
- 🟢 AssetsReady - 素材取得完了
- 🟣 VoiceReady - 音声生成完了（オプション）
- 🟢 Ready - レンダリング準備完了
- 🟠 Rendering - レンダリング中
- 🟢 Rendered - 動画生成完了
- ✅ Completed - 全処理完了
- ❌ Failed_Phase1 - Phase1失敗
- ❌ Failed_Phase2 - Phase2失敗
- ❌ Failed_Phase3 - Phase3失敗
- ❌ Failed_Phase4 - Phase4失敗
- ❌ Failed_Phase5 - Phase5失敗

#### Template IDセレクトオプション

- default
- hook01
- pain01
- solution01

## 🔄 移行マッピング

### Google Sheets → Notion

| Sheets列 | Notion プロパティ | 変換内容 |
|----------|------------------|----------|
| title | タイトル (title) | そのまま |
| articleId | Article ID (rich_text) | そのまま |
| scriptUrl | Script URL (url) | そのまま |
| assetsUrl | Assets URL (url) | そのまま |
| voiceUrl | Voice URL (url) | そのまま |
| subtitleUrl | Subtitle URL (url) | そのまま |
| videoUrl | Video URL (url) | そのまま |
| thumbUrl | Thumbnail URL (url) | そのまま |
| templateId | Template ID (select) | そのまま |
| status | Status (select) | そのまま |
| needsNarration | Needs Narration (checkbox) | boolean値 |
| createdAt | Created At (date) | ISO 8601形式 |
| completedAt | Completed At (date) | ISO 8601形式 |
| errorMessage | Error Message (rich_text) | そのまま |

## 🔧 ワークフロー変更点

### Phase 1: 台本整形

**変更前**: Google Sheets - 行追加  
**変更後**: Notion - ページ作成

```javascript
// Notionペイロード例
{
  "parent": { "database_id": "{{NOTION_WF7_DB_ID}}" },
  "properties": {
    "タイトル": {
      "title": [{ "text": { "content": "MEO対策の基本" } }]
    },
    "Article ID": {
      "rich_text": [{ "text": { "content": "note-abc123" } }]
    },
    "Script URL": {
      "url": "https://drive.google.com/.../script.json"
    },
    "Status": {
      "select": { "name": "Processing" }
    },
    "Needs Narration": {
      "checkbox": false
    },
    "Created At": {
      "date": { "start": "2025-10-29T12:00:00Z" }
    }
  }
}
```

### Phase 2-5: Trigger変更

**変更前**: Google Sheets Trigger（新規行/行更新）  
**変更後**: n8nのPolling Trigger（Notionデータベース問い合わせ）

**実装方法**:
1. Schedule Trigger（1分間隔）
2. Notion API: データベース問い合わせ（Status=特定値）
3. 前回実行時刻との比較で新規/更新を判定

```javascript
// Phase 2: Status='Processing'のページを取得
POST https://api.notion.com/v1/databases/{{DB_ID}}/query
{
  "filter": {
    "property": "Status",
    "select": {
      "equals": "Processing"
    }
  },
  "sorts": [{
    "property": "Created At",
    "direction": "descending"
  }]
}
```

## 📝 実装手順

### Step 1: Notionデータベース作成

1. Notionで新規データベース作成
2. データベース名: 「WF7 動画管理マスタ」
3. 上記のプロパティを全て追加
4. Statusセレクトオプションを全て追加
5. データベースIDをコピー（URLの `/` の後の32文字）

### Step 2: n8n環境変数更新

```bash
# 削除
GOOGLE_SHEETS_VIDEO_MASTER_ID=<削除>

# 追加
NOTION_WF7_MASTER_DB_ID=<NotionデータベースID>
```

### Step 3: ワークフロー更新

各Phaseワークフローを以下の順で更新：

#### Phase 1更新
- Google Sheets行追加ノード → Notion APIページ作成ノードに置き換え
- Notion MCP `API-post-page`を使用

#### Phase 2-5更新
- Google Sheets Triggerノード削除
- Schedule Trigger（1分間隔）+ Notion API Query に置き換え
- Google Sheets Updateノード → Notion API PATCH に置き換え
- Notion MCP `API-patch-page`を使用

### Step 4: テスト実行

1. Phase 1単体テスト（Webhook送信）
2. Notionでページ作成を確認
3. Phase 2-5の順次実行確認

## 🎯 メリット

### Google Sheets → Notion移行のメリット

| 項目 | Google Sheets | Notion Database |
|------|---------------|-----------------|
| **視覚性** | ❌ 表形式のみ | ✅ ボード/ギャラリービュー |
| **リレーション** | ❌ 手動管理 | ✅ ネイティブ対応 |
| **リッチコンテンツ** | ❌ 制限あり | ✅ 埋め込み/画像 |
| **通知** | ❌ 外部連携必要 | ✅ ネイティブ通知 |
| **コメント** | ❌ セルコメントのみ | ✅ ページコメント |
| **バージョン履歴** | ⚠️ 限定的 | ✅ 完全な履歴 |

## ⚠️ 注意事項

### Notion API制限

- **レート制限**: 3 requests/second
- **ページサイズ**: 最大100プロパティ
- **クエリ結果**: 最大100件（ページネーション対応）

### 移行時の考慮点

1. **Triggerの違い**: SheetsのリアルタイムTriggerがNotionでは不可
   - 対策: Schedule Trigger + Pollingで代替（1分間隔）

2. **データ移行**: 既存Sheetsデータの移行が必要な場合
   - 対策: 移行スクリプト作成またはCSVインポート

3. **バックアップ**: Notion APIエラー時の対応
   - 対策: エラーハンドリング強化、Slack通知

## 🔗 参考リンク

- [Notion API公式ドキュメント](https://developers.notion.com/)
- [n8n Notion Integration](https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.notion/)
- [Notion MCP Tools](https://github.com/makenotion/notion-sdk-js)

---

**作成日**: 2025-10-29  
**作成者**: Claude Code

