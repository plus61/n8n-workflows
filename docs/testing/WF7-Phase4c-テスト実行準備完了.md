# WF7 Phase4c テスト実行準備完了

**作成日**: 2025-11-08  
**目的**: Phase4cのテスト実行に必要なデータと手順をまとめる

---

## ✅ 準備完了

Phase4bの実行が成功し、Phase4cのテスト実行に必要なデータが準備できました。

### 準備されたファイル

1. **`phase4b_completed_data_v2.json`**: Phase4b完了データ（7本の動画）
2. **`phase4c_pin_data.json`**: Phase4c用Pin Data形式（n8n UIで使用）

---

## 📋 Phase4cテスト実行手順

### 方法1: n8n UIでノードを手動実行（推奨）

#### Step 1: ワークフローを開く

1. ブラウザで `https://n8n-python-production-344b.up.railway.app/` にアクセス
2. 左サイドバー → **"Workflows"** をクリック
3. **"WF7 Phase4 - V3 Fixed_final"** をクリック
4. ワークフローIDが `r9Sp5n0mkUCcH8cw` であることを確認

#### Step 2: Code - Phase4c FFmpeg Concatノードを開く

1. ワークフローエディタで **"Code - Phase4c FFmpeg Concat"** ノードを探す
2. ノードをクリックして選択
3. 右側の設定パネルが表示されることを確認

#### Step 3: Pin Dataを設定

1. 設定パネルで **"Pin Data"** タブを選択
2. **`phase4c_pin_data.json`** の内容をコピー&ペースト：

```json
[
  {
    "json": {
      "script_id": "test-phase4b-e2e-001",
      "articleId": "test-article-001",
      "videos_metadata": [
        {
          "section": "hook",
          "duration": 3,
          "video_url": "https://v3b.fal.media/files/b/monkey/ErYQSu7MBuZB7NBS-3-_J_output.mp4"
        },
        {
          "section": "intro",
          "duration": 10,
          "video_url": "https://v3b.fal.media/files/b/zebra/TL6NZ5rSbpAZRT4P8IA0C_output.mp4"
        },
        {
          "section": "point1",
          "duration": 13,
          "video_url": "https://v3b.fal.media/files/b/penguin/j1KJr6fbJYTxTZkTIjLlS_output.mp4"
        },
        {
          "section": "point2",
          "duration": 13,
          "video_url": "https://v3b.fal.media/files/b/panda/lGTFA7_HybUaGORhadu0g_output.mp4"
        },
        {
          "section": "point3",
          "duration": 14,
          "video_url": "https://v3b.fal.media/files/b/monkey/TbW1zMlq-vfVL6fHGt-Lv_output.mp4"
        },
        {
          "section": "summary",
          "duration": 20,
          "video_url": "https://v3b.fal.media/files/b/zebra/jU_MCQ884eXvR9-nVVA4y_output.mp4"
        },
        {
          "section": "cta",
          "duration": 7,
          "video_url": "https://v3b.fal.media/files/b/zebra/WammM1aF25B-8q6Q6t-mJ_output.mp4"
        }
      ]
    }
  }
]
```

3. **"Save"** をクリックしてPin Dataを保存

#### Step 4: ノードを実行

1. 設定パネルの下部にある **"Execute Node"** ボタンをクリック
2. 実行結果を確認
3. エラーが発生していないことを確認

#### Step 5: 各ノードの実行結果を確認

1. **Code - Phase4c FFmpeg Concat**:
   - ✅ `success: true` が返されている
   - ✅ `output_video_path` が設定されている
   - ✅ `output_video_size` が0より大きい
   - ✅ `total_duration` が80秒

2. **Code - Read Video Binary**:
   - ✅ `binary.data` が設定されている
   - ✅ Base64エンコードされた動画データが含まれている

3. **Google Drive - Upload Final Video**:
   - ✅ `webViewLink` が設定されている
   - ✅ Google Driveに動画がアップロードされている

4. **Notion - Update Script Record**:
   - ✅ HTTP 200 OKが返されている
   - ✅ Notion DBの`Status`が`Rendered`に更新されている
   - ✅ Notion DBの`Video URL`が更新されている

5. **Code - Cleanup Temp Files**:
   - ✅ `cleanup_success: true` が返されている

6. **Respond to Webhook**:
   - ✅ レスポンスが返されている
   - ✅ `success: true` が含まれている
   - ✅ `final_video_url` が設定されている

---

## 📊 テストデータ詳細

### 動画メタデータ

| セクション | 秒数 | 動画URL |
|-----------|------|---------|
| hook | 3秒 | `https://v3b.fal.media/files/b/monkey/ErYQSu7MBuZB7NBS-3-_J_output.mp4` |
| intro | 10秒 | `https://v3b.fal.media/files/b/zebra/TL6NZ5rSbpAZRT4P8IA0C_output.mp4` |
| point1 | 13秒 | `https://v3b.fal.media/files/b/penguin/j1KJr6fbJYTxTZkTIjLlS_output.mp4` |
| point2 | 13秒 | `https://v3b.fal.media/files/b/panda/lGTFA7_HybUaGORhadu0g_output.mp4` |
| point3 | 14秒 | `https://v3b.fal.media/files/b/monkey/TbW1zMlq-vfVL6fHGt-Lv_output.mp4` |
| summary | 20秒 | `https://v3b.fal.media/files/b/zebra/jU_MCQ884eXvR9-nVVA4y_output.mp4` |
| cta | 7秒 | `https://v3b.fal.media/files/b/zebra/WammM1aF25B-8q6Q6t-mJ_output.mp4` |

### 統計情報

- **動画数**: 7本
- **合計時間**: 80秒
- **script_id**: `test-phase4b-e2e-001`
- **articleId**: `test-article-001`

---

## ⚠️ 注意事項

### 動画URLの有効期限

- FAL APIで生成された動画URLには有効期限がある場合があります
- テスト実行前に動画URLが有効か確認してください
- 無効なURLの場合、Phase4cでダウンロードエラーが発生します

### script_idについて

- `script_id`は`test-phase4b-e2e-001`です
- Notion DB更新時には、有効なNotionページIDが必要です
- テスト用には任意の文字列でも動作しますが、Notion DB更新は失敗する可能性があります

### FFmpegの要件

- n8nサーバーにFFmpegがインストールされている必要があります
- 動画の結合には時間がかかる場合があります（最大600秒のタイムアウト設定）

---

## 🔗 関連ファイル

- `phase4b_completed_data_v2.json`: Phase4b完了データ（完全版）
- `phase4c_pin_data.json`: Phase4c用Pin Data形式
- `phase4b_response_v2.json`: Phase4bの完全なレスポンス
- `docs/testing/WF7-Phase4c-テスト実行手順.md`: 詳細なテスト実行手順

---

## ✅ 次のステップ

1. **n8n UIでテスト実行**: 上記の手順に従ってPhase4cをテスト実行
2. **実行結果の確認**: 各ノードが正常に動作することを確認
3. **エラーの確認**: エラーが発生した場合は、トラブルシューティングガイドを参照
4. **結果の記録**: テスト結果をドキュメントに記録

---

**作成者**: Claude Code (Composer)  
**更新日**: 2025-11-08  
**ステータス**: ✅ テスト実行準備完了

