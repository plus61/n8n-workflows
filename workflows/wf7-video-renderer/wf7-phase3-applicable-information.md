# WF7 Phase3: 適用可能情報の抽出結果

**作成日**: 2025-10-31
**調査元**: WF5, WF7 Phase1, WF7 Phase2の運用ワークフロー

---

## 📋 抽出した適用可能情報

### 1. 環境変数・認証情報

#### OpenAI API
- **Authorization**: `Bearer <OPENAI_API_KEY>`
- **URL**: `https://api.openai.com/v1/chat/completions`
- **使用モデル**:
  - Phase1: `gpt-4o-mini`
  - WF5: `gpt-4-turbo-preview`

#### Notion API
- **Authorization**: `Bearer <NOTION_API_TOKEN>`
- **Notion-Version**: `2022-06-28`
- **データベースID**:
  - note記事管理DB: `29968d5c-2986-81ad-90d0-c24ed710503e`
  - トピックマスタDB: `29968d5c-2986-81d7-8a8b-e921a0e06a9a`
  - **動画管理DB**: `29b68d5c-2986-817f-b4e6-f84cf75ea9ed` (Phase1で使用)

#### Slack Webhook
- **URL**: `<SLACK_WEBHOOK_URL>`
- **Content-Type**: `application/json`

### 2. Webhook設定パターン

#### Phase1 Webhook (成功例)
```javascript
{
  "type": "n8n-nodes-base.webhook",
  "typeVersion": 2.1,
  "parameters": {
    "path": "wf7-test-webhook",
    "httpMethod": "POST",
    "responseMode": "responseNode",
    "options": {}
  },
  "webhookId": "wf7-phase1-video-script",
  "onError": "continueRegularOutput"  // ノード設定レベルで指定
}
```

#### Phase2 Webhook (成功例)
```javascript
{
  "type": "n8n-nodes-base.webhook",
  "typeVersion": 2,
  "parameters": {
    "httpMethod": "POST",
    "path": "wf7-phase2-assets",
    "responseMode": "responseNode",
    "options": {}
  },
  "webhookId": "685e811e-859e-44b3-b6ec-415e3faae421"
}
```

### 3. Webhook入力データ解析パターン

#### Phase1での実装 (参考にすべきパターン)
```javascript
// Phase1: 入力データ整形ノード
const body = $input.first().json.body;

return {
  json: {
    articleId: body.articleId,
    title: body.title,
    keyPoints: body.keyPoints,
    createdAt: new Date().toISOString()
  }
};
```

#### Phase2での実装 (参考にすべきパターン)
```javascript
// Phase2: アセットタグ抽出ノード
const input = $input.first().json;
// Webhookからのデータを適切にパース
const body = input.body?.body || input.body || input;
const assetTags = (body.assetTags || '').split(',').map(t => t.trim()).filter(Boolean);
const articleId = body.articleId;
const notionPageId = body.notionPageId;

if (!articleId) {
  throw new Error('articleId is required');
}

if (!notionPageId) {
  throw new Error('notionPageId is required');
}

if (assetTags.length === 0) {
  throw new Error('No asset tags provided');
}
```

### 4. Notion API呼び出しパターン

#### ページ作成パターン (Phase1)
```javascript
// Notionペイロード作成ノード
const notionPayload = {
  parent: {
    database_id: '29b68d5c-2986-817f-b4e6-f84cf75ea9ed'
  },
  properties: {
    'Title': {
      title: [{
        text: {
          content: data.title
        }
      }]
    },
    'Article ID': {
      rich_text: [{
        text: {
          content: data.articleId
        }
      }]
    },
    'Status': {
      select: {
        name: 'Processing'
      }
    },
    'Needs Narration': {
      checkbox: false
    },
    'Created At': {
      date: {
        start: data.createdAt
      }
    }
  }
};
```

#### ページ更新パターン (Phase2)
```javascript
// HTTP Request Node設定
{
  "method": "PATCH",
  "url": "=https://api.notion.com/v1/pages/{{ $json.notionPageId }}",
  "authentication": "none",
  "sendHeaders": true,
  "headerParameters": {
    "parameters": [
      {
        "name": "Authorization",
        "value": "Bearer <NOTION_API_TOKEN>"
      },
      {
        "name": "Notion-Version",
        "value": "2022-06-28"
      },
      {
        "name": "Content-Type",
        "value": "application/json"
      }
    ]
  },
  "sendBody": true,
  "specifyBody": "json",
  "jsonBody": "={{ $json.notionPayload }}",
  "options": {
    "timeout": 10000
  }
}
```

### 5. エラーハンドリング・リトライ設定

#### WF5での実装 (ベストプラクティス)
```javascript
// Notion API呼び出し
"options": {
  "retry": {
    "enabled": true,
    "maxTries": 3,
    "waitBetween": 1000,
    "backoffRate": 2
  }
}

// GPT-4 API呼び出し
"options": {
  "retry": {
    "enabled": true,
    "maxTries": 2,
    "waitBetween": 1000
  }
}
```

#### Phase1での実装
```javascript
// GPT API呼び出し
"options": {
  "timeout": 30000
}

// Notion API呼び出し
"options": {
  "timeout": 10000
}
```

### 6. Slack通知フォーマット

#### Phase1での実装
```javascript
{
  "method": "POST",
  "url": "<SLACK_WEBHOOK_URL>",
  "sendBody": true,
  "specifyBody": "json",
  "jsonBody": "={{ {text: '✅ WF7 Phase1完了\\n\\n📄 ' + $json.title + '\\n🆔 ' + $json.articleId + '\\n🔗 ' + $json.notionPageUrl} }}"
}
```

### 7. Respond to Webhook設定

#### Phase1での実装
```javascript
{
  "type": "n8n-nodes-base.respondToWebhook",
  "typeVersion": 1.4,
  "parameters": {
    "respondWith": "json",
    "responseBody": "={{ {status: 'success', message: 'WF7 Phase1 completed', articleId: $json.articleId, title: $json.title, notionPageUrl: $json.notionPageUrl} }}",
    "options": {}
  },
  "onError": "continueRegularOutput"
}
```

### 8. ノード参照構文

#### 正しい参照方法 (Phase1/2/WF5で使用)
```javascript
// Phase1
const payloadNode = $('GPTペイロード作成').first().json;
const inputData = payloadNode.originalData;

// Phase2
const prevData = $('アセットタグ抽出').first().json;

// WF5
const top10Articles = $('Function - トップ10記事抽出').first().json.articles;
const trendKeywords = $('Function - GPT-4レスポンスパース').first().json.trendKeywords;
```

---

## 🎯 Phase3への適用推奨事項

### 優先度: 高 (即座に適用すべき)

1. **環境変数の適用**
   - OpenAI APIキー
   - Notion APIトークン
   - Notion Database ID: `29b68d5c-2986-817f-b4e6-f84cf75ea9ed`
   - Slack Webhook URL

2. **Webhook onError設定の確認**
   - 現在のPhase3 Webhook設定を確認し、`onError: "continueRegularOutput"`が設定されているか検証

3. **リトライロジックの強化**
   - 音声生成API (VOICEVOX)に対して`maxTries: 2-3`, `waitBetween: 1000`を設定
   - Notion API更新に対して`maxTries: 3`, `waitBetween: 1000`, `backoffRate: 2`を設定

4. **エラーメッセージの改善**
   - 必須パラメータ検証時のエラーメッセージを具体的に
   - 例: `'articleId and notionPageId are required'`

### 優先度: 中 (テスト前に適用推奨)

5. **Slack通知フォーマットの統一**
   - Phase1と同様のフォーマットで通知
   - ステータス、タイトル、articleId、Notion URLを含める

6. **Webhook Response形式の統一**
   - Phase1パターンに合わせてJSONレスポンスを返す
   - `{status, message, articleId, notionPageUrl}` 形式

7. **scriptUrl解析機能の実装**
   - Phase1の`ScriptJSON生成`ノードを参考に
   - 外部URLから`script.json`を取得してnarrationTextを抽出

### 優先度: 低 (Phase3 E2Eテスト後に検討)

8. **環境変数化の検討**
   - `$env.OPENAI_API_KEY`
   - `$env.NOTION_API_TOKEN`
   - `$env.NOTION_VIDEO_DB_ID`
   - `$env.SLACK_WEBHOOK_URL`
   - `$env.VOICEVOX_URL`

---

## 📊 Phase3現在の設定と推奨変更

### ナレーション抽出ノード

**現在**:
```javascript
const narrationText = 'こちらの動画では、MEO対策の基本を紹介します。'; // TODO
```

**推奨**: Phase1のscriptUrl解析パターンを参考に実装
```javascript
// scriptUrlが提供されている場合
if (scriptUrl) {
  // HTTP Requestでscript.jsonを取得
  const scriptResponse = await fetch(scriptUrl);
  const scriptData = await scriptResponse.json();
  const narrationText = scriptData.segments
    .map(s => s.narrationText)
    .filter(Boolean)
    .join(' ');
}
```

### 音声メタデータ保存ノード

**現在**:
```javascript
const voiceFileUrl = `https://storage.example.com/voice_${articleId}.wav`; // TODO
```

**推奨**: Phase2の外部ストレージパターンを参考に
```javascript
// 将来的な実装: Cloudflare R2, S3, GCS等
// 現在はダミーURLのまま、外部ストレージ統合は別タスク
```

### Notion API呼び出し設定

**推奨変更**:
```javascript
{
  "headerParameters": {
    "parameters": [
      {
        "name": "Authorization",
        "value": "Bearer <NOTION_API_TOKEN>"
      },
      {
        "name": "Notion-Version",
        "value": "2022-06-28"
      },
      {
        "name": "Content-Type",
        "value": "application/json"
      }
    ]
  },
  "options": {
    "timeout": 10000,
    "retry": {
      "enabled": true,
      "maxTries": 3,
      "waitBetween": 1000,
      "backoffRate": 2
    }
  }
}
```

---

## ✅ 次のアクション

1. **Phase3ワークフローの更新**: 上記の優先度「高」項目を適用
2. **構造的検証**: 変更後にvalidationを実行
3. **E2Eテスト準備**: テストデータの準備とVOICEVOX API確認
4. **E2Eテスト実行**: Webhook経由でのフルフロー確認

---

**最終更新**: 2025-10-31
**ステータス**: ✅ 調査完了、適用準備完了
