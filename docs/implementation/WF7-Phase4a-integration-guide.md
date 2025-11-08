# WF7 Phase4a 統合実装ガイド

**作成日**: 2025-11-08  
**対象ワークフロー**: WF7phase4_v3 (`qSN7EHj5yl0nPXij`)  
**目的**: Phase4a（スライド画像生成）を既存ワークフローに統合

---

## 📋 統合概要

既存の「データ統合」ノードの後に、Phase4aのスライド生成処理を挿入します。

### 統合ポイント

```
Webhook → Notion API呼び出し → URL抽出 → データ統合
                                                      ↓
                                    [Phase4a挿入ポイント]
                                                      ↓
                                    Code - Generate Slides
                                                      ↓
                                    Split Out → Drive Upload → Aggregate
                                                      ↓
                                    Set - Phase4a Payload
                                                      ↓
                                    [既存のSplit Outへ接続]
```

---

## 🔧 実装手順

### Step 1: Notion DBスキーマ確認

**確認項目**:
- `Motion Prompts` (JSON型またはrich_text型)
- `Duration Config` (JSON型またはrich_text型)
- `Visual Elements` (JSON型またはrich_text型)
- `Brand Colors` (JSON型またはrich_text型)

**注意**: これらのカラムが存在しない場合でも、`phase4a_slide_generator.py`はデフォルト値を使用するため動作しますが、推奨はしません。

---

### Step 2: Code Node追加

**ノード名**: `Code - Generate Slides with Pillow`  
**位置**: 「データ統合」ノードの直後  
**ノードタイプ**: `n8n-nodes-base.code`

#### 設定

```json
{
  "language": "python",
  "mode": "runOnceForAllItems",
  "pythonCode": "// phase4a_slide_generator.pyのコードをここにコピー\n\n# エントリーポイント\nfrom phase4a_slide_generator import generate_slides\n\n# データ統合ノードからの出力を取得\nnotionPageData = items[0]['json']\n\n# Notionページのpropertiesを取得（既存のNotion API呼び出しノードから）\n# 注意: 実際のデータ構造に応じて調整が必要\nnotionProps = notionPageData.get('properties', {})\n\n# スライド生成\nslides = generate_slides(notionProps)\n\n# 7つのスライドを個別アイテムとして返す\nreturn slides"
}
```

#### 実際の実装コード

`workflows/wf7-video-renderer/phase4a_slide_generator.py`の内容をCode Nodeに直接コピーし、以下のエントリーポイントを追加:

```python
# n8n Code Node用エントリーポイント
# phase4a_slide_generator.pyの全コードをここにコピー

# データ統合ノードからの出力を処理
notionPageData = items[0]['json']

# Notionページのpropertiesを取得
# 注意: 実際のワークフローでは、Notion API呼び出しノードの出力構造に応じて調整
notionProps = {}
if 'properties' in notionPageData:
    notionProps = notionPageData['properties']
elif 'scriptData' in notionPageData:
    # 既存のデータ統合ノードの出力構造に対応
    notionProps = notionPageData.get('scriptData', {})

# スライド生成
slides = generate_slides(notionProps)

# 7つのスライドを個別アイテムとして返す
return slides
```

---

### Step 3: データ統合ノードの出力構造確認

現在の「データ統合」ノードは以下の形式で出力しています:

```json
{
  "notionPageId": "...",
  "articleId": "...",
  "scriptData": {...},
  "assetsData": [...]
}
```

Phase4aでは、`scriptData`に加えて、Notionページの`properties`から直接データを取得する必要があります。

**解決策**: 「データ統合」ノードの前に、Notionページのpropertiesを保持するSetノードを追加するか、「データ統合」ノードを拡張してpropertiesも含める。

---

### Step 4: Split Outノード追加

**ノード名**: `Split Out - Individual Slides`  
**位置**: `Code - Generate Slides with Pillow`の後  
**ノードタイプ**: `n8n-nodes-base.splitOut`

#### 設定

```json
{
  "options": {}
}
```

**説明**: Code Nodeが返す7つのスライド配列を、個別のアイテムに分割します。

---

### Step 5: Google Drive Upload実装

**ノード名**: `Google Drive - Upload Slide Image`  
**位置**: `Split Out`の後  
**ノードタイプ**: `n8n-nodes-base.googleDrive`

#### 設定

```json
{
  "operation": "upload",
  "name": "={{ $json.filename }}",
  "binaryData": true,
  "binaryPropertyName": "image_base64",
  "options": {
    "parents": ["WF7_SLIDES_FOLDER_ID"],
    "mimeType": "image/png"
  }
}
```

**注意**: 
- `image_base64`はbase64文字列として扱う必要があります
- Google DriveフォルダIDは事前に作成し、環境変数または定数として設定

---

### Step 6: Aggregateノード追加

**ノード名**: `Aggregate - Combine All Slides`  
**位置**: `Google Drive Upload`の後  
**ノードタイプ**: `n8n-nodes-base.aggregate`

#### 設定

```json
{
  "aggregate": "aggregateAllItemData",
  "options": {}
}
```

**出力形式**:

```json
{
  "aggregatedData": [
    {
      "section": "hook",
      "duration": 3,
      "filename": "slide_1_hook.png",
      "motion_prompt": "...",
      "text": "...",
      "google_drive_id": "...",
      "google_drive_url": "...",
      "image_url": "https://drive.google.com/uc?export=download&id=..."
    }
    // ... 6 more slides
  ]
}
```

---

### Step 7: Set - Phase4a Payloadノード追加

**ノード名**: `Set - Phase4a Payload`  
**位置**: `Aggregate`の後  
**ノードタイプ**: `n8n-nodes-base.set`

#### 設定

```json
{
  "assignments": {
    "assignments": [
      {
        "name": "script_id",
        "value": "={{ $('データ統合').item.json.notionPageId }}",
        "type": "string"
      },
      {
        "name": "slides_metadata",
        "value": "={{ $json.aggregatedData.map(item => ({ section: item.section, duration: item.duration, image_url: item.image_url || 'https://drive.google.com/uc?export=download&id=' + item.google_drive_id, motion_prompt: item.motion_prompt, drive_file_id: item.google_drive_id, filename: item.filename })) }}",
        "type": "array"
      }
    ]
  }
}
```

**出力形式**:

```json
{
  "script_id": "29b68d5c-2986-817f-xxxx",
  "slides_metadata": [
    {
      "section": "hook",
      "duration": 3,
      "image_url": "https://drive.google.com/uc?export=download&id=...",
      "motion_prompt": "dramatic zoom in effect...",
      "drive_file_id": "1abc...",
      "filename": "slide_1_hook.png"
    }
    // ... 6 more slides
  ]
}
```

---

### Step 8: 既存ワークフローへの接続

`Set - Phase4a Payload`ノードの出力を、既存の「Split Out」ノード（アセット処理用）の代わりに、Phase4b処理へ接続します。

**注意**: 既存の「Split Out」ノードは、Phase4aの`slides_metadata`を受け取るように変更する必要があります。

---

## ⚠️ 重要な注意事項

1. **Notionページのproperties取得**: 現在の「データ統合」ノードは`scriptData`と`assetsData`のみを出力しています。Phase4aで必要な`motion_prompts`、`duration_config`などは、Notionページの`properties`から直接取得する必要があります。

2. **データ統合ノードの拡張**: 「データ統合」ノードを拡張して、Notionページのpropertiesも含めるように修正することを推奨します。

3. **エラーハンドリング**: Phase4a失敗時は、`IF - Phase4a Status`ノードでエラーを検出し、`Notion status = error`を設定して`Respond to Webhook`を即返却します。

---

## 🧪 テスト手順

1. **単体テスト**: Code Nodeのみを手動実行し、7枚のスライドが生成されることを確認
2. **統合テスト**: Phase4aノード群を実行し、Google Driveへのアップロードを確認
3. **E2Eテスト**: WebhookからPhase4aまで実行し、`slides_metadata`が正しく生成されることを確認

---

## 📝 次のステップ

Phase4a実装完了後、Phase4b（FAL Image-to-Video）の実装に進みます。

