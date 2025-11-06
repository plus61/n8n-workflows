# WF7 OAuth2 ノード更新手順書

**作成日**: 2025-11-05
**対象ワークフロー**: WF7 Phase2: 素材取得_google版 (ID: HrYFB54nhsPy5QPB)
**所要時間**: 約15分

---

## ✅ 前提条件

- [x] n8n OAuth2認証情報が「Account connected」状態
- [x] Railway環境変数が正しく設定済み
- [x] ワークフローがRailway上で動作中

---

## 🎯 更新対象ノード

以下の**5つのHTTP Requestノード**をOAuth2に更新します：

1. **Driveファイル作成**
2. **Driveコンテンツアップロード**
3. **Driveファイル情報取得**
4. **Google Sheets追記**
5. **Googleアクセストークン取得** (Code node - 削除)

---

## 📝 詳細手順

### Step 1: n8n UIでワークフローを開く

```
1. https://n8n-python-production-344b.up.railway.app にアクセス
2. 左サイドバー → Workflows
3. 「WF7 Phase2: 素材取得_google版」をクリック
```

---

### Step 2: ノード1 - Driveファイル作成

#### 2.1 ノードをクリック
```
「Driveファイル作成」ノードをクリックして設定画面を開く
```

#### 2.2 認証設定を変更
```
Parameters タブ:
- Authentication: "Predefined Credential Type" を選択
- Credential Type: "Google Drive OAuth2 API" を選択
- Credential for Google Drive OAuth2 API:
  作成済みの「Google Drive OAuth2」を選択
```

#### 2.3 Headers設定を削除
```
Send Headers: OFF に変更
（OAuth2が自動でAuthorizationヘッダーを追加するため）
```

#### 2.4 Body設定を更新
```
Send Body: ON
Body Content Type: "JSON"

JSONフィールドに以下を入力:
={
  "name": $json.articleId + "_asset" + $json.assetIndex + ".jpg",
  "mimeType": "image/jpeg"
}
```

#### 2.5 保存
```
右上の「Save」または画面外をクリックして保存
```

---

### Step 3: ノード2 - Driveコンテンツアップロード

#### 3.1 ノードをクリック
```
「Driveコンテンツアップロード」ノードをクリック
```

#### 3.2 認証設定を変更
```
Authentication: "Predefined Credential Type"
Credential Type: "Google Drive OAuth2 API"
Credential: 作成済みの「Google Drive OAuth2」を選択
```

#### 3.3 Headers設定を更新
```
Send Headers: ON (Content-Typeのみ残す)

Header Parameters:
- Name: Content-Type
- Value: ={{ $json.mimeType || 'image/jpeg' }}

※ Authorizationヘッダーは削除
  （OAuth2が自動追加）
```

#### 3.4 Body設定はそのまま
```
Send Body: ON
Body Content Type: "Binary Data"
（変更なし）
```

#### 3.5 保存
```
設定を保存
```

---

### Step 4: ノード3 - Driveファイル情報取得

#### 4.1 ノードをクリック
```
「Driveファイル情報取得」ノードをクリック
```

#### 4.2 認証設定を変更
```
Authentication: "Predefined Credential Type"
Credential Type: "Google Drive OAuth2 API"
Credential: 作成済みの「Google Drive OAuth2」を選択
```

#### 4.3 Headers設定を削除
```
Send Headers: OFF
（OAuth2が自動でAuthorizationヘッダーを追加）
```

#### 4.4 保存
```
設定を保存
```

---

### Step 5: ノード4 - Google Sheets追記

#### 5.1 ノードをクリック
```
「Google Sheets追記」ノードをクリック
```

#### 5.2 認証設定を変更
```
Authentication: "Predefined Credential Type"
Credential Type: "Google Sheets OAuth2 API"
Credential: 作成済みの「Google Drive OAuth2」を選択

※注: Google Drive OAuth2認証情報はGoogle Sheets APIにも使用可能
```

#### 5.3 Headers設定を削除
```
Send Headers: OFF
（OAuth2が自動でAuthorizationとContent-Typeヘッダーを追加）
```

#### 5.4 Body設定を更新
```
Send Body: ON
Body Content Type: "JSON"

JSONフィールドに以下を入力:
={
  "values": [[
    new Date().toISOString(),
    $json.articleId,
    $json.assetRecord.assetTag,
    $json.assetRecord.source,
    $json.driveFile.id,
    $json.driveFile.webViewLink
  ]]
}
```

#### 5.5 保存
```
設定を保存
```

---

### Step 6: ノード5 - Googleアクセストークン取得（削除）

#### 6.1 ノードを削除
```
1. 「Googleアクセストークン取得」Code nodeをクリック
2. Deleteキーを押すか、右クリック → Delete
3. 削除を確認
```

#### 6.2 接続を更新
```
Before:
WF7-Phase2 Webhook → Googleアクセストークン取得 (削除済み)
WF7-Phase2 Webhook → アセットタグ抽出

After:
WF7-Phase2 Webhook → アセットタグ抽出
（Googleアクセストークン取得への接続のみ削除）

※ 「アセットタグ抽出」への接続は維持
```

---

### Step 7: 接続の再確認

#### 7.1 主要な接続フロー
```
アセットメタ整形 → Driveファイル作成 → Driveコンテンツアップロード
  → Driveファイル情報取得 → Drive結果整形 → AssetsJSON生成
```

#### 7.2 接続の確認
```
1. 各ノード間の接続線が途切れていないか確認
2. 特に「アセットメタ整形」から「Driveファイル作成」への接続を確認
```

---

### Step 8: ワークフロー全体を保存

```
1. 右上の「Save」ボタンをクリック
2. 保存完了メッセージを確認
3. ワークフローが引き続き「Active」状態であることを確認
```

---

## 🧪 テスト実行

### テスト準備

#### Notionテストページ作成
```
Database: 記事管理データベース
Properties:
- Article ID: oauth-test-002
- Status: Draft
- Asset Tags: （空白のまま）

ページIDをコピー:
https://www.notion.so/oauth-test-002-[PAGE_ID]
                                    ^^^^^^^^^ これをコピー
```

### Webhook実行

```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase2-assets-google \
  -H "Content-Type: application/json" \
  -d '{
    "articleId": "oauth-test-002",
    "notionPageId": "[コピーしたページID]",
    "assetTags": "mountain,sunset,ocean"
  }'
```

### 期待される結果

#### 成功レスポンス
```json
{
  "status": "success",
  "articleId": "oauth-test-002",
  "assets": [
    {
      "assetTag": "mountain",
      "assetIndex": 0,
      "source": "pexels",
      "driveFileId": "1abc...",
      "driveWebViewLink": "https://drive.google.com/file/d/1abc.../view"
    },
    {
      "assetTag": "sunset",
      "assetIndex": 1,
      "source": "pexels",
      "driveFileId": "2def...",
      "driveWebViewLink": "https://drive.google.com/file/d/2def.../view"
    },
    {
      "assetTag": "ocean",
      "assetIndex": 2,
      "source": "unsplash",
      "driveFileId": "3ghi...",
      "driveWebViewLink": "https://drive.google.com/file/d/3ghi.../view"
    }
  ],
  "notionStatus": "AssetsReady"
}
```

#### 検証項目
- [ ] HTTP 200 OK レスポンス
- [ ] Google Driveに3つの画像ファイルが作成される
- [ ] Google Sheetsに3行追加される（GSHEET_ID設定済みの場合）
- [ ] Notion Statusが「AssetsReady」に更新される
- [ ] Railway logsにエラーがない

---

## 🚨 トラブルシューティング

### エラー1: Credential not found
```
症状: 「Credential for Google Drive OAuth2 API not found」
原因: OAuth2認証情報が選択されていない

解決策:
1. 各ノードの認証設定を再確認
2. Credential Typeが正しく選択されているか確認
3. 必要に応じて認証情報を再作成
```

### エラー2: Invalid authentication
```
症状: 401 Unauthorized エラー
原因: OAuth2トークンが無効または期限切れ

解決策:
1. n8n UI → Credentials → 「Google Drive OAuth2」
2. 「Reconnect」をクリック
3. Google認証フローを再実行
```

### エラー3: Missing required parameter
```
症状: 400 Bad Request - "name is required"
原因: Driveファイル作成のJSONボディが不正

解決策:
1. 「Driveファイル作成」ノードを開く
2. JSON bodyを再確認:
   ={
     "name": $json.articleId + "_asset" + $json.assetIndex + ".jpg",
     "mimeType": "image/jpeg"
   }
3. 式の構文が正しいか確認（= で始まる）
```

### エラー4: Workflow execution failed
```
症状: ワークフロー実行がエラーで停止
原因: ノード接続が不正

解決策:
1. 各ノード間の接続を再確認
2. 特に「アセットメタ整形 → Driveファイル作成」を確認
3. 「Googleアクセストークン取得」が削除されているか確認
```

---

## 📊 更新前後の比較

### Before (Custom JWT)

**利点**:
- 環境変数だけで動作
- UIでの認証不要

**欠点**:
- Code nodeで200行以上のJWT生成コード
- エラーが発生しやすい
- デバッグが困難
- メンテナンスコストが高い

### After (OAuth2)

**利点**:
- n8nが自動でトークン管理
- エラー処理が自動化
- トークン更新が自動
- コードがシンプル
- デバッグが容易

**欠点**:
- 初回OAuth認証が必要
- Google同意画面の設定が必要

---

## 📝 チェックリスト

### 更新前
- [ ] OAuth2認証情報が「Connected」状態を確認
- [ ] ワークフローのバックアップ（オプション）
- [ ] テスト用Notionページを準備

### 更新中
- [ ] Driveファイル作成ノードをOAuth2に更新
- [ ] DriveコンテンツアップロードノードをOAuth2に更新
- [ ] Driveファイル情報取得ノードをOAuth2に更新
- [ ] Google Sheets追記ノードをOAuth2に更新
- [ ] Googleアクセストークン取得ノードを削除
- [ ] ノード接続を確認
- [ ] ワークフロー全体を保存

### 更新後
- [ ] Webhookテストを実行
- [ ] Google Driveにファイルが作成されることを確認
- [ ] Google Sheetsに記録されることを確認
- [ ] Notionページが更新されることを確認
- [ ] Railway logsでエラーがないことを確認

---

## 🎯 次のステップ

### 即座に実行
1. ✅ この手順書に従ってノードを更新
2. ⏳ Webhookテストを実行
3. ⏳ 結果を検証

### 今週中
- [ ] 本番データでの動作確認
- [ ] エラーハンドリングの追加（オプション）
- [ ] パフォーマンス測定

### 長期的
- [ ] OAuth同意画面をProductionに公開
- [ ] 他のワークフローへのOAuth適用
- [ ] Google Sheets Native Nodeへの移行検討

---

**最終更新**: 2025-11-05 11:45 JST
**ステータス**: 手順書作成完了、n8n UI更新待ち
**次のアクション**: n8n UIで手順に従ってノードを更新
