# WF7 Phase4ab 統合ワークフロー インポート手順

**作成日**: 2025-11-08  
**対象ファイル**: `workflows/wf7_phase4ab_integrated.json`

---

## 📋 インポート前の確認事項

### 1. 必要な資格情報
以下の資格情報がn8nに設定されていることを確認してください：

- **Notion API**: `Notion account` (ID: `y89xQdP2gCTcdyup`)
- **Google Drive OAuth2**: `Google Drive account` (ID: `plniYONxQ1iPNoAi`)
- **FAL API**: `fal` (ID: `voV5kURaCkiUjLTZ`) - HTTP Header Auth

### 2. 環境要件
- Railway n8n環境: `https://n8n-python-production-344b.up.railway.app/`
- Python環境: Pillow (PIL) が利用可能
- フォント: `/usr/share/fonts/truetype/noto/NotoSansJP-Regular.ttf` が存在すること

---

## 🔧 インポート手順

### Step 1: JSONファイルのインポート

1. n8nのUIにアクセス: `https://n8n-python-production-344b.up.railway.app/`
2. 左メニューから「**Workflows**」を選択
3. 右上の「**Import from File**」ボタンをクリック
4. `workflows/wf7_phase4ab_integrated.json` を選択してアップロード
5. ワークフローがインポートされたことを確認

### Step 2: 資格情報の再設定

インポート後、以下のノードで資格情報を再設定してください：

#### 2.1 Notionノード
- **ノード名**: `Notion - Get Script Data`
- **設定**: 既存の「Notion account」資格情報を選択

#### 2.2 Google Driveノード
- **ノード名**: `Google Drive - Upload Slide Image`
- **設定**: 既存の「Google Drive account」資格情報を選択

#### 2.3 FAL APIノード（3箇所）
以下のノードでFAL API資格情報を設定：
- `HTTP Request - Submit to FAL`
- `HTTP Request - Check Status`
- `HTTP Request - Get Result`

**設定方法**:
- Authentication: **Header Auth**
- Name: `Authorization`
- Value: `Key YOUR_FAL_API_KEY` (YOUR_FAL_API_KEYを実際のAPIキーに置き換え)

### Step 3: Webhookパスの確認

- **ノード名**: `Webhook - Start`
- **パス**: `wf7-phase4ab-integrated`
- **Webhook URL**: `https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4ab-integrated`

このURLをメモしておいてください（他のワークフローから呼び出す際に使用します）。

### Step 4: ノード位置の調整（オプション）

ワークフローが長いため、必要に応じてノードの位置を調整してください：
- Phase4a部分: 左側（x: 240-1780）
- Phase4b部分: 右側（x: 2000-4200）

---

## ✅ インポート後の動作確認

### テスト実行

1. ワークフローを**保存**（Ctrl+S / Cmd+S）
2. ワークフローを**アクティブ化**（右上のトグルスイッチ）
3. テスト用のWebhookリクエストを送信：

```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4ab-integrated \
  -H "Content-Type: application/json" \
  -d '{
    "script_id": "YOUR_NOTION_PAGE_ID"
  }'
```

### 期待される動作

1. **Phase4a**: 7枚のスライド画像が生成され、Google Driveにアップロードされる
2. **Phase4b**: 各スライド画像がFAL APIで動画化される（最大10回のリトライ）
3. **最終レスポンス**: 以下の形式で返される：

```json
{
  "success": true,
  "script_id": "YOUR_NOTION_PAGE_ID",
  "videos_metadata": [
    {
      "section": "hook",
      "duration": 3,
      "video_url": "https://fal.ai/files/xxx/video.mp4",
      "fal_request_id": "fal_xxx_1",
      "motion_prompt": "...",
      "filename": "video_1_hook.mp4",
      "text": "...",
      "slide_index": 0,
      "script_id": "YOUR_NOTION_PAGE_ID"
    },
    // ... 6 more videos
  ],
  "videos_count": 7,
  "total_duration": 80
}
```

---

## 🐛 トラブルシューティング

### エラー: 資格情報が見つからない

**症状**: ノードで「Credential not found」エラーが表示される

**対処法**:
1. 該当ノードを開く
2. 「Credential」セクションで既存の資格情報を選択
3. 資格情報が存在しない場合は、新規作成

### エラー: Python Code NodeでPillowがインポートできない

**症状**: `Code - Generate Slides with Pillow` でエラーが発生

**対処法**:
1. Railway環境でPillowがインストールされているか確認
2. Dockerfileに `pip install Pillow` が含まれているか確認
3. 必要に応じて環境を再デプロイ

### エラー: FAL API認証エラー

**症状**: `HTTP Request - Submit to FAL` で401エラー

**対処法**:
1. FAL APIキーが正しく設定されているか確認
2. Header Authの形式が `Key YOUR_API_KEY` になっているか確認
3. APIキーに有効期限がないか確認

### エラー: Google Driveアップロード失敗

**症状**: `Google Drive - Upload Slide Image` でエラー

**対処法**:
1. Google Drive OAuth2資格情報が有効か確認
2. フォルダIDが正しく設定されているか確認（現在は`root`）
3. 必要に応じて特定のフォルダIDに変更

---

## 📝 次のステップ

統合ワークフローが正常に動作したら：

1. **Phase4c（FFmpeg結合）の追加**: 7本の動画を1本に結合する処理を追加
2. **Notionステータス更新**: 処理完了後にNotionのステータスを更新
3. **エラーハンドリング強化**: 失敗時の通知やログ記録を追加

---

## 🔗 関連ドキュメント

- `docs/implementation/WF7-Phase4abc-docking-plan.md` - 統合計画の詳細
- `docs/implementation/WF7-Phase4a-n8nワークフロー実装ガイド.md` - Phase4aの詳細
- `docs/implementation/WF7-Phase4b-n8nワークフロー実装ガイド.md` - Phase4bの詳細
- `docs/knowledge/wf7-phase4-troubleshooting-guide.md` - トラブルシューティングガイド


