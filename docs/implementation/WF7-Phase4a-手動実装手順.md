# WF7 Phase4a 手動実装手順

**作成日**: 2025-11-08  
**対象ワークフロー**: `WF7phase4_v3` (ID: `qSN7EHj5yl0nPXij`)  
**目的**: Phase4aのスライド生成機能をn8n UIで手動実装する手順書

---

## 📋 実装概要

Phase4aでは、`データ統合`ノードの後に、7枚のスライド画像を生成するCode Nodeを追加します。

### 実装フロー

```
データ統合
  ↓
Code - Generate Slides with Pillow (新規追加)
  ↓
Split Out - Slides (新規追加)
  ↓
Google Drive - Upload Slide Image (新規追加)
  ↓
Aggregate - Combine All Slides (新規追加)
  ↓
Set - Phase4a Payload (新規追加)
  ↓
既存のSplit Out (assetsData用) - 変更なし
```

---

## 🔧 Step 1: Code Node追加

### 1.1 ノード追加

1. n8n UIで `WF7phase4_v3` ワークフローを開く
2. `データ統合`ノードを選択
3. 右側に新しいノードを追加
4. ノードタイプ: **Code** を選択
5. ノード名: `Code - Generate Slides with Pillow`

### 1.2 ノード設定

**Language**: Python  
**Mode**: `Run Once for All Items`

**Python Code**: `workflows/wf7-video-renderer/phase4a_code_node.py` の内容をコピー&ペースト

**重要**: エントリーポイント部分を以下のように修正:

```python
# ============================================
# n8n Code Node用エントリーポイント
# ============================================
try:
    # データ統合ノードからの出力を取得
    dataIntegrationOutput = items[0]['json']
    
    # scriptDataを取得
    scriptData = dataIntegrationOutput.get('scriptData', {})
    
    # スライド生成
    slides = generate_slides(scriptData)
    
    # 7つのスライドを個別アイテムとして返す
    return slides
    
except Exception as e:
    # エラーハンドリング
    error_msg = f"Phase4aスライド生成エラー: {str(e)}"
    print(error_msg)
    return []
```

### 1.3 接続設定

- `データ統合` → `Code - Generate Slides with Pillow` を接続
- 既存の `データ統合` → `Split Out` の接続は**一時的に保持**（後で変更）

---

## 🔧 Step 2: Split Outノード追加

### 2.1 ノード追加

1. `Code - Generate Slides with Pillow` ノードの右側に新しいノードを追加
2. ノードタイプ: **Split Out** を選択
3. ノード名: `Split Out - Slides`

### 2.2 ノード設定

**Field to Split Out**: 設定不要（Code Nodeが配列を返すため、自動的に分割される）

### 2.3 接続設定

- `Code - Generate Slides with Pillow` → `Split Out - Slides` を接続

---

## 🔧 Step 3: Google Drive Uploadノード追加

### 3.1 ノード追加

1. `Split Out - Slides` ノードの右側に新しいノードを追加
2. ノードタイプ: **Google Drive** を選択
3. ノード名: `Google Drive - Upload Slide Image`

### 3.2 ノード設定

**Operation**: Upload  
**Name**: `={{ $json.filename }}`  
**Binary Data**: ✅ 有効  
**Binary Property Name**: `image_base64`

**Options**:
- **Parents**: `WF7_SLIDES_FOLDER_ID` (実際のフォルダIDに置き換え)
- **Mime Type**: `image/png`

**Credentials**: 既存のGoogle Drive認証情報を使用

### 3.3 base64デコード処理

Google Drive Uploadノードはbase64文字列を直接受け取れないため、前段でデコードが必要です。

**解決策**: `Split Out - Slides` と `Google Drive - Upload Slide Image` の間に、**Code Node**を追加してbase64デコード:

**ノード名**: `Code - Decode Base64 Image`

**Python Code**:
```python
import base64
import io

# 入力データ取得
image_base64 = items[0]['json'].get('image_base64', '')
filename = items[0]['json'].get('filename', 'slide.png')

# base64デコード
try:
    image_data = base64.b64decode(image_base64)
    
    # バイナリデータとして返す
    return [{
        'json': {
            'filename': filename,
            'section': items[0]['json'].get('section'),
            'duration': items[0]['json'].get('duration'),
            'motion_prompt': items[0]['json'].get('motion_prompt'),
            'text': items[0]['json'].get('text')
        },
        'binary': {
            'data': {
                'data': image_data,
                'mimeType': 'image/png',
                'fileName': filename
            }
        }
    }]
except Exception as e:
    print(f"base64デコードエラー: {e}")
    return []
```

### 3.4 接続設定

- `Split Out - Slides` → `Code - Decode Base64 Image` → `Google Drive - Upload Slide Image`

**Google Drive Uploadノードの設定変更**:
- **Binary Property Name**: `data` (Code Nodeの出力に合わせる)

---

## 🔧 Step 4: Aggregateノード追加

### 4.1 ノード追加

1. `Google Drive - Upload Slide Image` ノードの右側に新しいノードを追加
2. ノードタイプ: **Aggregate** を選択
3. ノード名: `Aggregate - Combine All Slides`

### 4.2 ノード設定

**Aggregate**: `Aggregate All Item Data`  
**Options**: デフォルト設定

### 4.3 接続設定

- `Google Drive - Upload Slide Image` → `Aggregate - Combine All Slides` を接続

---

## 🔧 Step 5: Set - Phase4a Payloadノード追加

### 5.1 ノード追加

1. `Aggregate - Combine All Slides` ノードの右側に新しいノードを追加
2. ノードタイプ: **Set** を選択
3. ノード名: `Set - Phase4a Payload`

### 5.2 ノード設定

**Assignments**:

1. **script_id** (String)
   - Value: `={{ $('データ統合').item.json.notionPageId }}`

2. **slides_metadata** (Array)
   - Value: 
   ```javascript
   ={{ $json.aggregatedData.map(item => ({
     section: item.section,
     duration: item.duration,
     image_url: item.json.webContentLink || item.json.webViewLink || 'https://drive.google.com/uc?export=download&id=' + item.json.id,
     motion_prompt: item.motion_prompt,
     drive_file_id: item.json.id,
     filename: item.filename
   })) }}
   ```

### 5.3 接続設定

- `Aggregate - Combine All Slides` → `Set - Phase4a Payload` を接続

---

## 🔧 Step 6: 既存ワークフローとの統合

### 6.1 接続変更

現在の接続:
- `データ統合` → `Split Out` (assetsData用)

新しい接続:
- `データ統合` → `Code - Generate Slides with Pillow` (Phase4a用)
- `Set - Phase4a Payload` → `Split Out` (assetsData用) - **変更が必要**

### 6.2 データ統合ノードの出力を両方のパスに渡す

**解決策**: `データ統合`ノードの出力を2つのパスに分岐させる

1. `データ統合` → `Code - Generate Slides with Pillow` (Phase4a用)
2. `データ統合` → `Split Out` (assetsData用) - **既存接続を保持**

**注意**: `Split Out`ノードは既存の`assetsData`を処理するため、Phase4aの`slides_metadata`とは別パスで処理する必要があります。

### 6.3 Phase4bへの接続準備

`Set - Phase4a Payload`の出力（`slides_metadata`）は、Phase4bで使用されます。現時点では、このノードの出力を一時的に保持するか、テスト用のWebhook Responseノードを追加してください。

---

## 🧪 テスト手順

### 1. Code Node単体テスト

1. `Code - Generate Slides with Pillow`ノードを手動実行
2. 出力を確認:
   - 7つのアイテムが返されること
   - 各アイテムに `section`, `duration`, `image_base64`, `filename`, `motion_prompt` が含まれること

### 2. Google Driveアップロード確認

1. `Split Out - Slides` → `Code - Decode Base64 Image` → `Google Drive - Upload Slide Image` まで実行
2. Google Driveで確認:
   - 7枚のスライド画像がアップロードされていること
   - ファイル名が正しいこと（`slide_1_hook.png`, `slide_2_intro.png`, など）

### 3. slides_metadata出力確認

1. `Set - Phase4a Payload`ノードの出力を確認
2. 期待される出力:
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
       },
       // ... 6 more slides
     ]
   }
   ```

---

## ⚠️ 注意事項

1. **Google DriveフォルダID**: `WF7_SLIDES_FOLDER_ID`は実際のフォルダIDに置き換えてください。

2. **base64デコード**: Google Drive Uploadノードはbase64文字列を直接受け取れないため、Code Nodeでデコードが必要です。

3. **データフロー**: Phase4aの`slides_metadata`と既存の`assetsData`は別パスで処理されます。Phase4bでは`slides_metadata`を使用します。

4. **エラーハンドリング**: Code Nodeでエラーが発生した場合、空配列を返すため、後続ノードでエラーハンドリングが必要です。

---

## 📝 次のステップ

Phase4a実装完了後、Phase4b（FAL Image-to-Video）の実装に進みます。

**参照ドキュメント**:
- `docs/implementation/WF7-Phase4-FAL実装計画書.md`
- `docs/implementation/WF7-Phase4a-integration-guide.md`
- `workflows/wf7-video-renderer/phase4a_code_node.py`

