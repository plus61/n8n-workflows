# WF7 Phase4c アプローチ4実装計画

**作成日**: 2025-11-09  
**対象ワークフロー**: `chPw11OY5sex6d9I` (WF7 Phase4c - Perfect Implementation)  
**目的**: アプローチ4（response_urlにPOSTリクエスト）を実装して、動画URL取得の問題を解決

---

## 📋 現在の状況

### 実行1039での問題
- **アプローチ1**: ステータスレスポンスから動画URLを抽出 → ❌ 失敗（`output`フィールドなし）
- **アプローチ2**: `response_url`にGETリクエスト → ❌ 失敗（422エラー: Field required: tracks）
- **アプローチ3**: `status_url`にGETリクエスト → ❌ 失敗（`output`フィールドなし）

### 根本原因の仮説
1. **`response_url`はGETリクエストを受け付けない**: 422エラー（Field required: tracks）が発生
2. **POSTリクエストが必要な可能性**: 元のリクエストペイロードを含める必要がある
3. **ステータスレスポンスに`output`フィールドが含まれない**: `/compose`エンドポイントの仕様によるもの

---

## 🎯 アプローチ4の実装内容

### 実装方針
`response_url`にPOSTリクエストを送信し、元のリクエストペイロード（`inputs`、`output_format`など）を含める。

### ワークフロー構造の変更

#### 現在の構造
```
Extract Video URL (Attempt 2)
    ↓
Needs Status URL Request? (needs_status_url_request === true)
    ├─ True → Get Status URL (Approach 3) → Extract Video URL (Attempt 3) → Merge Video URL
    └─ False → Merge Video URL
```

#### 変更後の構造
```
Extract Video URL (Attempt 2)
    ↓
Needs POST Request? (needs_post_request === true)
    ├─ True → Get Result (Approach 4) → Extract Video URL (Attempt 4) → Merge Video URL
    └─ False → Needs Status URL Request? (needs_status_url_request === true)
                ├─ True → Get Status URL (Approach 3) → Extract Video URL (Attempt 3) → Merge Video URL
                └─ False → Merge Video URL
```

---

## 🔧 実装手順

### Step 1: Extract Video URL (Attempt 2)のコードを修正

**目的**: 422エラーの場合に`needs_post_request: true`を設定

**修正内容**:
```javascript
// エラーレスポンスの場合（422エラーなど）
if (resultData.detail || resultData.error) {
  console.warn('Get Result returned error:', JSON.stringify(resultData));
  
  // 422エラーの場合、アプローチ4（POSTリクエスト）を試す
  const attempt1Data = $('Extract Video URL (Attempt 1)').item.json;
  const is422Error = resultData.detail?.includes('tracks') || resultData.error?.includes('tracks');
  const needsPostRequest = Boolean(is422Error && attempt1Data.raw_status_response?.response_url);
  
  return [{
    json: {
      video_url: null,
      error: resultData.detail || resultData.error,
      needs_post_request: needsPostRequest,
      needs_status_url_request: !needsPostRequest && Boolean(attempt1Data.raw_status_response?.status_url),
      request_id: attempt1Data.request_id,
      script_id: attempt1Data.script_id || 'unknown'
    }
  }];
}
```

### Step 2: Needs POST Request?ノードを追加

**ノード設定**:
- **名前**: `Needs POST Request?`
- **タイプ**: `n8n-nodes-base.if`
- **条件**: `={{ $json.needs_post_request }}` === `true`
- **位置**: `Extract Video URL (Attempt 2)`の後

### Step 3: Get Result (Approach 4)ノードを追加

**ノード設定**:
- **名前**: `Get Result (Approach 4)`
- **タイプ**: `n8n-nodes-base.httpRequest`
- **Method**: POST
- **URL**: `={{ $('Extract Video URL (Attempt 1)').item.json.raw_status_response.response_url }}`
- **Authentication**: FAL API Key (httpHeaderAuth)
- **Body**: `={{ JSON.stringify($('ペイロード構築').item.json) }}`
- **Options**: `neverError: true`
- **位置**: `Needs POST Request?`のtrue分岐の後

### Step 4: Extract Video URL (Attempt 4)ノードを追加

**ノード設定**:
- **名前**: `Extract Video URL (Attempt 4)`
- **タイプ**: `n8n-nodes-base.code`
- **コード**: アプローチ2と同じパターンで動画URLを抽出
- **位置**: `Get Result (Approach 4)`の後

**コード例**:
```javascript
// アプローチ4: response_urlのPOSTレスポンスから動画URLを抽出
const resultData = $input.first().json;

// デバッグ用: レスポンス構造をログ出力
console.log('Get Result (Approach 4) response keys:', Object.keys(resultData));
console.log('Get Result (Approach 4) response preview:', JSON.stringify(resultData).substring(0, 500));

// エラーレスポンスの場合
if (resultData.detail || resultData.error) {
  console.warn('Get Result (Approach 4) returned error:', JSON.stringify(resultData));
  const attempt1Data = $('Extract Video URL (Attempt 1)').item.json;
  return [{
    json: {
      video_url: null,
      error: resultData.detail || resultData.error,
      request_id: attempt1Data.request_id,
      script_id: attempt1Data.script_id || 'unknown'
    }
  }];
}

// 動画URL抽出（複数のパターンを試す）
let videoUrl = resultData.output?.video_url
  || resultData.output?.video?.url
  || resultData.output?.url
  || resultData.video_url
  || resultData.result?.video_url
  || resultData.video?.url
  || (resultData.url && !resultData.url.includes('/requests/') && !resultData.url.includes('/status'));

if (!videoUrl) {
  const availableKeys = Object.keys(resultData);
  const responsePreview = JSON.stringify(resultData, null, 2).substring(0, 2000);
  console.warn('Video URL not found in response_url POST response');
  console.warn('Available keys:', availableKeys);
  console.warn('Response preview:', responsePreview);
  const attempt1Data = $('Extract Video URL (Attempt 1)').item.json;
  return [{
    json: {
      video_url: null,
      error: 'Video URL not found in response_url POST response',
      raw_response: resultData,
      request_id: attempt1Data.request_id,
      script_id: attempt1Data.script_id || 'unknown'
    }
  }];
}

const attempt1Data = $('Extract Video URL (Attempt 1)').item.json;
return [{
  json: {
    video_url: videoUrl,
    raw_response: resultData,
    request_id: attempt1Data.request_id,
    script_id: attempt1Data.script_id || 'unknown'
  }
}];
```

### Step 5: Merge Video URLノードを更新

**目的**: アプローチ4の結果も考慮するようにコードを更新

**修正内容**:
- アプローチ4の結果を確認するコードを追加
- エラーメッセージにアプローチ4の情報を追加

---

## 🧪 テスト実行時の確認ポイント

### Step 1: Extract Video URL (Attempt 2)の確認
1. **422エラーの場合**: `needs_post_request: true`が設定されているか確認
2. **その他のエラーの場合**: `needs_status_url_request: true`が設定されているか確認

### Step 2: Needs POST Request?の確認
1. **分岐の確認**: 
   - `true`分岐: アプローチ4が実行される
   - `false`分岐: アプローチ3またはMerge Video URLに進む

### Step 3: Get Result (Approach 4)の確認
1. **エラーの有無**: エラーが発生しても処理が続行されるか確認（`neverError: true`）
2. **レスポンス構造**: 実行ログで`Get Result (Approach 4) response keys`を確認
3. **ペイロード**: 元のリクエストペイロードが正しく送信されているか確認

### Step 4: Extract Video URL (Attempt 4)の確認
1. **動画URLの抽出**: 成功した場合、`video_url`が正しく抽出されているか確認
2. **エラーハンドリング**: エラーの場合、`video_url: null`と`error`フィールドが返されるか確認

### Step 5: Merge Video URLの確認
1. **`approach`フィールド**: 使用されたアプローチを確認（`response_url_post`など）
2. **`video_url`の値**: 動画URLが正しく設定されているか確認
3. **エラーの有無**: すべてのアプローチが失敗した場合、詳細なエラーメッセージが表示されるか確認

---

## ⚠️ 注意事項

1. **ペイロードの構造**: 元のリクエストペイロード（`inputs`、`output_format`など）を正しく送信する必要がある
2. **認証**: FAL API Keyが正しく設定されているか確認
3. **エラーハンドリング**: `neverError: true`を設定して、エラーでも処理を続行できるようにする
4. **デバッグ**: 各ステップでログを確認して、レスポンス構造を把握する

---

## 📝 実装後の検証項目

1. ✅ アプローチ4が正しく実行されるか
2. ✅ `response_url`にPOSTリクエストが送信されるか
3. ✅ 動画URLが正しく抽出されるか
4. ✅ エラーハンドリングが正しく動作するか
5. ✅ すべてのアプローチが失敗した場合、詳細なエラーメッセージが表示されるか

---

## 🔗 関連ドキュメント

- [WF7-Phase4c-実行1032-1036-修正まとめ.md](WF7-Phase4c-実行1032-1036-修正まとめ.md)
- [WF7-Phase4c-MCP修正手順.md](WF7-Phase4c-MCP修正手順.md)

---

**作成者**: Claude Code (Composer)  
**最終更新**: 2025-11-09

