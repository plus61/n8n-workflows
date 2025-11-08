# WF7 Phase4a 7枚画像生成修正手順

**作成日**: 2025-11-08  
**最終更新**: 2025-11-08  
**対象ワークフロー**: `WF7 Phase4 - V3 Fixed` (ID: `qSN7EHj5yl0nPXij`)  
**問題**: 現在1枚の画像しか生成されていない  
**解決策**: Code Nodeを追加して7枚の画像を直接生成する  
**実装ステータス**: ✅ **実装完了**（2025-11-08）

---

## 🎉 実装完了サマリー

Phase4aの7枚画像生成機能の実装が完了しました。

### 実装内容

- ✅ Code Node（Python）: 7枚のスライド画像を生成
- ✅ Split Outノード: 7つのアイテムに分割
- ✅ Code Node（JavaScript）: Base64→Binary変換
- ✅ Google Drive Upload: 7枚の画像をアップロード
- ✅ Aggregateノード: 7枚の結果を統合
- ✅ Setノード: Phase4a Payloadを設定

### 次のアクション

1. **テスト実行**（優先度: 高）
   - ワークフローを実行して7枚のスライド生成を確認
   - Google Driveへのアップロードを確認
   - 各ノードの出力を検証

2. **Phase4b統合準備**
   - Phase4aテスト完了後、Phase4b（FAL Image-to-Video）の実装に進む

---

## 📋 問題の原因

現在のワークフローでは「HTTP Request - Call Phase4a」ノードが別のワークフロー（webhook）を呼び出しており、そのワークフローが1枚の画像しか生成していない可能性があります。

---

## 🔧 解決手順

### Step 1: Code Nodeを追加

1. n8n UIでワークフロー `qSN7EHj5yl0nPXij` を開く
2. 「データ統合」ノードを選択
3. 右側に新しいノードを追加
4. ノードタイプ: **Code** を選択
5. ノード名: `Code - Generate Slides with Pillow`

#### Code Nodeの設定

**Language**: Python  
**Mode**: `Run Once for All Items`

**Python Code**: `workflows/wf7-video-renderer/phase4a_code_node.py` の内容を**そのまま**コピー&ペースト

**重要**: `phase4a_code_node.py`のエントリーポイント（267-294行目）は、`データ統合`ノードの出力構造に応じて自動調整されるため、**修正不要**です。

エントリーポイントは以下の3つのパターンに対応しています:
1. `properties`を含む場合 → `notionProps = notionPageData['properties']`
2. `scriptData`を含む場合 → `notionProps = notionPageData['scriptData']`
3. 直接propertiesが渡される場合 → `notionProps = notionPageData`

**現在のワークフロー**（`wf7_phase4_v3.json`）では、`データ統合`ノードが`scriptData`を含むため、パターン2が適用されます。

### Step 2: Split Outノードを追加

1. `Code - Generate Slides with Pillow`ノードの後に新しいノードを追加
2. ノードタイプ: **Split Out** を選択
3. ノード名: `Split Out - Individual Slides`

#### Split Outノードの設定

**重要**: Code Nodeが配列を返すため、Split Outノードは**設定不要**です。n8nが自動的に配列を個別アイテムに分割します。

**オプション設定**（必要に応じて）:
- **Field to Split Out**: 設定不要（デフォルトで配列全体が分割される）
- **Include**: `allFields`（デフォルト）

**注意**: Code Nodeが7つのスライドオブジェクトの配列を返すため、Split Outノードは自動的に7つのアイテムに分割します。

### Step 3: Code Node（Base64→Binary変換）を追加

1. `Split Out - Individual Slides`ノードの後に新しいノードを追加
2. ノードタイプ: **Code** を選択
3. ノード名: `Code - Convert to Binary`

#### Code Nodeの設定

**Language**: JavaScript

**JavaScript Code**:
```javascript
// Base64画像をバイナリデータに変換してGoogle Driveアップロード用に準備
const base64Data = $json.image_base64;
const binaryData = Buffer.from(base64Data, 'base64');

return {
  json: {
    section: $json.section,
    duration: $json.duration,
    filename: $json.filename,
    motion_prompt: $json.motion_prompt,
    text: $json.text
  },
  binary: {
    data: {
      data: binaryData.toString('base64'),
      mimeType: 'image/png',
      fileName: $json.filename,
      fileExtension: 'png'
    }
  }
};
```

### Step 4: Google Drive Uploadノードを追加

1. `Code - Convert to Binary`ノードの後に新しいノードを追加
2. ノードタイプ: **Google Drive** を選択
3. ノード名: `Google Drive - Upload Slide Image`

#### Google Driveノードの設定

- **Operation**: `Upload`
- **Name**: `={{ $json.filename }}`
- **Binary Data**: ✅ `true` を選択
- **Binary Property Name**: `data`（Code - Convert to Binaryノードの出力に合わせる）
- **Options**:
  - **Parents**: `[WF7_SLIDES_FOLDER_ID]`（実際のフォルダIDに置き換え）
    - 例: `["1abc123def456ghi789"]`
  - **Mime Type**: `image/png`

**Google DriveフォルダIDの取得方法**:
1. Google Driveでスライド画像用フォルダを作成
2. フォルダを開き、URLからIDを取得
   - URL例: `https://drive.google.com/drive/folders/1abc123def456ghi789`
   - フォルダID: `1abc123def456ghi789`
3. n8n UIでノード設定の`Parents`フィールドに配列形式で設定: `["1abc123def456ghi789"]`

**Credentials**: 既存のGoogle Drive認証情報を使用（`Google Drive account`）

### Step 5: Aggregateノードを追加

1. `Google Drive - Upload Slide Image`ノードの後に新しいノードを追加
2. ノードタイプ: **Aggregate** を選択
3. ノード名: `Aggregate - Combine All Slides`

#### Aggregateノードの設定

- **Aggregate**: `aggregateAllItemData`
- **Options**: デフォルトのまま

### Step 6: Setノードを追加（Phase4a Payload）

1. `Aggregate - Combine All Slides`ノードの後に新しいノードを追加
2. ノードタイプ: **Set** を選択
3. ノード名: `Set - Phase4a Payload`

#### Setノードの設定

**Assignments**に以下のフィールドを追加:

1. **script_id** (String)
   - Value: `={{ $('データ統合').item.json.notionPageId }}`

2. **slides_metadata** (Array)
   - Value: 
   ```javascript
   ={{ $json.aggregatedData.map(item => ({
     section: item.section || item.json.section,
     duration: item.duration || item.json.duration,
     image_url: 'https://drive.google.com/uc?export=download&id=' + (item.id || item.json.id),
     motion_prompt: item.motion_prompt || item.json.motion_prompt,
     drive_file_id: item.id || item.json.id,
     filename: item.filename || item.json.filename
   })) }}
   ```

3. **slides_count** (Number)
   - Value: `={{ $json.aggregatedData.length }}`

4. **phase4a_success** (Boolean)
   - Value: `={{ $json.aggregatedData.length === 7 }}`

**注意**: Google Drive Uploadノードの出力構造に応じて、`item.json.id`または`item.id`を使用してください。通常は`item.json.id`がGoogle DriveファイルIDです。

### Step 7: 接続の更新

**重要**: 現在のワークフロー（`wf7_phase4_v3.json`）には「HTTP Request - Call Phase4a」ノードが存在しないため、接続の削除は不要です。

**接続手順**:

1. **既存接続の確認**
   - 「データ統合」→「Split Out」（assetsData用）の接続を**保持**
   - この接続は既存のアセット処理用のため、削除しない

2. **Phase4aパスの接続追加**
   - 「データ統合」→「Code - Generate Slides with Pillow」を接続
   - 「Code - Generate Slides with Pillow」→「Split Out - Individual Slides」を接続
   - 「Split Out - Individual Slides」→「Code - Convert to Binary」を接続
   - 「Code - Convert to Binary」→「Google Drive - Upload Slide Image」を接続
   - 「Google Drive - Upload Slide Image」→「Aggregate - Combine All Slides」を接続
   - 「Aggregate - Combine All Slides」→「Set - Phase4a Payload」を接続

3. **後続処理への接続**
   - 「Set - Phase4a Payload」→「Split Out」（既存のassetsData用）を接続
   - または、Phase4b処理へ接続（Phase4b実装時）

**注意**: 「データ統合」ノードから2つのパスが分岐します:
- Phase4aパス: スライド画像生成用
- 既存パス: assetsData処理用（変更なし）

### Step 8: IFノードの条件を更新（オプション）

**重要**: 現在のワークフロー（`wf7_phase4_v3.json`）には「IF - Phase4a Success Check」ノードが存在しないため、このステップは**オプション**です。

Phase4aの成功チェックが必要な場合は、以下のノードを追加してください:

1. **IFノードを追加**
   - 「Set - Phase4a Payload」ノードの後に新しいノードを追加
   - ノードタイプ: **IF** を選択
   - ノード名: `IF - Phase4a Success Check`

2. **IFノードの条件設定**
   - **条件1**: `phase4a_success` が `true` である
     - Left Value: `={{ $json.phase4a_success }}`
     - Operation: `equals`
     - Right Value: `true`
   - **条件2**: `slides_count` が `7` である
     - Left Value: `={{ $json.slides_count }}`
     - Operation: `equals`
     - Right Value: `7`
   - **Combinator**: `AND`

3. **接続設定**
   - 「Set - Phase4a Payload」→「IF - Phase4a Success Check」を接続
   - 「IF - Phase4a Success Check」→ 後続処理（成功時）
   - 「IF - Phase4a Success Check」→ エラーハンドリング（失敗時）

**注意**: Phase4aのエラーハンドリングが必要な場合は、失敗時のパスにエラーレスポンスノードを追加してください。

---

## ✅ 確認事項

1. Code Nodeが7枚のスライドを生成しているか確認
2. Split Outノードが7つのアイテムに分割しているか確認
3. Google Driveに7枚の画像がアップロードされているか確認
4. Aggregateノードが7枚の結果を統合しているか確認
5. Setノードが正しい形式でデータを設定しているか確認

---

## 🧪 テスト手順

### テスト実行チェックリスト

1. **ワークフロー実行**
   - [ ] Webhookからワークフローを実行
   - [ ] エラーなく実行完了することを確認

2. **Code Nodeの出力確認**
   - [ ] Code Nodeが7枚のスライドを生成しているか確認
   - [ ] 各スライドに`section`, `duration`, `image_base64`, `filename`, `motion_prompt`, `text`が含まれているか確認

3. **Split Outノードの出力確認**
   - [ ] Split Outノードが7つのアイテムに分割しているか確認
   - [ ] 各アイテムが正しいデータ構造を持っているか確認

4. **Code - Convert to Binaryノードの出力確認**
   - [ ] Base64データがバイナリデータに変換されているか確認
   - [ ] バイナリプロパティ`data`が正しく設定されているか確認

5. **Google Driveアップロード確認**
   - [ ] Google Driveに7枚の画像がアップロードされているか確認
   - [ ] ファイル名が正しいか確認（`slide_1_hook.png`, `slide_2_intro.png`, など）
   - [ ] 各画像が正しいフォルダにアップロードされているか確認

6. **Aggregateノードの出力確認**
   - [ ] Aggregateノードが7枚の結果を統合しているか確認
   - [ ] `aggregatedData`配列に7つのアイテムが含まれているか確認

7. **Setノードの出力確認**
   - [ ] `slides_count`が7であるか確認
   - [ ] `phase4a_success`が`true`であるか確認
   - [ ] `slides_metadata`が正しい形式か確認
     - [ ] 各スライドに`section`, `duration`, `image_url`, `motion_prompt`, `drive_file_id`, `filename`が含まれているか
     - [ ] `image_url`が正しいGoogle Drive URL形式か確認

### テスト実行時の注意点

- **エラーハンドリング**: Code Nodeでエラーが発生した場合、空配列を返すため、後続ノードでエラーハンドリングが必要です
- **Google DriveフォルダID**: 正しいフォルダIDが設定されているか確認してください
- **データ構造**: `データ統合`ノードの出力構造に応じて、Code Nodeのエントリーポイントが正しく動作するか確認してください

---

## 📝 注意事項

1. **Google DriveフォルダID**: `WF7_SLIDES_FOLDER_ID`を実際のフォルダIDに置き換える必要があります
2. **データ構造**: データ統合ノードの出力構造に応じて、Code Nodeのエントリーポイントを調整する必要がある場合があります
3. **エラーハンドリング**: Code Nodeでエラーが発生した場合、空配列を返すため、後続ノードでエラーハンドリングが必要です

---

## 🔗 関連ファイル

- `workflows/wf7-video-renderer/phase4a_code_node.py`: Code Node用のPythonコード
- `workflows/wf7-video-renderer/phase4a_slide_generator.py`: スライド生成ロジック

---

## 📊 実装状況

**最終更新**: 2025-11-08

### ✅ 完了項目

1. ✅ Phase4a Code Node用Pythonコードの準備完了
   - `workflows/wf7-video-renderer/phase4a_code_node.py` が完成
   - 7枚のスライド生成ロジック実装済み
   - n8n Code Node用エントリーポイント実装済み

2. ✅ 実装手順書の作成完了
   - 修正手順書作成済み
   - 統合ガイド作成済み
   - 手動実装手順書作成済み

3. ✅ **n8n UIでの実装完了**（2025-11-08）
   - Step 1-8をn8n UIで実行完了
   - 各ノードの設定を手順書に従って実施完了
   - ワークフロー `wf7_phase4_v3.json` にPhase4aノード群を追加完了

### 🔄 進行中項目

1. 🔄 **テスト実行**
   - Code Node単体テスト
   - Google Driveアップロード確認
   - 7枚のスライド生成確認

### 📋 次のステップ

1. **テスト実行と検証**（優先度: 高）
   - ✅ Code Nodeの出力確認（7枚のスライドが生成されているか）
   - ✅ Split Outノードの出力確認（7つのアイテムに分割されているか）
   - ✅ Google Driveに7枚の画像がアップロードされているか確認
   - ✅ Aggregateノードの出力確認（7枚の結果が統合されているか）
   - ✅ Setノードの出力確認（`slides_count`が7であるか、`slides_metadata`が正しい形式か）

2. **Phase4b統合準備**（Phase4aテスト完了後）
   - Phase4b（FAL Image-to-Video）の実装に進む
   - Phase4aの`slides_metadata`をPhase4bに渡す準備
   - 関連ドキュメント: `docs/implementation/WF7-Phase4-FAL実装計画書.md`

---

## 💡 実装時の注意点

### Code Nodeのエントリーポイント修正

`phase4a_code_node.py`のエントリーポイントは、`データ統合`ノードの出力構造に応じて自動調整されますが、実際のワークフローで確認が必要です。

**確認ポイント**:
- `データ統合`ノードが`scriptData`を含むか
- `scriptData`内に`Brand Colors`、`Duration Config`、`Motion Prompts`、`Visual Elements`が含まれるか

### Google DriveフォルダID設定

`Google Drive - Upload Slide Image`ノードの設定で、`WF7_SLIDES_FOLDER_ID`を実際のフォルダIDに置き換える必要があります。

**設定方法**:
1. Google Driveでスライド画像用フォルダを作成
2. フォルダIDを取得（URLから取得可能）
3. n8n UIでノード設定の`Parents`フィールドに設定

