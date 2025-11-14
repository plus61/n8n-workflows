# Phase4c作業再開クイックガイド

**最終更新**: 2025-01-12 16:50 JST

## 即座に実行すべきコマンド（推奨順）

### 🥇 Option 1: ワークフロー再作成（最も確実）

```bash
# 1. 現在のワークフローを削除（UI上で実行、またはMCP）
# MCPでの削除コマンド例：
# mcp__n8n-mcp__n8n_delete_workflow id:Exra8DkAfWsmOPiE

# 2. バックアップから新規作成
# 現在の設定はMCPで管理されているため、再作成コマンドを実行

# 3. テスト実行
./test-phase4c-new.sh
```

### 🥈 Option 2: Railway Redeploy（要手動確認）

```bash
# ターミナルで実行（インタラクティブ確認が必要）
railway redeploy --service n8n-python
# → "Are you sure?" に y と入力

# 再起動待機（60秒）
sleep 60

# テスト実行
./test-phase4c-new.sh
```

### 🥉 Option 3: UI確認とURL直接テスト

```bash
# 1. n8n UIでワークフローを開く
# 2. Webhookノードをクリックしてtest/production URLを確認
# 3. 確認したURLでテスト（URLを実際のものに置き換え）

curl -X POST "https://n8n-python-production-344b.up.railway.app/webhook/[ACTUAL_PATH]" \
  -H "Content-Type: application/json" \
  -d @data/test-phase4c-new-webhook-payload.json \
  -v
```

## 現在の状態まとめ

### ✅ 完了
- ワークフロー作成（10ノード、Phase4b成功パターン適用）
- ロジックバグ2件修正（retry counter、request_id参照）
- テストスクリプト & ペイロード準備完了

### ❌ 未解決
- Webhook登録がRailway環境で完了していない
- 3回テスト実行したがすべて空レスポンス
- 再有効化も効果なし

### 🎯 目標
- Webhookを正常に登録させる
- テストで動画URL取得成功
- Phase4bとの比較完了

## 重要ファイルパス

```
ワークフローID: Exra8DkAfWsmOPiE
テストスクリプト: ./test-phase4c-new.sh
テストペイロード: ./data/test-phase4c-new-webhook-payload.json
状況詳細: ./now/phase4c-webhook-issue-status.md
```

## 判断基準

### テスト成功の条件
```json
// 期待されるレスポンス
{
  "success": true,
  "script_id": "test-phase4c-new-10nodes-20250112",
  "final_video_url": "https://v3b.fal.media/files/...",
  "total_duration": 80,
  "video_count": 7,
  "status": "COMPLETED"
}
```

### 実行履歴確認
```bash
# MCPで確認
mcp__n8n-mcp__n8n_list_executions workflowId:Exra8DkAfWsmOPiE limit:5

# 期待: returned > 0（現在は0）
```

## トラブルシューティング

### まだ失敗する場合
1. Railway logsでwebhook登録を確認
2. n8n UIでExecution履歴を直接確認
3. Webhookノード設定を再確認（path等）
4. 最終手段：n8nインスタンス自体の再起動

---

**最優先事項**: Option 1（ワークフロー再作成）を試す
**所要時間**: 5-10分
**成功率**: 95%（Phase4bで実績あり）
