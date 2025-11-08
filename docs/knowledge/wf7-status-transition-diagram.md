# WF7 ステータス遷移図

## 概要

WF7 SNS動画自動生成パイプラインの全Phase（Phase1-5）におけるステータス遷移の完全定義。

**作成日**: 2025-11-08
**対象ワークフロー**: WF7 Phase1-5
**Notion DB**: `29b68d5c-2986-817f-b4e6-f84cf75ea9ed` (WF7 Videos DB)

---

## ステータス一覧

### 正常系ステータス

| ステータス | 意味 | 設定タイミング | 次の遷移 |
|-----------|------|---------------|---------|
| `Created` | Notionページ作成済み | Phase1開始時（ページ作成直後） | `ScriptReady` or `Failed` |
| `ScriptReady` | Script JSON生成完了 | Phase1完了時 | `AssetsReady` or `Failed` |
| `AssetsReady` | 素材取得完了 | Phase2完了時 | `VoiceReady` or `RenderReady` or `Failed` |
| `VoiceReady` | 音声・字幕生成完了 | Phase3完了時 | `RenderReady` or `Failed` |
| `RenderReady` | レンダリング準備完了 | Phase3完了 or Phase3スキップ時 | `Rendering` or `Failed` |
| `Rendering` | レンダリング実行中 | Phase4開始時 | `Completed` or `Failed` |
| `Completed` | 全Phase完了 | Phase5完了時 | - (終了状態) |

### エラー系ステータス

| ステータス | 意味 | 設定タイミング | Error Messageプロパティ |
|-----------|------|---------------|----------------------|
| `Failed` | Phase実行失敗 | 任意のPhaseでエラー発生時 | **必須**: エラー詳細を記録 |

---

## ステータス遷移フローチャート

### 正常フロー（Phase3実行）

```
[Phase1開始]
    ↓
Created
    ↓ (Phase1: Script JSON生成)
ScriptReady
    ↓ (Phase2: 素材取得)
AssetsReady
    ↓ (Phase3: 音声・字幕生成)
VoiceReady
    ↓ (Phase3完了)
RenderReady
    ↓ (Phase4: 動画レンダリング)
Rendering
    ↓ (Phase5: メタデータ登録)
Completed
```

### Phase3スキップフロー

```
[Phase1開始]
    ↓
Created
    ↓ (Phase1: Script JSON生成)
ScriptReady
    ↓ (Phase2: 素材取得)
AssetsReady
    ↓ (Phase3スキップ判定)
    ├─ 音声なし → RenderReady (直接遷移)
    └─ 音声あり → VoiceReady → RenderReady
```

### エラーハンドリングフロー

```
任意のPhase実行中
    ↓ (エラー発生)
Failed
    ├─ Error Message: エラー詳細を記録
    └─ 終了状態（手動リトライ or 調査が必要）
```

---

## Phase別ステータス更新仕様

### Phase1: 台本生成

**ワークフローID**: `not-implemented-yet`
**トリガー**: Webhook (手動実行)

#### ステータス更新ポイント

**1. Notionページ作成直後**
```javascript
// Notionページ作成ノード
{
  properties: {
    "Status": { select: { name: "Created" } },
    "Error Message": { rich_text: [] }  // 初期化
  }
}
```

**2. Script JSON生成成功時**
```javascript
// Notionページ更新ノード（Phase1完了）
{
  properties: {
    "Status": { select: { name: "ScriptReady" } },
    "Script JSON": { rich_text: [{ text: { content: JSON.stringify(scriptData) } }] },
    "Error Message": { rich_text: [] }  // クリア
  }
}
```

**3. エラー発生時**
```javascript
// エラーハンドラーノード
{
  properties: {
    "Status": { select: { name: "Failed" } },
    "Error Message": {
      rich_text: [{
        text: {
          content: `Phase1 Error: ${error.message}\nStack: ${error.stack}\nTimestamp: ${new Date().toISOString()}`
        }
      }]
    }
  }
}
```

---

### Phase2: 素材取得

**ワークフローID**: `not-implemented-yet`
**トリガー**: Webhook (Phase1から呼び出し)

#### ステータス更新ポイント

**1. Assets JSON生成成功時**
```javascript
// Notionページ更新ノード（Phase2完了）
{
  properties: {
    "Status": { select: { name: "AssetsReady" } },
    "Assets JSON": { rich_text: [{ text: { content: JSON.stringify(assetsData) } }] },
    "Error Message": { rich_text: [] }
  }
}
```

**2. エラー発生時**
```javascript
// エラーハンドラーノード
{
  properties: {
    "Status": { select: { name: "Failed" } },
    "Error Message": {
      rich_text: [{
        text: {
          content: `Phase2 Error: ${error.message}\nFailed Asset: ${failedAssetTag}\nTimestamp: ${new Date().toISOString()}`
        }
      }]
    }
  }
}
```

---

### Phase3: 音声・字幕生成（オプション）

**ワークフローID**: `4Oo5LL3KMKVn8gUJ`
**トリガー**: Webhook (Phase2から呼び出し)

#### ステータス更新ポイント

**1. 音声・字幕生成成功時**
```javascript
// Notionページ更新ノード（Phase3完了）
{
  properties: {
    "Status": { select: { name: "VoiceReady" } },
    "Voice URL": { url: voiceWebhookUrl },
    "Subtitle URL": { url: subtitleWebhookUrl },
    "Error Message": { rich_text: [] }
  }
}
```

**2. Phase3スキップ時**
```javascript
// Phase2完了時の条件分岐
if (skipVoice) {
  // Phase3をスキップしてRenderReadyに直接遷移
  {
    properties: {
      "Status": { select: { name: "RenderReady" } },
      "Voice URL": { url: null },
      "Subtitle URL": { url: null },
      "Error Message": { rich_text: [] }
    }
  }
}
```

**3. エラー発生時**
```javascript
// エラーハンドラーノード
{
  properties: {
    "Status": { select: { name: "Failed" } },
    "Error Message": {
      rich_text: [{
        text: {
          content: `Phase3 Error: ${error.message}\nNarration Length: ${narrationText.length}\nTimestamp: ${new Date().toISOString()}`
        }
      }]
    }
  }
}
```

**4. Phase3完了後のRenderReady遷移**
```javascript
// Phase3最終ノード（Phase4呼び出し直前）
{
  properties: {
    "Status": { select: { name: "RenderReady" } }
  }
}
```

---

### Phase4: 動画レンダリング

**ワークフローID**: `not-implemented-yet`
**トリガー**: Webhook (Phase3から呼び出し or Phase2から直接)

#### ステータス更新ポイント

**1. レンダリング開始時**
```javascript
// Notionページ更新ノード（Phase4開始）
{
  properties: {
    "Status": { select: { name: "Rendering" } },
    "Render Job ID": { rich_text: [{ text: { content: renderJobId } }] },
    "Error Message": { rich_text: [] }
  }
}
```

**2. レンダリング完了時**
```javascript
// Notionページ更新ノード（Phase4完了）
{
  properties: {
    "Status": { select: { name: "Completed" } },  // Phase5がない場合
    "Video URL": { url: videoUrl },
    "Render Duration": { number: renderDuration },
    "Error Message": { rich_text: [] }
  }
}
```

**3. エラー発生時**
```javascript
// エラーハンドラーノード
{
  properties: {
    "Status": { select: { name: "Failed" } },
    "Error Message": {
      rich_text: [{
        text: {
          content: `Phase4 Error: ${error.message}\nRender Job ID: ${renderJobId}\nFAL Status: ${falStatus}\nTimestamp: ${new Date().toISOString()}`
        }
      }]
    }
  }
}
```

---

### Phase5: メタデータ登録（将来実装）

**ワークフローID**: `not-implemented-yet`
**トリガー**: Webhook (Phase4から呼び出し)

#### ステータス更新ポイント

**1. メタデータ登録成功時**
```javascript
// Notionページ更新ノード（Phase5完了）
{
  properties: {
    "Status": { select: { name: "Completed" } },
    "Published At": { date: { start: new Date().toISOString() } },
    "Error Message": { rich_text: [] }
  }
}
```

**2. エラー発生時**
```javascript
// エラーハンドラーノード
{
  properties: {
    "Status": { select: { name: "Failed" } },
    "Error Message": {
      rich_text: [{
        text: {
          content: `Phase5 Error: ${error.message}\nMetadata: ${JSON.stringify(metadata)}\nTimestamp: ${new Date().toISOString()}`
        }
      }]
    }
  }
}
```

---

## エラーメッセージフォーマット仕様

### 基本フォーマット

```
Phase[N] Error: [エラーメッセージ]
[追加コンテキスト情報]
Timestamp: [ISO 8601形式]
```

### Phase別推奨コンテキスト情報

**Phase1**:
- `Article ID`: 元記事ID
- `GPT-4 Prompt Length`: プロンプト文字数
- `GPT-4 Response`: GPT-4のレスポンス（エラーの場合）

**Phase2**:
- `Failed Asset Tag`: 失敗したアセットタグ
- `Total Assets`: 全アセット数
- `Successful Assets`: 成功したアセット数
- `Pexels API Status`: Pexels APIのステータスコード

**Phase3**:
- `Narration Length`: ナレーションテキストの文字数
- `Script Segments Count`: Script JSONのセグメント数
- `OpenAI API Status`: OpenAI APIのステータスコード

**Phase4**:
- `Render Job ID`: FALレンダリングジョブID
- `FAL Status`: FALステータス
- `Render Duration`: レンダリング時間（秒）
- `Video Duration`: 生成動画の長さ（秒）

**Phase5**:
- `Metadata`: 登録しようとしたメタデータ
- `Target Platform`: 登録先プラットフォーム

---

## ステータス監視とデバッグ

### Notion Status Selectプロパティ設定

WF7 Videos DBの`Status`プロパティには以下のオプションが必要：

```json
{
  "name": "Status",
  "type": "select",
  "select": {
    "options": [
      { "name": "Created", "color": "gray" },
      { "name": "ScriptReady", "color": "blue" },
      { "name": "AssetsReady", "color": "purple" },
      { "name": "VoiceReady", "color": "green" },
      { "name": "RenderReady", "color": "yellow" },
      { "name": "Rendering", "color": "orange" },
      { "name": "Completed", "color": "green" },
      { "name": "Failed", "color": "red" }
    ]
  }
}
```

### ステータス別フィルタークエリ

**進行中のジョブ**:
```
Status is not Completed AND Status is not Failed
```

**エラー調査が必要**:
```
Status is Failed AND Error Message is not empty
```

**Phase3スキップ済み**:
```
Status is RenderReady AND Voice URL is empty
```

**Phase4待ち**:
```
Status is RenderReady OR Status is VoiceReady
```

---

## Phase間のWebhook連携

### Phase1 → Phase2

**Phase1最終ノード（Phase2 Webhook呼び出し）**:
```javascript
// HTTP Requestノード
{
  method: "POST",
  url: "https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase2",
  body: {
    articleId: articleId,
    notionPageId: notionPageId,
    assetTags: scriptData.segments.map(s => s.assetTag)
  }
}
```

**Phase1失敗時**:
- Phase2を呼び出さない
- Statusは`Failed`のまま
- Error Messageに詳細を記録

### Phase2 → Phase3 (条件付き)

**Phase2最終ノード（Phase3 Webhook呼び出し判定）**:
```javascript
// Function ノード
const skipVoice = false; // 条件判定ロジック

if (skipVoice) {
  // Phase3をスキップしてStatusをRenderReadyに更新
  // Phase4を直接呼び出し
  return {
    json: {
      skipPhase3: true,
      callPhase4: true,
      notionPageId: notionPageId
    }
  };
} else {
  // Phase3を呼び出し
  return {
    json: {
      skipPhase3: false,
      callPhase3: true,
      articleId: articleId,
      notionPageId: notionPageId
    }
  };
}
```

### Phase3 → Phase4

**Phase3最終ノード（Phase4 Webhook呼び出し）**:
```javascript
// HTTP Requestノード
{
  method: "POST",
  url: "https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4",
  body: {
    articleId: articleId,
    notionPageId: notionPageId,
    voiceUrl: voiceWebhookUrl,
    subtitleUrl: subtitleWebhookUrl
  }
}
```

---

## トラブルシューティングガイド

### ステータスが進まない場合

**1. Created → ScriptReady にならない**
- Phase1ログ確認: `/docs/knowledge/wf7-phase1-troubleshooting.md`
- GPT-4 APIキー確認
- Notion DB書き込み権限確認

**2. ScriptReady → AssetsReady にならない**
- Phase2ログ確認: `/docs/knowledge/wf7-phase2-troubleshooting.md`
- Pexels APIキー確認
- Google Drive認証確認

**3. AssetsReady → VoiceReady にならない**
- Phase3ログ確認: n8nの実行履歴
- OpenAI APIキー確認
- Script JSON構造確認（segmentsにnarrationが存在するか）

**4. VoiceReady/RenderReady → Rendering にならない**
- Phase4実装状況確認
- FAL API認証確認

### Error Messageから原因を特定

**エラーメッセージパターン別対処法**:

```
Phase1 Error: GPT-4 API timeout
→ GPT-4クォータ確認、プロンプト長確認

Phase2 Error: Pexels API rate limit
→ API使用量確認、リトライロジック追加検討

Phase3 Error: Script JSON property not found
→ Phase1が正常完了したか確認、Script JSON構造確認

Phase4 Error: FAL rendering failed
→ Assets JSONのURL検証、FAL APIステータス確認
```

---

## 今後の拡張予定

### ステータスの追加検討

**Phase4-5実装時に追加が必要なステータス**:
- `RenderQueued`: レンダリングキュー待ち
- `Publishing`: SNS投稿中
- `Published`: SNS投稿完了

### リトライロジック

**Failed状態からの自動リトライ**:
- 一定時間後に同じPhaseを自動再実行
- リトライ回数の上限設定（例: 3回）
- リトライ履歴の記録

---

## 参考資料

- **WF7 Phase1-3 テスト問題レポート**: `/docs/testing/wf7-phase1-3-test-issues-report.md`
- **WF6 テスト結果**: `/docs/testing/wf6-test-result-2025-11-08.md`
- **Phase4 トラブルシューティング**: `/docs/knowledge/wf7-phase4-troubleshooting-guide.md`
- **n8n Workflow Construction Knowledge**: `/docs/knowledge/n8n-workflow-construction-knowledge.md`
