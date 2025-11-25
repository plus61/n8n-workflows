# webContentLink + Runway Gen-3 互換性テスト計画

**作成日時**: 2025-11-16 17:05:58 JST
**目的**: Google Drive webContentLinkがRunway Gen-3 APIで使用可能か検証
**期待効果**: Base64 Data URI不要、ペイロードサイズ削減

---

## テスト戦略

### フェーズ1: webContentLink仕様確認（10分）

#### テスト1-1: webContentLinkリダイレクト挙動確認
```bash
# テストコマンド
curl -I "https://drive.google.com/uc?export=download&id=FILE_ID&confirm=t"

# 期待結果A（リダイレクトなし）:
HTTP/2 200
content-type: image/png
content-length: 123456

# 期待結果B（リダイレクトあり）:
HTTP/2 302
location: https://drive.google.com/...
```

**判定基準**:
- ✅ 200応答 → Runway Gen-3成功の可能性高
- ❌ 302/307応答 → 失敗の可能性高（WF10 v2dと同じ）

#### テスト1-2: webContentLink MIME Type確認
```bash
curl -I "https://drive.google.com/uc?export=download&id=FILE_ID&confirm=t" | grep content-type

# 期待結果:
content-type: image/png
# または
content-type: image/jpeg
```

**判定基準**:
- ✅ 明示的MIME type → Runway Gen-3成功の可能性高
- ⚠️ `application/octet-stream` → 失敗の可能性（v2b/v2cと同じ）

---

### フェーズ2: Runway Gen-3 minimal test（30分）

#### 前提条件
- Google Drive上にテスト画像配置済み
- n8n WF10-Main v2eが動作中
- FAL API credentials設定済み

#### テスト2-1: Upload + webContentLink取得
**ノード構成**:
```
Node 1: Download from Drive (既存)
  ↓
Node 2: Upload file (新規追加)
  type: n8n-nodes-base.googleDrive
  operation: upload
  parameters:
    driveId: My Drive
    folderId: [test folder ID]
    options:
      fileContent: =binary (from Node 1)
      fileName: test-image.png
```

**期待出力**:
```json
{
  "id": "1XxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxX",
  "name": "test-image.png",
  "mimeType": "image/png",
  "webContentLink": "https://drive.google.com/uc?export=download&id=1XxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxX&confirm=t",
  "webViewLink": "https://drive.google.com/file/d/1XxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxX/view?usp=drivesdk"
}
```

#### テスト2-2: Runway Gen-3 POST with webContentLink
**ノード構成**:
```json
Node 3: HTTP Request (Runway Gen-3 API)
{
  "name": "Test Runway Gen-3 webContentLink",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "method": "POST",
    "url": "https://fal.run/fal-ai/runway-gen3/turbo/image-to-video",
    "authentication": "predefinedCredentialType",
    "nodeCredentialType": "falAiApi",
    "sendHeaders": true,
    "headerParameters": {
      "parameters": [
        {
          "name": "Content-Type",
          "value": "application/json"
        }
      ]
    },
    "sendBody": true,
    "specifyBody": "json",
    "jsonBody": "={\n  \"image_url\": \"{{ $('Upload file').first().json.webContentLink }}\",\n  \"prompt\": \"A serene lake with mountains in the background\",\n  \"duration\": 5\n}"
  }
}
```

**期待結果（成功）**:
```json
{
  "request_id": "546b0378-a8e8-487f-9064-f97ad3128edc",
  "status": "IN_QUEUE"
}
```

**期待結果（失敗）**:
```json
{
  "detail": "Could not load image from url: https://drive.google.com/uc?export=download&id=..."
}
```

---

### フェーズ3: エンドツーエンドテスト（1時間）

#### 成功シナリオ（フェーズ2成功時）

**テスト3-1: WF10-Main v2f実装**
```
Node 1: Webhook Trigger
  ↓
Node 2: Set pindata (台本本文)
  ↓
Node 3: Download from Drive (Phase 2画像)
  ↓
Node 4: Upload file (webContentLink取得)
  ↓
Node 5: HTTP Request (Runway Gen-3)
  - image_url: {{ $('Upload file').first().json.webContentLink }}
  - webhook_url: https://n8n-python-production-344b.up.railway.app/webhook/wf10-webhook
  ↓
Node 6: Set response
```

**検証項目**:
1. ✅ Runway Gen-3が`IN_QUEUE`を返す
2. ✅ Webhookが正常に呼び出される
3. ✅ `video_url`が正しく抽出される
4. ✅ Notion更新が成功する

**成功時のアクション**:
- v2f実装ガイド作成
- v2e（Base64）との性能比較
- 本番環境移行計画策定

#### 失敗シナリオ（フェーズ2失敗時）

**Root Cause分析**:
```
失敗パターン1: リダイレクト（302/307）
→ 原因: Googleのセキュリティポリシー
→ 対策: Base64継続（v2e）

失敗パターン2: MIME type不正
→ 原因: Google Driveの自動判定失敗
→ 対策: Upload時にMIME type明示指定

失敗パターン3: ファイルアクセス権限
→ 原因: webContentLinkに認証トークンなし
→ 対策: ファイル共有設定を「リンク知っている人全員」に変更
```

**フォールバックプラン**:
1. ltxv-13b API検証（テンプレートと同じendpoint）
2. Cloudinary経由でのホスティング検討
3. v2e（Base64）パフォーマンス最適化

---

## 性能比較指標

### ペイロードサイズ比較

**Base64 Data URI（v2e現行）**:
```json
{
  "image_url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...[約500KB]",
  "prompt": "...",
  "duration": 10
}
// 総ペイロードサイズ: ~500KB
```

**webContentLink（v2f提案）**:
```json
{
  "image_url": "https://drive.google.com/uc?export=download&id=1Xxx&confirm=t",
  "prompt": "...",
  "duration": 10
}
// 総ペイロードサイズ: ~1KB
```

**削減効果**: 約99.8%（500KB → 1KB）

### 実行時間比較

| ステップ | v2e (Base64) | v2f (webContentLink) | 差分 |
|---------|--------------|----------------------|------|
| Download from Drive | 2s | 2s | - |
| Binary → Base64変換 | 0.5s | - | -0.5s |
| Upload to Drive | - | 3s | +3s |
| POST Runway Gen-3 | 1s（大ペイロード） | 0.3s（小ペイロード） | -0.7s |
| **合計** | **3.5s** | **5.3s** | **+1.8s** |

**トレードオフ**:
- ✅ ペイロードサイズ大幅削減
- ❌ 実行時間わずかに増加（Upload追加のため）
- ✅ n8nメモリ使用量削減
- ✅ ネットワーク帯域削減

---

## 判定基準

### 成功条件（v2f採用）
1. ✅ Runway Gen-3が`IN_QUEUE`を返す（HTTP 200）
2. ✅ 10回連続テストで成功率100%
3. ✅ Webhook呼び出しが正常（v3データ構造）
4. ✅ ペイロードサイズ削減効果確認

### 失敗条件（v2e継続）
1. ❌ Runway Gen-3がエラーを返す（HTTP 422）
2. ❌ 10回中1回でも失敗
3. ❌ webContentLink有効期限問題
4. ❌ パフォーマンス劣化

---

## テスト実行ログフォーマット

```markdown
### テスト実行記録

**実行日時**: YYYY-MM-DD HH:MM:SS JST
**テスター**: Claude Code
**環境**: n8n Railway production

#### フェーズ1結果
- [ ] テスト1-1: リダイレクト挙動
  - コマンド: `curl -I "..."`
  - 結果: HTTP/2 [STATUS_CODE]
  - 判定: [PASS/FAIL]

- [ ] テスト1-2: MIME Type
  - コマンド: `curl -I "..."`
  - 結果: content-type: [MIME_TYPE]
  - 判定: [PASS/FAIL]

#### フェーズ2結果
- [ ] テスト2-1: webContentLink取得
  - ノード: Upload file
  - webContentLink: https://drive.google.com/uc?export=download&id=...
  - 判定: [PASS/FAIL]

- [ ] テスト2-2: Runway Gen-3 POST
  - Request Body: { "image_url": "...", ... }
  - Response: { "request_id": "...", "status": "..." }
  - 判定: [PASS/FAIL]
  - エラー詳細（失敗時）: [ERROR_MESSAGE]

#### フェーズ3結果（成功時のみ）
- [ ] テスト3-1: エンドツーエンド
  - Execution ID: [EXEC_ID]
  - 実行時間: [DURATION]秒
  - ペイロードサイズ: [SIZE]KB
  - 判定: [PASS/FAIL]

#### 総合判定
- **最終結論**: [v2f採用 / v2e継続 / 追加調査必要]
- **理由**: [詳細な判定理由]
```

---

## 次のアクション

### 即座実行（今すぐ可能）
1. ✅ テストファイルをGoogle Driveにアップロード
2. ✅ n8n WF10-Mainを開く
3. ✅ Upload fileノード追加
4. ✅ HTTP Requestノード修正（webContentLink使用）
5. ✅ Manual実行でフェーズ2テスト

### 成功時（30分以内）
1. ✅ 10回連続テスト実行
2. ✅ ログ記録（上記フォーマット）
3. ✅ v2f実装ガイド作成
4. ✅ v2eとの性能比較レポート

### 失敗時（1時間以内）
1. ✅ エラー詳細分析
2. ✅ Root Cause特定
3. ✅ ltxv-13b API検証計画
4. ✅ v2eパフォーマンス最適化

---

**ステータス**: 実行準備完了
**推定所要時間**: 1-2時間
**リスクレベル**: 低（既存v2eで動作保証あり）
