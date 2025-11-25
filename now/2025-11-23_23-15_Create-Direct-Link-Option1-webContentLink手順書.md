# WF10 Create Direct Link 修正手順書 - Option 1 (webContentLink使用)

**作成日時**: 2025-11-23 23:15:13 JST
**対象ワークフロー**: WF10-Main: kie.ai Sora 2 ビデオ生成 (ID: kxKLB0EWlOhOjaOv)
**修正対象ノード**: Create Direct Link (Set node)

---

## 🎯 修正目的

Create Direct LinkノードでGoogle Drive APIが提供する`webContentLink`を直接使用し、正しいダウンロードURLをkie.ai APIに送信する。

---

## 📋 現在の問題

### Execution #3906の実行結果

**現在の出力** (WRONG):
```json
{
  "image_direct_url": "https://drive.google.com/uc?export=view&id=anyoneWithLink",
  "google_drive_id": " 1Lbsn6jTfG7SSEvvrscw8m_O5FZILa-3v"
}
```

**問題点**:
1. ❌ `image_direct_url`が無効なID (`anyoneWithLink`) を使用
2. ❌ `google_drive_id`に先頭スペースが含まれる

**結果**:
```json
{
  "code": 500,
  "msg": "image_url File type not supported",
  "data": null
}
```
→ kie.ai APIが無効なURLを拒否

---

## ✅ 修正内容

### Upload to Google Driveノードの実際の出力 (Execution #3906)

```json
{
  "id": "1Lbsn6jTfG7SSEvvrscw8m_O5FZILa-3v",
  "name": "image_1763903574901.jpg",
  "mimeType": "image/jpeg",
  "webContentLink": "https://drive.google.com/uc?id=1Lbsn6jTfG7SSEvvrscw8m_O5FZILa-3v&export=download",
  "size": "516689",
  "imageMediaMetadata": {
    "width": 1920,
    "height": 1080
  }
}
```

**重要**: `webContentLink`フィールドがすでに完全なダウンロードURLを提供している

---

## 🔧 n8n UI経由の手動修正手順

### Step 1: n8n UIを開く

```
https://n8n-python-production-344b.up.railway.app
```

### Step 2: ワークフローを開く

- ワークフロー名: **WF10-Main: kie.ai Sora 2 ビデオ生成(Webhook Manual Trigger版)**
- ワークフローID: `kxKLB0EWlOhOjaOv`

### Step 3: Create Direct Linkノードをクリック

### Step 4: Assignmentsセクションを編集

#### Assignment 1: image_direct_url

**現在の値** (削除):
```
=https://drive.google.com/uc?export=view&id={{ $json.id }}
```

**新しい値** (正しい):
```
={{ $('Upload to Google Drive').item.json.webContentLink }}
```

#### Assignment 2: google_drive_id

**現在の値** (削除):
```
= {{ $('Upload to Google Drive').item.json.id }}
```
⚠️ 注意: 先頭の`= `（スペース付き）がエラーの原因

**新しい値** (正しい):
```
={{ $('Upload to Google Drive').item.json.id }}
```
⚠️ 注意: `=`の後にスペースなし

### Step 5: 保存

- **Saveボタン**をクリック
- ワークフローが**Active状態**（トグルON）であることを確認

---

## 🧪 修正後の期待される出力

### Create Direct Link出力 (修正後)

```json
{
  "image_direct_url": "https://drive.google.com/uc?id=1Lbsn6jTfG7SSEvvrscw8m_O5FZILa-3v&export=download",
  "google_drive_id": "1Lbsn6jTfG7SSEvvrscw8m_O5FZILa-3v"
}
```

### Create Video Task成功レスポンス (期待)

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "job_id": "7629519cd4936fb8e9295113e081a3fc"
  }
}
```

---

## ✅ 検証手順

### 修正完了後のE2Eテスト

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"page_id": "2b368d5c2986811f87ecf2aecaedf1cf"}' \
  -w "\nHTTP Status: %{http_code}\nTotal Time: %{time_total}s\n" \
  https://n8n-python-production-344b.up.railway.app/webhook/wf10-notion-trigger \
  > now/2025-11-23_23-15_e2e-test-option1-response.txt 2>&1

cat now/2025-11-23_23-15_e2e-test-option1-response.txt
```

### 期待される結果

- ✅ **HTTP Status**: 200 OK
- ✅ **実行完了ノード**: 14/14 (100%)
- ✅ **Create Video Task成功**: `job_id`が返される
- ✅ **image_direct_url**: `https://drive.google.com/uc?id=...&export=download`形式
- ✅ **google_drive_id**: 先頭スペースなし

---

## 📊 データフロー図（修正後）

```
Upload to Google Drive
  → output: {
      id: "1Lbsn6jTfG7SSEvvrscw8m_O5FZILa-3v",
      webContentLink: "https://drive.google.com/uc?id=...&export=download"
    }
  ↓
Share File (Google Drive permission操作)
  → output: { id: "anyoneWithLink", type: "anyone", role: "reader" }
  ↓
Create Direct Link (Set node) ✅ 修正箇所
  → 直接Upload to Google Driveを参照
  → webContentLinkを使用
  → output: {
      image_direct_url: "https://drive.google.com/uc?id=...&export=download",
      google_drive_id: "1Lbsn6jTfG7SSEvvrscw8m_O5FZILa-3v"
    }
  ↓
Create Video Task (HTTP Request to kie.ai API)
  → POST https://api.kie.ai/api/v1/jobs/createTask
  → body: { image_url: "https://drive.google.com/uc?id=...&export=download", ... }
  → response: { code: 200, data: { job_id: "..." } } ✅
```

---

## 🚀 次のステップ

1. ✅ この手順書に従ってCreate Direct Linkノードを修正
2. ⏳ E2Eテストを実行
3. ⏳ 全14ノード完走確認（100%達成目標）
4. ⏳ Google Sheets統合の再開検討

---

**ドキュメント保存先**: `now/2025-11-23_23-15_Create-Direct-Link-Option1-webContentLink手順書.md`
