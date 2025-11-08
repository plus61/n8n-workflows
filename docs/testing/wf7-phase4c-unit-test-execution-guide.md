# WF7 Phase4c 単体テスト実行ガイド

**作成日**: 2025-11-08
**ワークフローID**: chPw11OY5sex6d9I
**テストデータ**: `/test-phase4c-real-urls.json`

---

## 🎯 テスト目的

Phase4cワークフローの以下の機能を検証：
1. 7本の動画URLの集約（Aggregate Videos）
2. FAL API `/compose` 用ペイロード構築
3. FAL APIへのリクエスト送信と `request_id` 取得
4. ステータスポーリング（最大20回、10秒間隔）
5. レンダリング完了判定（status === "COMPLETED"）
6. 完成動画のダウンロード
7. Google Driveへのアップロード
8. Notion DBのステータス更新

---

## 📋 前提条件チェックリスト

- [ ] n8n UIにアクセス可能: `https://n8n-python-production-344b.up.railway.app/`
- [ ] FAL API認証情報が設定済み (Header Auth)
- [ ] Google Drive OAuth2認証が設定済み
- [ ] Notion API認証が設定済み
- [ ] ワークフローID `chPw11OY5sex6d9I` が存在
- [ ] テストデータファイル `/test-phase4c-real-urls.json` が準備済み

---

## 🚀 テスト実行手順

### ステップ1: n8n UIでワークフローを開く

1. ブラウザで `https://n8n-python-production-344b.up.railway.app/` にアクセス
2. 左サイドバー → "Workflows" → "WF7 Phase4c - Perfect Implementation" をクリック
3. ワークフローIDが `chPw11OY5sex6d9I` であることを確認

### ステップ2: Manual Trigger ノードにPin Dataを設定

1. **"When clicking 'Test workflow'"** (Manual Trigger) ノードをクリック
2. 右サイドバー → **"Pin Data"** タブを選択
3. 以下のJSONデータをコピー&ペースト：

```json
[
  {
    "section": "hook",
    "duration": 3,
    "video_url": "https://v3b.fal.media/files/b/penguin/X6YpaYnUTrgdaoUwG1RpN_output.mp4",
    "order": 1,
    "script_id": "test-script-real-001"
  },
  {
    "section": "intro",
    "duration": 10,
    "video_url": "https://v3b.fal.media/files/b/rabbit/W0yXmayD3qLoY9pCzcZGr_output.mp4",
    "order": 2,
    "script_id": "test-script-real-001"
  },
  {
    "section": "point1",
    "duration": 13,
    "video_url": "https://v3b.fal.media/files/b/penguin/X6YpaYnUTrgdaoUwG1RpN_output.mp4",
    "order": 3,
    "script_id": "test-script-real-001"
  },
  {
    "section": "point2",
    "duration": 13,
    "video_url": "https://v3b.fal.media/files/b/rabbit/W0yXmayD3qLoY9pCzcZGr_output.mp4",
    "order": 4,
    "script_id": "test-script-real-001"
  },
  {
    "section": "point3",
    "duration": 13,
    "video_url": "https://v3b.fal.media/files/b/penguin/X6YpaYnUTrgdaoUwG1RpN_output.mp4",
    "order": 5,
    "script_id": "test-script-real-001"
  },
  {
    "section": "summary",
    "duration": 20,
    "video_url": "https://v3b.fal.media/files/b/rabbit/W0yXmayD3qLoY9pCzcZGr_output.mp4",
    "order": 6,
    "script_id": "test-script-real-001"
  },
  {
    "section": "cta",
    "duration": 7,
    "video_url": "https://v3b.fal.media/files/b/penguin/X6YpaYnUTrgdaoUwG1RpN_output.mp4",
    "order": 7,
    "script_id": "test-script-real-001"
  }
]
```

4. **"Save"** または自動保存を確認

⚠️ **注意**: 上記データは提供された2本の動画URL（hook, intro）を再利用しています。実際のテストでは、残りの5本（point1-3, summary, cta）の実際の動画URLに置き換えてください。

### ステップ3: ワークフローの保存

1. 右上の **"Save"** ボタンをクリック
2. 保存完了メッセージを確認

### ステップ4: テストワークフローを実行

1. 右上の **"Test workflow"** ボタンをクリック
2. 実行開始を確認（各ノードに実行インジケータが表示される）

### ステップ5: 各ノードの実行結果を検証

実行完了後、以下の順序で各ノードの出力を確認：

#### ノード1: "Aggregate Videos"

**期待される出力**:
```json
{
  "video_url": [
    "https://v3b.fal.media/files/b/penguin/X6YpaYnUTrgdaoUwG1RpN_output.mp4",
    "https://v3b.fal.media/files/b/rabbit/W0yXmayD3qLoY9pCzcZGr_output.mp4",
    "https://v3b.fal.media/files/b/penguin/X6YpaYnUTrgdaoUwG1RpN_output.mp4",
    "https://v3b.fal.media/files/b/rabbit/W0yXmayD3qLoY9pCzcZGr_output.mp4",
    "https://v3b.fal.media/files/b/penguin/X6YpaYnUTrgdaoUwG1RpN_output.mp4",
    "https://v3b.fal.media/files/b/rabbit/W0yXmayD3qLoY9pCzcZGr_output.mp4",
    "https://v3b.fal.media/files/b/penguin/X6YpaYnUTrgdaoUwG1RpN_output.mp4"
  ]
}
```

✅ **検証ポイント**:
- `video_url` が配列であること
- 配列の長さが7であること
- URLの順序が order 1→7 と一致すること

#### ノード2: "ペイロード構築"

**期待される出力**:
```json
{
  "inputs": [
    {
      "type": "video",
      "url": "https://v3b.fal.media/files/b/penguin/X6YpaYnUTrgdaoUwG1RpN_output.mp4"
    },
    {
      "type": "video",
      "url": "https://v3b.fal.media/files/b/rabbit/W0yXmayD3qLoY9pCzcZGr_output.mp4"
    },
    // ... 7個の入力オブジェクト
  ],
  "output_format": "mp4",
  "concat_method": "concat",
  "video_codec": "h264",
  "audio_codec": "aac"
}
```

✅ **検証ポイント**:
- `inputs` 配列の長さが7であること
- 各要素に `type: "video"` と `url` が存在すること
- `output_format`, `concat_method`, `video_codec`, `audio_codec` が正しいこと

#### ノード3: "Submit to FAL"

**期待される出力**:
```json
{
  "request_id": "fal-ai-ffmpeg-api-XXXXXXXXXXXXXXXX",
  "status": "IN_QUEUE",
  "queue_position": 0
}
```

✅ **検証ポイント**:
- `request_id` が存在すること（UUIDまたは一意の文字列）
- HTTPステータスコードが `200` または `202` であること
- エラーメッセージがないこと

❌ **エラーケース**:
- `401 Unauthorized` → FAL API認証情報を確認
- `422 Unprocessable Entity` → 動画URLが無効またはアクセス不可
- `400 Bad Request` → ペイロード構造が不正

#### ノード4: "Wait for Processing"

**期待される動作**:
- 10秒間待機（プログレスバーが表示される）
- 前のノードのデータ（`request_id`）がそのまま引き継がれる

✅ **検証ポイント**:
- 待機時間が約10秒であること
- データが変更されていないこと

#### ノード5: "Fetch Status"

**期待される出力** (ポーリング完了時):
```json
{
  "request_id": "fal-ai-ffmpeg-api-XXXXXXXXXXXXXXXX",
  "status": "COMPLETED",
  "output": {
    "video": {
      "url": "https://fal.media/files/XXXXXXXXX/output.mp4",
      "content_type": "video/mp4",
      "file_size": 12345678,
      "width": 1920,
      "height": 1080
    }
  }
}
```

✅ **検証ポイント**:
- `status` が `"COMPLETED"` であること
- `output.video.url` が存在し、アクセス可能なURLであること
- リトライが適切に行われたこと（ログで確認）

⚠️ **途中経過の出力例**:
```json
{
  "request_id": "fal-ai-ffmpeg-api-XXXXXXXXXXXXXXXX",
  "status": "IN_PROGRESS",
  "progress": 0.45
}
```

❌ **エラーケース**:
- `status: "FAILED"` → FAL APIのレンダリング失敗
- タイムアウト（200秒超） → 動画が長すぎるまたはFALサーバーの問題

#### ノード6: "Render Completed?"

**期待される動作**:
- IF条件: `$json.status === "COMPLETED"`
- **True分岐** → "Download Video" ノードへ
- **False分岐** → "Error Handler" ノードへ

✅ **検証ポイント**:
- True分岐が実行されていること
- False分岐（Error Handler）が実行されていないこと

#### ノード7: "Download Video"

**期待される出力**:
- バイナリデータ（動画ファイル）
- `data` プロパティにMP4ファイルが格納される

✅ **検証ポイント**:
- バイナリデータが存在すること
- ファイルサイズが0より大きいこと
- `mimeType` が `video/mp4` であること

#### ノード8: "Upload to Google Drive"

**期待される出力**:
```json
{
  "id": "1XXXXXXXXXXXXXXXXXXXXXXXXXX",
  "name": "WF7_Final_test-script-real-001_20251108_093000.mp4",
  "mimeType": "video/mp4",
  "webViewLink": "https://drive.google.com/file/d/1XXXXXXXXXXXXXXXXXXXXXXXXXX/view",
  "webContentLink": "https://drive.google.com/uc?id=1XXXXXXXXXXXXXXXXXXXXXXXXXX&export=download",
  "size": "12345678"
}
```

✅ **検証ポイント**:
- `id` が存在すること（Google DriveのファイルID）
- `webViewLink` にアクセスして動画が再生できること
- ファイル名が正しい形式であること: `WF7_Final_{script_id}_{timestamp}.mp4`

❌ **エラーケース**:
- `403 Forbidden` → OAuth2認証が期限切れ
- `404 Not Found` → フォルダIDが無効

#### ノード9: "Update Notion DB"

**期待される出力**:
```json
{
  "object": "page",
  "id": "test-script-real-001",
  "properties": {
    "status": {
      "status": {
        "name": "completed"
      }
    },
    "final_video_url": {
      "url": "https://drive.google.com/file/d/1XXXXXXXXXXXXXXXXXXXXXXXXXX/view"
    },
    "completed_at": {
      "date": {
        "start": "2025-11-08T09:30:00.000Z"
      }
    }
  }
}
```

✅ **検証ポイント**:
- `properties.status.status.name` が `"completed"` であること
- `final_video_url` にGoogle Driveのリンクがセットされていること
- `completed_at` にISO 8601形式のタイムスタンプがセットされていること

❌ **エラーケース**:
- `400 Bad Request` → `script_id` (pageId) が無効
- `401 Unauthorized` → Notion APIトークンが無効

#### ノード10: "Respond to Webhook"

**期待される出力**:
```json
{
  "success": true,
  "message": "Phase4c completed",
  "final_video_url": "https://drive.google.com/file/d/1XXXXXXXXXXXXXXXXXXXXXXXXXX/view"
}
```

✅ **検証ポイント**:
- `success: true` であること
- `final_video_url` が正しいこと

---

## 📊 テスト結果の記録

実行後、以下のテンプレートで結果を記録：

```yaml
テスト実行日時: 2025-11-08 09:30:00
ワークフローID: chPw11OY5sex6d9I
テストデータ: test-phase4c-real-urls.json

実行結果:
  ✅ Aggregate Videos: PASS
  ✅ ペイロード構築: PASS
  ✅ Submit to FAL: PASS
  ✅ Wait for Processing: PASS
  ✅ Fetch Status: PASS
  ✅ Render Completed?: PASS (True分岐)
  ✅ Download Video: PASS
  ✅ Upload to Google Drive: PASS
  ✅ Update Notion DB: PASS
  ✅ Respond to Webhook: PASS

実行時間:
  Total: XXX秒
  - Submit to FAL: ~2秒
  - Wait for Processing: 10秒
  - Fetch Status (polling): ~XX秒 (リトライ回数: X回)
  - Download Video: ~5秒
  - Upload to Google Drive: ~10秒
  - Update Notion DB: ~2秒

FAL API レスポンス:
  request_id: fal-ai-ffmpeg-api-XXXXXXXXXXXXXXXX
  最終ステータス: COMPLETED
  レンダリング時間: ~XX秒

完成動画:
  Google Drive URL: https://drive.google.com/file/d/...
  ファイル名: WF7_Final_test-script-real-001_YYYYMMDD_HHMMSS.mp4
  ファイルサイズ: XX MB
  再生時間: XX秒 (期待値: 79秒)
  品質: ✅ 良好 / ⚠️ 要確認 / ❌ 不良

エラー:
  - なし

備考:
  - point1-3, summary, ctaの動画URLはhook/introのURLを再利用
  - 実際のE2Eテストでは7本すべて異なる動画を使用する必要あり
```

---

## 🐛 トラブルシューティング

### ケース1: "Aggregate Videos" でエラー

**症状**: `video_url` が配列にならない

**原因**: 入力データの構造が不正

**対処**:
1. Pin Dataが正しく設定されているか確認
2. 各アイテムに `video_url` フィールドが存在するか確認
3. Manual Triggerノードを再実行

### ケース2: "Submit to FAL" で401エラー

**症状**: `401 Unauthorized`

**原因**: FAL API認証情報が無効

**対処**:
1. Settings → Credentials → FAL API Key を確認
2. Header Name が `Authorization` であることを確認
3. Value が `Key YOUR_ACTUAL_FAL_API_KEY` 形式であることを確認
4. APIキーが有効期限内であることを確認

### ケース3: "Fetch Status" がタイムアウト

**症状**: 200秒経過後もステータスが `COMPLETED` にならない

**原因**: FALのレンダリングが長時間実行中またはスタック

**対処**:
1. FAL Dashboardでリクエストのステータスを確認
2. 動画の長さ/ファイルサイズが適切か確認（合計79秒、<50MB推奨）
3. Fetch Status ノードの `maxRetries` を30に増やす（300秒）
4. FAL APIの制限やクォータを確認

### ケース4: "Upload to Google Drive" で403エラー

**症状**: `403 Forbidden`

**原因**: OAuth2認証が期限切れまたは権限不足

**対処**:
1. Credentials → Google Drive Account で再認証
2. Google Driveのフォルダに書き込み権限があることを確認
3. フォルダIDが正しいことを確認

### ケース5: 動画が結合されていない

**症状**: ダウンロードした動画が1本だけ、または結合が不完全

**原因**: FAL API `/compose` のペイロードが不正

**対処**:
1. "ペイロード構築" ノードの出力を確認
2. `inputs` 配列に7個の要素が存在するか確認
3. 各動画URLがアクセス可能か確認（ブラウザで直接開く）
4. FAL APIのドキュメントでペイロード仕様を再確認

---

## ✅ 成功基準

以下をすべて満たす場合、Phase4c単体テストは成功：

1. ✅ 全10ノードがエラーなく実行完了
2. ✅ FAL API `/compose` から `request_id` を取得
3. ✅ ステータスポーリングで `COMPLETED` を取得
4. ✅ 完成動画をGoogle Driveにアップロード成功
5. ✅ Notion DBのステータスを `completed` に更新成功
6. ✅ Google Driveの動画が再生可能
7. ✅ 動画の再生時間が約79秒（±5秒）
8. ✅ ファイルサイズが50MB以下
9. ✅ 動画の結合がスムーズ（トランジションなし）
10. ✅ 総実行時間が5分以内

---

## 🔗 次のステップ

Phase4c単体テストが成功したら、次は **E2Eテスト** を実行：

1. Phase4a → Phase4b → Phase4c の完全パイプラインテスト
2. Webhook経由での実行（`/webhook/wf7-video-script`）
3. 実際のNotion Databaseとの連携確認

詳細は `/docs/testing/wf7-phase4c-test-setup-guide.md` の「ステップ4: Phase4a→4b→4c E2Eテスト」を参照してください。
