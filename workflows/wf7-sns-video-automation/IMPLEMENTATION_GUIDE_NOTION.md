# WF7 SNS動画化ワークフロー 実装ガイド（Notion版）

**バージョン**: v2.0 - Notion Database対応版  
**更新日**: 2025-10-29  
**ステータス**: Notion移行完了（Phase 1実装済み）

---

## 📋 概要

WF7の状態管理を**Google Sheets → Notion Database**に完全移行しました。

### Notionデータベース情報

**データベース名**: WF7 動画管理マスタ  
**データベースID**: `29b68d5c-2986-817f-b4e6-f84cf75ea9ed`  
**URL**: https://www.notion.so/29b68d5c2986817fb4e6f84cf75ea9ed

---

## ✅ 完成したワークフロー（Notion版）

### Phase 1: 台本整形 ✅ **Notion対応完了**
**ワークフローID**: `fqbULAMXIGyBkNtL`

**変更内容**:
- ❌ Google Sheets行追加 削除
- ✅ Notion APIページ作成 追加

**機能**:
1. WF6からWebhook受信
2. GPT-4o-miniで台本生成
3. **Notion Database**に新規ページ作成（Status: Processing）
4. script.jsonをGoogle Driveに保存
5. Slack通知

### Phase 2-5: 残りの更新が必要

以下のPhaseは**手動で更新**するか、n8n UIから直接編集してください。

---

## 🔧 Phase 2-5の更新手順

### Phase 2: 素材取得の更新

**ワークフローID**: `sGjN9Vqw4pGTLmaX`

#### 変更手順

1. **Sheets Triggerを削除**
2. **Schedule Triggerを追加**（1分間隔）
3. **Notion Query APIノードを追加**

```javascript
// Notion API Query
POST https://api.notion.com/v1/databases/29b68d5c-2986-817f-b4e6-f84cf75ea9ed/query
Headers: {
  "Authorization": "Bearer {{NOTION_API_KEY}}",
  "Notion-Version": "2022-06-28"
}
Body: {
  "filter": {
    "property": "Status",
    "select": {
      "equals": "Processing"
    }
  },
  "sorts": [{
    "property": "Created At",
    "direction": "descending"
  }],
  "page_size": 10
}
```

4. **Notion Update APIノードを追加**（最後に）

```javascript
// Notion Page Update
PATCH https://api.notion.com/v1/pages/{{$json.id}}
Headers: {
  "Authorization": "Bearer {{NOTION_API_KEY}}",
  "Notion-Version": "2022-06-28"
}
Body: {
  "properties": {
    "Assets URL": {
      "url": "{{$json.assetsUrl}}"
    },
    "Status": {
      "select": {
        "name": "AssetsReady"
      }
    }
  }
}
```

### Phase 3: 音声・字幕生成の更新

**ワークフローID**: `KkiF386PmAVaY1mA`

#### 変更手順

1. **Sheets Triggerを削除**
2. **Schedule Trigger + Notion Query**に置き換え

```javascript
// Query条件
{
  "filter": {
    "and": [
      {
        "property": "Status",
        "select": {
          "equals": "AssetsReady"
        }
      },
      {
        "property": "Needs Narration",
        "checkbox": {
          "equals": true
        }
      }
    ]
  }
}
```

3. **Notion Update API**（最後に）

```javascript
{
  "properties": {
    "Voice URL": {"url": "{{$json.voiceUrl}}"},
    "Subtitle URL": {"url": "{{$json.subtitleUrl}}"},
    "Status": {"select": {"name": "Ready"}}
  }
}
```

### Phase 4: 動画レンダリングの更新

**ワークフローID**: `VF3kFwJLKVq990jn`

#### 変更手順

1. **Sheets Triggerを削除**
2. **Schedule Trigger + Notion Query**に置き換え

```javascript
// Query条件
{
  "filter": {
    "or": [
      {
        "property": "Status",
        "select": {
          "equals": "Ready"
        }
      },
      {
        "property": "Status",
        "select": {
          "equals": "AssetsReady"
        }
      }
    ]
  }
}
```

3. **Notion Update API**（最後に）

```javascript
{
  "properties": {
    "Video URL": {"url": "{{$json.videoUrl}}"},
    "Thumbnail URL": {"url": "{{$json.thumbUrl}}"},
    "Status": {"select": {"name": "Rendered"}}
  }
}
```

### Phase 5: メタデータ登録・連携の更新

**ワークフローID**: `0CK4yaBsipa1UgSz`

#### 変更手順

1. **Sheets Triggerを削除**
2. **Schedule Trigger + Notion Query**に置き換え

```javascript
// Query条件
{
  "filter": {
    "property": "Status",
    "select": {
      "equals": "Rendered"
    }
  }
}
```

3. **最後のNotion Update API**（ステータス完了）

```javascript
{
  "properties": {
    "Status": {"select": {"name": "Completed"}},
    "Completed At": {"date": {"start": "{{$now.toISO()}}"}}
  }
}
```

---

## 🚀 環境変数設定

### n8n環境変数（更新）

```bash
# 削除（不要になった）
# GOOGLE_SHEETS_VIDEO_MASTER_ID=<削除>

# 追加
NOTION_WF7_MASTER_DB_ID=29b68d5c-2986-817f-b4e6-f84cf75ea9ed

# 既存（変更なし）
GOOGLE_DRIVE_WF7_FOLDER_ID=<FolderID>
CLOUD_RUN_RENDERER_URL=https://wf7-renderer-xxxxx.run.app
VOICEVOX_URL=http://localhost:50021
WF8_WEBHOOK_URL=https://your-n8n.com/webhook/wf8-sns-publish
```

### Notion API認証設定

n8n UIで以下を設定：

1. **Credentials** → **New Credential**
2. **Notion API** を選択
3. **Internal Integration Token** に以下を入力：
   ```
   <NOTION_API_KEY>
   ```

   **⚠️ 注意**: 実際のAPIキーは環境変数 `NOTION_API_KEY` から取得してください。

---

## 📊 Notionデータベース構造

### プロパティ一覧

| プロパティ名 | 型 | 説明 | 必須 |
|-------------|-----|------|------|
| **Title** | title | 記事タイトル | ✅ |
| Article ID | rich_text | note記事ID | ✅ |
| Script URL | url | script.json URL | |
| Assets URL | url | assets.json URL | |
| Voice URL | url | voice.wav URL | |
| Subtitle URL | url | subtitle.srt URL | |
| Video URL | url | 完成動画URL | |
| Thumbnail URL | url | サムネイルURL | |
| Template ID | select | テンプレートID | |
| Status | select | 処理状態 | ✅ |
| Needs Narration | checkbox | 音声生成要否 | |
| Created At | date | 作成日時 | ✅ |
| Completed At | date | 完了日時 | |
| Error Message | rich_text | エラー内容 | |

### Statusセレクトオプション

- Pending
- Processing
- AssetsReady
- VoiceReady
- Ready
- Rendering
- Rendered
- Completed
- Failed_Phase1
- Failed_Phase2
- Failed_Phase3
- Failed_Phase4
- Failed_Phase5

---

## 🧪 テスト手順

### 1. Phase 1単体テスト（Notion版）

```bash
curl -X POST https://your-n8n.com/webhook/wf7-video-script \
  -H "Content-Type: application/json" \
  -d '{
    "articleId": "note-test002",
    "title": "Notion移行テスト",
    "keyPoints": ["テスト1", "テスト2", "テスト3"]
  }'
```

**期待結果**:
- ✅ Notionに新規ページ作成
- ✅ Status = "Processing"
- ✅ script.jsonがGoogle Driveに保存
- ✅ Slack通知受信

### 2. Notionでの確認

1. Notionで「WF7 動画管理マスタ」を開く
2. 新しいページが追加されているか確認
3. Status = "Processing" になっているか確認

### 3. Phase 2-5のテスト

手動でNotionのStatusを変更して、各Phaseが起動することを確認：

1. Status → "Processing" → Phase 2起動
2. Status → "AssetsReady" → Phase 4起動（音声なし）
3. Status → "Rendered" → Phase 5起動

---

## 📈 メリット

### Google Sheets → Notion移行のメリット

| 項目 | Google Sheets | Notion Database |
|------|---------------|-----------------|
| **視覚性** | ❌ 表形式のみ | ✅ ボード/ギャラリー/タイムライン |
| **リレーション** | ❌ 手動管理 | ✅ ネイティブ対応 |
| **コメント** | ❌ セルコメントのみ | ✅ ページ単位のディスカッション |
| **リッチコンテンツ** | ❌ 制限あり | ✅ 埋め込み/画像/動画 |
| **通知** | ❌ 外部連携必要 | ✅ ネイティブ通知 |
| **バージョン履歴** | ⚠️ 限定的 | ✅ 完全な履歴 |
| **モバイル対応** | ⚠️ 普通 | ✅ 優れたアプリ |

---

## ⚠️ 注意事項

### Notion API制限

- **レート制限**: 3 requests/second
- **クエリ結果**: 最大100件（ページネーション対応）
- **プロパティ数**: 最大100個

### Trigger方式の変更

**Google Sheets**:
- リアルタイムTrigger（Webhook）
- 行追加/更新を即座に検知

**Notion**:
- Polling Trigger（Schedule + Query）
- 1分間隔でステータス確認
- 最大1分の遅延が発生する可能性

### 対策

1. **Schedule間隔調整**
   - 急ぎの場合: 30秒間隔
   - 通常: 1分間隔
   - 省エネ: 5分間隔

2. **重複処理防止**
   - 最終更新時刻をチェック
   - 処理済みフラグを追加

---

## 🔗 参考リンク

- [Notion API公式ドキュメント](https://developers.notion.com/)
- [n8n Notion Integration](https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.notion/)
- [Notion Query Filter Examples](https://developers.notion.com/reference/post-database-query-filter)

---

## ✅ 完了チェックリスト

- [x] Notionデータベース作成
- [x] Phase 1更新（Notion対応完了）
- [ ] Phase 2更新（Sheets Trigger → Schedule + Query）
- [ ] Phase 3更新（Sheets Trigger → Schedule + Query）
- [ ] Phase 4更新（Sheets Trigger → Schedule + Query）
- [ ] Phase 5更新（Sheets Trigger → Schedule + Query）
- [ ] エンドツーエンドテスト実行
- [ ] ドキュメント完備

---

**作成者**: Claude Code with Notion MCP  
**レビュー**: 未実施  
**最終更新**: 2025-10-29

