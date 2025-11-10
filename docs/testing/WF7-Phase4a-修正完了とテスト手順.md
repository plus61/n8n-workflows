# WF7 Phase4a 修正完了とテスト手順

**作成日**: 2025-11-09  
**修正内容**: Phase4aの1枚しか出力されない問題を修正  
**対象ワークフロー**: `WF7 Phase4a - Slide Generator` (`wf7_phase4a.json`)

---

## 🔧 修正内容

### 1. Split Outノードの設定を修正

**問題**: `include: "noOtherFields"`が設定されていたため、出力が0になっていた

**修正**:
- `include: "noOtherFields"`を削除
- `fieldToSplitOut`を削除（Code Nodeが配列を返す場合、自動的に分割される）

**修正前**:
```json
{
  "parameters": {
    "fieldToSplitOut": "={{ $json }}",
    "include": "noOtherFields",
    "options": {}
  }
}
```

**修正後**:
```json
{
  "parameters": {
    "options": {}
  }
}
```

### 2. Code NodeにMode設定を追加

**問題**: Code Nodeが配列を返す際に、正しく動作するためにMode設定が必要

**修正**:
- `mode: "runOnceForAllItems"`を追加

**修正前**:
```json
{
  "parameters": {
    "language": "python",
    "pythonCode": "..."
  }
}
```

**修正後**:
```json
{
  "parameters": {
    "language": "python",
    "mode": "runOnceForAllItems",
    "pythonCode": "..."
  }
}
```

### 3. Code - Merge Slide Metadataノードの出力を改善

**問題**: `filename`と`drive_file_id`が出力に含まれていなかった

**修正**:
- `filename`と`drive_file_id`を追加

**修正前**:
```javascript
return {
  json: {
    section: slideMetadata.section,
    duration: slideMetadata.duration,
    motion_prompt: slideMetadata.motion_prompt,
    image_url: `https://drive.google.com/uc?export=download&id=${driveData.id}`
  }
};
```

**修正後**:
```javascript
return {
  json: {
    section: slideMetadata.section,
    duration: slideMetadata.duration,
    motion_prompt: slideMetadata.motion_prompt,
    filename: slideMetadata.filename,
    image_url: `https://drive.google.com/uc?export=download&id=${driveData.id}`,
    drive_file_id: driveData.id
  }
};
```

### 4. Respond to Webhookノードのレスポンス式を修正

**問題**: `google_drive_url`フィールドが存在しない可能性がある

**修正**:
- `image_url || google_drive_url`を使用して、どちらのフィールドでも対応できるように修正

**修正前**:
```javascript
google_drive_urls: $json.slides_metadata.map(s => s.google_drive_url)
```

**修正後**:
```javascript
google_drive_urls: $json.slides_metadata.map(s => s.image_url || s.google_drive_url)
```

---

## 📋 修正後の動作フロー

1. **Webhook - Phase 4a Start**: リクエストを受信
2. **Notion - Get Script Data**: Notionページのデータを取得
3. **Code - Generate Slides with Pillow**: 7枚のスライド画像を生成（`mode: runOnceForAllItems`）
4. **Split Out - Individual Slides**: 7つのアイテムに分割（`include: noOtherFields`を削除）
5. **Code - Convert to Binary**: Base64画像をバイナリデータに変換
6. **Google Drive - Upload Slide Image**: 7枚の画像をアップロード
7. **Code - Merge Slide Metadata**: メタデータとGoogle Drive URLをマージ
8. **Aggregate - Combine All Slides**: 7枚の結果を統合
9. **Set - Phase 4b Input Data**: Phase4b用のデータを設定
10. **Respond to Webhook - Success**: レスポンスを返す

---

## 🧪 テスト手順

### Step 1: ワークフローをn8nにインポート

1. n8n UIを開く
2. ワークフローをインポート: `workflows/wf7_phase4a.json`
3. ワークフローをアクティブにする

### Step 2: テスト実行

**テスト用NotionページID**: `2a068d5c-2986-81a3-ab0c-ff0bc1e4ebb9`

**方法1: curlコマンドで実行**
```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4a-slide-generator \
  -H "Content-Type: application/json" \
  -d '{"script_id": "2a068d5c-2986-81a3-ab0c-ff0bc1e4ebb9"}'
```

**方法2: テストスクリプトを使用**
```bash
./test-phase4a-7slides.sh 2a068d5c-2986-81a3-ab0c-ff0bc1e4ebb9
```

### Step 3: 実行結果の確認

n8n UIで以下のノードの出力を確認してください：

1. **Code - Generate Slides with Pillow**
   - ✅ 7つのアイテムが出力されているか
   - ✅ 各アイテムに`section`, `duration`, `image_base64`, `filename`, `motion_prompt`, `text`が含まれているか

2. **Split Out - Individual Slides**
   - ✅ 7つのアイテムに分割されているか
   - ✅ 出力数が7であるか

3. **Code - Convert to Binary**
   - ✅ 7回実行されているか
   - ✅ 各アイテムに`binary.data`が含まれているか

4. **Google Drive - Upload Slide Image**
   - ✅ 7回実行されているか
   - ✅ 各実行でGoogle DriveファイルIDが取得できているか

5. **Aggregate - Combine All Slides**
   - ✅ 7枚の結果が統合されているか
   - ✅ `$json.data`が7要素の配列になっているか

6. **Set - Phase 4b Input Data**
   - ✅ `slides_count`が7であるか
   - ✅ `slides_metadata`が7要素の配列であるか
   - ✅ 各スライドに`section`, `duration`, `image_url`, `motion_prompt`, `filename`, `drive_file_id`が含まれているか

7. **Respond to Webhook - Success**
   - ✅ レスポンスが返されているか
   - ✅ `success: true`であるか
   - ✅ `slides_generated: 7`であるか
   - ✅ `slides_metadata`が7要素の配列であるか

---

## ✅ 期待される結果

### レスポンス例

```json
{
  "success": true,
  "script_id": "2a068d5c-2986-81a3-ab0c-ff0bc1e4ebb9",
  "slides_generated": 7,
  "google_drive_urls": [
    "https://drive.google.com/uc?export=download&id=...",
    "https://drive.google.com/uc?export=download&id=...",
    // ... 7本のURL
  ],
  "slides_metadata": [
    {
      "section": "hook",
      "duration": 3,
      "motion_prompt": "...",
      "filename": "slide_1_hook.png",
      "image_url": "https://drive.google.com/uc?export=download&id=...",
      "drive_file_id": "..."
    },
    {
      "section": "intro",
      "duration": 10,
      "motion_prompt": "...",
      "filename": "slide_2_intro.png",
      "image_url": "https://drive.google.com/uc?export=download&id=...",
      "drive_file_id": "..."
    },
    // ... 5 more slides
  ]
}
```

---

## 🐛 トラブルシューティング

### 問題1: レスポンスが空

**原因**: ワークフローがn8nにインポートされていない、またはアクティブになっていない

**解決方法**:
1. n8n UIでワークフローが存在するか確認
2. ワークフローがアクティブになっているか確認
3. Webhook URLが正しいか確認

### 問題2: Split Outノードの出力が0

**原因**: `include: "noOtherFields"`が設定されている

**解決方法**:
- Split Outノードの設定を確認し、`include`フィールドを削除

### 問題3: Code Nodeが1枚しか生成しない

**原因**: `mode: "runOnceForAllItems"`が設定されていない

**解決方法**:
- Code Nodeの設定を確認し、`mode: "runOnceForAllItems"`を追加

### 問題4: Google Driveアップロードが失敗する

**原因**: Google Drive認証情報が設定されていない、またはフォルダIDが間違っている

**解決方法**:
1. Google Drive認証情報を確認
2. フォルダIDが正しいか確認

---

## 📝 次のステップ

1. ✅ 修正したワークフローをn8nにインポート
2. ✅ テストを実行して7枚のスライドが生成されることを確認
3. ✅ Phase4bとの統合テストを実施
4. ✅ Phase4cとの統合テストを実施

---

**作成者**: AI Assistant (Claude Sonnet 4.5)  
**最終更新**: 2025-11-09

