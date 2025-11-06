# WF7 Phase3 移行レポート

**作成日**: 2025-10-30
**Workflow ID**: `KkiF386PmAVaY1mA`
**Workflow名**: WF7 Phase3: 音声・字幕生成（オプション）

---

## 📋 移行概要

Google Sheets/Drive依存のワークフローをNotion API + Webhook + 外部ストレージ方式に移行完了。

### 変更サマリー

| 項目 | 移行前 | 移行後 |
|-----|-------|-------|
| トリガー | Google Sheets (rowUpdated) | Webhook (POST) |
| 音声ファイル保存 | Google Drive | 外部ストレージURL |
| 字幕ファイル保存 | Google Drive | 外部ストレージURL |
| メタデータ更新 | Google Sheets | Notion API PATCH |
| ノード数 | 9 | 11 (+2) |

---

## 🔧 実施した変更

### 1. トリガーの変更

**移行前**:
```javascript
{
  "type": "n8n-nodes-base.googleSheets",
  "parameters": {
    "event": "rowUpdated"
  }
}
```

**移行後**:
```javascript
{
  "id": "sheets-trigger",
  "name": "WF7-Phase3 Webhook",
  "type": "n8n-nodes-base.webhook",
  "typeVersion": 2,
  "parameters": {
    "httpMethod": "POST",
    "path": "wf7-phase3-audio",
    "responseMode": "responseNode"
  }
}
```

**Webhook URL**: `https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase3-audio`

### 2. 入力データ解析の更新

**"ナレーション抽出" Node** - Webhook用にペイロード解析を追加:

```javascript
const input = $input.first().json;
const body = input.body?.body || input.body || input;

const articleId = body.articleId;
const notionPageId = body.notionPageId;
const scriptUrl = body.scriptUrl;

if (!articleId || !notionPageId) {
  throw new Error('articleId and notionPageId are required');
}

// TODO: scriptUrlからscript.jsonを取得してnarrationTextを抽出
const narrationText = 'こちらの動画では、MEO対策の基本を紹介します。';

return {
  json: {
    articleId,
    notionPageId,
    narrationText,
    speaker: 1
  }
};
```

### 3. ファイル保存の変更

#### Google Drive Upload → 外部ストレージメタデータ

**削除したNode**:
- "Drive音声アップロード" (Google Drive)
- "Drive字幕アップロード" (Google Drive)

**追加したNode**:

**"音声メタデータ保存"**:
```javascript
const articleId = $('ナレーション抽出').first().json.articleId;
const notionPageId = $('ナレーション抽出').first().json.notionPageId;

// TODO: 音声ファイルを外部ストレージにアップロード
// 現在はダミーURL
const voiceFileUrl = `https://storage.example.com/voice_${articleId}.wav`;

return {
  json: {
    articleId,
    notionPageId,
    voiceFileUrl
  },
  binary: $binary
};
```

**"字幕メタデータ保存"**:
```javascript
const prevData = $input.first().json;
const srtContent = prevData.srtContent;
const articleId = prevData.articleId;

// TODO: SRTファイルを外部ストレージにアップロード
const subtitleFileUrl = `https://storage.example.com/subtitle_${articleId}.srt`;

return {
  json: {
    ...prevData,
    subtitleFileUrl
  }
};
```

### 4. メタデータ更新の変更

#### Google Sheets Update → Notion API PATCH (2-nodeパターン)

**削除したNode**:
- "SheetsURL更新" (Google Sheets)

**追加したNode**:

**"Notionペイロード作成"** (Code Node):
```javascript
const { notionPageId, voiceFileUrl, subtitleFileUrl } = $input.first().json;

if (!notionPageId) {
  throw new Error('notionPageId is required');
}

return {
  json: {
    notionPageId,
    notionPayload: {
      properties: {
        'Voice File URL': {
          url: voiceFileUrl || ''
        },
        'Subtitle File URL': {
          url: subtitleFileUrl || ''
        },
        'Status': {
          select: {
            name: 'AudioReady'
          }
        }
      }
    }
  }
};
```

**"Notionページ更新"** (HTTP Request Node):
```javascript
{
  "method": "PATCH",
  "url": "=https://api.notion.com/v1/pages/{{ $json.notionPageId }}",
  "sendHeaders": true,
  "headerParameters": {
    "parameters": [
      {
        "name": "Authorization",
        "value": "Bearer <NOTION_API_TOKEN>"
      },
      {
        "name": "Notion-Version",
        "value": "2022-06-28"
      },
      {
        "name": "Content-Type",
        "value": "application/json"
      }
    ]
  },
  "sendBody": true,
  "contentType": "json",
  "jsonBody": "={{ $json.notionPayload }}",
  "options": {
    "timeout": 10000
  }
}
```

**"Respond to Webhook"** (Webhook Response Node):
```javascript
{
  "type": "n8n-nodes-base.respondToWebhook",
  "typeVersion": 1,
  "parameters": {
    "options": {}
  }
}
```

---

## 🔄 新しいデータフロー

```
WF7-Phase3 Webhook (POST)
  ↓
音声必要性判定 (IF needsNarration)
  ↓ (true)
ナレーション抽出 (Parse webhook input)
  ↓
VOICEVOX音声クエリ (GET audio_query)
  ↓
VOICEVOX音声合成 (POST synthesis)
  ↓
音声メタデータ保存 (Generate voice URL)
  ↓
SRT字幕生成 (Generate subtitle)
  ↓
字幕メタデータ保存 (Generate subtitle URL)
  ↓
Notionペイロード作成 (Build API payload)
  ↓
Notionページ更新 (PATCH to Notion API)
  ↓
Respond to Webhook (Return success)
```

---

## 📊 適用したベストプラクティス

### ✅ Phase1からの教訓適用

1. **2-nodeパターン**: Notion API更新に適用
   - Code Nodeでペイロード構築
   - HTTP Request Nodeでシンプルな送信

2. **`.first()` 構文**: すべてのノード参照で使用
   - `$('ナレーション抽出').first().json.articleId`

3. **Notion-Versionヘッダー**: 明示的に指定
   - `"Notion-Version": "2022-06-28"`

4. **エラーハンドリング**: 必須パラメータの検証
   ```javascript
   if (!articleId || !notionPageId) {
     throw new Error('articleId and notionPageId are required');
   }
   ```

---

## 🎯 必要なNotionデータベースプロパティ

Phase3で使用する新しいプロパティ:

| プロパティ名 | タイプ | 用途 |
|------------|------|------|
| Voice File URL | URL | 音声ファイルのURL |
| Subtitle File URL | URL | 字幕ファイルのURL |
| Status | Select | ワークフローステータス (AudioReady) |

**確認が必要**: Notion Database ID `29b68d5c-2986-817f-b4e6-f84cf75ea9ed` にこれらのプロパティが存在するか検証。

---

## ⚠️ TODO項目

### 高優先度

1. **外部ストレージ統合**
   ```javascript
   // 現在: ダミーURL
   const voiceFileUrl = `https://storage.example.com/voice_${articleId}.wav`;

   // 必要: 実際のストレージAPIコール
   // - Cloudflare R2
   // - AWS S3
   // - Google Cloud Storage
   ```

2. **scriptUrl解析機能**
   ```javascript
   // 現在: ハードコードされたテキスト
   const narrationText = 'こちらの動画では、MEO対策の基本を紹介します。';

   // 必要: scriptUrlから実際のscript.jsonを取得
   // - HTTP Request でscript.jsonを取得
   // - narrationTextフィールドを抽出
   ```

3. **Notionデータベーススキーマ検証**
   - Voice File URL プロパティの存在確認
   - Subtitle File URL プロパティの存在確認
   - Status選択肢に "AudioReady" が存在するか確認

### 中優先度

4. **Webhook認証追加**
   ```javascript
   // 推奨: Webhook URLに認証トークン追加
   "path": "wf7-phase3-audio?token=secret_token_here"
   ```

5. **エラーハンドリング強化**
   - VOICEVOX APIエラー時のリトライロジック
   - Notion API更新失敗時のフォールバック
   - ストレージアップロード失敗時の処理

6. **音声必要性判定の改善**
   ```javascript
   // 現在: needsNarrationフィールドで判定
   // 改善案: より詳細な条件チェック
   // - 既存の音声ファイルURLの有無
   // - テンプレート設定の確認
   ```

---

## 🧪 テスト計画

### Phase3単体テスト

**前提条件**:
1. n8nワークフローをアクティブ化
2. VOICEVOX API が稼働中 (`$env.VOICEVOX_URL` 設定済み)
3. Notion Database ID が正しく設定されている

**テストケース1: 正常系 (音声生成あり)**

```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase3-audio \
  -H "Content-Type: application/json" \
  -d '{
    "body": {
      "articleId": "test-article-001",
      "notionPageId": "29c68d5c-2986-8133-a61e-c1d7fa737aa0",
      "scriptUrl": "https://storage.example.com/script_test-article-001.json",
      "needsNarration": true
    }
  }'
```

**期待結果**:
- ✅ VOICEVOX APIが呼び出される
- ✅ 音声ファイルURLが生成される
- ✅ 字幕ファイルURLが生成される
- ✅ Notion APIが正常にPATCHリクエストを送信
- ✅ Notionページに Voice File URL, Subtitle File URL, Status=AudioReady が設定される
- ✅ Webhook レスポンスが返る

**テストケース2: スキップ系 (音声生成なし)**

```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase3-audio \
  -H "Content-Type: application/json" \
  -d '{
    "body": {
      "articleId": "test-article-002",
      "notionPageId": "29c68d5c-2986-8133-a61e-c1d7fa737aa0",
      "needsNarration": false
    }
  }'
```

**期待結果**:
- ✅ 音声必要性判定でスキップ
- ✅ VOICEVOX APIが呼び出されない
- ✅ Webhook レスポンスが即座に返る

**テストケース3: エラー系 (必須パラメータ欠落)**

```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase3-audio \
  -H "Content-Type: application/json" \
  -d '{
    "body": {
      "articleId": "test-article-003"
    }
  }'
```

**期待結果**:
- ❌ "notionPageId is required" エラーが返る
- ✅ エラーが適切にハンドリングされる

---

## 📝 検証チェックリスト

### 構造的検証 ✅

- [x] Webhook トリガーが正しく設定されている
- [x] すべてのノードが正しく接続されている
- [x] `.first()` 構文が使用されている
- [x] 2-nodeパターンが適用されている
- [x] Notion-Versionヘッダーが設定されている

### 実行時検証 ⏳

- [ ] n8nワークフローがアクティブ化可能
- [ ] Webhook URLが正常に登録される
- [ ] VOICEVOX APIとの連携が動作する
- [ ] Notion API更新が成功する
- [ ] エラーハンドリングが正常に機能する

### 統合検証 ⏳

- [ ] Phase2からの連携動作 (Phase2 → Phase3 Webhook呼び出し)
- [ ] Phase4への連携動作 (Phase3完了 → Phase4トリガー)
- [ ] 外部ストレージ統合後の動作確認

---

## 🚀 次のステップ

### 即時対応

1. **Phase3をアクティブ化してテスト実行**
   ```bash
   # n8n UIでワークフローをアクティブ化
   # 上記のテストケース1を実行
   ```

2. **実行結果の確認**
   - n8n実行ログの確認
   - Notionページの更新確認
   - エラーがあれば修正

### 段階的移行継続

3. **Phase4の移行** (Phase3テスト完了後)
   - Google Sheets → Webhook
   - Google Sheets Update → Notion API PATCH

4. **Phase5の移行** (Phase4テスト完了後)
   - Google Sheets → Webhook
   - Google Sheets Update → Notion API PATCH

---

## 📚 参考ドキュメント

- Phase1ナレッジ: `/docs/knowledge/wf7-phase1-lessons-learned.md`
- Phase2-5修正レポート: `/workflows/wf7-video-renderer/wf7-phase2-5-fixes.md`
- n8nナレッジベース: `/docs/knowledge/n8n-workflow-construction-knowledge.md`

---

**移行完了日**: 2025-10-30
**最終更新**: 2025-10-30 21:31 UTC
**ステータス**: ✅ 構造的移行完了、⏳ 実行テスト待機
