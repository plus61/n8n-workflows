# WF7 OAuth2 JSON Body設定修正

**問題**: HTTP Request v4ノードでJSON Body式が受け付けられない
**エラー**: "The value ... is not supported!"

---

## 🔧 修正方法

### ノード1: Driveファイル作成

#### ❌ 誤った設定（エラーが出る）
```
Send Body: ON
Body Content Type: "JSON"
JSON Field: ={ "name": ... }
```

#### ✅ 正しい設定

**Method**: POST

**URL**: `https://www.googleapis.com/drive/v3/files`

**Authentication**:
- Type: `Predefined Credential Type`
- Credential Type: `Google Drive OAuth2 API`
- Credential: 作成済みの「Google Drive OAuth2」

**Send Query Parameters**: OFF

**Send Headers**: OFF

**Send Body**: ON

**Specify Body**: `Using Fields Below` を選択

**Body Parameters** セクションで以下を設定:

| Name | Value |
|------|-------|
| name | `={{ $json.articleId + "_asset" + $json.assetIndex + ".jpg" }}` |
| mimeType | `image/jpeg` |

**重要**:
- Valueフィールドには `={{ }}` で囲んだ式を入力
- `=` で始めることで、n8nが式として評価します

---

### ノード4: Google Sheets追記

#### ✅ 正しい設定

**Method**: POST

**URL**: `=https://sheets.googleapis.com/v4/spreadsheets/{{ $env.GSHEET_ID }}/values/{{ $env.GSHEET_RANGE || 'Assets!A:F' }}:append?valueInputOption=USER_ENTERED`

**Authentication**:
- Type: `Predefined Credential Type`
- Credential Type: `Google Sheets OAuth2 API`
- Credential: 作成済みの「Google Drive OAuth2」

**Send Headers**: OFF

**Send Body**: ON

**Specify Body**: `Using Fields Below`

**Body Parameters**:

| Name | Value |
|------|-------|
| values | `={{ [[ new Date().toISOString(), $json.articleId, $json.assetRecord.assetTag, $json.assetRecord.source, $json.driveFile.id, $json.driveFile.webViewLink ]] }}` |

---

## 🎯 設定手順（画像付き説明）

### Step 2.4 修正版: Driveファイル作成

1. **Driveファイル作成**ノードをクリック

2. **Parameters** タブで以下を設定:

   **Request Settings**:
   - Method: `POST`
   - URL: `https://www.googleapis.com/drive/v3/files`

   **Authentication**:
   - Authentication: `Predefined Credential Type`
   - Credential Type: `Google Drive OAuth2 API`
   - Credential for Google Drive OAuth2 API: 作成済みの認証情報を選択

3. **Query Parameters**: `Send Query Parameters` を **OFF**

4. **Headers**: `Send Headers` を **OFF**

5. **Body**:
   - `Send Body` を **ON**
   - `Specify Body` を **Using Fields Below** に設定

6. **Body Parameters** セクション:

   **Parameter 1**:
   - Name: `name`
   - Value: `={{ $json.articleId + "_asset" + $json.assetIndex + ".jpg" }}`

   **Parameter 2を追加** (+ Add Parameter をクリック):
   - Name: `mimeType`
   - Value: `image/jpeg` (式なしの固定値)

7. **Options**: デフォルトのまま

8. **Save** をクリック

---

### Step 5.4 修正版: Google Sheets追記

1. **Google Sheets追記**ノードをクリック

2. **Parameters** タブで以下を設定:

   **Request Settings**:
   - Method: `POST`
   - URL: `=https://sheets.googleapis.com/v4/spreadsheets/{{ $env.GSHEET_ID }}/values/{{ $env.GSHEET_RANGE || 'Assets!A:F' }}:append?valueInputOption=USER_ENTERED`

   **Authentication**:
   - Authentication: `Predefined Credential Type`
   - Credential Type: `Google Sheets OAuth2 API`
   - Credential: 作成済みの「Google Drive OAuth2」

3. **Headers**: `Send Headers` を **OFF**

4. **Body**:
   - `Send Body` を **ON**
   - `Specify Body` を **Using Fields Below**

5. **Body Parameters**:

   **Parameter 1**:
   - Name: `values`
   - Value:
   ```
   ={{ [[
     new Date().toISOString(),
     $json.articleId,
     $json.assetRecord.assetTag,
     $json.assetRecord.source,
     $json.driveFile.id,
     $json.driveFile.webViewLink
   ]] }}
   ```

6. **Save** をクリック

---

## 💡 重要なポイント

### HTTP Request v4の仕様

HTTP Request v4では、JSONボディを設定する方法が2つあります：

#### 方法1: Using Fields Below（推奨）
```
Specify Body: "Using Fields Below"
Body Parameters:
  - name: {{ 式 }}
  - mimeType: 固定値
```

**利点**:
- 各フィールドを個別に設定できる
- 式と固定値を混在できる
- UIで設定が見やすい

#### 方法2: Using JSON（式全体を記述）
```
Specify Body: "Using JSON"
JSON: { "name": "固定値", "mimeType": "image/jpeg" }
```

**注意**:
- このフィールドに式（={{ }}）を直接入力するとエラー
- 固定値のJSONのみ対応

---

## 🔍 n8n式の基本ルール

### 式の書き方

#### ✅ 正しい式
```javascript
={{ $json.articleId + "_asset" + $json.assetIndex + ".jpg" }}
```

#### ❌ 間違った式
```javascript
={ "name": $json.articleId + "_asset" + $json.assetIndex + ".jpg" }
// JSONオブジェクトを式の中に書くのは間違い
```

### 式が使える場所

- ✅ URL フィールド
- ✅ Header Value フィールド
- ✅ Body Parameter Value フィールド
- ❌ JSON Body フィールド（方法2の場合）

---

## 📋 完全なノード設定チェックリスト

### Driveファイル作成
- [ ] Method: POST
- [ ] URL: https://www.googleapis.com/drive/v3/files
- [ ] Authentication: Predefined Credential Type
- [ ] Credential Type: Google Drive OAuth2 API
- [ ] Send Headers: OFF
- [ ] Send Body: ON
- [ ] Specify Body: Using Fields Below
- [ ] Body Parameter 1: name = `={{ $json.articleId + "_asset" + $json.assetIndex + ".jpg" }}`
- [ ] Body Parameter 2: mimeType = `image/jpeg`

### Driveコンテンツアップロード
- [ ] Method: PATCH
- [ ] URL: `=https://www.googleapis.com/upload/drive/v3/files/{{ $json.id }}?uploadType=media`
- [ ] Authentication: Predefined Credential Type
- [ ] Credential Type: Google Drive OAuth2 API
- [ ] Send Headers: ON
- [ ] Header Parameter 1: Content-Type = `={{ $json.mimeType || 'image/jpeg' }}`
- [ ] Send Body: ON
- [ ] Body Content Type: Binary Data

### Driveファイル情報取得
- [ ] Method: GET
- [ ] URL: `=https://www.googleapis.com/drive/v3/files/{{ $json.id }}?fields=id,name,webViewLink,webContentLink,thumbnailLink`
- [ ] Authentication: Predefined Credential Type
- [ ] Credential Type: Google Drive OAuth2 API
- [ ] Send Headers: OFF
- [ ] Send Body: OFF

### Google Sheets追記
- [ ] Method: POST
- [ ] URL: `=https://sheets.googleapis.com/v4/spreadsheets/{{ $env.GSHEET_ID }}/values/{{ $env.GSHEET_RANGE || 'Assets!A:F' }}:append?valueInputOption=USER_ENTERED`
- [ ] Authentication: Predefined Credential Type
- [ ] Credential Type: Google Sheets OAuth2 API
- [ ] Send Headers: OFF
- [ ] Send Body: ON
- [ ] Specify Body: Using Fields Below
- [ ] Body Parameter 1: values = 配列の式

---

## 🚨 よくあるエラーと解決策

### エラー1: "The value ... is not supported!"
```
原因: JSON Body フィールドに式を直接入力した
解決策: "Using Fields Below" に変更して、各フィールドを個別に設定
```

### エラー2: "Cannot read property 'articleId' of undefined"
```
原因: $json が存在しない、または前のノードが実行されていない
解決策:
1. ノードの接続を確認
2. 前のノード（アセットメタ整形など）が正常に実行されているか確認
```

### エラー3: "Invalid JSON"
```
原因: Body Parameters の式が不正
解決策: 式が ={{ }} で囲まれているか確認
```

---

**最終更新**: 2025-11-05 12:00 JST
**ステータス**: JSON Body設定方法の修正手順完成
