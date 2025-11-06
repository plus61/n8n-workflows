# WF7 Phase3: 適用した改善内容

**適用日**: 2025-10-31
**Workflow ID**: `KkiF386PmAVaY1mA`
**ベース**: WF5, WF7 Phase1, WF7 Phase2 の運用ノウハウ

---

## 📋 適用した改善内容サマリー

### 1. Webhook設定の強化

**適用前**:
```javascript
{
  "typeVersion": 2,
  "parameters": {
    "httpMethod": "POST",
    "path": "wf7-phase3-audio",
    "responseMode": "responseNode",
    "options": {
      "onError": "continueRegularOutput"
    }
  }
}
```

**適用後**:
```javascript
{
  "typeVersion": 2.1,  // Phase1と同じバージョン
  "parameters": {
    "httpMethod": "POST",
    "path": "wf7-phase3-audio",
    "responseMode": "responseNode",
    "options": {}
  },
  "onError": "continueRegularOutput"  // ノードレベルで設定
}
```

**理由**: Phase1で検証済みのパターン。`onError`はノードレベルで設定する方が推奨される。

---

### 2. リトライロジックの追加

#### VOICEVOX音声クエリ

**適用前**:
```javascript
"options": {
  "timeout": 10000
}
```

**適用後**:
```javascript
"options": {
  "timeout": 10000,
  "retry": {
    "enabled": true,
    "maxTries": 2,
    "waitBetween": 1000
  }
}
```

**理由**: GPT-4 API呼び出しと同じリトライパターンを適用。外部API呼び出しの安定性向上。

#### VOICEVOX音声合成

**適用前**:
```javascript
"options": {
  "response": {"response": {"responseFormat": "file"}},
  "timeout": 30000
}
```

**適用後**:
```javascript
"options": {
  "response": {"response": {"responseFormat": "file"}},
  "timeout": 30000,
  "retry": {
    "enabled": true,
    "maxTries": 2,
    "waitBetween": 1000
  }
}
```

**理由**: 音声合成は時間がかかる処理のため、リトライロジックで安定性を向上。

#### Notionページ更新

**適用前**:
```javascript
"options": {
  "timeout": 10000
}
```

**適用後**:
```javascript
"options": {
  "timeout": 10000,
  "retry": {
    "enabled": true,
    "maxTries": 3,
    "waitBetween": 1000,
    "backoffRate": 2
  }
}
```

**理由**: WF5の実績あるリトライ設定を適用。Notion APIの429エラー対策として指数バックオフを実装。

---

### 3. Webhook Response の強化

**適用前**:
```javascript
{
  "typeVersion": 1,
  "parameters": {
    "options": {}
  }
}
```

**適用後**:
```javascript
{
  "typeVersion": 1.4,
  "parameters": {
    "respondWith": "json",
    "responseBody": "={{ {
      status: 'success',
      message: 'WF7 Phase3 completed',
      articleId: $('ナレーション抽出').first().json.articleId,
      notionPageId: $('ナレーション抽出').first().json.notionPageId,
      voiceFileUrl: $('音声メタデータ保存').first().json.voiceFileUrl,
      subtitleFileUrl: $('字幕メタデータ保存').first().json.subtitleFileUrl
    } }}",
    "options": {}
  },
  "onError": "continueRegularOutput"
}
```

**理由**: Phase1と同様の構造化されたJSONレスポンス。呼び出し元でステータス確認が可能。

---

### 4. Connections の修正

**問題点**: 存在しない `Sheets素材完了検知` ノードへの接続が残っていた。

**修正前**:
```javascript
"connections": {
  "Sheets素材完了検知": {  // ❌ 存在しないノード
    "main": [[{"node": "音声必要性判定", ...}]]
  },
  // ...
}
```

**修正後**:
```javascript
"connections": {
  "WF7-Phase3 Webhook": {  // ✅ 正しいトリガーノード
    "main": [[{"node": "音声必要性判定", ...}]]
  },
  // ...
}
```

**理由**: Google Sheets トリガーから Webhook トリガーへの移行時に古い接続が残っていた。

---

## 🎯 適用しなかった項目（TODO）

### 優先度: 中

1. **scriptUrl解析機能** (現在: ハードコードされたテキスト)
   ```javascript
   // 現在
   const narrationText = 'こちらの動画では、MEO対策の基本を紹介します。';

   // 将来的に実装
   if (scriptUrl) {
     const scriptResponse = await fetch(scriptUrl);
     const scriptData = await scriptResponse.json();
     const narrationText = scriptData.segments
       .map(s => s.narrationText)
       .filter(Boolean)
       .join(' ');
   }
   ```

2. **外部ストレージ統合** (現在: ダミーURL)
   ```javascript
   // 現在
   const voiceFileUrl = `https://storage.example.com/voice_${articleId}.wav`;

   // 将来的に実装: Cloudflare R2, AWS S3, GCS等
   ```

### 優先度: 低

3. **環境変数化**
   - OpenAI APIキー
   - Notion APIトークン
   - Database IDs
   - Slack Webhook URL
   - VOICEVOX URL

---

## 📊 適用結果

### ノード構成

| ノード名 | タイプ | 主な変更 |
|---------|--------|---------|
| WF7-Phase3 Webhook | webhook | typeVersion 2.1, onError設定 |
| 音声必要性判定 | if | 変更なし |
| ナレーション抽出 | code | 変更なし |
| VOICEVOX音声クエリ | httpRequest | リトライ追加 (maxTries: 2) |
| VOICEVOX音声合成 | httpRequest | リトライ追加 (maxTries: 2) |
| 音声メタデータ保存 | code | 変更なし |
| SRT字幕生成 | code | 変更なし |
| 字幕メタデータ保存 | code | 変更なし |
| Notionペイロード作成 | code | 変更なし |
| Notionページ更新 | httpRequest | リトライ追加 (maxTries: 3, backoff) |
| Respond to Webhook | respondToWebhook | typeVersion 1.4, JSONレスポンス追加 |

### 接続フロー

```
WF7-Phase3 Webhook
  ↓
音声必要性判定
  ↓ (true)
ナレーション抽出
  ↓
VOICEVOX音声クエリ [リトライ: maxTries=2]
  ↓
VOICEVOX音声合成 [リトライ: maxTries=2]
  ↓
音声メタデータ保存
  ↓
SRT字幕生成
  ↓
字幕メタデータ保存
  ↓
Notionペイロード作成
  ↓
Notionページ更新 [リトライ: maxTries=3, backoffRate=2]
  ↓
Respond to Webhook [JSON形式のレスポンス]
```

---

## 🚀 次のステップ

### 即座に実施

1. **E2Eテスト実行**
   ```bash
   curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase3-audio \
     -H "Content-Type: application/json" \
     -d @/tmp/wf7-phase3-test-data.json
   ```

2. **テストケース**:
   - ✅ 正常系 (needsNarration: true)
   - ⏳ スキップ系 (needsNarration: false)
   - ⏳ エラー系 (必須パラメータ欠落)

### 検証項目

1. **Webhook動作確認**
   - リクエスト受信確認
   - 入力データパース確認
   - onError設定の動作確認

2. **リトライロジック確認**
   - VOICEVOX API障害時の自動リトライ
   - Notion API 429エラー時の指数バックオフ
   - 最大リトライ回数到達時の挙動

3. **レスポンス確認**
   - JSON形式のレスポンス
   - 必要なフィールドがすべて含まれているか
   - エラー時のレスポンス

---

**最終更新**: 2025-10-31
**ステータス**: ✅ 改善適用完了、⏳ E2Eテスト準備完了
