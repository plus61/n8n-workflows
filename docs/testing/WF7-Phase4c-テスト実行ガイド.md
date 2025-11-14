# WF7 Phase4c テスト実行ガイド

**作成日**: 2025-11-08  
**対象ワークフロー**: `WF7 Phase4 - V3 Fixed_final` (ID: `r9Sp5n0mkUCcH8cw`)  
**目的**: Phase4c（FFmpeg動画結合）のテスト実行を簡単に行う

---

## 🚀 クイックスタート

### Step 1: n8n UIにアクセス

1. ブラウザで以下にアクセス:
   ```
   https://n8n-python-production-344b.up.railway.app/
   ```

2. ログイン（必要な場合）

### Step 2: ワークフローを開く

1. 左サイドバー → **"Workflows"** をクリック
2. **"WF7 Phase4 - V3 Fixed_final"** をクリック
3. ワークフローIDが `r9Sp5n0mkUCcH8cw` であることを確認

### Step 3: Code - Phase4c FFmpeg Concatノードを開く

1. ワークフローエディタで **"Code - Phase4c FFmpeg Concat"** ノードを探す
2. ノードをクリックして選択
3. 右側の設定パネルが表示されることを確認

### Step 4: Pin Dataを設定

1. 設定パネルで **"Pin Data"** タブを選択
2. 以下のファイルを開いて内容をコピー:
   ```
   test-phase4c-pindata.json
   ```
3. コピーした内容をPin Dataフィールドにペースト
4. **"Save"** をクリックしてPin Dataを保存

### Step 5: ノードを実行

1. 設定パネルの下部にある **"Execute Node"** ボタンをクリック
2. 実行結果を確認
3. エラーが発生していないことを確認

---

## ✅ 実行結果の確認

### Code - Phase4c FFmpeg Concat の期待される出力

```json
{
  "success": true,
  "script_id": "test-script-phase4c-001",
  "output_video_path": "/tmp/wf7_phase4c_xxx/final_video_test-script-phase4c-001_1234567890.mp4",
  "output_video_size": 15728640,
  "total_duration": 80,
  "videos_count": 7,
  "temp_dir": "/tmp/wf7_phase4c_xxx",
  "articleId": "test-article-001"
}
```

**確認ポイント**:
- ✅ `success: true` が返されている
- ✅ `output_video_path` が設定されている
- ✅ `output_video_size` が0より大きい
- ✅ `total_duration` が80秒（3+10+13+13+14+20+7）

### 次のノードの実行

Pin Dataを設定した後、以下のノードを順番に実行して確認:

1. **Code - Read Video Binary**: `binary.data` が設定されていることを確認
2. **Google Drive - Upload Final Video**: `webViewLink` が設定されていることを確認
3. **Notion - Update Script Record**: HTTP 200 OKが返されていることを確認
4. **Code - Cleanup Temp Files**: `cleanup_success: true` が返されていることを確認
5. **Respond to Webhook**: レスポンスが返されていることを確認

---

## 🔧 トラブルシューティング

### エラー1: FFmpeg結合失敗

**症状**: `Code - Phase4c FFmpeg Concat`でエラーが発生

**確認事項**:
- FFmpegがn8nサーバーにインストールされているか
- 動画URLが有効か
- 動画ファイルの形式がMP4か

**解決方法**:
- n8nサーバーでFFmpegがインストールされているか確認
- 動画URLが有効か確認（ブラウザで直接アクセスできるか）
- 動画ファイルの形式を確認（MP4形式であることを確認）

### エラー2: Google Driveアップロード失敗

**症状**: `Google Drive - Upload Final Video`でエラーが発生

**確認事項**:
- Google Drive OAuth2認証情報が有効か
- `binaryData: true` と `binaryPropertyName: "data"` が設定されているか

**解決方法**:
- Google Drive OAuth2認証情報を確認
- ノード設定で `binaryData: true` と `binaryPropertyName: "data"` が設定されているか確認

### エラー3: Notion DB更新失敗

**症状**: `Notion - Update Script Record`でエラーが発生

**確認事項**:
- Notion API認証情報が有効か
- `script_id`が存在するか
- プロパティ名が正確か（`Status`, `Video URL`）

**解決方法**:
- Notion API認証情報を確認
- `script_id`が有効なNotionページIDか確認
- プロパティ名が正確か確認（`Status`, `Video URL`）

---

## 📝 テストチェックリスト

- [ ] n8n UIにアクセス可能
- [ ] ワークフローID `r9Sp5n0mkUCcH8cw` が存在し、アクティブ
- [ ] Google Drive OAuth2認証が設定済み
- [ ] Notion API認証が設定済み
- [ ] Pin Dataを設定済み
- [ ] `Code - Phase4c FFmpeg Concat`が正常に実行される
- [ ] 7本の動画がダウンロードされる
- [ ] FFmpegで動画が結合される
- [ ] `Code - Read Video Binary`が正常に実行される
- [ ] `Google Drive - Upload Final Video`が正常に実行される
- [ ] `Notion - Update Script Record`が正常に実行される
- [ ] `Code - Cleanup Temp Files`が正常に実行される
- [ ] `Respond to Webhook`が正常に実行される

---

## 🔗 関連ファイル

- `test-phase4c-pindata.json`: Pin Data用のテストデータ
- `docs/testing/WF7-Phase4c-テスト実行手順.md`: 詳細なテスト実行手順
- `workflows/wf7_phase4b_fixed_r9Sp5n0mkUCcH8cw.json`: 現在のワークフローJSON

---

**作成者**: Claude Code (Composer)  
**更新日**: 2025-11-08




