# WF7 Phase4a テスト実行手順

**作成日**: 2025-11-08  
**対象ワークフロー**: `WF7 Phase4 - V3 Fixed` (ID: `qSN7EHj5yl0nPXij`)  
**目的**: 7枚の画像が正しく生成されることを確認

---

## 📋 テスト前の確認事項

### 1. ワークフロー構造の確認

以下のノードが正しく追加されていることを確認：

- ✅ `Code - Generate Slides with Pillow` (位置: -2480, -272)
- ✅ `Code - Convert to Binary` (位置: -2032, -272)
- ✅ `Google Drive - Upload Slide Image` (位置: -1808, -272)
- ✅ `Aggregate - Combine All Slides` (位置: -1584, -272)
- ✅ `Set - Phase4a Payload New` (位置: -1360, -272)

### 2. 接続の確認

以下の接続が正しく設定されていることを確認：

- ✅ `データ統合` → `Code - Generate Slides with Pillow`
- ✅ `Code - Generate Slides with Pillow` → `Code - Convert to Binary`
- ✅ `Code - Convert to Binary` → `Google Drive - Upload Slide Image`
- ✅ `Google Drive - Upload Slide Image` → `Aggregate - Combine All Slides`
- ✅ `Aggregate - Combine All Slides` → `Set - Phase4a Payload New`
- ✅ `Set - Phase4a Payload New` → `IF - Phase4a Success Check`

### 3. Google DriveフォルダIDの確認

`Google Drive - Upload Slide Image`ノードで、正しいフォルダIDが設定されていることを確認してください。

---

## 🧪 テスト実行方法

### 方法1: Webhook経由で実行（推奨）

#### Step 1: Webhook URLの確認

n8n UIでワークフローを開き、「Webhook」ノードを確認して、Webhook URLを取得してください。

例: `https://n8n-python-production-344b.up.railway.app/webhook/wf7-video-script`

#### Step 2: テストデータの準備

Notionページに以下のプロパティが設定されていることを確認：

- `hook_text_5options`: フックテキスト（配列または文字列）
- `introduction_text`: 導入テキスト
- `main_point_1`: ポイント1
- `main_point_2`: ポイント2
- `main_point_3`: ポイント3
- `summary_text`: まとめテキスト
- `cta_text_3options`: CTAテキスト（配列または文字列）
- `Brand Colors`: ブランドカラー（JSON形式、オプション）
- `Visual Elements`: 視覚要素（JSON形式、オプション）
- `Duration Config`: 秒数設定（JSON形式、オプション）
- `Motion Prompts`: モーションプロンプト（JSON形式、オプション）

#### Step 3: Webhookをトリガー

```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-video-script \
  -H "Content-Type: application/json" \
  -d '{"notionPageId": "YOUR_NOTION_PAGE_ID"}'
```

**注意**: `YOUR_NOTION_PAGE_ID`を実際のNotionページIDに置き換えてください。

### 方法2: n8n UIで手動実行

1. n8n UIでワークフロー `qSN7EHj5yl0nPXij` を開く
2. 「データ統合」ノードを選択
3. 「Execute Node」ボタンをクリック
4. 実行結果を確認

**注意**: この方法では、Webhookノードからのデータが必要な場合、手動でテストデータを入力する必要があります。

---

## ✅ 確認ポイント

### 1. Code - Generate Slides with Pillow ノード

**確認項目**:
- ✅ 7枚のスライドデータが生成されているか
- ✅ 各スライドに以下のフィールドが含まれているか:
  - `section`: セクション名（hook, intro, point1, point2, point3, summary, cta）
  - `duration`: 秒数
  - `image_base64`: Base64エンコードされた画像データ
  - `filename`: ファイル名（slide_1_hook.png など）
  - `motion_prompt`: モーションプロンプト
  - `text`: テキスト内容

**期待される出力**:
```json
[
  {
    "section": "hook",
    "duration": 3,
    "image_base64": "iVBORw0KGgoAAAANS...",
    "filename": "slide_1_hook.png",
    "motion_prompt": "dramatic zoom in effect...",
    "text": "フックテキスト"
  },
  // ... 6 more slides
]
```

### 2. Code - Convert to Binary ノード

**確認項目**:
- ✅ 7つのアイテムが処理されているか
- ✅ 各アイテムにバイナリデータが含まれているか
- ✅ `binary.data`プロパティが正しく設定されているか

### 3. Google Drive - Upload Slide Image ノード

**確認項目**:
- ✅ 7枚の画像がアップロードされているか
- ✅ 各画像にGoogle DriveファイルIDが返されているか
- ✅ ファイル名が正しいか（slide_1_hook.png など）

**期待される出力**:
各アイテムに以下のフィールドが含まれている:
- `id`: Google DriveファイルID
- `name`: ファイル名
- `mimeType`: image/png

### 4. Aggregate - Combine All Slides ノード

**確認項目**:
- ✅ 7枚の結果が統合されているか
- ✅ `aggregatedData`配列に7つのアイテムが含まれているか

**期待される出力**:
```json
{
  "aggregatedData": [
    {
      "section": "hook",
      "duration": 3,
      "filename": "slide_1_hook.png",
      "id": "1abc...xyz",
      "motion_prompt": "...",
      "text": "..."
    },
    // ... 6 more slides
  ]
}
```

### 5. Set - Phase4a Payload New ノード

**確認項目**:
- ✅ `slides_count`が7であるか
- ✅ `phase4a_success`が`true`であるか
- ✅ `slides_metadata`に7つのアイテムが含まれているか
- ✅ 各スライドに`image_url`が正しく設定されているか

**期待される出力**:
```json
{
  "script_id": "notion-page-id",
  "slides_metadata": [
    {
      "section": "hook",
      "duration": 3,
      "image_url": "https://drive.google.com/uc?export=download&id=...",
      "motion_prompt": "...",
      "drive_file_id": "...",
      "filename": "slide_1_hook.png"
    },
    // ... 6 more slides
  ],
  "slides_count": 7,
  "phase4a_success": true
}
```

### 6. IF - Phase4a Success Check ノード

**確認項目**:
- ✅ `phase4a_success`が`true`の場合、`HTTP Request - Call Phase4b`に接続されているか
- ✅ `phase4a_success`が`false`の場合、`エラー時Notion更新`に接続されているか

---

## 🐛 トラブルシューティング

### 問題1: Code Nodeでエラーが発生する

**症状**: Code Nodeの実行でエラーが発生し、空配列が返される

**確認事項**:
1. Pythonコードが正しくコピーされているか
2. データ統合ノードの出力構造が期待通りか
3. Notionページのプロパティが正しく設定されているか

**対処法**:
- Code Nodeのエラーメッセージを確認
- データ統合ノードの出力を確認して、エントリーポイントを調整

### 問題2: Split Outノードで7つに分割されない

**症状**: Split Outノードの出力が7つにならない

**確認事項**:
1. Code Nodeが7枚のスライドを返しているか
2. Split Outノードの設定が正しいか（`fieldToSplitOut: "={{ $json }}"`）

**対処法**:
- Code Nodeの出力を確認
- Split Outノードの設定を確認

### 問題3: Google Driveアップロードが失敗する

**症状**: Google Driveアップロードでエラーが発生する

**確認事項**:
1. Google Drive認証情報が正しく設定されているか
2. フォルダIDが正しいか
3. バイナリデータが正しく変換されているか

**対処法**:
- Google Drive認証情報を確認
- フォルダIDを確認
- Code - Convert to Binaryノードの出力を確認

### 問題4: Aggregateノードで7枚が統合されない

**症状**: Aggregateノードの出力に7枚が含まれていない

**確認事項**:
1. Google Driveアップロードが7回成功しているか
2. Aggregateノードの設定が正しいか

**対処法**:
- 各ノードの実行回数を確認
- Aggregateノードの設定を確認

---

## 📊 テスト結果の記録

テスト実行後、以下の情報を記録してください：

1. **実行日時**: 
2. **使用したNotionページID**: 
3. **Code Nodeの出力**: スライド数（期待値: 7）
4. **Split Outノードの出力**: アイテム数（期待値: 7）
5. **Google Driveアップロード**: 成功数（期待値: 7）
6. **Aggregateノードの出力**: 統合されたアイテム数（期待値: 7）
7. **Setノードの出力**: `slides_count`（期待値: 7）、`phase4a_success`（期待値: true）
8. **発生したエラー**: あれば記録

---

## 🎯 成功基準

以下のすべてが満たされた場合、テストは成功とみなします：

- ✅ Code Nodeが7枚のスライドを生成
- ✅ Split Outノードが7つのアイテムに分割
- ✅ Google Driveに7枚の画像がアップロード
- ✅ Aggregateノードが7枚の結果を統合
- ✅ Setノードの`slides_count`が7
- ✅ Setノードの`phase4a_success`が`true`
- ✅ IFノードが正しく分岐（`true`ブランチに進む）

---

## 📝 次のステップ

テストが成功したら：

1. Phase4b（FAL Image-to-Video）の実装に進む
2. Phase4c（FFmpeg結合）の実装に進む
3. E2Eテストを実施

テストが失敗した場合は、上記のトラブルシューティングを参照してください。

