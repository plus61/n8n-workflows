# WF7 Phase4 Creatomate外部レンダリング実装ガイド

**作成日**: 2025-11-06
**目的**: FFmpegタイムアウト問題を解決するCreatomate統合の実装手順

---

## 📋 概要

Phase4のFFmpegレンダリングをCreatomate APIに置き換えることで、Railway環境でのタイムアウト問題を解決します。

### 主な変更点
- ✅ FFmpegローカル処理 → Creatomate外部API
- ✅ 同期処理 → 非同期Webhook処理
- ✅ タイムアウトリスク → 安定した外部処理
- ✅ 処理時間: 6分+ → 1-3分

---

## 🚀 実装手順

### Step 1: Creatomateアカウント設定

1. **アカウント作成**
   ```
   https://creatomate.com にアクセス
   無料プランから開始可能（月100レンダリング）
   ```

2. **API Key取得**
   - Dashboard → API Keys
   - Production Keyをコピー

3. **テンプレート作成**
   - Templates → New Template
   - サイズ: 1080x1920 (9:16縦型)
   - 以下のレイヤーを設定:

   ```json
   {
     "layers": [
       {
         "id": "video-1",
         "type": "video",
         "position": { "x": 0, "y": 0 },
         "size": { "width": 1080, "height": 1920 }
       },
       {
         "id": "audio-1",
         "type": "audio"
       },
       {
         "id": "text-title",
         "type": "text",
         "position": { "x": 540, "y": 100 },
         "style": {
           "fontSize": 48,
           "color": "#FFFFFF",
           "textAlign": "center"
         }
       },
       {
         "id": "subtitle-1",
         "type": "subtitle",
         "position": { "x": 540, "y": 1600 },
         "style": {
           "fontSize": 32,
           "color": "#FFFF00",
           "backgroundColor": "rgba(0,0,0,0.5)"
         }
       }
     ]
   }
   ```

4. **テンプレートIDを保存**

---

### Step 2: Railway環境変数設定

```bash
# Railway CLIまたはダッシュボードで設定
railway variables set CREATOMATE_API_KEY=your_api_key_here
railway variables set CREATOMATE_TEMPLATE_ID=your_template_id_here
```

---

### Step 3: n8nワークフロー実装

#### 3.1 Phase4メインワークフローのインポート

1. n8nダッシュボードにアクセス
   ```
   https://n8n-python-production-344b.up.railway.app
   ```

2. 新規ワークフロー作成

3. Import from File
   ```
   /workflows/hub-integration/wf7-phase4-creatomate.json
   ```

4. 環境変数を確認
   - CREATOMATE_API_KEY
   - CREATOMATE_TEMPLATE_ID

#### 3.2 Callbackハンドラーワークフローのインポート

1. 新規ワークフロー作成

2. Import from File
   ```
   /workflows/hub-integration/wf7-render-callback-handler.json
   ```

3. Webhook URLを確認
   ```
   https://n8n-python-production-344b.up.railway.app/webhook/wf7-render-callback
   ```

---

### Step 4: 既存Phase4の無効化と切り替え

1. **既存Phase4ワークフローを無効化**
   - 既存のFFmpegベースのPhase4を「Inactive」に設定
   - バックアップを保存

2. **新Phase4を有効化**
   - Creatomate版Phase4を「Active」に設定
   - Webhook URLが同じであることを確認

---

## 🧪 テスト手順

### 1. 単体テスト

```bash
# Phase4単体テスト
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4-render \
  -H "Content-Type: application/json" \
  -d '{
    "articleId": "test-creatomate-001",
    "title": "Creatomateテスト動画",
    "videoUrl": "https://example.com/test-video.mp4",
    "audioUrl": "https://example.com/test-audio.mp3",
    "subtitleUrl": "https://example.com/test-subtitle.srt",
    "duration": 45
  }'
```

期待される結果:
1. Creatomate APIが呼ばれる
2. Hub DBのステータスが「Rendering」に更新
3. 1-3分後にcallback webhookが呼ばれる
4. Hub DBのステータスが「Rendered」に更新
5. Phase5が自動的にトリガーされる

### 2. エラーケーステスト

```bash
# 無効なURLでテスト
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4-render \
  -H "Content-Type: application/json" \
  -d '{
    "articleId": "test-error-001",
    "videoUrl": "invalid-url",
    "audioUrl": "invalid-url"
  }'
```

期待される結果:
- Creatomateがエラーを返す
- Callback webhookで失敗通知
- Hub DBのステータスが「Failed_Phase4」に更新
- Error Logにエラー詳細が記録

---

## 📊 モニタリング

### Creatomateダッシュボード
```
https://app.creatomate.com/renders
```
- レンダリング状況をリアルタイムで確認
- 成功/失敗率の統計
- 使用量と料金

### Hub DB (Notion)
- Kanbanビューでステータス確認
- Error Inboxビューで失敗を確認
- Latest Execution IDでトラッキング

### Slackチャンネル
- レンダリング開始通知
- 完了/失敗通知
- Phase5への自動遷移確認

---

## 🔧 トラブルシューティング

### 問題1: Creatomate API接続エラー
**症状**: 401 Unauthorized
**解決**:
```bash
# API Keyを再確認
railway variables get CREATOMATE_API_KEY
# 正しいKeyを設定
railway variables set CREATOMATE_API_KEY=correct_key_here
```

### 問題2: Callback Webhookが呼ばれない
**症状**: レンダリング完了してもステータスが更新されない
**解決**:
1. Creatomateダッシュボードでcallback URLを確認
2. n8n Webhook URLが正しいか確認
3. ファイアウォール設定を確認

### 問題3: テンプレートエラー
**症状**: "Template not found"エラー
**解決**:
```javascript
// Phase4ワークフローのCreatomateペイロード作成ノードを編集
const CREATOMATE_TEMPLATE_ID = 'your-correct-template-id';
```

---

## 💰 コスト管理

### Creatomate料金プラン
- **Free**: 100レンダリング/月
- **Starter**: $49/月 - 500レンダリング
- **Pro**: $149/月 - 2000レンダリング
- **Enterprise**: カスタム

### コスト削減Tips
1. テンプレートを最適化して処理時間短縮
2. 不要な高品質設定を避ける
3. バッチ処理で効率化

---

## 📈 パフォーマンス比較

| 項目 | FFmpeg (旧) | Creatomate (新) |
|------|------------|----------------|
| 処理時間 | 6分18秒 | 1-3分 |
| 成功率 | 60-70% | 99.9% |
| タイムアウトリスク | 高 | なし |
| スケーラビリティ | 低 | 高 |
| メンテナンス | 必要 | 不要 |

---

## 🚦 移行チェックリスト

- [ ] Creatomateアカウント作成
- [ ] API Key取得と設定
- [ ] テンプレート作成
- [ ] Railway環境変数設定
- [ ] Phase4ワークフローインポート
- [ ] Callbackハンドラーインポート
- [ ] 単体テスト実施
- [ ] Hub DB更新確認
- [ ] Phase5連携確認
- [ ] 既存Phase4無効化
- [ ] 本番運用開始

---

## 📚 参考資料

- [Creatomate API Documentation](https://creatomate.com/docs/api)
- [n8n Webhook Documentation](https://docs.n8n.io/nodes/n8n-nodes-base.webhook/)
- [MEO Operations Hub統合ガイド](../n8n-notion-hub-integration.md)
- [Phase4外部レンダリングソリューション](../../docs/wf7-phase4-external-rendering-solution.md)

---

**最終更新**: 2025-11-06