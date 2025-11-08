# WF7 Phase4b テストデータ作成ガイド

**作成日**: 2025-11-08  
**目的**: Phase4cのテスト実行用に、Phase4b完了後のデータ形式を作成する方法を説明

---

## 📋 Phase4b完了データの形式

Phase4bが正常に完了すると、以下の形式のデータが返されます：

```json
{
  "success": true,
  "script_id": "29b68d5c-2986-817f-xxxx-xxxxxxxxxxxx",
  "videos_metadata": [
    {
      "section": "hook",
      "duration": 3,
      "video_url": "https://v3b.fal.media/files/b/penguin/xxxxx_output.mp4",
      "fal_request_id": "uuid-here",
      "motion_prompt": "dramatic zoom in effect...",
      "filename": "video_1_hook.mp4",
      "text": "フックテキスト",
      "slide_index": 0,
      "script_id": "29b68d5c-2986-817f-xxxx-xxxxxxxxxxxx"
    },
    {
      "section": "intro",
      "duration": 10,
      "video_url": "https://v3b.fal.media/files/b/rabbit/xxxxx_output.mp4",
      ...
    },
    // ... point1, point2, point3, summary, cta の5つ
  ],
  "videos_count": 7,
  "total_duration": 80
}
```

### 必須フィールド

Phase4cで使用される必須フィールド：

- `script_id`: NotionページID（文字列）
- `videos_metadata`: 動画メタデータ配列（7本）
  - `section`: セクション名（`hook`, `intro`, `point1`, `point2`, `point3`, `summary`, `cta`）
  - `duration`: 動画の長さ（秒、数値）
  - `video_url`: 動画のURL（文字列）

### オプションフィールド

- `articleId`: 記事ID（文字列、オプション）
- `videos_count`: 動画数（数値、通常7）
- `total_duration`: 合計時間（秒、数値）

---

## 🎯 Phase4b完了データの作成方法

### 方法1: 実際のPhase4bを実行する（推奨）

実際のPhase4bワークフローを実行して、完了後のデータを取得します。

#### Step 1: Phase4bワークフローを実行

1. **Phase4bワークフローを開く**
   - n8n UIでPhase4bワークフローを開く
   - ワークフローID: `wHaKi98mTlUvFIOR`（Phase4b単体ワークフロー）

2. **Webhookをトリガー**
   ```bash
   curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4b-start \
     -H "Content-Type: application/json" \
     -d '{
       "script_id": "29b68d5c-2986-817f-xxxx-xxxxxxxxxxxx",
       "slides_metadata": [
         {
           "section": "hook",
           "duration": 3,
           "image_base64": "...",
           "motion_prompt": "...",
           "text": "..."
         },
         // ... 残り6スライド
       ]
     }'
   ```

3. **実行結果を確認**
   - n8n UIで実行履歴を確認
   - `Respond to Webhook - Success`ノードの出力を確認
   - レスポンスデータをコピー

#### Step 2: レスポンスデータを保存

Phase4bのレスポンスデータをJSONファイルとして保存：

```bash
# レスポンスをファイルに保存
curl -X POST ... > phase4b_response.json
```

---

### 方法2: Phase4a → Phase4bを連続実行する

Phase4aとPhase4bを連続実行して、実際のデータフローを確認します。

#### Step 1: Phase4aを実行

```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4a-start \
  -H "Content-Type: application/json" \
  -d '{
    "notionPageId": "29b68d5c-2986-817f-xxxx-xxxxxxxxxxxx"
  }'
```

#### Step 2: Phase4aのレスポンスからPhase4bを実行

Phase4aのレスポンスから`slides_metadata`を取得し、Phase4bを実行：

```bash
# Phase4aのレスポンスを取得
PHASE4A_RESPONSE=$(curl -X POST ...)

# slides_metadataを抽出してPhase4bを実行
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4b-start \
  -H "Content-Type: application/json" \
  -d "{
    \"script_id\": \"29b68d5c-2986-817f-xxxx-xxxxxxxxxxxx\",
    \"slides_metadata\": $(echo $PHASE4A_RESPONSE | jq '.slides_metadata')
  }"
```

#### Step 3: Phase4bのレスポンスを保存

Phase4bのレスポンスをJSONファイルとして保存：

```bash
curl -X POST ... > phase4b_response.json
```

---

### 方法3: テスト用モックデータを作成する

実際のPhase4bを実行せずに、テスト用のモックデータを作成します。

#### Step 1: テンプレートファイルをコピー

既存のテストデータテンプレートを使用：

```bash
cp test-phase4c-payload.json my-test-data.json
```

#### Step 2: 動画URLを更新

実際のFAL動画URLに置き換えます：

```json
{
  "script_id": "your-notion-page-id",
  "articleId": "your-article-id",
  "videos_metadata": [
    {
      "section": "hook",
      "duration": 3,
      "video_url": "https://v3b.fal.media/files/b/penguin/YOUR_ACTUAL_VIDEO_ID.mp4"
    },
    // ... 残り6本の動画URLを更新
  ]
}
```

#### Step 3: 動画URLの取得方法

**FAL APIで生成された動画URL**:
- Phase4bの実行結果から取得
- FAL APIのレスポンスから`video_url`を抽出
- または、既存のFAL動画URLを使用

**Google Driveの動画URL**:
- Google Driveにアップロードされた動画のURL
- 形式: `https://drive.google.com/file/d/FILE_ID/view`
- Phase4cでは自動的にダウンロード可能な形式に変換されます

---

## 📝 テストデータの検証

作成したテストデータが正しい形式か確認します：

### 必須チェック項目

- [ ] `script_id`が設定されている
- [ ] `videos_metadata`が配列形式である
- [ ] `videos_metadata`に7本の動画が含まれている
- [ ] 各動画に`section`が設定されている（`hook`, `intro`, `point1`, `point2`, `point3`, `summary`, `cta`）
- [ ] 各動画に`duration`が設定されている（数値）
- [ ] 各動画に`video_url`が設定されている（有効なURL）

### セクション順序の確認

`videos_metadata`は以下の順序である必要があります：

1. `hook`
2. `intro`
3. `point1`
4. `point2`
5. `point3`
6. `summary`
7. `cta`

### 動画URLの検証

各動画URLが有効か確認：

```bash
# 動画URLがアクセス可能か確認
curl -I https://v3b.fal.media/files/b/penguin/xxxxx_output.mp4

# HTTP 200 OKが返されることを確認
```

---

## 🔧 Phase4cでの使用方法

### 方法1: Pin Dataとして設定（n8n UI）

1. `Code - Phase4c FFmpeg Concat`ノードを開く
2. **"Pin Data"**タブを選択
3. 以下の形式でデータを設定：

```json
[
  {
    "json": {
      "script_id": "test-script-phase4c-001",
      "articleId": "test-article-001",
      "videos_metadata": [
        {
          "section": "hook",
          "duration": 3,
          "video_url": "https://v3b.fal.media/files/b/penguin/xxxxx_output.mp4"
        },
        // ... 残り6本
      ]
    }
  }
]
```

### 方法2: Webhook経由で実行

Phase4b完了後のデータをそのまま使用：

```bash
# Phase4bのレスポンスをそのままPhase4cに渡す
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-video-script \
  -H "Content-Type: application/json" \
  -d @phase4b_response.json
```

---

## 📋 サンプルテストデータ

### 最小限のテストデータ

```json
{
  "script_id": "test-script-phase4c-001",
  "videos_metadata": [
    {
      "section": "hook",
      "duration": 3,
      "video_url": "https://v3b.fal.media/files/b/penguin/X6YpaYnUTrgdaoUwG1RpN_output.mp4"
    },
    {
      "section": "intro",
      "duration": 10,
      "video_url": "https://v3b.fal.media/files/b/rabbit/W0yXmayD3qLoY9pCzcZGr_output.mp4"
    },
    {
      "section": "point1",
      "duration": 13,
      "video_url": "https://v3b.fal.media/files/b/penguin/X6YpaYnUTrgdaoUwG1RpN_output.mp4"
    },
    {
      "section": "point2",
      "duration": 13,
      "video_url": "https://v3b.fal.media/files/b/rabbit/W0yXmayD3qLoY9pCzcZGr_output.mp4"
    },
    {
      "section": "point3",
      "duration": 14,
      "video_url": "https://v3b.fal.media/files/b/penguin/X6YpaYnUTrgdaoUwG1RpN_output.mp4"
    },
    {
      "section": "summary",
      "duration": 20,
      "video_url": "https://v3b.fal.media/files/b/rabbit/W0yXmayD3qLoY9pCzcZGr_output.mp4"
    },
    {
      "section": "cta",
      "duration": 7,
      "video_url": "https://v3b.fal.media/files/b/penguin/X6YpaYnUTrgdaoUwG1RpN_output.mp4"
    }
  ]
}
```

### 完全なテストデータ（オプションフィールド含む）

```json
{
  "success": true,
  "script_id": "29b68d5c-2986-817f-xxxx-xxxxxxxxxxxx",
  "articleId": "article-001",
  "videos_metadata": [
    {
      "section": "hook",
      "duration": 3,
      "video_url": "https://v3b.fal.media/files/b/penguin/xxxxx_output.mp4",
      "fal_request_id": "uuid-here",
      "motion_prompt": "dramatic zoom in effect, professional business style, sharp focus",
      "filename": "video_1_hook.mp4",
      "text": "あなたのビジネス、本当に見つけられていますか？",
      "slide_index": 0,
      "script_id": "29b68d5c-2986-817f-xxxx-xxxxxxxxxxxx"
    },
    // ... 残り6本
  ],
  "videos_count": 7,
  "total_duration": 80
}
```

---

## ⚠️ 注意事項

### 動画URLの有効期限

- FAL APIで生成された動画URLには有効期限がある場合があります
- テスト実行前に動画URLが有効か確認してください
- 無効なURLの場合、Phase4cでダウンロードエラーが発生します

### script_idの形式

- `script_id`はNotionページIDである必要があります
- UUID形式: `29b68d5c-2986-817f-xxxx-xxxxxxxxxxxx`
- テスト用には任意の文字列でも動作しますが、Notion DB更新時には有効なページIDが必要です

### セクション名の正確性

- セクション名は正確に一致する必要があります（大文字小文字を含む）
- `hook`, `intro`, `point1`, `point2`, `point3`, `summary`, `cta`の7つ
- 順序は任意ですが、Phase4cでは順序通りに結合されます

---

## 🔗 関連ドキュメント

- `docs/testing/WF7-Phase4c-テスト実行手順.md`: Phase4cテスト実行手順
- `test-phase4c-payload.json`: テストデータサンプル
- `docs/implementation/WF7-Phase4b-integration-instructions.md`: Phase4b統合指示書
- `docs/testing/wf7-phase4b-e2e-test-report.md`: Phase4b E2Eテストレポート

---

**作成者**: Claude Code (Composer)  
**更新日**: 2025-11-08  
**次のステップ**: テストデータを作成後、Phase4cのテスト実行を実施

