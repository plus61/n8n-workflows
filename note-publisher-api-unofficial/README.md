# note記事自動投稿API (非公式)

Phase2 WF6: note記事自動生成ワークフロー用のAPIサーバー

## 概要

note.comへの記事投稿を自動化するためのVercelサーバーレス関数。n8nワークフローから呼び出され、GPT-4で生成した記事を自動的にnoteへ投稿します。

**⚠️ 注意**: このAPIはnote非公式APIを使用しています。利用規約を確認の上、自己責任でご使用ください。

## アーキテクチャ

```
n8n Workflow (WF6)
  ↓ HTTP POST
Vercel API (/api/publish-note)
  ↓ note非公式API
note.com (記事公開)
  ↓ レスポンス
Notion DB登録 + Slack通知
```

## 機能

### `/api/publish-note` (POST)
- **目的**: note記事の自動投稿
- **認証**: `X-API-Key` ヘッダー
- **ステータス**: `published` (自動公開)
- **レート制限**: 10 requests/分

### `/api/health` (GET)
- **目的**: システムヘルスチェック
- **機能**: 環境変数とnoteセッション有効性の確認
- **認証**: 不要

### `/api/debug` (GET)
- **目的**: 環境変数デバッグ
- **機能**: API設定の確認（本番環境では無効化推奨）
- **認証**: 不要

## セットアップ

### 1. noteセッションクッキーの取得

1. ブラウザでnote.comにログイン
2. Chrome DevToolsを開く (F12)
3. `Application` > `Cookies` > `https://note.com`
4. `_note_session_v5` の値をコピー

### 2. 環境変数の設定

Vercelダッシュボードで以下の環境変数を設定：

```bash
# API認証キー（ランダム生成推奨）
API_SECRET_KEY=your-random-secret-key-here

# noteセッションクッキー
NOTE_SESSION_COOKIE=your-note-session-cookie-value
```

**生成例**:
```bash
# macOS/Linux
openssl rand -base64 32

# Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"
```

### 3. Vercelデプロイ

```bash
# Vercel CLIインストール
npm install -g vercel

# ログイン
vercel login

# デプロイ
cd note-publisher-api-unofficial
vercel --prod
```

### 4. 動作確認

```bash
# ヘルスチェック
curl https://your-app.vercel.app/api/health

# 期待されるレスポンス:
# {
#   "status": "healthy",
#   "checks": {
#     "apiKeyConfigured": true,
#     "noteSessionConfigured": true,
#     "noteSessionValid": true
#   }
# }
```

## API使用方法

### リクエスト例

```bash
curl -X POST https://your-app.vercel.app/api/publish-note \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-secret-key" \
  -d '{
    "title": "英語学童の選び方：失敗しない3つのポイント",
    "body": "## はじめに\n\n英語学童を選ぶ際に...",
    "categories": ["英語教育", "バイリンガル", "学童保育"]
  }'
```

### レスポンス例（成功）

```json
{
  "success": true,
  "url": "https://note.com/61beef/n/n123abc456def",
  "articleId": "n123abc456def",
  "title": "英語学童の選び方：失敗しない3つのポイント",
  "publishedAt": "2025-10-29T01:23:45.678Z"
}
```

### レスポンス例（エラー）

```json
{
  "success": false,
  "error": "note authentication failed",
  "details": "Session cookie may be expired. Status: 401"
}
```

## n8n統合

### HTTP Requestノード設定

```json
{
  "method": "POST",
  "url": "https://your-app.vercel.app/api/publish-note",
  "authentication": "none",
  "sendHeaders": true,
  "headerParameters": {
    "parameters": [
      {
        "name": "X-API-Key",
        "value": "={{$env.NOTE_API_SECRET_KEY}}"
      }
    ]
  },
  "sendBody": true,
  "bodyParameters": {
    "parameters": [
      {
        "name": "title",
        "value": "={{$json.title}}"
      },
      {
        "name": "body",
        "value": "={{$json.body}}"
      },
      {
        "name": "categories",
        "value": "={{$json.categories}}"
      }
    ]
  }
}
```

## トラブルシューティング

### セッションクッキーが期限切れ

**症状**: 401エラー「note authentication failed」

**対処法**:
1. ブラウザでnote.comに再ログイン
2. 新しい`_note_session_v5`を取得
3. Vercel環境変数 `NOTE_SESSION_COOKIE` を更新
4. `/api/health` で確認

### レート制限エラー

**症状**: 429エラー「Rate limit exceeded」

**対処法**:
- 10 requests/分の制限を遵守
- n8nワークフローに適切な遅延を追加
- 必要に応じてレート制限を調整

### note API変更

**症状**: 500エラー「note API request failed」

**対処法**:
1. Chrome DevToolsでnote.com APIを調査
2. エンドポイントやリクエスト形式の変更を確認
3. `publish-note.ts` を更新

## セキュリティ

### 推奨事項

✅ **実施済み**:
- API Key認証
- レート制限（10 req/分）
- 環境変数による機密情報管理
- タイムアウト設定（30秒）

⚠️ **追加推奨**:
- Vercel環境変数の定期的なローテーション
- アクセスログの監視
- 本番環境で `/api/debug` を無効化
- IPアドレス制限（n8nサーバーのみ許可）

### セッションクッキー管理

- **有効期限**: 通常30-90日（note仕様による）
- **定期チェック**: `/api/health` を毎日実行
- **アラート**: 401エラー時にSlack緊急通知

## パフォーマンス

- **実行時間**: 1-3秒
- **Vercel制限**: 無料プランで月100GB転送
- **想定負荷**: 1日1本 × 30日 = 30リクエスト/月

## 関連ドキュメント

- [Phase2 WF6実装プロンプト](../../docs/prompts/phase2-wf6-note-article-generation-prompt.md)
- [Phase2設計書](../../Phase2_n8nワークフロー詳細設計書_改訂版_v2.0.md)

## ライセンス

Private use only

---

**最終更新**: 2025-10-29
