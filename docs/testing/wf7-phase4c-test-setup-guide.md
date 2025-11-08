# WF7 Phase4c テストセットアップガイド

**作成日**: 2025-11-08
**ワークフローID**: chPw11OY5sex6d9I
**目的**: Phase4c単体テストおよびE2Eテストの実行手順

---

## 📋 前提条件

- n8n UIアクセス可能: `https://n8n-python-production-344b.up.railway.app/`
- FAL APIアカウントとAPIキー
- Google Drive APIアクセス権限
- Notion APIトークン
- Phase4cワークフローがアップロード済み (ID: chPw11OY5sex6d9I)

---

## 🔧 ステップ1: 認証情報の設定

### 1.1 FAL API Key (Header Auth)

n8n UI → Settings → Credentials → Add Credential → Header Auth

```yaml
Name: FAL API Key
Header Name: Authorization
Value: Key YOUR_ACTUAL_FAL_API_KEY
```

**取得方法**:
1. https://fal.ai/ にログイン
2. Dashboard → API Keys
3. 新しいキーを作成するか既存のキーをコピー

### 1.2 Google Drive OAuth2

n8n UI → Settings → Credentials → Add Credential → Google Drive OAuth2 API

```yaml
Name: Google Drive Account
```

**設定手順**:
1. Google Cloud Console でOAuth 2.0クライアントIDを作成
2. n8nのリダイレクトURIを設定: `https://n8n-python-production-344b.up.railway.app/rest/oauth2-credential/callback`
3. クライアントIDとシークレットをn8nに入力
4. 認証フローを完了

### 1.3 Notion API

n8n UI → Settings → Credentials → Add Credential → Notion API

```yaml
Name: Notion API
API Token: YOUR_NOTION_INTEGRATION_TOKEN
```

**取得方法**:
1. https://www.notion.so/my-integrations にアクセス
2. 新しいインテグレーションを作成
3. Internal Integration Token をコピー
4. 対象のNotion Databaseに権限を付与

---

## 🔧 ステップ2: ワークフロー設定の更新

### 2.1 認証情報の割り当て

ワークフローID `chPw11OY5sex6d9I` を開き、以下のノードに認証情報を割り当て：

#### "Submit to FAL" ノード
- Credential Type: Header Auth
- Select: "FAL API Key" (上記で作成したもの)

#### "Fetch Status" ノード
- Credential Type: Header Auth
- Select: "FAL API Key" (同上)

#### "Upload to Google Drive" ノード
- Credential Type: Google Drive OAuth2 API
- Select: "Google Drive Account" (上記で作成したもの)

#### "Update Notion DB" ノード
- Credential Type: Notion API
- Select: "Notion API" (上記で作成したもの)

### 2.2 Google Drive フォルダIDの設定

"Upload to Google Drive" ノードのパラメータを更新：

```json
{
  "parents": {
    "folderId": "YOUR_ACTUAL_GOOGLE_DRIVE_FOLDER_ID"
  }
}
```

**フォルダIDの取得方法**:
1. Google Driveで対象フォルダを開く
2. URLから抽出: `https://drive.google.com/drive/folders/{FOLDER_ID}`

---

## 🧪 ステップ3: Phase4c単体テスト

### 3.1 テストデータの準備

`/Users/yuichiroooosuger/Desktop/n8n-workflows/test-phase4c-mock-data.json` の内容を使用します。

**重要**: このモックデータは**プレースホルダーURL**を使用しています。実際のFAL APIテストには、有効な動画URLが必要です。

### 3.2 Pin Dataの設定

n8n UI でワークフローを開き：

1. "When clicking 'Test workflow'" (Manual Trigger) ノードを選択
2. 右サイドバー → "Pin Data"
3. 以下のJSONを貼り付け：

```json
[
  {
    "section": "hook",
    "duration": 3,
    "video_url": "https://fal.media/files/lion/test-video-hook-3s.mp4",
    "order": 1,
    "script_id": "test-script-001"
  },
  {
    "section": "intro",
    "duration": 10,
    "video_url": "https://fal.media/files/lion/test-video-intro-10s.mp4",
    "order": 2,
    "script_id": "test-script-001"
  },
  {
    "section": "point1",
    "duration": 13,
    "video_url": "https://fal.media/files/lion/test-video-point1-13s.mp4",
    "order": 3,
    "script_id": "test-script-001"
  },
  {
    "section": "point2",
    "duration": 13,
    "video_url": "https://fal.media/files/lion/test-video-point2-13s.mp4",
    "order": 4,
    "script_id": "test-script-001"
  },
  {
    "section": "point3",
    "duration": 13,
    "video_url": "https://fal.media/files/lion/test-video-point3-13s.mp4",
    "order": 5,
    "script_id": "test-script-001"
  },
  {
    "section": "summary",
    "duration": 20,
    "video_url": "https://fal.media/files/lion/test-video-summary-20s.mp4",
    "order": 6,
    "script_id": "test-script-001"
  },
  {
    "section": "cta",
    "duration": 7,
    "video_url": "https://fal.media/files/lion/test-video-cta-7s.mp4",
    "order": 7,
    "script_id": "test-script-001"
  }
]
```

### 3.3 単体テスト実行

1. "Test workflow" ボタンをクリック
2. 各ノードの実行結果を確認：

#### 期待される結果

**Aggregate Videos ノード**:
```json
{
  "video_url": [
    "https://fal.media/files/lion/test-video-hook-3s.mp4",
    "https://fal.media/files/lion/test-video-intro-10s.mp4",
    // ... 7本のURL配列
  ]
}
```

**ペイロード構築 ノード**:
```json
{
  "inputs": [
    {"type": "video", "url": "https://fal.media/files/lion/test-video-hook-3s.mp4"},
    {"type": "video", "url": "https://fal.media/files/lion/test-video-intro-10s.mp4"}
    // ... 7個の入力オブジェクト
  ],
  "output_format": "mp4",
  "concat_method": "concat",
  "video_codec": "h264",
  "audio_codec": "aac"
}
```

**Submit to FAL ノード**:
```json
{
  "request_id": "fal-ai-ffmpeg-api-xxxxxxxx"
}
```

**Fetch Status ノード** (最終的に):
```json
{
  "status": "COMPLETED",
  "output": {
    "video": {
      "url": "https://fal.media/files/lion/rendered-video.mp4",
      "content_type": "video/mp4",
      "file_size": 12345678
    }
  }
}
```

### 3.4 エラーハンドリング検証

以下のケースをテスト：

1. **空配列エラー**: Pin Dataを空配列 `[]` にして実行 → エラーメッセージ確認
2. **FAL APIタイムアウト**: Fetch Status が20回リトライ後にタイムアウト → Error Handler 確認
3. **レンダリング失敗**: status が "FAILED" の場合 → Error Handler 確認

---

## 🚀 ステップ4: Phase4a→4b→4c E2Eテスト

### 4.1 前提条件

- Phase4a ワークフローが稼働中
- Phase4b ワークフローが稼働中
- Phase4c ワークフロー (chPw11OY5sex6d9I) が設定完了

### 4.2 E2Eテスト実行

#### 4.2.1 Webhook呼び出し

```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-video-script \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "AIの未来",
    "target_audience": "ビジネスパーソン",
    "duration": 60,
    "style": "informative"
  }'
```

#### 4.2.2 実行フロー確認

1. **Phase4a**: 7枚のスライド画像生成 (Pillow) → Notion DB更新
2. **Phase4b**: 7本の動画生成 (FAL Image-to-Video) → Google Drive保存
3. **Phase4c**: 1本の完成動画生成 (FAL FFmpeg) → Google Drive保存 → Notion DB更新

#### 4.2.3 期待される結果

**Phase4c完了後のNotion DB**:
```yaml
status: completed
final_video_url: https://drive.google.com/file/d/...
completed_at: 2025-11-08T12:34:56.789Z
```

**Google Drive**:
- ファイル名: `WF7_Final_test-script-001_20251108_123456.mp4`
- 再生時間: 約60-90秒
- ファイルサイズ: < 50MB

### 4.3 パフォーマンス測定

E2Eテスト実行時に以下を記録：

```yaml
Phase4a実行時間: ~X秒
Phase4b実行時間: ~Y秒 (7本 × Z秒)
Phase4c実行時間: ~W秒
  - FAL Submit: ~2秒
  - レンダリング待機: ~10秒
  - ステータスポーリング: ~N秒
  - ダウンロード: ~5秒
  - Google Driveアップロード: ~10秒
  - Notion更新: ~2秒
合計実行時間: ~X+Y+W秒
```

---

## 🐛 トラブルシューティング

### FAL API エラー

**エラー**: `401 Unauthorized`
- **原因**: FAL APIキーが無効
- **対処**: Settings → Credentials → FAL API Key を確認

**エラー**: `422 Unprocessable Entity`
- **原因**: 動画URLが無効またはアクセス不可
- **対処**: Phase4bの出力URLが正しいことを確認

**エラー**: `Timeout after 200 seconds`
- **原因**: FALのレンダリングが長時間実行中
- **対処**:
  - Fetch Status ノードの `maxRetries` を増やす
  - 動画の長さ/ファイルサイズを確認

### Google Drive エラー

**エラー**: `403 Forbidden`
- **原因**: OAuth2認証が期限切れ
- **対処**: Credentials → Google Drive Account で再認証

**エラー**: `404 Not Found` (Folder ID)
- **原因**: フォルダIDが無効
- **対処**: Google DriveのURLからフォルダIDを再確認

### Notion API エラー

**エラー**: `400 Bad Request` (Update Notion DB)
- **原因**: `script_id` (pageId) が無効
- **対処**: Phase4aで生成されたNotion PageのIDを確認

**エラー**: `401 Unauthorized`
- **原因**: Notion APIトークンが無効
- **対処**: Integration Tokenを再発行

---

## 📊 テスト結果記録テンプレート

```yaml
テスト実行日時: YYYY-MM-DD HH:MM:SS
テスト種別: 単体テスト / E2Eテスト

Phase4c単体テスト:
  ✅ Aggregate Videos: PASS / FAIL
  ✅ ペイロード構築: PASS / FAIL
  ✅ Submit to FAL: PASS / FAIL
  ✅ Fetch Status: PASS / FAIL
  ✅ Render Completed?: PASS / FAIL
  ✅ Download Video: PASS / FAIL
  ✅ Upload to Google Drive: PASS / FAIL
  ✅ Update Notion DB: PASS / FAIL
  ✅ Respond to Webhook: PASS / FAIL

E2Eテスト:
  Phase4a実行時間: X秒
  Phase4b実行時間: Y秒
  Phase4c実行時間: W秒
  合計実行時間: Z秒

  最終動画:
    URL: https://drive.google.com/...
    再生時間: XX秒
    ファイルサイズ: XX MB
    品質: ✅ 良好 / ⚠️ 要改善 / ❌ 不良

エラー:
  - [エラー詳細を記録]

備考:
  - [その他の気づき]
```

---

## 🔗 関連ドキュメント

- `/docs/implementation/WF7-Phase4c-perfect-implementation.md`: Phase4c技術仕様
- `/docs/implementation/WF7-Phase4-FAL実装計画書.md`: Phase4全体計画
- `/docs/knowledge/wf7-phase4-troubleshooting-guide.md`: トラブルシューティングガイド
- `/test-phase4c-mock-data.json`: テストデータ

---

**次のステップ**: 上記の設定を完了後、Phase4c単体テストを実行してください。
