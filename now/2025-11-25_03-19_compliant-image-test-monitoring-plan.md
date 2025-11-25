# WF10-Main コンプライアント画像テスト - 監視計画

**作成日時**: 2025-11-25 03:19:23 JST

## 🎯 テスト概要

### テスト目的
kie.ai API コンテンツポリシー準拠画像（人物なし）を使用した場合の、WF10-Main ワークフローの完全なE2E成功を検証する。

### テストページ情報
- **Notion Page ID**: `2b568d5c-2986-814a-8e2bf4d141605f62`
- **Title**: "WF10テスト - コンプライアント画像検証 - 2025-11-25 03:16"
- **Image URL**: `https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1920`
  - **内容**: 純粋な雪山風景（人物なし）
  - **kie.ai準拠**: ✅ 人物が含まれないためAPI受理

### kie.ai taskId
- **taskId**: `5b99b1760c2c7c25720f9d3644f994f1`
- **生成開始**: 2025-11-25 03:17:10 JST
- **API Status**: 正常（HTTP 200 OK）

## 📊 実行タイムライン

| 時刻 | ステータス | 詳細 |
|-----|----------|------|
| 03:16:29 | ✅ Notionページ作成 | MCP API経由で正常作成 |
| 03:17:10 | ✅ Webhook トリガー | curlコマンド実行 |
| 03:17:17 | ✅ Webhook応答 | 7.02秒でtaskId返却（HTTP 200） |
| 03:17:17-03:27:17 | 🔄 Wait実行中 | n8n Wait Node（600秒） |
| 03:27:17 | ⏳ 最初のステータス確認予定 | `GET /api/v1/veo/record-info?taskId=xxx` |
| ~03:32:17 | 🎯 ビデオ生成完了予想 | kie.ai推定時間：4-5分 |
| ~03:37:17 | 🎯 Notion更新完了予想 | 2回目のWait後に完了判定 |

## 🔍 確認項目

### Phase 1: Webhook応答確認（完了 ✅）
- [x] HTTP Status 200 OK
- [x] taskId生成成功: `5b99b1760c2c7c25720f9d3644f994f1`
- [x] kie.ai API即座エラーなし（人物画像の場合はHTTP 400発生）

### Phase 2: kie.ai APIステータス確認（03:27:17予定）
- [ ] `GET /api/v1/veo/record-info?taskId=5b99b1760c2c7c25720f9d3644f994f1`
- [ ] レスポンス `data.state`: `"processing"` または `"success"`
- [ ] `data.resultJson` 内に `resultUrls[0]` が存在（成功時）

### Phase 3: Notion更新確認（03:37:17予定）
- [ ] `Video_URL` プロパティが設定される
- [ ] `Status` が "Completed" に更新される
- [ ] ビデオURLが有効（アクセス可能）

## 📝 検証コマンド

### Notionページステータス確認（03:27以降実行）
```bash
# MCPツール経由でNotionページを取得
# page_id: 2b568d5c-2986-814a-8e2bf4d141605f62
```

### kie.ai APIステータス確認（手動検証用）
```bash
curl -H "Authorization: Bearer $KIE_AI_API_KEY" \
  "https://api.kie.ai/api/v1/veo/record-info?taskId=5b99b1760c2c7c25720f9d3644f994f1"
```

## 🎯 成功基準

### ✅ 完全成功条件
1. kie.ai APIがビデオ生成完了（`state: "success"`）
2. `resultUrls[0]` に有効なビデオURLが返却される
3. Notionページが自動更新される：
   - `Video_URL`: 生成されたビデオURL
   - `Status`: "Completed"
4. 生成されたビデオURLにアクセス可能

### ⚠️ 部分成功条件（追加調査必要）
- kie.ai APIがタイムアウト（10分Wait × 複数回でも完了しない）
- `data: null` レスポンス（taskId有効期限切れの可能性）

### ❌ 失敗条件
- kie.ai API HTTP 400エラー（コンテンツポリシー違反）
- kie.ai API HTTP 401/403エラー（認証エラー）
- n8n ワークフロー実行エラー

## 📊 過去のテスト結果との比較

### 旧テスト（人物画像）
- **Image**: `https://images.unsplash.com/photo-1506748686214-e9df14d4d9d0?w=800`
- **結果**: ❌ kie.ai API即座にHTTP 400エラー
- **エラーメッセージ**: "OpenAI currently do not support uploads of images containing photorealistic people."
- **影響**: ワークフローが無限ループ（6時間以上実行）

### 新テスト（コンプライアント画像）
- **Image**: `https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1920`
- **結果**: ✅ Webhook応答成功（HTTP 200、taskId生成）
- **期待**: ビデオ生成完了後、Notion自動更新

## 🔧 トラブルシューティング

### ケース1: 10分Wait後もstill processing
**対応**: さらに10分Wait（ループ実行）継続監視

### ケース2: data: null レスポンス
**考えられる原因**:
- taskId有効期限切れ
- kie.ai側の内部エラー

**対応**: 新しいtaskIdで再テスト

### ケース3: Notion更新失敗
**確認項目**:
- n8n実行ログ
- Notion API認証状態
- Video_URLフィールド型（URL型として正しく設定されているか）

## 📌 重要な発見

### kie.ai APIコンテンツポリシー
- ❌ **禁止**: Photorealistic people（写実的な人物）
- ✅ **許可**: 風景、物体、抽象的なビジュアル

### 修正済み項目（前回セッションから）
1. ✅ APIエンドポイント: `/api/v1/veo/record-info` に修正
2. ✅ Wait時間: 300s → 600s（10分）に延長
3. ✅ テスト画像: 人物なし画像に変更

## 🎓 教訓

1. **API仕様の事前確認の重要性**: kie.aiのコンテンツポリシーを最初から確認していれば、6時間以上の無限ループテストを回避できた
2. **エラーレスポンスの即座分析**: HTTP 400エラーが発生した時点で、画像コンテンツを疑うべきだった
3. **バックグラウンドプロセスの監視**: 長時間実行テストは適切なタイムアウトと監視が必要
