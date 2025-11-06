# WF8: SNS投稿自動化ワークフロー (Twitter/Instagram/TikTok)

**作成日**: 2025-11-05
**更新日**: 2025-11-05
**ステータス**: 🟡 設計完了 - API認証設定が必要
**目的**: WF7で生成された動画を自動的にTwitter(X)、Instagram、TikTokに投稿

---

## ワークフロー概要

### アーキテクチャ
```
WF7 Phase5 → WF8 Webhook
  ↓
入力データ解析 (articleId, videoUrl, title, thumbUrl)
  ↓
AI Caption Generation (GPT-4) - プラットフォーム別キャプション生成
  ↓
Caption Parsing - JSON解析とフォールバック処理
  ↓
[3プラットフォームに分岐]
  ├→ Twitter投稿準備 → Twitter投稿 (TODO)
  ├→ Instagram投稿準備 → Instagram投稿 (TODO)
  └→ TikTok投稿準備 → TikTok投稿 (TODO)
  ↓
投稿結果マージ
  ↓
投稿サマリー作成
  ↓
Notion投稿記録更新 (Status: Completed → SNS Posted)
  ↓
Respond to Webhook
```

### ノード構成 (15ノード)
1. **WF8-SNS投稿 Webhook** - Phase5からのトリガー
2. **入力データ解析** - 入力バリデーションとデータ抽出
3. **AI Caption Generation (GPT-4)** - プラットフォーム別キャプション生成
4. **Caption Parsing** - GPT-4レスポンス解析
5-7. **投稿準備ノード** (Twitter/Instagram/TikTok) - プラットフォーム別データ準備
8-10. **投稿ノード** (Twitter/Instagram/TikTok) - 実際の投稿処理 (TODO)
11. **投稿結果マージ** - 3プラットフォームの結果統合
12. **投稿サマリー作成** - レポート生成
13. **Notion投稿記録更新** - ステータス更新
14. **Respond to Webhook** - レスポンス返却

---

## テンプレート分析に基づく設計

### 参考テンプレート
- **Template 3895** (4,061 views): 📢 Multi-Platform Video Publisher – YouTube, Instagram & TikTok
- **Template 2894** (31,334 views): Upload to Instagram, Tiktok & Youtube from Google Drive
- **Template 3524** (3,458 views): Upload Carousel of Images to Tiktok and Instagram with upload-post.com
- **Template 4568** (49,609 views): Transform Podcasts to TikTok Clips
- **Template 5787** (90 views): Google Drive → Instagram/TikTok/YouTube with Airtable tracking

### 採用パターン
1. **AI Caption Generation**: GPT-4でプラットフォーム別に最適化されたキャプション生成
2. **Multi-Platform Support**: 3プラットフォーム同時投稿 (Twitter/X, Instagram, TikTok)
3. **Error Resilience**: 1プラットフォーム失敗でも他は継続実行
4. **Metadata Tracking**: Notion DBで投稿履歴管理
5. **upload-post.com Integration**: Instagram/TikTok投稿に推奨される第三者API活用

---

## 入力データ構造

### Phase5からの入力 (Webhook)
```json
{
  "articleId": "string",
  "notionPageId": "string (UUID)",
  "title": "string",
  "videoUrl": "string (https://...)",
  "thumbUrl": "string (https://...)"
}
```

### バリデーション
- ✅ `articleId`: 必須
- ✅ `videoUrl`: 必須
- ✅ `title`: 必須
- ⚪ `notionPageId`: オプション (Notion更新時のみ必要)
- ⚪ `thumbUrl`: オプション

---

## AI Caption Generation

### GPT-4プロンプト
```
あなたはSNS投稿の専門家です。動画タイトルから魅力的な投稿文を3パターン作成してください。

1) Twitter/X用(280文字以内、ハッシュタグ3-5個)
2) Instagram用(300文字以内、絵文字活用)
3) TikTok用(100文字以内、キャッチー)

JSON形式で返してください:
{
  "twitter": "string",
  "instagram": "string",
  "tiktok": "string"
}
```

### 期待される出力例
```json
{
  "twitter": "MEO対策の基本を徹底解説🎬\n\nGoogleマップで上位表示を目指すなら必見です👀\n\n▶️ 動画はこちら\nhttps://...\n\n#MEO対策 #Googleマップ #ローカルSEO #集客 #マーケティング",

  "instagram": "MEO対策の基本📍✨\n\nGoogleマップで上位表示するための秘訣を大公開！🎯\n\n詳しくはプロフィールのリンクから👆\n\n#MEO対策 #Googleマップ #ローカルSEO #ビジネス #マーケティング #集客術",

  "tiktok": "MEO対策の基本🎬 Googleマップで上位表示するコツを解説！ #MEO #集客"
}
```

### フォールバック処理
GPT-4がエラーの場合、シンプルなテンプレートキャプションを自動生成:
```javascript
{
  twitter: `${title} 🎬\n\n動画をチェック👇\n${videoUrl}\n\n#動画 #AI #自動化`,
  instagram: `${title}\n\n📹 最新動画を公開しました！\n\n詳しくはプロフィールのリンクから👆\n\n#動画 #AI #自動化`,
  tiktok: `${title.substring(0, 80)}... 🎬`
}
```

---

## SNS投稿設定 (TODO実装)

### Twitter/X API v2
**必要な認証情報**:
- API Key
- API Secret
- Access Token
- Access Token Secret

**エンドポイント**: `POST /2/tweets`

**リクエスト例**:
```json
{
  "text": "{{ $json.caption }}"
}
```

**n8n設定**:
```javascript
{
  "method": "POST",
  "url": "https://api.twitter.com/2/tweets",
  "authentication": "oAuth2",
  "sendBody": true,
  "specifyBody": "json",
  "jsonBody": "={{ { \"text\": $json.caption } }}"
}
```

**実装ノート**: Twitter API v2 OAuth 2.0認証が必要

---

### Instagram Reels (Meta Graph API)
**必要な認証情報**:
- Instagram Business Account ID
- Facebook Page Access Token (long-lived推奨)

**エンドポイント**: `POST /{ig-user-id}/media`

**2ステップアップロード**:

**Step 1: メディアコンテナ作成**
```json
{
  "media_type": "REELS",
  "video_url": "{{ $json.videoUrl }}",
  "caption": "{{ $json.caption }}"
}
```

**Step 2: メディア公開**
```json
{
  "creation_id": "{{ $json.containerId }}"
}
```

**n8n設定例**:
```javascript
{
  "method": "POST",
  "url": "=https://graph.facebook.com/v18.0/{{ $env.INSTAGRAM_BUSINESS_ID }}/media",
  "sendBody": true,
  "specifyBody": "json",
  "jsonBody": "={{ {\n  \"media_type\": \"REELS\",\n  \"video_url\": $json.videoUrl,\n  \"caption\": $json.caption,\n  \"access_token\": $env.FACEBOOK_PAGE_ACCESS_TOKEN\n} }}"
}
```

**必要な権限**:
- `instagram_basic`
- `instagram_content_publish`
- `pages_read_engagement`

**実装ノート**: Meta Graph API (Reels) または upload-post.com経由の投稿が必要

---

### TikTok API
**必要な認証情報**:
- Access Token (OAuth 2.0)
- Open API App ID

**エンドポイント**: `POST /share/video/upload/`

**リクエスト例**:
```json
{
  "video": {
    "video_url": "{{ $json.videoUrl }}"
  },
  "post_info": {
    "title": "{{ $json.caption }}",
    "privacy_level": "PUBLIC_TO_EVERYONE",
    "disable_duet": false,
    "disable_comment": false,
    "disable_stitch": false,
    "video_cover_timestamp_ms": 1000
  },
  "source_info": {
    "source": "FILE_UPLOAD",
    "video_url": "{{ $json.videoUrl }}"
  }
}
```

**n8n設定例**:
```javascript
{
  "method": "POST",
  "url": "https://open.tiktokapis.com/v2/post/publish/video/init/",
  "sendHeaders": true,
  "headerParameters": {
    "parameters": [
      {
        "name": "Authorization",
        "value": "=Bearer {{ $env.TIKTOK_ACCESS_TOKEN }}"
      },
      {
        "name": "Content-Type",
        "value": "application/json"
      }
    ]
  },
  "sendBody": true,
  "specifyBody": "json",
  "jsonBody": "={{ /* TikTok payload */ }}"
}
```

**実装ノート**: TikTok API または upload-post.com経由の投稿が必要

---

### upload-post.com 統合 (推奨オプション)

**概要**: Instagram/TikTok投稿を簡略化する第三者API (Template 3524, 2894で実証済み)

**必要な認証情報**:
- upload-post.com API Token
- プラットフォーム別アカウント識別子

**エンドポイント**: `POST https://api.upload-post.com/v1/upload`

**リクエスト例**:
```json
{
  "platform": "instagram|tiktok",
  "video_url": "{{ $json.videoUrl }}",
  "caption": "{{ $json.caption }}",
  "user": "account_identifier"
}
```

**n8n設定例**:
```javascript
{
  "method": "POST",
  "url": "https://api.upload-post.com/v1/upload",
  "sendHeaders": true,
  "headerParameters": {
    "parameters": [
      {
        "name": "Authorization",
        "value": "=Bearer {{ $env.UPLOADPOST_API_TOKEN }}"
      }
    ]
  },
  "sendBody": true,
  "specifyBody": "json",
  "jsonBody": "={{ {\n  \"platform\": \"instagram\",\n  \"video_url\": $json.videoUrl,\n  \"caption\": $json.caption,\n  \"user\": $env.UPLOADPOST_INSTAGRAM_USER\n} }}"
}
```

**メリット**:
- 複雑なOAuth認証が不要
- Instagram/TikTokの両方に対応
- エラーハンドリングが簡単
- n8nテンプレートで実証済み (31,334 views)

**セットアップ**:
1. https://upload-post.com でアカウント登録
2. API Tokenを取得
3. Instagram/TikTokアカウント連携
4. n8n環境変数に設定

---

## 出力データ構造

### Webhook Response
```json
{
  "articleId": "string",
  "notionPageId": "string",
  "timestamp": "ISO 8601 string",
  "platforms": [
    {
      "platform": "twitter",
      "status": "pending|success|error",
      "message": "string",
      "caption": "string"
    },
    {
      "platform": "instagram",
      "status": "pending|success|error",
      "message": "string",
      "caption": "string"
    },
    {
      "platform": "tiktok",
      "status": "pending|success|error",
      "message": "string",
      "caption": "string"
    }
  ]
}
```

### Notion更新内容
```javascript
{
  "properties": {
    "Status": {
      "select": {
        "name": "SNS Posted"  // Completed → SNS Posted
      }
    },
    "Posted Platforms": {
      "multi_select": [
        { "name": "twitter" },
        { "name": "instagram" },
        { "name": "tiktok" }
      ]
    }
  }
}
```

---

## セットアップ手順

### 1. ワークフローインポート
```bash
# n8n UIでインポート
workflows/wf8-sns-posting.json
```

### 2. 環境変数設定 (Railway)
```bash
# OpenAI API (既存)
OPENAI_API_KEY=sk-proj-...

# Twitter/X API (TODO)
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret

# Instagram Reels (Meta Graph API) - Option 1
INSTAGRAM_BUSINESS_ID=your_ig_business_id
FACEBOOK_PAGE_ACCESS_TOKEN=your_long_lived_token

# TikTok API - Option 1
TIKTOK_ACCESS_TOKEN=your_tiktok_access_token
TIKTOK_OPEN_API_APP_ID=your_app_id

# upload-post.com - Option 2 (推奨)
UPLOADPOST_API_TOKEN=your_uploadpost_token
UPLOADPOST_INSTAGRAM_USER=your_instagram_identifier
UPLOADPOST_TIKTOK_USER=your_tiktok_identifier

# Notion API (既存)
NOTION_API_TOKEN=ntn_...
```

### 3. Phase5との連携
Phase5の以下のノードを有効化:
- **WF8ペイロード構築** (現在無効)
- **WF8Webhook送信** (現在無効)

Phase5の`WF8ペイロード構築`ノード設定例:
```javascript
{
  "articleId": $json.articleId,
  "notionPageId": $json.notionPageId,
  "title": $json.title,
  "videoUrl": $json.videoUrl,
  "thumbUrl": $json.thumbUrl || ""
}
```

### 4. Webhookテスト
```bash
curl -X POST "https://n8n-python-production-344b.up.railway.app/webhook/wf8-sns-posting" \
  -H "Content-Type: application/json" \
  -d '{
    "articleId": "test-wf8-001",
    "notionPageId": "2a268d5c-2986-8180-9a4f-c3eabe4d1329",
    "title": "MEO対策の基本を徹底解説",
    "videoUrl": "https://n8n-python-production-344b.up.railway.app/webhook/wf7-files-video?articleId=test-video-001",
    "thumbUrl": "https://example.com/thumb.jpg"
  }'
```

---

## 実装ステータス

### ✅ 完了済み
- [x] ワークフロー構造設計
- [x] Webhook入力処理
- [x] AI Caption Generation (GPT-4統合)
- [x] プラットフォーム別データ準備
- [x] 投稿結果マージロジック
- [x] Notion更新処理
- [x] エラーハンドリング (フォールバック)

### ⏳ TODO (API認証設定)
- [ ] Twitter/X API v2認証設定
- [ ] Instagram Reels API設定 (Meta Graph API または upload-post.com)
- [ ] TikTok API設定 (TikTok Open API または upload-post.com)
- [ ] 各API実装ノードの完成
- [ ] upload-post.com アカウント作成 (推奨オプション)

### 🔮 将来の拡張
- [ ] YouTube Shorts自動投稿
- [ ] 承認ワークフロー (Slack/Telegram通知)
- [ ] 投稿スケジューリング機能
- [ ] A/Bテスト機能 (複数キャプション比較)
- [ ] 投稿分析ダッシュボード
- [ ] ハッシュタグトレンド分析機能
- [ ] 動画パフォーマンストラッキング

---

## テンプレートパターンとの比較

| 機能 | Template 3895 | Template 2894 | WF8設計 |
|------|---------------|---------------|---------|
| プラットフォーム数 | 3 (YouTube/IG/TT) | 3 (IG/TT/YT) | 3 (Twitter/IG/TT) |
| AI Caption | なし | OpenAI Whisper | GPT-4 ✅ |
| 承認ワークフロー | なし | なし | なし (将来実装) |
| エラー処理 | 継続実行 | 継続実行 | 継続実行 |
| メタデータ管理 | なし | なし | Notion統合 ✅ |
| 動画自動生成連携 | なし | Google Drive | WF7統合 ✅ |
| 投稿API | Meta/TikTok直接 | upload-post.com | 両方対応 ✅ |

### WF8の差別化ポイント
1. **完全自動化パイプライン**: WF7 (動画生成) → WF8 (SNS投稿) のシームレス連携
2. **Notion統合**: すべての投稿履歴とメタデータを一元管理
3. **GPT-4 AI**: プラットフォーム別に最適化されたキャプション自動生成
4. **柔軟な投稿方法**: 直接API または upload-post.com 両方に対応
5. **拡張性**: 将来的なプラットフォーム追加が容易な設計

---

## トラブルシューティング

### Issue 1: GPT-4レスポンスがJSON形式でない
**原因**: `response_format: { type: "json_object" }` 未設定

**解決策**:
```javascript
"jsonBody": "={{ {\n  \"model\": \"gpt-4\",\n  \"response_format\": { \"type\": \"json_object\" },\n  ...\n} }}"
```

### Issue 2: Twitter API 401 Unauthorized
**原因**: OAuth 1.0a認証の署名エラー

**解決策**: n8n Twitter認証情報で正しく設定:
- Credential Type: "Twitter OAuth2 API"
- すべての必要なトークンを入力

### Issue 3: Instagram Reels投稿が失敗する
**原因**: Business Account未設定、または動画形式の問題

**解決策**:
1. Instagram Business Accountに変換されているか確認
2. FacebookページとInstagramアカウントが連携されているか確認
3. 動画形式がInstagram Reelsの要件を満たしているか確認:
   - 解像度: 1080x1920 (9:16縦型推奨)
   - フォーマット: MP4またはMOV
   - 長さ: 15秒～90秒
   - サイズ: 最大1GB
4. upload-post.com を使用する場合は要件を確認

### Issue 4: TikTok投稿が認証エラー
**原因**: Access Tokenの期限切れ、または権限不足

**解決策**:
1. TikTok Developer Portalで新しいAccess Tokenを取得
2. 必要な権限を確認:
   - `video.upload`
   - `video.publish`
3. upload-post.com を使用する場合はアカウント連携を再確認

---

## パフォーマンス指標

### 目標値
- **処理時間**: < 15秒 (AI生成含む)
- **成功率**: ≥ 95% (プラットフォーム単位)
- **同時投稿**: 3プラットフォーム並列実行
- **リトライ**: 各プラットフォーム最大3回

### 実測値 (TODO)
- AI Caption Generation: ~3-5秒
- Twitter投稿: ~1-2秒
- Instagram Reels投稿: ~3-5秒 (2ステップアップロード)
- TikTok投稿: ~2-4秒
- 合計処理時間: ~10-16秒

---

## セキュリティ考慮事項

### API Key管理
- ✅ すべてのAPIキーは環境変数で管理
- ✅ Gitにコミットしない (.gitignore設定済み)
- ✅ Railway環境変数で暗号化保存

### Notion統合
- ✅ 最小権限の原則 (必要なDBのみアクセス)
- ✅ トークンはサーバーサイドのみ使用

### 入力バリデーション
- ✅ 必須パラメータチェック
- ✅ URL形式検証
- ✅ XSS対策 (Notion API側で処理)

---

## 参考リンク

### API Documentation
- [Twitter API v2](https://developer.twitter.com/en/docs/twitter-api)
- [Instagram Graph API](https://developers.facebook.com/docs/instagram-api/)
- [TikTok Open API](https://developers.tiktok.com/)
- [upload-post.com API](https://upload-post.com/docs)
- [OpenAI API](https://platform.openai.com/docs/api-reference)

### n8n Templates
- [Template 3895](https://n8n.io/workflows/3895) - Multi-Platform Video Publisher
- [Template 2894](https://n8n.io/workflows/2894) - Upload to Instagram, TikTok & YouTube
- [Template 3524](https://n8n.io/workflows/3524) - Upload Carousel with upload-post.com
- [Template 4568](https://n8n.io/workflows/4568) - Transform Podcasts to TikTok Clips

### Knowledge Base
- [n8n Workflow Construction Knowledge](/docs/knowledge/n8n-workflow-construction-knowledge.md)
- [WF7 Phase5 Documentation](/workflows/wf7-video-renderer/phase5-metadata.md)

---

**Last Updated**: 2025-11-05
**Status**: 🟡 Design Complete - Requires API Authentication Setup
**Next Step**: Configure API credentials and test each platform integration
