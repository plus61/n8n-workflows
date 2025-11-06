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

## 更新履歴

| 日付 | 更新内容 | 担当 |
|------|----------|------|
| 2025-11-04 | 初版作成（Execution 101, URL修正問題） | AI Assistant |

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
| WF7-Phase4 Webhook | 7957d8d7-f929-42f8-92e2-0844eea7d960 | Webhookエントリーポイント |
| 動画レンダリング実行 | 76598e25-bde1-4f96-970f-03d7e67630ad | FFmpeg実行（タイムアウト修正対象） |
| 動画メタデータ抽出 | f5dc47f2-a343-4d1f-ba29-d83b6c79abe5 | URL構築（プロトコル修正対象） |

### テスト用Notion Page

```
Page ID: 2a068d5c-2986-81a3-ab0c-ff0bc1e4ebb9
Title: "Phase1→Phase4統合テスト記事"
Article ID: integration-test-001
Database: 29b68d5c-2986-817f-b4e6-f84cf75ea9ed
```

### テスト実行コマンド

```bash
curl -X POST "https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4-render" \
  -H "Content-Type: application/json" \
  -d '{"notionPageId": "2a068d5c-2986-81a3-ab0c-ff0bc1e4ebb9"}'
```

期待レスポンス: 200 OK, Duration: 15-30秒
