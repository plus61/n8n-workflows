# Create Direct Link ノード修正 - n8n UI経由手順書

**作成日時**: 2025-11-23 17:31:03 JST

## 🎯 修正目的

Create Direct Linkノードの`$json.id`参照を`$('Upload to Google Drive').item.json.id`に変更し、正しいGoogle DriveファイルIDを使用する。

---

## 📋 手動修正手順（n8n UI経由）

### Step 1: n8n UIを開く
```
https://n8n-python-production-344b.up.railway.app
```

### Step 2: ワークフロー選択
- ワークフロー名: **WF10-Main: kie.ai Sora 2 ビデオ生成(Webhook Manual Trigger版)**
- ワークフローID: `kxKLB0EWlOhOjaOv`

### Step 3: Create Direct Linkノードをクリック

### Step 4: Assignmentsセクション編集

#### Assignment 1: image_direct_url

**現在の値** (WRONG):
```
https://drive.google.com/uc?export=view&id={{ $json.id }}
```

**正しい値** (CORRECT):
```
https://drive.google.com/uc?export=view&id={{ $('Upload to Google Drive').item.json.id }}
```

#### Assignment 2: google_drive_id

**現在の値** (WRONG):
```
{{ $json.id }}
```

**正しい値** (CORRECT):
```
{{ $('Upload to Google Drive').item.json.id }}
```

### Step 5: 保存
- **Saveボタン**をクリック
- ワークフローが**Active状態**（トグルON）であることを確認

---

## ✅ 修正完了後の検証手順

### 11回目E2Eテスト実行
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"page_id": "2b368d5c2986811f87ecf2aecaedf1cf"}' \
  -w "\nHTTP Status: %{http_code}\nTotal Time: %{time_total}s\n" \
  https://n8n-python-production-344b.up.railway.app/webhook/wf10-notion-trigger \
  > now/2025-11-23_17-31_e2e-test-11th-response.txt 2>&1

cat now/2025-11-23_17-31_e2e-test-11th-response.txt
```

### 期待される結果
- **HTTP Status**: 200 OK
- **Create Video Task成功**: job_id生成確認
- **Google Drive URL**: `https://drive.google.com/uc?export=view&id=1j3BXoaSzvYHPcdt9_Gtulh67TzCgvpQu`形式（正しいファイルID）

---

## 🔧 修正理由の技術的説明

### 問題の根本原因

**データフロー**:
```
Upload to Google Drive
  → output: { id: "1j3BXo...", name: "image_...", webContentLink: "..." }
  ↓
Share File (Google Drive permission操作)
  → output: { id: "anyoneWithLink", type: "anyone", role: "reader" }
  ↓
Create Direct Link (Set node)
  → 現在: $json.id を使用 → "anyoneWithLink"を取得 ❌
  → 正しい: $('Upload to Google Drive').item.json.id → "1j3BXo..."を取得 ✅
```

### なぜ$json.idが間違っているのか

- `$json`は**直前のノードの出力**のみ参照
- Create Direct Linkの直前は**Share File**
- Share Fileの出力は**権限ID**（`anyoneWithLink`）であり、**ファイルID**ではない

### 正しい参照方法

`$('Upload to Google Drive').item.json.id` を使用することで:
- 特定のノード名を明示的に指定
- Upload to Google Driveの出力から正しいファイルIDを取得
- Share Fileの出力に影響されない

---

## 📊 期待される影響

### 修正前（現在）
```
image_direct_url: https://drive.google.com/uc?export=view&id=anyoneWithLink
                                                             ↑ 無効なID
↓
Create Video Task → kie.ai API
↓
HTTP 500: "image_url File type not supported"
↓
ワークフロー停止（8/14ノード完了、57%）
```

### 修正後（期待）
```
image_direct_url: https://drive.google.com/uc?export=view&id=1j3BXoaSzvYHPcdt9_Gtulh67TzCgvpQu
                                                             ↑ 正しいファイルID
↓
Create Video Task → kie.ai API
↓
HTTP 200: { job_id: "...", code: 200 }
↓
ワークフロー継続（9/14ノード以降も実行）
```

---

## 🚨 注意事項

### KIE_AI_API_KEY問題

修正後もCreate Video Taskが失敗する場合、`KIE_AI_API_KEY`環境変数の値が間違っている可能性があります。

**現在の誤った値**:
```
7629519cd4936fb8e9295113e081a3fc
```
これは**job_id形式**であり、**APIキーではありません**。

**対応方法**:
1. kie.aiダッシュボードから正しいAPIキーを取得
2. Railway環境変数`KIE_AI_API_KEY`を更新
3. n8nサービスを再デプロイ

---

## 📝 次のステップ

1. ✅ この手順書に従ってCreate Direct Linkノードを修正
2. ✅ 11回目E2Eテストを実行
3. ⏳ Create Video Task成功確認
4. ⏳ 必要に応じてKIE_AI_API_KEY更新
5. ⏳ 全14ノード完走確認（100%達成目標）

---

**ドキュメント保存先**: `now/2025-11-23_17-31_Create-Direct-Link手動修正手順書.md`
