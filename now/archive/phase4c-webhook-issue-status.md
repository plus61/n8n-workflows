# Phase4c Webhook登録問題 - 現在の状況

**日時**: 2025-01-12 16:50 JST
**問題**: Phase4c新ワークフロー（10ノード）のwebhookが登録されない

## 現在の技術的問題

### 症状
- HTTP 200レスポンスだがボディが空
- n8n実行履歴がゼロ（webhookが一度もトリガーされていない）
- UI上でワークフローはactive: true表示
- 再有効化を実行しても改善せず

### 確認済み事項
✅ ワークフローID: `Exra8DkAfWsmOPiE`
✅ Webhook path設定: `wf7-phase4c-video-concatenator` (正しい)
✅ ワークフロー構造: 10ノード、Phase4b成功パターン適用済み
✅ ロジックバグ: 2件修正済み（retry counter、request_id参照）
✅ versionCounter: 8（最新）
❌ Webhook実登録: されていない

### 修正済みバグ

#### Bug 1: Retry Counter (修正済み)
**Before**:
```json
{
  "id": "retry_count",
  "name": "retry_count",
  "value": 0,
  "type": "number"
}
```

**After**:
```json
{
  "id": "retry_count",
  "name": "retry_count",
  "value": "={{ $json.retry_count ? $json.retry_count + 1 : 0 }}",
  "type": "string"
},
{
  "id": "request_id",
  "name": "request_id",
  "value": "={{ $json.request_id || $('HTTP Request - Submit to FAL').item.json.request_id }}",
  "type": "string"
}
```

#### Bug 2: Request ID参照 (修正済み)
**Before**:
```javascript
url: "=https://queue.fal.run/fal-ai/ffmpeg-api/requests/{{ $('HTTP Request - Submit to FAL').item.json.request_id }}/status"
```

**After**:
```javascript
url: "=https://queue.fal.run/fal-ai/ffmpeg-api/requests/{{ $json.request_id }}/status"
```

### Railway Logs確認結果
- Phase4b webhookエラー多数（過去のもの）
- Phase4c webhook登録ログなし
- 別のwebhook `wf7-phase4c-ffmpeg-concat` のエラーあり（異なるワークフロー？）

## 次に実行すべき内容

### Option 1: ワークフロー再作成（推奨）✨
最も確実な方法。以下の手順：

1. **現在のワークフローをバックアップ**
   ```bash
   # MCPで取得済み、workflows/ディレクトリに保存されている
   ```

2. **ワークフローを削除**
   - n8n UIでワークフロー `Exra8DkAfWsmOPiE` を削除

3. **新規ワークフローを作成**
   - MCPで `n8n_create_workflow` を使用
   - または UI上でインポート

4. **Activate & Test**
   ```bash
   ./test-phase4c-new.sh
   ```

### Option 2: Railway Redeploy（手動）
Railway CLIのインタラクティブプロンプトに応答が必要：

```bash
railway redeploy --service n8n-python
# "Are you sure you want to redeploy n8n-python?" → y
```

再起動後、30-60秒待ってからテスト：
```bash
sleep 60 && ./test-phase4c-new.sh
```

### Option 3: UI上でWebhook URL確認
1. n8n UIでワークフローを開く
2. Webhookノードをクリック
3. "Test URL" または "Production URL" をコピー
4. コピーしたURLで直接curlテスト

## テストファイル

### テストスクリプト
`/Users/yuichiroooosuger/Desktop/n8n-workflows/test-phase4c-new.sh`

### テストペイロード
`/Users/yuichiroooosuger/Desktop/n8n-workflows/data/test-phase4c-new-webhook-payload.json`

7本の実動画URL、合計80秒：
- hook: 3秒
- intro: 10秒
- point1: 13秒
- point2: 13秒
- point3: 14秒
- summary: 20秒
- cta: 7秒

## 想定される次のステップ

### 成功した場合
1. ✅ HTTP 200 + JSON response body
2. ✅ n8n実行履歴に記録
3. ✅ `final_video_url` が返る
4. ✅ FAL FFmpeg APIが正常に呼ばれる

次の作業：
- Phase4bとの結果比較
- 動画品質確認
- パフォーマンス測定

### 失敗が続く場合の診断
1. n8n UIでExecution履歴を直接確認
2. Webhookノードの設定を再確認
3. Railway環境変数確認（N8N_PATH等）
4. n8nログで詳細なエラー確認

## 関連ファイル

### ワークフローバックアップ
- `/Users/yuichiroooosuger/Desktop/n8n-workflows/workflows/phase4c-backup-26nodes-20250112.json` (旧26ノード版)
- 現在の10ノード版はMCPで管理（ID: Exra8DkAfWsmOPiE）

### ログファイル
- `/tmp/phase4c-new-test-curl.log` (初回テスト)
- `/tmp/phase4c-new-test-fixed-curl.log` (バグ修正後テスト)
- `/tmp/phase4c-new-test-reactivated.log` (再有効化後テスト)

### ドキュメント
- `docs/testing/WF7-Phase4c-テスト実行結果記録.md`
- `docs/testing/WF7-Phase4c-IFノード問題解決-v2.md`

## 技術的背景

### Phase4c簡素化の目的
- 26ノード → 10ノードに削減
- 4種類のURL抽出ロジック → 1種類（Phase4b成功パターン）
- 複雑なエラーハンドリング → シンプルなリトライループ

### Phase4b成功パターンの適用
- ✅ Tracks形式のペイロード構造
- ✅ 累積時間でkeyframes配置
- ✅ 優先順位付きURL抽出（`video?.url` → `outputs[0]` → `video_url`）
- ✅ 安定したrequest_id参照

## 現在の作業セッション情報

**開始時刻**: 2025-01-12 約15:00 JST
**経過時間**: 約1時間50分
**実行したテスト回数**: 3回（すべて失敗）
**適用した修正**: 2件（ロジックバグ修正）
**再有効化実行**: 1回（効果なし）

**次回セッション開始時の最優先事項**:
1. Option 1（ワークフロー再作成）を実行
2. 再作成後すぐにテスト
3. 成功したら即座にコミット

---

**メモ**: Phase4cワークフローのロジック自体は正しい。問題はRailway環境でのwebhook登録のみ。ワークフロー再作成で解決する可能性が高い。
