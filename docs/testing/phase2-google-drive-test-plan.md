# WF7 Phase2: Google Drive統合テスト計画

## テスト目的
実際のGoogle Drive APIを使用してアセット収集機能のプロダクション品質を検証

## 前提条件

### 1. Google Drive API設定
- [ ] n8nでGoogle Drive認証情報を設定済み
- [ ] OAuth 2.0クライアントID/シークレット設定済み
- [ ] テスト用Google Driveフォルダ作成済み

### 2. テスト用画像準備
推奨仕様:
- 解像度: 1080x1920 (9:16)
- フォーマット: JPEG または PNG
- ファイルサイズ: 1-5MB
- 枚数: 最低4枚（4セグメント動画用）

## テストシナリオ

### シナリオ1: 成功ケース（基本）
**目的**: Google Driveから正常に画像をダウンロードできることを確認

**テストデータ**:
```json
{
  "articleId": "gdrive-test-001",
  "notionPageId": "<新規作成>",
  "assetsData": [
    {
      "assetIndex": 0,
      "assetTag": "opening",
      "driveFileId": "<実際のGoogle DriveファイルID>"
    },
    {
      "assetIndex": 1,
      "assetTag": "problem",
      "driveFileId": "<実際のGoogle DriveファイルID>"
    },
    {
      "assetIndex": 2,
      "assetTag": "solution",
      "driveFileId": "<実際のGoogle DriveファイルID>"
    },
    {
      "assetIndex": 3,
      "assetTag": "cta",
      "driveFileId": "<実際のGoogle DriveファイルID>"
    }
  ]
}
```

**実行手順**:
1. Notionに新規テストページ作成
2. Assets JSONに上記のdriveFileIdを設定
3. Script JSONは既存のものを使用
4. WF7 Phase4 webhookをトリガー
5. Railway logsで進捗モニタリング

**成功基準**:
- ✅ 全4画像がGoogle Driveからダウンロード成功
- ✅ `/tmp/asset_gdrive-test-001_0.jpg` など4ファイルが作成
- ✅ ダウンロード時間 <30秒
- ✅ 画像品質: 1080x1920解像度維持
- ✅ ファイルサイズ: 1-5MB範囲内
- ✅ 動画レンダリング成功
- ✅ NotionページのStatusが"Rendered"に更新

---

### シナリオ2: エラーケース（無効なファイルID）
**目的**: 無効なファイルIDに対するエラーハンドリングを検証

**テストデータ**:
```json
{
  "assetsData": [
    {
      "assetIndex": 0,
      "driveFileId": "INVALID_FILE_ID_12345"
    }
  ]
}
```

**成功基準**:
- ✅ Google Drive APIエラーをキャッチ
- ✅ Notion Error Messageフィールドに詳細記録
- ✅ Status="Failed"に更新
- ✅ ワークフロー全体が中断せず適切に終了

---

### シナリオ3: エラーケース（権限エラー）
**目的**: アクセス権限がないファイルへのエラーハンドリングを検証

**テストデータ**:
- 他のGoogleアカウントが所有するプライベートファイルID

**成功基準**:
- ✅ 403 Forbiddenエラーをキャッチ
- ✅ エラーメッセージに権限不足を明記
- ✅ Notion Error Messageに記録
- ✅ Status="Failed"

---

### シナリオ4: 混合ケース（Python生成 + Google Drive）
**目的**: Python生成画像とGoogle Drive画像の混在を検証

**テストデータ**:
```json
{
  "assetsData": [
    {
      "assetIndex": 0,
      "fileUrl": "/tmp/integration_asset_0.jpg"  // Python生成
    },
    {
      "assetIndex": 1,
      "driveFileId": "<Google DriveファイルID>"  // Google Drive
    },
    {
      "assetIndex": 2,
      "fileUrl": "/tmp/integration_asset_2.jpg"  // Python生成
    },
    {
      "assetIndex": 3,
      "driveFileId": "<Google DriveファイルID>"  // Google Drive
    }
  ]
}
```

**成功基準**:
- ✅ driveFileId を持つアセットのみGoogle Driveからダウンロード
- ✅ fileUrlのアセットはそのまま使用
- ✅ 動画レンダリング成功

---

## 実装チェックリスト

### Phase 1: 環境準備
- [ ] n8nでGoogle Drive認証設定
- [ ] テスト用Google Driveフォルダ作成
- [ ] 4枚のテスト画像をアップロード（1080x1920推奨）
- [ ] 各画像のファイルIDを取得

**ファイルID取得方法**:
```
Google Driveで画像を右クリック → 「リンクを取得」
URL: https://drive.google.com/file/d/1ABC...XYZ/view
↑ この "1ABC...XYZ" 部分がファイルID
```

### Phase 2: n8nワークフロー確認
- [ ] Phase4ワークフローが有効化されている
- [ ] Google Drive認証情報が「Drive画像取得」ノードに設定済み
- [ ] Railway環境でGoogle Drive APIアクセス可能

### Phase 3: テスト実行
- [ ] Notion新規テストページ作成
- [ ] Assets JSONにdriveFileId設定
- [ ] Webhook トリガー実行
- [ ] Railway logsモニタリング
- [ ] 結果検証

### Phase 4: 品質検証
- [ ] ダウンロード時間計測
- [ ] 画像解像度確認（ffprobe使用）
- [ ] ファイルサイズ確認
- [ ] 動画品質確認
- [ ] エラーハンドリング確認

---

## コスト見積もり

**Google Drive API**:
- 無料枠: 1日あたり 10,000リクエスト
- テスト実行1回: 4リクエスト（画像4枚）
- 推定コスト: **$0.00/テスト** (無料枠内)

**ストレージ**:
- Railway /tmp ストレージ: エフェメラル（無料）
- テスト画像合計: ~20MB (4枚 x 5MB)

---

## 次のステップ

1. ✅ この計画書を確認
2. ⏳ Google Driveにテスト画像をアップロード
3. ⏳ ファイルIDを取得
4. ⏳ Notionテストページ作成
5. ⏳ テスト実行
6. ⏳ 結果レポート作成

---

## トラブルシューティング

### エラー: "Google Drive authentication failed"
**解決策**: n8nでGoogle Drive認証情報を再設定

### エラー: "File not found"
**解決策**: ファイルIDが正しいか確認、ファイルの共有設定を確認

### エラー: "Download timeout"
**解決策**: ファイルサイズが大きすぎる可能性、5MB以下を推奨

### エラー: "Insufficient permissions"
**解決策**: n8n認証アカウントがファイルにアクセス権を持つか確認
