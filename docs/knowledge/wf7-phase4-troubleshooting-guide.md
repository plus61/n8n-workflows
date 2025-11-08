# WF7 Phase3 & Phase4: URL生成トラブルシューティングガイド

**作成日**: 2025-11-04
**対象**: WF7 Phase3 音声・字幕生成 (4Oo5LL3KMKVn8gUJ) & Phase4 動画レンダリング (xvlnFeJJwHKMHBwK)
**環境**: Railway (n8n-python-production-344b.up.railway.app)

---

## 概要

このドキュメントは、WF7 Phase3とPhase4ワークフローで発生したURL生成問題、タイムアウト障害、根本原因、解決策をまとめたナレッジベースです。

**Phase3ワークフロー構成**:
- **Workflow ID**: 4Oo5LL3KMKVn8gUJ
- **Webhook**: `POST /webhook/wf7-phase3-audio`
- **入力**: `{"articleId": "<id>", "notionPageId": "<page-id>", "needsNarration": true, "scriptUrl": "<url>"}`
- **処理フロー**: 音声必要性判定 → ナレーション抽出 → OpenAI TTS音声生成 → SRT字幕生成 → Notion更新
- **主要ノード数**: 12ノード

**Phase4ワークフロー構成**:
- **Workflow ID**: xvlnFeJJwHKMHBwK
- **Webhook**: `POST /webhook/wf7-phase4-render`
- **入力**: `{"notionPageId": "<page-id>"}`
- **処理フロー**: Notionデータ取得 → Google Drive画像ダウンロード → FFmpeg動画レンダリング → Notion更新
- **主要ノード数**: 14ノード

---

## 問題1: Execution 101 タイムアウト障害（7時間51分）

### 症状
```
Execution ID: 101
Status: Error
Duration: 7h51m
Error: Timeout after 28800 seconds
```

### 根本原因

**「動画レンダリング実行」ノード**（ID: 76598e25-bde1-4f96-970f-03d7e67630ad）のコマンドが複数行に渡っていた。

```javascript
// ❌ 問題のあるコマンド（改行あり）
command: `python -c "from PIL import Image; colors=['blue','green','red','yellow','purple','orange','pink','cyan','magenta','brown']; [Image.new('RGB', (1080, 1920), color=colors[i]).save(f'/tmp/integration_asset_{i}.jpg') for i in range(10)]"
echo '{{ $json.scriptJson }}' > {{ $json.scriptPath }}
echo '{{ $json.assetsJson }}' > {{ $json.assetsPath }}
python /app/render_video_ffmpeg.py --script {{ $json.scriptPath }} --assets {{ $json.assetsPath }} --out {{ $json.outputPath }}`
```

**n8nの制約**: Execute Commandノードは複数行コマンドを改行区切りで解釈せず、最初の行のみ実行される。

### 解決策

**コマンドを1行に統合** - `&&`で連結:

```javascript
// ✅ 修正後のコマンド（1行）
command: `python -c "from PIL import Image; colors=['blue','green','red','yellow','purple','orange','pink','cyan','magenta','brown']; [Image.new('RGB', (1080, 1920), color=colors[i]).save(f'/tmp/integration_asset_{i}.jpg') for i in range(10)]" && echo '{{ $json.scriptJson }}' > {{ $json.scriptPath }} && echo '{{ $json.assetsJson }}' > {{ $json.assetsPath }} && python /app/render_video_ffmpeg.py --script {{ $json.scriptPath }} --assets {{ $json.assetsPath }} --out {{ $json.outputPath }}`
```

### 適用方法

```javascript
// n8n MCP APIを使用
mcp__n8n-mcp__n8n_update_full_workflow({
  id: "xvlnFeJJwHKMHBwK",
  nodes: [...],  // 全ノード配列
  connections: {...}  // 全接続オブジェクト
})
```

### 検証結果

```
✅ Execution 146: 成功
Duration: 19秒
Status: Success
Video URL: 正常生成
```

**改善効果**: 7h51m → 19s（約1500倍の高速化）

---

## 問題2: Notion URL形式不正（Railway インスタンス誤り）

### 症状

Notionに保存されるURLが運用中のRailwayインスタンスと異なる:

```
期待: https://n8n-python-production-344b.up.railway.app/webhook/...
実際: https://n8n-python-production-344b.up.railway.app/webhook/...
```

### 根本原因

**「動画メタデータ抽出」ノード**（ID: f5dc47f2-a343-4d1f-ba29-d83b6c79abe5）のフォールバックURLが古いインスタンスを指定:

```javascript
// ❌ 問題のあるコード
const baseUrl = $env.N8N_HOST || 'https://n8n-python-production-344b.up.railway.app';
```

**背景**: 環境変数`$env.N8N_HOST`が未設定の場合、誤ったフォールバックURLが使用される。

### 解決策

**フォールバックURLを正しいインスタンスに変更**:

```javascript
// ✅ 修正後のコード
const baseUrl = $env.N8N_HOST || 'https://n8n-python-production-344b.up.railway.app';
```

### 検証結果

```
✅ Notion保存URL（修正後）:
Video URL: https://n8n-python-production-344b.up.railway.app/webhook/wf7-files-video?articleId=...
Thumbnail URL: https://n8n-python-production-344b.up.railway.app/webhook/wf7-files-thumb?articleId=...
```

---

## 問題3: Notion URLからプロトコル欠落

### 症状

問題2の修正後、新たにプロトコルが欠落する問題が発見:

```
期待: https://n8n-python-production-344b.up.railway.app/webhook/...
実際: n8n-python-production-344b.up.railway.app/webhook/...
```

### 根本原因

`$env.N8N_HOST`がプロトコルなしで設定されている可能性に対応していない:

```javascript
// ❌ プロトコル検証なし
const baseUrl = $env.N8N_HOST || 'https://n8n-python-production-344b.up.railway.app';
const videoUrl = `${baseUrl}/webhook/...`;  // baseUrlにhttps://がないと不正なURL
```

### 解決策

**プロトコル存在チェックを追加**:

```javascript
// ✅ 修正後のコード
const articleId = $('レンダリングリクエスト構築').first().json.articleId;
const notionPageId = $('レンダリングリクエスト構築').first().json.notionPageId;
const baseUrl = $env.N8N_HOST || 'https://n8n-python-production-344b.up.railway.app';

// baseUrlがhttps://で始まっていなければ追加（環境変数にプロトコルがない場合に対応）
const fullBaseUrl = baseUrl.startsWith('http') ? baseUrl : `https://${baseUrl}`;

// n8n File Server経由で配信する想定（クエリパラメータ方式）
const videoUrl = `${fullBaseUrl}/webhook/wf7-files-video?articleId=${articleId}`;
const thumbUrl = `${fullBaseUrl}/webhook/wf7-files-thumb?articleId=${articleId}`;

return {
  json: {
    articleId,
    notionPageId,
    videoUrl,
    thumbUrl,
    jobId: `video-${articleId}-${Date.now()}`
  }
};
```

### 検証結果

```
✅ Notion保存URL（最終修正後）:
Video URL: https://n8n-python-production-344b.up.railway.app/webhook/wf7-files-video?articleId=integration-test-001
Thumbnail URL: https://n8n-python-production-344b.up.railway.app/webhook/wf7-files-thumb?articleId=integration-test-001

Last Updated: 2025-11-04 02:04:00
Status: Rendered
```

---

## 問題4: Phase3 URL生成問題（Phase4と同様のパターン）

### 症状

Phase4と同じURL生成問題がPhase3ワークフローでも発生:

**症状1: 間違ったRailwayインスタンス**
```
期待: https://n8n-python-production-344b.up.railway.app/webhook/wf7-files-audio?...
実際: https://n8n-python-production-344b.up.railway.app/webhook/wf7-files-audio?...
```

**症状2: プロトコル欠落**
```
期待: https://n8n-python-production-344b.up.railway.app/webhook/...
実際: n8n-python-production-344b.up.railway.app/webhook/...
```

### 根本原因

**2つのノードで同じ問題が発生**:

1. **「音声メタデータ保存」ノード** (ID: 08a4623b-56e6-4cad-8b3e-c45057d8876e)
2. **「字幕メタデータ保存」ノード** (ID: 32344475-3f6e-44e5-b449-136adf3f609a)

両ノードのコード:
```javascript
// ❌ 問題のあるコード
const baseUrl = $env.N8N_HOST || 'https://n8n-python-production-344b.up.railway.app';  // 誤ったインスタンス
const voiceFileUrl = `${baseUrl}/webhook/wf7-files-audio?articleId=${articleId}`;  // プロトコルチェックなし
```

### 解決策

**Phase4と同じパターンを適用**:

**音声メタデータ保存ノード**:
```javascript
// ✅ 修正後のコード
const articleId = $('ナレーション抽出').first().json.articleId;
const notionPageId = $('ナレーション抽出').first().json.notionPageId;
const baseUrl = $env.N8N_HOST || 'https://n8n-python-production-344b.up.railway.app';  // 正しいインスタンス
const fullBaseUrl = baseUrl.startsWith('http') ? baseUrl : `https://${baseUrl}`;  // プロトコルチェック

const voiceFileUrl = `${fullBaseUrl}/webhook/wf7-files-audio?articleId=${articleId}`;

return {
  json: {
    articleId,
    notionPageId,
    voiceFileUrl,
    voiceFileName: `voice_${articleId}.wav`
  }
};
```

**字幕メタデータ保存ノード**:
```javascript
// ✅ 修正後のコード
const prevData = $input.first().json;
const articleId = $('ナレーション抽出').first().json.articleId;
const baseUrl = $env.N8N_HOST || 'https://n8n-python-production-344b.up.railway.app';  // 正しいインスタンス
const fullBaseUrl = baseUrl.startsWith('http') ? baseUrl : `https://${baseUrl}`;  // プロトコルチェック

const subtitleFileUrl = `${fullBaseUrl}/webhook/wf7-files-subtitle?articleId=${articleId}`;

return {
  json: {
    ...prevData,
    subtitleFileUrl,
    subtitleFileName: `subtitle_${articleId}.srt`
  }
};
```

### 適用方法

```javascript
// n8n MCP APIを使用
// 1. ワークフロー取得
const workflow = await mcp__n8n-mcp__n8n_get_workflow({ id: "4Oo5LL3KMKVn8gUJ" });

// 2. 対象ノードを修正
const audioMetaNode = workflow.nodes.find(n => n.id === "08a4623b-56e6-4cad-8b3e-c45057d8876e");
const subtitleMetaNode = workflow.nodes.find(n => n.id === "32344475-3f6e-44e5-b449-136adf3f609a");

audioMetaNode.parameters.jsCode = "...";  // 上記の修正コード
subtitleMetaNode.parameters.jsCode = "...";  // 上記の修正コード

// 3. ワークフロー全体を更新
await mcp__n8n-mcp__n8n_update_full_workflow({
  id: "4Oo5LL3KMKVn8gUJ",
  name: workflow.name,
  nodes: workflow.nodes,
  connections: workflow.connections
});
```

### ワークフロー再起動（キャッシュクリア）

修正後、n8nワークフローキャッシュをクリアするため再起動:

```javascript
// ワークフローを更新（自動的に再起動される）
// Version 4 → 6 → 8 (キャッシュクリア成功)
```

### 検証結果

**Phase3テスト実行**:
```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase3-audio \
  -H "Content-Type: application/json" \
  -d '{"articleId": "integration-test-001", "notionPageId": "2a068d5c-2986-81a3-ab0c-ff0bc1e4ebb9", "needsNarration": true, "scriptUrl": "https://example.com/script.json"}' \
  --max-time 60
```

**レスポンス（成功）**:
```json
{
  "status": "success",
  "message": "WF7 Phase3 completed",
  "articleId": "integration-test-001",
  "notionPageId": "2a068d5c-2986-81a3-ab0c-ff0bc1e4ebb9",
  "voiceFileUrl": "https://n8n-python-production-344b.up.railway.app/webhook/wf7-files-audio?articleId=integration-test-001",
  "subtitleFileUrl": "https://n8n-python-production-344b.up.railway.app/webhook/wf7-files-subtitle?articleId=integration-test-001"
}
```

**Notion保存URL（検証）**:
```
✅ Voice URL: https://n8n-python-production-344b.up.railway.app/webhook/wf7-files-audio?articleId=integration-test-001
✅ Subtitle URL: https://n8n-python-production-344b.up.railway.app/webhook/wf7-files-subtitle?articleId=integration-test-001
✅ Status: VoiceReady
✅ Last Updated: 2025-11-04 02:31:00
✅ 実行時間: 約4秒（正常範囲）
```

**Phase3とPhase4統合検証**:

Notion Page 2a068d5c-2986-81a3-ab0c-ff0bc1e4ebb9 の最終状態:
```
Video URL:    https://n8n-python-production-344b.up.railway.app/webhook/wf7-files-video?articleId=integration-test-001 ✅
Thumbnail URL: https://n8n-python-production-344b.up.railway.app/webhook/wf7-files-thumb?articleId=integration-test-001 ✅
Voice URL:    https://n8n-python-production-344b.up.railway.app/webhook/wf7-files-audio?articleId=integration-test-001 ✅
Subtitle URL: https://n8n-python-production-344b.up.railway.app/webhook/wf7-files-subtitle?articleId=integration-test-001 ✅
Status: Rendered
Last Updated: 2025-11-04 02:35:00
```

**結論**: すべてのURL（Phase3とPhase4）が正しいRailwayインスタンスとhttps://プロトコルを使用。

---

## n8n MCP API使用パターン

### n8n_update_partial_workflow の検証エラー

**問題**:
```json
{
  "success": false,
  "error": "Invalid request: request/body must NOT have additional properties",
  "code": "VALIDATION_ERROR"
}
```

**原因**: パラメータスキーマとの不一致または未対応のフィールド。

**対策**: **n8n_update_full_workflow を使用**

```javascript
// ✅ 推奨パターン
// 1. 現在のワークフロー取得
const workflow = await mcp__n8n-mcp__n8n_get_workflow({ id: "xvlnFeJJwHKMHBwK" });

// 2. 必要な修正を適用
workflow.nodes.find(n => n.id === "target-node-id").parameters.jsCode = "...";

// 3. 全体を更新
await mcp__n8n-mcp__n8n_update_full_workflow({
  id: "xvlnFeJJwHKMHBwK",
  name: workflow.name,
  nodes: workflow.nodes,
  connections: workflow.connections
});
```

**注意点**:
- `n8n_update_full_workflow`は完全な`nodes`配列と`connections`オブジェクトを要求
- 部分更新より確実だが、全体取得→修正→全体更新のステップが必要

---

## ベストプラクティス

### 1. Execute Commandノードのコマンド構築

**DO**:
```javascript
// ✅ 1行コマンド（&&連結）
command: `cmd1 && cmd2 && cmd3`
```

**DON'T**:
```javascript
// ❌ 複数行（改行）
command: `cmd1
cmd2
cmd3`
```

### 2. 環境変数フォールバック設計

**DO**:
```javascript
// ✅ プロトコルチェックあり
const baseUrl = $env.N8N_HOST || 'https://default-instance.railway.app';
const fullBaseUrl = baseUrl.startsWith('http') ? baseUrl : `https://${baseUrl}`;
```

**DON'T**:
```javascript
// ❌ プロトコルチェックなし、古いフォールバック
const baseUrl = $env.N8N_HOST || 'https://old-instance.railway.app';
```

### 3. Railway デプロイメント後の確認

**チェックリスト**:
1. ✅ ワークフロー有効化状態確認
2. ✅ Webhook URLアクセス確認（200 OK）
3. ✅ テスト実行（統合テストページ使用）
4. ✅ Notion保存データ形式確認
5. ✅ 実行時間が妥当か確認（Phase4: 15-30秒が正常）

### 4. URL構築パターン

**DO**:
```javascript
// ✅ クエリパラメータ方式（Railwayと互換性高い）
const videoUrl = `${baseUrl}/webhook/wf7-files-video?articleId=${articleId}`;
```

**DON'T**:
```javascript
// ❌ パスパラメータ（:id）はRailwayで動作しない
path: "wf7-files-video/:articleId"  // Railway非対応
```

---

## トラブルシューティングフローチャート

```
[ワークフロー失敗]
    |
    ├─ タイムアウト？
    |   └─ Yes → Execute Commandノードのコマンドを1行化
    |
    ├─ Notion URLが不正？
    |   ├─ 間違ったホスト → baseUrlのフォールバック修正
    |   └─ プロトコル欠落 → fullBaseUrlでプロトコルチェック追加
    |
    └─ n8n MCP API エラー？
        └─ n8n_update_partial_workflow失敗 → n8n_update_full_workflowに切り替え
```

---

## 関連ドキュメント

- [WF7 Phase1 Lessons Learned](./wf7-phase1-lessons-learned.md)
- [WF7 Google to Notion Migration Lessons](./wf7-google-to-notion-migration-lessons.md)
- [WF7 Webhook Registration Pattern](./wf7-webhook-registration-pattern.md)
- [n8n Workflow Construction Knowledge](./n8n-workflow-construction-knowledge.md)
- [render_video_ffmpeg.py](/Users/yuichiroooosuger/Desktop/n8n-workflows/workflows/wf7-video-renderer/render_video_ffmpeg.py)

---

## 問題5: FAL API Submit to FAL ノードのタイムアウト設定不備

### 症状

**Execution ID: 734** でエラー発生:
```
Status: Error
Duration: 1.5秒
Error: "The connection was aborted, perhaps the server is offline"
Node: Submit to FAL
Timeout: 300ms (実際の設定値)
```

**エラーログ**:
```json
{
  "error": "timeout of 300ms exceeded",
  "httpCode": "ECONNABORTED",
  "message": "The connection was aborted, perhaps the server is offline"
}
```

### 根本原因

**「Submit to FAL」ノード**（ID: f21d892c-8100-4b31-ba7c-9455a31e9cf5）のタイムアウト設定が正しく反映されていない可能性。

- **期待値**: 300000ms (300秒)
- **実際の動作**: 300ms (0.3秒) でタイムアウト

FAL APIへのリクエストは通常500ms以上かかるため、300msでは確実にタイムアウトする。

### 解決策

**ワークフロー全体を更新してタイムアウト設定を明示的に確認・修正**:

```javascript
// Submit to FAL ノードの設定
{
  "parameters": {
    "method": "POST",
    "url": "https://queue.fal.run/fal-ai/ffmpeg-api/compose",
    "options": {
      "timeout": 300000,  // 300秒（300000ミリ秒）
      "response": {
        "response": {
          "responseFormat": "json"
        }
      }
    }
  }
}
```

**他のFAL API呼び出しノードも同様に確認**:
- **Fetch Status** (ID: eb3a8689-faa9-4db4-9fb2-d26343a34827): `timeout: 300000`
- **Check Render Status** (ID: 512c653b-e527-4b6c-875a-13dbbb04b694): `timeout: 300000`
- **Get Image Result URL** (ID: 14d89d20-3adc-4438-b9e8-78fc0df9812e): `timeout: 300000`

### 適用方法

```javascript
// n8n MCP APIを使用してワークフロー全体を更新
mcp__n8n-mcp__n8n_update_full_workflow({
  id: "SDO8X6oR5W5y2s6A",
  name: "WF7 Phase4 - V2 Fixed",
  nodes: [...],  // 全ノード配列（タイムアウト設定を確認）
  connections: {...}  // 全接続オブジェクト
})
```

### 検証結果

**修正後（2025-11-08）**:
```
✅ ワークフロー更新成功
Version Counter: 71 → 73
Submit to FAL ノード: timeout: 300000 に設定確認
```

**期待される動作**:
- FAL APIへのリクエストが300秒以内に完了するまで待機
- タイムアウトエラーが発生しない

---

## 問題6: Wait for Processingノードがwebhook待機で停止（Execution 744）

### 症状

**Execution ID: 744** が27分経過しても`waiting`状態のまま進展がない:
```
Status: waiting
StartedAt: 2025-11-08T02:27:25.437Z
StoppedAt: 2025-11-08T02:27:27.733Z
Duration: 2296ms (約2.3秒)
Finished: false
```

**停止ノード**: "Wait for Processing" (ID: ec05e49c-5d59-40a3-8afa-4aab3501d143)

### 根本原因

**「Wait for Processing」ノード**がwebhook待機モードに設定されていた:
```javascript
// ❌ 問題のある設定
{
  "parameters": {
    "resume": "webhook",
    "limit": {
      "amount": 300  // 300分 = 5時間
    }
  },
  "webhookId": "video-render-wait"
}
```

**問題点**:
- FAL APIは非同期処理のため、webhookを呼び出す仕組みがない
- webhook待機モードでは、外部からwebhookを呼び出さない限り実行が進まない
- 実行が`waiting`状態で永続的に停止する

### 解決策

**Waitノードを時間ベース待機に変更**:
```javascript
// ✅ 修正後の設定
{
  "parameters": {
    "resume": "time",
    "waitTime": 5  // 5秒待機
  }
}
```

**ポーリングループの動作**:
1. `Fetch Status` → FAL APIステータス取得
2. `Wait for Processing` → 5秒待機（時間ベース）
3. `Check Render Status` → ステータス再確認
4. `Render Completed?` → 完了チェック
   - `COMPLETED` → 結果取得へ
   - 未完了 → `Retry Counter` → `Wait Before Retry` → ループバック

**「Wait Before Retry」ノードも同様に修正**:
```javascript
// ✅ 修正後の設定
{
  "parameters": {
    "resume": "time",
    "waitTime": 5  // 5秒待機
  }
}
```

### 適用方法

```javascript
// n8n MCP APIを使用してワークフロー全体を更新
mcp__n8n-mcp__n8n_update_full_workflow({
  id: "SDO8X6oR5W5y2s6A",
  name: "WF7 Phase4 - V2 Fixed",
  nodes: [...],  // Wait for Processingノードを時間ベースに変更
  connections: {...}  // 接続は変更なし
})
```

### 検証結果

**修正後（2025-11-08）**:
```
✅ ワークフロー更新成功
Version Counter: 73 → 75
Wait for Processing ノード: resume: "time", waitTime: 5 に変更
Wait Before Retry ノード: resume: "time", waitTime: 5 に変更
```

**期待される動作**:
- 5秒ごとにFAL APIステータスをポーリング
- 完了まで自動的にループ継続
- 最大20回リトライ（合計100秒）後にタイムアウト
- `waiting`状態で停止しない

### ベストプラクティス

**非同期APIポーリングパターン**:
- ✅ **時間ベース待機**: `resume: "time"`, `waitTime: 5`
- ❌ **webhook待機**: `resume: "webhook"`（外部からの呼び出しが必要）

**FAL APIのような非同期処理**:
- webhook待機は使用しない
- 時間ベースのポーリングループを実装
- リトライ回数とタイムアウトを適切に設定

---

## 問題7: Check Retry Limitノードの接続が逆（Execution 756）

### 症状

**Execution ID: 756** で`Get Image Result URL`に到達しない:
```
Status: success
Duration: 8.2秒
問題: retry_count: 1でretry_count < 20がTrueなのに、Timeout Error Responseに到達
```

**実行フロー**:
1. `Render Completed?` → `status: "IN_PROGRESS"` → Falseパス → `Retry Counter`
2. `Retry Counter` → `retry_count: 1`を設定
3. `Check Retry Limit` → `retry_count < 20`がTrueなのに、Falseパス（`Timeout Error Response`）に流れる
4. `Get Image Result URL`に到達しない

### 根本原因

**「Check Retry Limit」ノード**（ID: 9db6c6c7-f0d4-45ef-bfbb-6c18f337dab4）の接続が逆になっていた:

```javascript
// ❌ 問題のある接続
{
  "Check Retry Limit": {
    "main": [
      [
        { "node": "Timeout Error Response" }  // main[0] = Trueパス（間違い）
      ],
      [
        { "node": "Wait Before Retry" }  // main[1] = Falseパス（間違い）
      ]
    ]
  }
}
```

**n8nのIFノードの動作**:
- `main[0]` = Trueパス（条件が満たされた場合）
- `main[1]` = Falseパス（条件が満たされない場合）

**問題点**:
- `retry_count < 20`がTrueの場合、`main[0]`に流れるべき
- しかし、`main[0]`が`Timeout Error Response`に接続されていた
- そのため、リトライ可能な場合でもタイムアウトエラーが返されていた

### 解決策

**接続を正しい順序に修正**:

```javascript
// ✅ 修正後の接続
{
  "Check Retry Limit": {
    "main": [
      [
        { "node": "Wait Before Retry" }  // main[0] = Trueパス（retry_count < 20）
      ],
      [
        { "node": "Timeout Error Response" }  // main[1] = Falseパス（retry_count >= 20）
      ]
    ]
  }
}
```

**正しい動作**:
- `retry_count < 20`（True）→ `main[0]` → `Wait Before Retry` → リトライ継続
- `retry_count >= 20`（False）→ `main[1]` → `Timeout Error Response` → タイムアウト

### 適用方法

```javascript
// n8n MCP APIを使用してワークフロー全体を更新
mcp__n8n-mcp__n8n_update_full_workflow({
  id: "SDO8X6oR5W5y2s6A",
  name: "WF7 Phase4 - V2 Fixed",
  nodes: [...],  // 全ノード配列
  connections: {
    "Check Retry Limit": {
      "main": [
        [
          { "node": "Wait Before Retry", "type": "main", "index": 0 }
        ],
        [
          { "node": "Timeout Error Response", "type": "main", "index": 0 }
        ]
      ]
    }
  }
})
```

### 検証結果

**修正後（2025-11-08）**:
```
✅ ワークフロー更新成功
Version Counter: 77 → 79
Check Retry Limit ノード: 接続を修正
- main[0]（True）→ Wait Before Retry（リトライ継続）
- main[1]（False）→ Timeout Error Response（タイムアウト）
```

**期待される動作**:
- `retry_count < 20`の場合、`Wait Before Retry`に進み、リトライループを継続
- `retry_count >= 20`の場合、`Timeout Error Response`に進み、タイムアウトエラーを返す
- FAL APIのレンダリングが完了するまで、最大20回リトライ（合計100秒）を試行

### ベストプラクティス

**IFノードの接続確認**:
- ✅ **Trueパス（main[0]）**: 条件が満たされた場合の処理
- ✅ **Falseパス（main[1]）**: 条件が満たされない場合の処理
- ❌ **接続の逆転**: True/Falseパスが逆になっていると、ロジックエラーが発生

**リトライロジックの検証**:
- リトライカウンターの初期値を確認
- リトライ制限の条件を確認
- IFノードの接続が正しいか確認

---

## 問題8: Get Image Result URLノードのHTTPメソッドエラー（Execution 760）

### 症状

**Execution ID: 760** でエラー発生:
```
Status: Error
Duration: 8.9秒
Error: "405: Method Not Allowed"
Node: Get Image Result URL
```

**エラーログ**:
```json
{
  "error": "Method not allowed - please check you are using the right HTTP method",
  "httpCode": "405",
  "message": "Method not allowed - please check you are using the right HTTP method",
  "request": {
    "method": "GET",
    "uri": "https://queue.fal.run/fal-ai/ffmpeg-api/compose/requests/4f29d47c-8b37-4dc6-a609-27d588185f5d"
  }
}
```

### 根本原因

**「Get Image Result URL」ノード**（ID: 14d89d20-3adc-4438-b9e8-78fc0df9812e）の設定に問題がありました:

1. **URLが古い形式を使用**: `/compose/requests/`というパスが使われていた（エラーログより）
2. **`response_url`を直接使用していない**: `Submit to FAL`のレスポンスに含まれる`response_url`を使用すべき
3. **HTTPメソッドが明示されていない**: `method`パラメータが指定されていない

**FAL APIの正しい動作**:
- `Submit to FAL`のレスポンスに`response_url`が含まれる
- `response_url`は`https://queue.fal.run/fal-ai/ffmpeg-api/requests/{request_id}`の形式
- 結果を取得するには、`response_url`にGETリクエストを送る必要がある

### 解決策

**`Get Image Result URL`ノードを修正**:

```javascript
// ✅ 修正後の設定
{
  "parameters": {
    "method": "GET",
    "url": "={{ $json.response_url }}",
    "authentication": "genericCredentialType",
    "genericAuthType": "httpHeaderAuth",
    "sendHeaders": false,
    "sendBody": false,
    "options": {
      "timeout": 300000,
      "response": {
        "response": {
          "responseFormat": "json"
        }
      }
    }
  }
}
```

**重要な変更点**:
- `method`: `GET`を明示的に指定
- `url`: `response_url`を直接使用（`Submit to FAL`のレスポンスから取得）
- `sendHeaders`: `false`に設定（認証は`httpHeaderAuth`で自動的に処理される）
- `sendBody`: `false`に設定（GETリクエストでは不要）

### 適用方法

```javascript
// n8n MCP APIを使用してワークフロー全体を更新
mcp__n8n-mcp__n8n_update_full_workflow({
  id: "SDO8X6oR5W5y2s6A",
  name: "WF7 Phase4 - V2 Fixed",
  nodes: [...],  // Get Image Result URLノードを修正
  connections: {...}  // 接続は変更なし
})
```

### 検証結果

**修正後（2025-11-08）**:
```
✅ ワークフロー更新成功
Version Counter: 85 → 87
Get Image Result URL ノード: 
- method: GET を明示的に指定
- url: {{ $json.response_url }} を使用
- sendHeaders: false
- sendBody: false
```

**期待される動作**:
- `Submit to FAL`のレスポンスから`response_url`を取得
- `response_url`にGETリクエストを送信
- FAL APIから結果（`video_url`など）を正常に取得
- 405エラーが発生しない

### ベストプラクティス

**FAL API結果取得パターン**:
- ✅ **`response_url`を直接使用**: `Submit to FAL`のレスポンスに含まれる`response_url`を使用
- ✅ **GETメソッドを明示**: `method: "GET"`を明示的に指定
- ✅ **認証は自動処理**: `httpHeaderAuth`を使用し、`sendHeaders: false`で自動的に認証ヘッダーを追加
- ❌ **手動でURL構築**: `/compose/requests/{request_id}`のような手動URL構築は避ける

**FAL APIレスポンス構造**:
```json
{
  "status": "COMPLETED",
  "request_id": "uuid-here",
  "response_url": "https://queue.fal.run/fal-ai/ffmpeg-api/requests/uuid-here",
  "status_url": "https://queue.fal.run/fal-ai/ffmpeg-api/requests/uuid-here/status",
  "video_url": "https://fal.media/files/..."
}
```

---

## 問題9: Get Image Result URLノードでresponse_urlが取得できない問題

### 症状

**Execution ID: 766** などで、`Render Completed?`ノードが`COMPLETED`になっても`Get Image Result URL`に進めない、または`response_url`が未定義でエラーが発生する。

**エラーログ**:
```json
{
  "error": "response_url is undefined",
  "node": "Get Image Result URL"
}
```

### 根本原因

**「Get Image Result URL」ノード**（ID: 14d89d20-3adc-4438-b9e8-78fc0df9812e）が`response_url`を直接参照していたが、`Check Render Status`のレスポンスに`response_url`が含まれていない場合がある。

**問題点**:
- `Check Render Status`のレスポンスには`response_url`が含まれているが、`Render Completed?`のTrueパスに正しく伝播されない場合がある
- `response_url`が未定義の場合、URL構築に失敗する

### 解決策

**`Get Image Result URL`ノードにフォールバックを追加**:

```javascript
// ✅ 修正後の設定
{
  "parameters": {
    "method": "GET",
    "url": "={{ $json.response_url || 'https://queue.fal.run/fal-ai/ffmpeg-api/requests/' + $json.request_id }}",
    "authentication": "genericCredentialType",
    "genericAuthType": "httpHeaderAuth",
    "sendHeaders": false,
    "sendBody": false,
    "options": {
      "timeout": 300000,
      "response": {
        "response": {
          "responseFormat": "json"
        }
      }
    }
  }
}
```

**`Retry Counter`ノードにも`response_url`を保持するように追加**:

```javascript
// ✅ 修正後の設定
{
  "parameters": {
    "assignments": {
      "assignments": [
        {
          "name": "retry_count",
          "value": "={{ $json.retry_count ? $json.retry_count + 1 : 1 }}"
        },
        {
          "name": "status_url",
          "value": "={{ $json.status_url }}"
        },
        {
          "name": "request_id",
          "value": "={{ $json.request_id }}"
        },
        {
          "name": "status",
          "value": "={{ $json.status }}"
        },
        {
          "name": "response_url",
          "value": "={{ $json.response_url || 'https://queue.fal.run/fal-ai/ffmpeg-api/requests/' + $json.request_id }}"
        }
      ]
    }
  }
}
```

**`Download Image`ノードにもフォールバックを追加**:

```javascript
// ✅ 修正後の設定
{
  "parameters": {
    "url": "={{ $json.images && $json.images[0] ? $json.images[0].url : ($json.video_url || $json.url) }}"
  }
}
```

### 適用方法

```javascript
// n8n MCP APIを使用してワークフロー全体を更新
mcp__n8n-mcp__n8n_update_full_workflow({
  id: "SDO8X6oR5W5y2s6A",
  name: "WF7 Phase4 - V2 Fixed",
  nodes: [...],  // Get Image Result URL、Retry Counter、Download Imageノードを修正
  connections: {...}  // 接続は変更なし
})
```

### 検証結果

**修正後（2025-11-08）**:
```
✅ ワークフロー更新成功
Version Counter: 89 → 91
Get Image Result URL ノード: response_urlフォールバック追加
Retry Counter ノード: response_url保持を追加
Download Image ノード: 複数のレスポンス形式に対応
```

**期待される動作**:
- `response_url`が存在する場合、それを優先的に使用
- `response_url`が存在しない場合、`request_id`からURLを構築
- FAL APIのレスポンス形式（`images[0].url`、`video_url`、`url`）に対応
- `Get Image Result URL`に正常に到達し、結果を取得できる

### ベストプラクティス

**FAL API結果取得パターン（改善版）**:
- ✅ **`response_url`を優先**: `response_url`が存在する場合は優先的に使用
- ✅ **フォールバックURL構築**: `response_url`が存在しない場合、`request_id`からURLを構築
- ✅ **複数のレスポンス形式に対応**: `images[0].url`、`video_url`、`url`など複数の形式に対応
- ✅ **`Retry Counter`で`response_url`を保持**: リトライループでも`response_url`を保持

**FAL APIレスポンス構造（複数パターン対応）**:
```json
// パターン1: response_urlを含む
{
  "status": "COMPLETED",
  "request_id": "uuid-here",
  "response_url": "https://queue.fal.run/fal-ai/ffmpeg-api/requests/uuid-here",
  "video_url": "https://fal.media/files/..."
}

// パターン2: images配列を含む
{
  "status": "COMPLETED",
  "request_id": "uuid-here",
  "images": [
    {
      "url": "https://fal.media/files/..."
    }
  ]
}

// パターン3: urlフィールドを含む
{
  "status": "COMPLETED",
  "request_id": "uuid-here",
  "url": "https://fal.media/files/..."
}
```

---

## 更新履歴

| 日付 | 更新内容 | 担当 |
|------|----------|------|
| 2025-11-04 | 初版作成（Execution 101, URL修正問題） | AI Assistant |
| 2025-11-08 | 問題5追加（FAL APIタイムアウト設定不備） | AI Assistant |
| 2025-11-08 | 問題6追加（Wait for Processingノードのwebhook待機問題） | AI Assistant |
| 2025-11-08 | 問題7追加（Check Retry Limitノードの接続が逆） | AI Assistant |
| 2025-11-08 | 問題8追加（Get Image Result URLノードのHTTPメソッドエラー） | AI Assistant |
| 2025-11-08 | 問題9追加（Get Image Result URLノードでresponse_urlが取得できない問題） | AI Assistant |

---

## クイックリファレンス

### コマンドテンプレート

**動画レンダリング実行コマンド（1行版）**:
```bash
python -c "from PIL import Image; colors=['blue','green','red','yellow','purple','orange','pink','cyan','magenta','brown']; [Image.new('RGB', (1080, 1920), color=colors[i]).save(f'/tmp/integration_asset_{i}.jpg') for i in range(10)]" && echo '{{ $json.scriptJson }}' > {{ $json.scriptPath }} && echo '{{ $json.assetsJson }}' > {{ $json.assetsPath }} && python /app/render_video_ffmpeg.py --script {{ $json.scriptPath }} --assets {{ $json.assetsPath }} --out {{ $json.outputPath }}
```

### ノードID参照

| ノード名 | Node ID | 用途 |
|---------|---------|------|
| Webhook | c86282e3-6130-4bfb-8607-9e5d7dacd398 | Webhookエントリーポイント |
| Submit to FAL | f21d892c-8100-4b31-ba7c-9455a31e9cf5 | FAL API呼び出し（タイムアウト修正対象） |
| Fetch Status | eb3a8689-faa9-4db4-9fb2-d26343a34827 | FAL APIステータス取得（タイムアウト設定確認） |
| Wait for Processing | ec05e49c-5d59-40a3-8afa-4aab3501d143 | ポーリング待機（webhook待機→時間ベース待機に修正） |
| Check Render Status | 512c653b-e527-4b6c-875a-13dbbb04b694 | レンダリングステータス確認（タイムアウト設定確認） |
| Get Image Result URL | 14d89d20-3adc-4438-b9e8-78fc0df9812e | 結果URL取得（response_urlフォールバック追加、GETメソッド明示） |
| Retry Counter | 0d32b86a-ea3f-4fb9-993e-94d024350bf7 | リトライカウンター（response_url保持を追加） |
| Download Image | d7ebee07-778c-4ea0-85af-e7b407bc8067 | 画像ダウンロード（複数のレスポンス形式に対応） |
| Wait Before Retry | 89dccc13-3413-4d65-94fa-652758d14a5a | リトライ前待機（webhook待機→時間ベース待機に修正） |

### テスト用Notion Page

```
Page ID: 2a068d5c-2986-81a3-ab0c-ff0bc1e4ebb9
Title: "Phase1→Phase4統合テスト記事"
Article ID: integration-test-001
Database: 29b68d5c-2986-817f-b4e6-f84cf75ea9ed
```

### テスト実行コマンド

**WF7 Phase4 V2 Fixed** (Workflow ID: SDO8X6oR5W5y2s6A):
```bash
curl -X POST "https://n8n-python-production-344b.up.railway.app/webhook/wf7-video-script" \
  -H "Content-Type: application/json" \
  -d '{"notionPageId": "2a068d5c-2986-81a3-ab0c-ff0bc1e4ebb9"}' \
  --max-time 600
```

期待レスポンス: 200 OK, Duration: 15-30秒（FAL API処理時間により変動）
