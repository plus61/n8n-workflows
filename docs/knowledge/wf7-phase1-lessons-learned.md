# WF7 Phase1検証で得られたナレッジ

**作成日**: 2025-10-30
**検証ワークフロー**: WF7 Phase1: SNS動画台本整形 (fqbULAMXIGyBkNtL)
**検証結果**: ✅ 成功 (Execution ID: 942, 12.3秒)

---

## 🎯 重要な教訓サマリー

| # | 問題 | 解決策 | 適用優先度 |
|---|------|--------|-----------|
| 1 | HTTP Request Node v4で複雑なjsonBodyが構文エラー | 2-nodeパターン（Code + HTTP Request） | 🔴 Critical |
| 2 | Notion API プロパティ検証エラー | データベーススキーマ事前確認 | 🔴 Critical |
| 3 | Webhook URLパス混乱 | 本番: /webhook/, テスト: /webhook-test/ | 🟡 Medium |

---

## 📋 教訓1: HTTP Request Node v4の複雑なペイロード問題

### 問題の詳細

**症状**:
- HTTP Request Node v4の`jsonBody`パラメータに複雑なネストされたJSONオブジェクトを直接記述すると"invalid syntax"エラーが発生
- n8nの式パーサーが複雑なテンプレートリテラルや深くネストされたオブジェクトを正しく解析できない

**影響範囲**:
- GPT-4o-mini API呼び出し
- Notion API呼び出し
- その他の複雑なペイロードを持つすべての外部API統合

### 解決策: 2-Nodeパターン

**パターン構造**:
```
[Code Node: ペイロード作成] → [HTTP Request Node: シンプル参照]
```

**実装例**:

#### ✅ 正しい実装（2-nodeパターン）

**Node 1: GPTペイロード作成 (Code Node)**
```javascript
const data = $input.first().json;

const payload = {
  model: 'gpt-4o-mini',
  messages: [
    {
      role: 'system',
      content: 'あなたは縦型ショート動画の台本作成の専門家です。'
    },
    {
      role: 'user',
      content: `以下のnote記事情報から動画スクリプトを生成してください。

記事タイトル: ${data.title}
キーポイント: ${data.keyPoints.join(', ')}`
    }
  ],
  temperature: 0.7,
  response_format: { type: 'json_object' }
};

return {
  json: {
    originalData: data,
    gptPayload: payload  // ← ペイロードを出力
  }
};
```

**Node 2: GPT API呼び出し (HTTP Request Node)**
```javascript
{
  "method": "POST",
  "url": "https://api.openai.com/v1/chat/completions",
  "sendBody": true,
  "specifyBody": "json",
  "jsonBody": "={{ $json.gptPayload }}",  // ← シンプルな参照のみ
  "sendHeaders": true,
  "headerParameters": {
    "parameters": [
      {
        "name": "Authorization",
        "value": "Bearer sk-proj-..."
      }
    ]
  }
}
```

#### ❌ 避けるべき実装

**HTTP Request Nodeに直接複雑な式を記述**
```javascript
{
  "jsonBody": "={{ { model: 'gpt-4o-mini', messages: [...], ... } }}"
  // ↑ これは構文エラーになる
}
```

### メリット

1. **可読性向上**: JavaScriptコードとして明確に記述できる
2. **デバッグ容易性**: Code Nodeの出力を個別に確認できる
3. **n8nパーサー回避**: 式パーサーの制限を回避
4. **再利用性**: ペイロード作成ロジックを他のワークフローに移植しやすい

### 適用すべきケース

- ✅ ネストされたオブジェクト（3階層以上）
- ✅ テンプレートリテラルを含むペイロード
- ✅ 配列操作（map, join等）を含むペイロード
- ✅ 条件分岐を含むペイロード構築

### 適用不要なケース

- ✅ シンプルな1階層のオブジェクト
- ✅ 既存の変数をそのまま渡すだけのケース

---

## 📋 教訓2: Notion APIプロパティ検証エラー

### 問題の詳細

**発生したエラー**:
```json
{
  "object": "error",
  "status": 400,
  "code": "validation_error",
  "message": "Script JSON is not a property that exists.",
  "request_id": "467d3c28-1905-4b6c-8607-4db62f0bae69"
}
```

**原因**:
- NotionペイロードにターゲットデータベースID `29b68d5c-2986-817f-b4e6-f84cf75ea9ed` に存在しないプロパティ名を含めていた
- Notion API v2022-06-28は、ページ作成前に全プロパティの存在を厳密にチェックする

**具体的な問題**:
- "Script JSON" プロパティを含めていたが、データベースに存在しない
- "children" 配列も不要だった

### 解決策

#### ステップ1: データベーススキーマの事前確認

**方法1: Notion UI で確認**
1. Notion でターゲットデータベースを開く
2. プロパティ一覧を確認
3. プロパティ名とタイプを正確に記録

**方法2: Notion API で確認**
```bash
curl -X GET 'https://api.notion.com/v1/databases/29b68d5c-2986-817f-b4e6-f84cf75ea9ed' \
  -H 'Authorization: Bearer ntn_...' \
  -H 'Notion-Version: 2022-06-28'
```

#### ステップ2: 最小限のプロパティから開始

**✅ 推奨アプローチ**:
```javascript
const notionPayload = {
  parent: {
    database_id: '29b68d5c-2986-817f-b4e6-f84cf75ea9ed'
  },
  properties: {
    // 必須プロパティのみ
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
    'Created At': {
      date: {
        start: data.createdAt
      }
    }
  }
  // children配列は不要（基本的なページ作成には不要）
};
```

#### ステップ3: 段階的にプロパティを追加

1. 最小限のプロパティでテスト実行
2. 成功したら必要なプロパティを1つずつ追加
3. 各追加後にテスト実行
4. エラーが出たプロパティを特定

### 予防策

**チェックリスト**:
- [ ] ターゲットデータベースIDを確認
- [ ] データベーススキーマをドキュメント化
- [ ] プロパティ名の正確なスペルを確認（大文字小文字、スペース）
- [ ] プロパティタイプを確認（title, rich_text, select, date等）
- [ ] 他のワークフロー（WF6等）のNotionペイロードを参照しない（別データベースの可能性）
- [ ] 最小限のプロパティから開始
- [ ] エラーメッセージから問題のプロパティ名を特定

### 他のPhaseへの適用

**Phase2-5で確認すべき点**:
- Notion API呼び出しがある場合、同じデータベースか別のデータベースか確認
- 各Phaseで使用するプロパティ名がデータベースに存在するか確認
- 2-nodeパターンを適用してペイロード構築とAPI呼び出しを分離

---

## 📋 教訓3: Production vs Test Webhook URL

### 問題の詳細

**症状**:
```json
{
  "code": 404,
  "message": "The requested webhook \"wf7-test-webhook\" is not registered."
}
```

**原因**:
- Production環境（workflow active: true）で `/webhook-test/` パスを使用していた
- Test mode と Production mode でWebhook URLのパスが異なる

### 解決策

#### Webhook URLパスのルール

| Mode | 状態 | URLパス | 動作 |
|------|------|---------|------|
| **Production** | Workflow Active (ON) | `/webhook/{path}` | 常時有効 |
| **Test** | Manual Execution | `/webhook-test/{path}` | "Execute Workflow"クリック後1回のみ |

#### 正しいURL構成

**Production Webhook** (Workflow Active = ON):
```
https://n8n-python-production-344b.up.railway.app/webhook/wf7-test-webhook
```

**Test Webhook** (Manual Execution):
```
https://n8n-python-production-344b.up.railway.app/webhook-test/wf7-test-webhook
```

### 確認方法

**n8n UIでの確認**:
1. ワークフローを開く
2. Webhook Nodeをクリック
3. "Test URL" と "Production URL" が表示される
4. Workflow が Active かどうかを確認

**cURLテスト**:
```bash
# Production URL (workflow active)
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-test-webhook \
  -H "Content-Type: application/json" \
  -d @/tmp/wf7-phase1-test-data.json

# Test URL (manual execution mode)
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook-test/wf7-test-webhook \
  -H "Content-Type: application/json" \
  -d @/tmp/wf7-phase1-test-data.json
```

### ベストプラクティス

1. **開発時**: Test URL を使用して、n8n UIで実行を確認
2. **デバッグ時**: Test URL を使用して、各ノードの出力を個別に確認
3. **統合テスト時**: Workflow を Active にして Production URL でE2Eテスト
4. **本番運用時**: Production URL のみを外部システムに登録

---

## 🔧 Phase2-5への適用チェックリスト

### 各Phaseで確認すべき項目

#### HTTP Request Node チェック
- [ ] `jsonBody` に複雑なネストされた式が含まれていないか
- [ ] 3階層以上のオブジェクト、テンプレートリテラル、配列操作がある場合は2-nodeパターンを適用
- [ ] `specifyBody: "json"` + `jsonBody: "={{ $json.propertyName }}"` のシンプル参照パターンを使用

#### Notion API統合チェック
- [ ] ターゲットデータベースIDを確認
- [ ] データベーススキーマを確認（プロパティ名とタイプ）
- [ ] 最小限のプロパティから開始
- [ ] 他のワークフローのペイロードを流用していないか確認

#### Webhook設定チェック
- [ ] Webhook Node の設定を確認
- [ ] Production URL と Test URL を明確に区別
- [ ] E2Eテスト時は Production URL を使用

#### 一般的なベストプラクティス
- [ ] `.first()` メソッドを使用（`.item` は非推奨）
- [ ] ノード参照は正確な名前を使用: `$('NodeName').first().json.property`
- [ ] エラーハンドリングを実装: `continueOnFail: true` または `onError: "continueErrorOutput"`
- [ ] タイムアウト設定を適切に設定: `options.timeout: 30000` (30秒)

---

## 📊 Phase1検証結果

### 成功した実行（Execution ID: 942）

**実行時間**: 12.3秒
**ステータス**: success
**実行ノード数**: 10/10

#### ノード別実行時間

| ノード名 | 実行時間 | ステータス | 備考 |
|---------|---------|-----------|------|
| WF6完了Webhook | 1ms | success | Webhook受信 |
| 入力データ整形 | 7ms | success | データ整形 |
| GPTペイロード作成 | 5ms | success | 2-nodeパターン適用 |
| GPT API呼び出し | 11.15秒 | success | GPT-4o-mini |
| スクリプトJSON解析 | 8ms | success | JSON解析 |
| Notionペイロード作成 | 6ms | success | 2-nodeパターン適用 |
| Notion API呼び出し | 786ms | success | ページ作成成功 |
| ScriptJSON生成 | 12ms | success | JSONファイル生成 |
| Slack通知 | 298ms | success | 通知送信 |
| Respond to Webhook | 1ms | success | レスポンス返却 |

#### 生成されたリソース

**Notionページ**:
- Page ID: `29c68d5c-2986-8133-a61e-c1d7fa737aa0`
- Title: "MEO対策の基本"
- URL: https://www.notion.so/MEO-29c68d5c29868133a61ec1d7fa737aa0

**GPT生成スクリプト**:
- 4セクション構成: Hook, Pain, Solution, CTA
- 各セクションにテロップ、ナレーション、アセットタグを含む
- JSON形式で正しく出力

---

## 🚀 次のステップ

### Phase2: 素材取得 (Workflow ID: sGjN9Vqw4pGTLmaX)

**確認ポイント**:
- Pexels API, Unsplash APIの統合
- Google Drive ファイルアップロード
- 複雑なペイロードの有無

### Phase3: 音声・字幕生成 (Workflow ID: KkiF386PmAVaY1mA)

**確認ポイント**:
- VOICEVOX Docker API呼び出し
- 条件分岐（needsNarration）
- 音声ファイル処理

### Phase4: 動画レンダリング (Workflow ID: VF3kFwJLKVq990jn)

**確認ポイント**:
- 動画レンダリングAPI統合
- ポーリング/待機ロジック
- Cloud Run/Lambda統合

### Phase5: メタデータ登録・連携 (Workflow ID: 0CK4yaBsipa1UgSz)

**確認ポイント**:
- Notion API呼び出し（Phase1と同じ問題の可能性）
- Slack通知
- WF8 Webhook統合

---

**ドキュメント作成**: 2025-10-30
**最終更新**: 2025-10-30
**検証者**: Claude Code SuperClaude
