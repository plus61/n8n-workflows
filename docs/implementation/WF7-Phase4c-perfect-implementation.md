# WF7 Phase4c 完璧版実装ドキュメント

**作成日**: 2025-11-08
**ベース**: 稼働実績のある `WF7phase4_v3` (ID: `qSN7EHj5yl0nPXij`)
**目的**: FAL FFmpeg API `/compose`を使用した動画結合の完璧な実装

---

## 📋 概要

### Phase4cの役割

- **入力**: Phase4bから生成された7本の動画URL (`videos_metadata`)
- **処理**: FAL FFmpeg API `/compose`エンドポイントで動画結合
- **出力**: 1本の完成動画（60-90秒）をGoogle Driveにアップロード、Notion DB更新

### 既存WF7phase4_v3との関係

現在のWF7phase4_v3は以下の構造で動作:
```
Webhook → Notion API → データ統合 → Submit to FAL → Fetch Status →
Wait for Processing → Render Completed? → Drive Upload → Notion Update → Response
```

Phase4cは、この既存の**FAL処理パターン**（Submit → Polling → Download → Upload）を踏襲しつつ、以下の変更を加えます:

1. **入力データ**: `slides_metadata`（画像7枚）→ `videos_metadata`（動画7本）
2. **FAL API**: `/compose` (スライド→動画) → `/compose` (動画結合)
3. **ペイロード構築**: 画像URLの配列 → 動画URLの配列

---

## 🏗️ アーキテクチャ設計

### ノード構成（8ノード）

```yaml
Node 1: Aggregate Videos
  Type: Aggregate
  Purpose: Phase4bの7本の動画を配列に集約
  Input: videos_metadata (7 items)
  Output: { "videos": [url1, url2, ...url7] }

Node 2: ペイロード構築 (FAL Compose)
  Type: Code (JavaScript)
  Purpose: FAL FFmpeg API `/compose` 用のペイロードを構築
  Input: videos配列
  Output: FAL API request payload

Node 3: Submit to FAL
  Type: HTTP Request
  Purpose: FAL `/compose` エンドポイントに動画結合リクエストを送信
  Input: payload from Node 2
  Output: { "request_id": "..." }

Node 4: Wait for Processing
  Type: Wait
  Purpose: FALのレンダリング開始を待つ
  Duration: 10秒

Node 5: Fetch Status
  Type: HTTP Request
  Purpose: FALのステータスをポーリング
  Loop: max 20 retries, interval 10s

Node 6: Render Completed?
  Type: IF
  Purpose: レンダリング完了チェック
  Condition: status === "COMPLETED"

Node 7: Download & Upload to Drive
  Type: HTTP Request (2 requests)
  Purpose: 完成動画のダウンロード → Google Driveアップロード

Node 8: Update Notion DB & Response
  Type: HTTP Request + Respond to Webhook
  Purpose: Notion DBのステータス更新 & Webhook応答
```

---

## 🔧 詳細実装仕様

### Node 1: Aggregate Videos

```json
{
  "name": "Aggregate Videos",
  "type": "n8n-nodes-base.aggregate",
  "parameters": {
    "aggregate": "aggregateIndividualFields",
    "fieldsToAggregate": {
      "fieldToAggregate": [
        {
          "fieldToAggregate": "video_url",
          "renameField": false
        }
      ]
    },
    "options": {
      "keepOnlySet": false,
      "mergeLists": true
    }
  }
}
```

**説明**:
- Phase4bの出力（7個のアイテム、各々に`video_url`）を1つのアイテムに集約
- `video_url`フィールドを配列化: `["url1", "url2", ..., "url7"]`
- 順序保持: hook → intro → point1-3 → summary → cta

---

### Node 2: ペイロード構築 (FAL Compose)

```json
{
  "name": "ペイロード構築",
  "type": "n8n-nodes-base.code",
  "parameters": {
    "language": "javaScript",
    "jsCode": "// FAL FFmpeg API /compose endpoint payload construction\n\nconst videoUrls = $input.first().json.video_url;\n\nif (!Array.isArray(videoUrls) || videoUrls.length === 0) {\n  throw new Error('video_url must be a non-empty array');\n}\n\n// FAL /compose API payload\nconst payload = {\n  inputs: videoUrls.map(url => ({\n    type: 'video',\n    url: url\n  })),\n  output_format: 'mp4',\n  concat_method: 'concat',\n  video_codec: 'h264',\n  audio_codec: 'aac'\n};\n\nreturn [{ json: payload }];"
  }
}
```

**説明**:
- 入力: `{ "video_url": ["url1", "url2", ...] }`
- 出力: FAL API `/compose`用のペイロード
- エラーハンドリング: 空配列チェック

**FAL API `/compose` エンドポイント仕様**:
```yaml
URL: https://queue.fal.run/fal-ai/ffmpeg-api/compose
Method: POST
Authentication: Header Auth (Key YOUR_FAL_API_KEY)
Body:
  inputs:
    - type: video
      url: https://...
  output_format: mp4
  concat_method: concat
  video_codec: h264
  audio_codec: aac
```

---

### Node 3: Submit to FAL

```json
{
  "name": "Submit to FAL",
  "type": "n8n-nodes-base.httpRequest",
  "typeVersion": 4,
  "parameters": {
    "url": "https://queue.fal.run/fal-ai/ffmpeg-api/compose",
    "method": "POST",
    "authentication": "genericCredentialType",
    "genericAuthType": "httpHeaderAuth",
    "sendBody": true,
    "specifyBody": "json",
    "jsonBody": "={{ JSON.stringify($json) }}",
    "options": {
      "timeout": 30000
    }
  },
  "credentials": {
    "httpHeaderAuth": {
      "id": "YOUR_FAL_CREDENTIAL_ID",
      "name": "FAL API Key"
    }
  }
}
```

**説明**:
- **CRITICAL**: `specifyBody: "json"` + `jsonBody` を使用（HTTP Request Node v4）
- タイムアウト: 30秒
- レスポンス: `{ "request_id": "..." }`

---

### Node 4: Wait for Processing

```json
{
  "name": "Wait for Processing",
  "type": "n8n-nodes-base.wait",
  "parameters": {
    "amount": 10,
    "unit": "seconds"
  }
}
```

**説明**:
- FALのレンダリング開始待ち（10秒）
- この間にFALサーバーがリクエストを処理開始

---

### Node 5: Fetch Status

```json
{
  "name": "Fetch Status",
  "type": "n8n-nodes-base.httpRequest",
  "typeVersion": 4,
  "parameters": {
    "url": "=https://queue.fal.run/fal-ai/ffmpeg-api/requests/{{ $json.request_id }}/status",
    "method": "GET",
    "authentication": "genericCredentialType",
    "genericAuthType": "httpHeaderAuth",
    "options": {
      "timeout": 30000,
      "retry": {
        "maxRetries": 20,
        "retryInterval": 10000
      }
    }
  }
}
```

**説明**:
- ステータスポーリング: 最大20回、10秒間隔
- レスポンス例:
  ```json
  {
    "status": "IN_PROGRESS" | "COMPLETED" | "FAILED",
    "output": {
      "video": {
        "url": "https://...",
        "content_type": "video/mp4",
        "file_size": 12345678
      }
    }
  }
  ```

---

### Node 6: Render Completed?

```json
{
  "name": "Render Completed?",
  "type": "n8n-nodes-base.if",
  "parameters": {
    "conditions": {
      "string": [
        {
          "value1": "={{ $json.status }}",
          "operation": "equals",
          "value2": "COMPLETED"
        }
      ]
    }
  }
}
```

**説明**:
- True分岐: Node 7 (Download & Upload)
- False分岐: エラーハンドリング（Retry Counter または Error Handler）

---

### Node 7: Download & Upload to Drive

#### 7-1: Download Video

```json
{
  "name": "Download Video",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "url": "={{ $json.output.video.url }}",
    "method": "GET",
    "options": {
      "response": {
        "responseFormat": "file"
      }
    }
  }
}
```

#### 7-2: Upload to Google Drive

```json
{
  "name": "Upload to Google Drive",
  "type": "n8n-nodes-base.googleDrive",
  "parameters": {
    "operation": "upload",
    "name": "=WF7_Final_{{ $json.script_id }}_{{ $now.toFormat('yyyyMMdd_HHmmss') }}.mp4",
    "parents": {
      "folderId": "YOUR_GOOGLE_DRIVE_FOLDER_ID"
    },
    "binaryData": true,
    "binaryPropertyName": "data"
  }
}
```

**説明**:
- FALからMP4をダウンロード → バイナリデータとして保存
- Google Driveにアップロード（ファイル名: `WF7_Final_{script_id}_{timestamp}.mp4`）
- 出力: `{ "id": "...", "webViewLink": "...", "webContentLink": "..." }`

---

### Node 8: Update Notion DB & Response

#### 8-1: Update Notion DB

```json
{
  "name": "Update Notion DB",
  "type": "n8n-nodes-base.notion",
  "parameters": {
    "resource": "databasePage",
    "operation": "update",
    "pageId": "={{ $json.script_id }}",
    "properties": {
      "properties": [
        {
          "name": "status",
          "value": "completed"
        },
        {
          "name": "final_video_url",
          "value": "={{ $json.webViewLink }}"
        },
        {
          "name": "completed_at",
          "value": "={{ $now.toISO() }}"
        }
      ]
    }
  }
}
```

#### 8-2: Respond to Webhook

```json
{
  "name": "Respond to Webhook",
  "type": "n8n-nodes-base.respondToWebhook",
  "parameters": {
    "respondWith": "json",
    "responseBody": "={{ { \"success\": true, \"message\": \"Phase4c completed\", \"final_video_url\": $json.webViewLink } }}"
  }
}
```

**説明**:
- Notion DBの`status`を`completed`に更新
- `final_video_url`と`completed_at`を記録
- Webhookに成功レスポンスを返却

---

## 🔗 接続構成

```
[Aggregate Videos] → [ペイロード構築] → [Submit to FAL] → [Wait for Processing] →
[Fetch Status] → [Render Completed?]
                    ↓ (True)
                  [Download Video] → [Upload to Google Drive] →
                  [Update Notion DB] → [Respond to Webhook]
                    ↓ (False)
                  [Error Handler]
```

---

## 🧪 テスト計画

### 単体テスト

1. **Aggregate Videos**: 7本の動画URLが正しく配列化されるか
2. **ペイロード構築**: FAL API仕様に準拠したペイロードが生成されるか
3. **Submit to FAL**: `request_id`が正しく返却されるか
4. **Fetch Status**: ポーリングが正しく動作し、完了ステータスを検知できるか
5. **Download & Upload**: 動画のダウンロードとGoogle Driveアップロードが成功するか
6. **Notion Update**: ステータス更新が正しく反映されるか

### E2Eテスト

```yaml
シナリオ: Phase4a → Phase4b → Phase4c 完全パイプライン
手順:
  1. Webhook `/wf7-video-script` にPOSTリクエスト
  2. Phase4a: 7枚のスライド画像生成
  3. Phase4b: 7本の動画生成（各3-20秒）
  4. Phase4c: 1本の完成動画生成（60-90秒）
  5. Google Driveにアップロード確認
  6. Notion DBのステータス確認

期待結果:
  ✅ 60-90秒の完成動画が生成される
  ✅ 動画の結合がスムーズ（トランジションなし）
  ✅ ファイルサイズ < 50MB
  ✅ Notion DBのstatusが"completed"
```

---

## 📊 パフォーマンス指標

```yaml
Phase4c実行時間:
  - FAL Submit: ~2秒
  - レンダリング待機: 10秒 (初回Wait)
  - ステータスポーリング: 10-180秒 (動画サイズに依存)
  - ダウンロード: ~5秒
  - Google Driveアップロード: ~10秒
  - Notion更新: ~2秒
  - 合計: 約40-220秒 (平均120秒)

コスト:
  - FAL /compose: $0.10/リクエスト
  - Google Drive: 無料（ストレージ制限内）
  - 合計: $0.10/動画
```

---

## 🚨 エラーハンドリング

### 想定エラーケース

1. **FAL API タイムアウト**
   - 対処: Retry Counter（最大20回）
   - 超過時: Error Handlerでログ記録 & Notion更新（status = "failed"）

2. **ステータスポーリング失敗**
   - 対処: 10秒間隔で再試行（最大20回 = 200秒）
   - 超過時: タイムアウトエラー

3. **Google Driveアップロード失敗**
   - 対処: 3回リトライ（n8n標準リトライ機能）
   - 失敗時: エラーログ & Webhook応答にエラーメッセージ

4. **Notion DB更新失敗**
   - 対処: 非同期エラーハンドリング（Phase4c自体は成功扱い）
   - ログ記録: Railway logsに詳細を出力

---

## 📝 実装チェックリスト

### 準備

- [x] WF7phase4_v3 バックアップ完了
- [x] FAL API認証情報の確認
- [ ] Google Drive API認証情報の確認
- [ ] Notion API認証情報の確認

### 実装

- [ ] Node 1: Aggregate Videos 追加
- [ ] Node 2: ペイロード構築 追加
- [ ] Node 3: Submit to FAL 追加
- [ ] Node 4: Wait for Processing 追加
- [ ] Node 5: Fetch Status 追加（ポーリング設定）
- [ ] Node 6: Render Completed? 追加（IF分岐）
- [ ] Node 7: Download & Upload 追加（2ステップ）
- [ ] Node 8: Update Notion DB & Response 追加

### テスト

- [ ] 単体テスト: 各ノードの動作確認
- [ ] E2Eテスト: Phase4a → 4b → 4c パイプライン
- [ ] 異常系テスト: タイムアウト、リトライ、エラーハンドリング
- [ ] パフォーマンステスト: 実行時間、コスト測定

### デプロイ

- [ ] n8n UIで手動実装（または MCP経由で更新）
- [ ] Webhookエンドポイント確認: `https://n8n-python-production-344b.up.railway.app/webhook/wf7-video-script`
- [ ] Railway logsでエラーなし確認
- [ ] Phase4a/4bとの統合確認

---

## 🔗 関連ドキュメント

- `docs/implementation/WF7-Phase4-FAL実装計画書.md`: Phase4全体の実装計画
- `docs/testing/wf7-phase4-v3-test-report.md`: 既存WF7phase4_v3のテスト結果
- `docs/knowledge/n8n-workflow-construction-knowledge.md`: n8nワークフロー構築ナレッジ
- `workflows/wf7_phase4_v3.json`: ベースワークフローのバックアップ

---

**次のステップ**: 上記仕様に基づき、n8n UIまたはMCPツールでPhase4cノードを実装
