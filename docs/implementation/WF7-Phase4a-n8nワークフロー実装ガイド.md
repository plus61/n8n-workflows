# WF7 Phase 4a: n8nワークフロー実装ガイド

**作成日**: 2025-11-06
**バージョン**: 1.0
**目的**: Pillowスライド画像生成ワークフローのn8n実装手順書

---

## 📋 概要

Phase 4aは、Notion DBのスクリプトデータから7枚のスライド画像を生成し、Google Driveにアップロードするワークフローです。

### 処理フロー

```
Webhook受信
  ↓
Notion DB Query（スクリプト取得）
  ↓
Python Code Node（phase4a_slide_generator.py実行）
  ↓
Split Out（7枚の画像を個別処理）
  ↓
Google Drive Upload（各画像をアップロード）
  ↓
Aggregate（7枚の結果を統合）
  ↓
Set Variables（Phase 4bへデータ渡し）
```

### 入力

- **Webhook**: `script_id` (Notion DB Record ID)

### 出力

- **Google Drive**: 7枚のPNG画像（1080x1920）
- **データ**: 7つの画像URL + メタデータ（section, duration, motion_prompt, text）

---

## 🔧 ノード構成

### 1. Webhook Trigger

**ノード名**: `Webhook - Phase 4a Start`
**ノードタイプ**: `n8n-nodes-base.webhook`

#### 設定

```json
{
  "httpMethod": "POST",
  "path": "wf7-phase4a-slide-generator",
  "responseMode": "responseNode",
  "options": {}
}
```

#### 想定リクエスト

```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4a-slide-generator \
  -H "Content-Type: application/json" \
  -d '{"script_id": "29b68d5c-2986-817f-xxxx"}'
```

#### レスポンスフォーマット

```json
{
  "success": true,
  "script_id": "29b68d5c-2986-817f-xxxx",
  "slides_generated": 7,
  "google_drive_urls": [
    "https://drive.google.com/file/d/xxx/view",
    "..."
  ],
  "slides_metadata": [
    {
      "section": "hook",
      "duration": 3,
      "filename": "slide_1_hook.png",
      "motion_prompt": "dramatic zoom in effect...",
      "text": "あなたのビジネス、本当に見つけられていますか？",
      "google_drive_url": "https://drive.google.com/file/d/xxx/view",
      "google_drive_id": "xxx"
    }
  ]
}
```

---

### 2. Notion DB Query

**ノード名**: `Notion - Get Script Data`
**ノードタイプ**: `n8n-nodes-base.notion`

#### 設定

```json
{
  "resource": "databasePage",
  "operation": "get",
  "pageId": "={{ $json.body.script_id }}",
  "options": {}
}
```

#### Credentials

- **Notion API Credentials**: 既存のWF7用認証情報を使用

#### 出力例

```json
{
  "id": "29b68d5c-2986-817f-xxxx",
  "properties": {
    "hook_text_5options": ["あなたのビジネス、本当に見つけられていますか？"],
    "introduction_text": "多くの地域ビジネスが、Googleマップで見つけられずに機会を失っています",
    "main_point_1": "MEO対策で検索順位を大幅に改善できます",
    "main_point_2": "実際の成功事例では3ヶ月で問い合わせが3倍に",
    "main_point_3": "今すぐ始めれば、競合に差をつけられます",
    "summary_text": "MEO対策は地域ビジネス成長の鍵です",
    "cta_text_3options": ["無料診断を今すぐ申し込む"],
    "Brand Colors": "{\"background\":\"#1a1a2e\",\"primary_text\":\"#ffffff\",...}",
    "Visual Elements": "{\"hook\":{\"icon\":\"⚠️\"},...}",
    "Duration Config": "{\"hook\":3,\"intro\":10,...}",
    "Motion Prompts": "{\"hook\":\"dramatic zoom in effect\",...}"
  }
}
```

---

### 3. Python Code Node

**ノード名**: `Code - Generate Slides with Pillow`
**ノードタイプ**: `n8n-nodes-base.code`

#### 設定

```json
{
  "language": "python",
  "mode": "runOnceForAllItems",
  "pythonCode": "# phase4a_slide_generator.pyのコードをコピー\n\n# エントリーポイント\nslides = generate_slides(items[0]['json']['properties'])\nreturn slides"
}
```

#### ⚠️ 重要な注意事項

1. **フォントパス**: Railway環境のフォントパスを使用
   ```python
   FONT_PATH = "/usr/share/fonts/truetype/noto/NotoSansJP-Regular.ttf"
   FONT_BOLD_PATH = "/usr/share/fonts/truetype/noto/NotoSansJP-Bold.ttf"
   ```

2. **依存関係**: n8n Code Nodeで以下のライブラリが利用可能
   - `Pillow` (PIL)
   - `base64`
   - `io`
   - `json`
   - `textwrap`

3. **メモリ制限**: 7枚の1080x1920画像生成は約50MB必要（Railway 512MB環境で問題なし）

#### 出力例

```json
[
  {
    "section": "hook",
    "duration": 3,
    "image_base64": "iVBORw0KGgoAAAANSUhEUgAAA...",
    "filename": "slide_1_hook.png",
    "motion_prompt": "dramatic zoom in effect, professional business style, sharp focus",
    "text": "あなたのビジネス、本当に見つけられていますか？"
  },
  {
    "section": "intro",
    "duration": 10,
    "image_base64": "iVBORw0KGgoAAAANSUhEUgAAA...",
    "filename": "slide_2_intro.png",
    "motion_prompt": "smooth slide transition, calm professional tone, steady camera",
    "text": "多くの地域ビジネスが、Googleマップで見つけられずに機会を失っています"
  }
  // ... 5 more slides
]
```

---

### 4. Split Out

**ノード名**: `Split Out - Individual Slides`
**ノードタイプ**: `n8n-nodes-base.splitOut`

#### 設定

```json
{
  "options": {}
}
```

#### 説明

7つのスライドを個別のアイテムに分割し、後続のGoogle Drive Uploadノードで並列処理を可能にします。

#### 出力

7つの個別アイテム（各スライド1つずつ）

---

### 5. Google Drive Upload

**ノード名**: `Google Drive - Upload Slide Image`
**ノードタイプ**: `n8n-nodes-base.googleDrive`

#### 設定

```json
{
  "operation": "upload",
  "name": "={{ $json.filename }}",
  "fileContent": {
    "binaryData": false,
    "dataPropertyName": "image_base64"
  },
  "options": {
    "parents": ["WF7 Slides Folder ID"],
    "mimeType": "image/png"
  }
}
```

#### Credentials

- **Google Drive OAuth2**: 既存のWF7用認証情報を使用

#### ⚠️ 重要な注意事項

1. **Base64デコード**: n8nは自動的にbase64文字列をバイナリデータとして扱います
2. **フォルダID事前作成**: Google Driveに「WF7 Slides」フォルダを作成し、IDを設定に記載
3. **命名規則**: `slide_1_hook.png`, `slide_2_intro.png`, ...

#### 出力例

```json
{
  "id": "1abc...xyz",
  "name": "slide_1_hook.png",
  "mimeType": "image/png",
  "webViewLink": "https://drive.google.com/file/d/1abc...xyz/view",
  "webContentLink": "https://drive.google.com/uc?id=1abc...xyz&export=download"
}
```

---

### 6. Aggregate

**ノード名**: `Aggregate - Combine All Slides`
**ノードタイプ**: `n8n-nodes-base.aggregate`

#### 設定

```json
{
  "aggregate": "aggregateAllItemData",
  "options": {}
}
```

#### 説明

7つの個別アイテムを1つの配列にまとめます。

#### 出力例

```json
{
  "aggregatedData": [
    {
      "section": "hook",
      "duration": 3,
      "filename": "slide_1_hook.png",
      "motion_prompt": "dramatic zoom in effect...",
      "text": "あなたのビジネス、本当に見つけられていますか？",
      "google_drive_id": "1abc...xyz",
      "google_drive_url": "https://drive.google.com/file/d/1abc...xyz/view"
    }
    // ... 6 more slides
  ]
}
```

---

### 7. Set Variables

**ノード名**: `Set - Phase 4b Input Data`
**ノードタイプ**: `n8n-nodes-base.set`

#### 設定

```json
{
  "mode": "manual",
  "fields": {
    "values": [
      {
        "name": "script_id",
        "type": "string",
        "value": "={{ $('Notion - Get Script Data').item.json.id }}"
      },
      {
        "name": "slides_metadata",
        "type": "array",
        "value": "={{ $json.aggregatedData }}"
      },
      {
        "name": "slides_count",
        "type": "number",
        "value": "={{ $json.aggregatedData.length }}"
      }
    ]
  }
}
```

#### 出力例

```json
{
  "script_id": "29b68d5c-2986-817f-xxxx",
  "slides_metadata": [
    {
      "section": "hook",
      "duration": 3,
      "filename": "slide_1_hook.png",
      "motion_prompt": "dramatic zoom in effect...",
      "text": "あなたのビジネス、本当に見つけられていますか？",
      "google_drive_id": "1abc...xyz",
      "google_drive_url": "https://drive.google.com/file/d/1abc...xyz/view"
    }
    // ... 6 more slides
  ],
  "slides_count": 7
}
```

---

### 8. Respond to Webhook

**ノード名**: `Respond to Webhook - Success`
**ノードタイプ**: `n8n-nodes-base.respondToWebhook`

#### 設定

```json
{
  "respondWith": "json",
  "responseBody": "={{ JSON.stringify({ success: true, script_id: $json.script_id, slides_generated: $json.slides_count, google_drive_urls: $json.slides_metadata.map(s => s.google_drive_url), slides_metadata: $json.slides_metadata }) }}"
}
```

---

## 🧪 テスト手順

### 1. 単体テスト（Python Code Nodeのみ）

```python
# phase4a_slide_generator.pyをローカルで実行
if __name__ == "__main__":
    sample_data = {
        "hook_text_5options": ["あなたのビジネス、本当に見つけられていますか？"],
        "introduction_text": "多くの地域ビジネスが、Googleマップで見つけられずに機会を失っています",
        "main_point_1": "MEO対策で検索順位を大幅に改善できます",
        "main_point_2": "実際の成功事例では3ヶ月で問い合わせが3倍に",
        "main_point_3": "今すぐ始めれば、競合に差をつけられます",
        "summary_text": "MEO対策は地域ビジネス成長の鍵です",
        "cta_text_3options": ["無料診断を今すぐ申し込む"],
        "Brand Colors": json.dumps(DEFAULT_BRAND_COLORS),
        "Visual Elements": json.dumps({...}),
        "Duration Config": json.dumps({...}),
        "Motion Prompts": json.dumps({...})
    }

    slides = generate_slides(sample_data)
    print(f"✅ {len(slides)}枚のスライドを生成しました")

    # 画像ファイル保存確認
    for slide in slides:
        img_data = base64.b64decode(slide['image_base64'])
        with open(slide['filename'], 'wb') as f:
            f.write(img_data)
        print(f"  ✅ {slide['filename']} 保存完了")
```

### 2. n8n統合テスト

#### Step 1: Webhook → Notion Query

```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4a-slide-generator \
  -H "Content-Type: application/json" \
  -d '{"script_id": "実際のNotion Record ID"}'
```

**期待結果**: Notion Queryノードが正常にデータ取得

#### Step 2: Code Node実行

n8n UIで手動実行し、以下を確認：
- ✅ 7つのスライドが生成される
- ✅ 各スライドに`image_base64`が存在
- ✅ `motion_prompt`が正しく設定される

#### Step 3: Google Drive Upload

- ✅ 7枚の画像がGoogle Driveにアップロードされる
- ✅ ファイル名が正しい（`slide_1_hook.png`など）
- ✅ 画像サイズが1080x1920であることを確認

#### Step 4: E2E テスト

```bash
# 正常系テスト
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4a-slide-generator \
  -H "Content-Type: application/json" \
  -d '{"script_id": "正常なNotion Record ID"}'

# 期待結果
{
  "success": true,
  "script_id": "...",
  "slides_generated": 7,
  "google_drive_urls": [...]
}
```

---

## ⚠️ エラーハンドリング

### 1. Notion Record Not Found

**エラー**: `Notion API: Object not found`

**対処**: Webhook Triggerの後に「IF」ノードを追加

```json
{
  "conditions": {
    "string": [
      {
        "value1": "={{ $json.body.script_id }}",
        "operation": "isNotEmpty"
      }
    ]
  }
}
```

### 2. フォント読み込みエラー

**エラー**: `Cannot open resource`

**対処**: Railway環境でフォント確認

```bash
# Railwayコンソールで実行
ls -la /usr/share/fonts/truetype/noto/NotoSansJP-*.ttf
```

フォントがない場合は、Railwayのセットアップスクリプトに追加：

```dockerfile
RUN apt-get update && apt-get install -y fonts-noto-cjk
```

### 3. Google Drive Quota Exceeded

**エラー**: `User rate limit exceeded`

**対処**: リトライロジック追加

```json
{
  "retryOnFail": true,
  "maxTries": 3,
  "waitBetweenTries": 5000
}
```

---

## 📊 パフォーマンス指標

### 目標値

- **処理時間**: <30秒（7枚の画像生成 + アップロード）
- **メモリ使用**: <100MB
- **成功率**: 99%+

### 実測値の取得方法

n8n UIの「Execution Time」パネルで各ノードの実行時間を確認：

```
Webhook: <1s
Notion Query: ~2s
Code Node: ~15s (画像生成)
Split Out: <1s
Google Drive Upload: ~2s × 7 = ~14s (並列処理)
Aggregate: <1s
Set Variables: <1s
Total: ~28s
```

---

## 🔐 セキュリティ

### 1. Webhook認証

**推奨**: Railway環境変数で認証トークン設定

```json
{
  "authentication": "headerAuth",
  "headerAuth": {
    "name": "X-WF7-Auth-Token",
    "value": "={{ $env.WF7_WEBHOOK_TOKEN }}"
  }
}
```

### 2. Google Drive権限

**推奨**: サービスアカウント使用
- 最小権限の原則（`drive.file` scope のみ）
- WF7専用フォルダへのアクセス制限

---

## 📝 次のステップ

Phase 4a完了後、以下を実施：

1. ✅ **Todo #6完了**: n8nワークフロー実装ガイド作成完了
2. ⏳ **Todo #7**: 7枚の画像生成テスト実施と品質確認
3. ⏳ **Todo #8**: Phase 4b FAL API統合実装開始

---

**作成者**: Claude Code (Sonnet 4.5)
**更新日**: 2025-11-06
**関連ドキュメント**:
- WF7-Phase4-FAL実装計画書.md
- phase4a_slide_generator.py
- Phase2-3-ChatGPT-STEP11-追加プロンプト.md
