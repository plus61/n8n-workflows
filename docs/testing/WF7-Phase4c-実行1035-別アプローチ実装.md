# WF7 Phase4c 実行1035 別アプローチ実装

**作成日**: 2025-11-09  
**対象ワークフロー**: `chPw11OY5sex6d9I` (WF7 Phase4c - Perfect Implementation)  
**実行ID**: 1035  
**問題**: `/requests/{request_id}/result`エンドポイントが405エラー（Method Not Allowed）

---

## 🔍 問題の詳細

### エラー内容
- **ノード**: `Get Result`
- **エラー**: `405 - Method Not Allowed`
- **原因**: `/requests/{request_id}/result`エンドポイントはGETメソッドをサポートしていない

### 実行結果の分析

実行1035の結果を確認したところ：
1. **`Fetch Status`ノード**: 成功（`status: "COMPLETED"`）
2. **`Get Result`ノード**: 405エラー（`/requests/{request_id}/result`エンドポイントがGETメソッドをサポートしていない）

---

## 🔧 実装した別アプローチ

最終目的「FAL APIから動画URLを取得してダウンロードする」を達成するため、**2つのアプローチを実装**しました。

### アプローチ1: Fetch Statusのレスポンスから直接動画URLを抽出

**ノード**: `Extract Video URL (Attempt 1)`

ステータスが`COMPLETED`の場合、`Fetch Status`のレスポンスに動画URLが含まれている可能性があります。

**実装内容**:
```javascript
// Fetch Statusのレスポンスから直接動画URLを抽出
const statusData = $input.first().json;

// 動画URL抽出の試行（複数のパターン）
let videoUrl = statusData.output?.video_url
  || statusData.output?.video?.url
  || statusData.output?.url
  || statusData.video_url
  || statusData.result?.video_url
  || statusData.video?.url
  || (statusData.url && !statusData.url.includes('/requests/') && !statusData.url.includes('/status'));

// アプローチ2が必要かどうかのフラグ
const needsGetRequest = !videoUrl && statusData.response_url;
```

**メリット**:
- 追加のHTTPリクエストが不要
- 処理が高速

**デメリット**:
- レスポンスに動画URLが含まれていない場合がある

---

### アプローチ2: response_urlにGETリクエストを送信（成功実例と同じ方法）

**ノード**: `Get Result (Approach 2)` → `Extract Video URL (Attempt 2)`

成功実例（`wf7_phase4b.json`）と同じ方法で、`response_url`にGETリクエストを送信して動画URLを取得します。

**実装内容**:
```javascript
// response_urlにGETリクエストを送信
// URL: ={{ $json.response_url }}

// レスポンスから動画URLを抽出
let videoUrl = resultData.output?.video_url
  || resultData.output?.video?.url
  || resultData.output?.url
  || resultData.video_url
  || resultData.result?.video_url
  || resultData.video?.url
  || (resultData.url && !resultData.url.includes('/requests/') && !resultData.url.includes('/status'));
```

**メリット**:
- 成功実例で動作確認済み
- 確実に動画URLを取得できる可能性が高い

**デメリット**:
- 追加のHTTPリクエストが必要

---

## 🔄 ワークフローの流れ

```
Fetch Status
    ↓
Render Completed? (status === COMPLETED)
    ↓
Extract Video URL (Attempt 1) ← アプローチ1: ステータスレスポンスから直接抽出
    ↓
Needs Get Request? (動画URLが見つからない場合)
    ├─ True → Get Result (Approach 2) → Extract Video URL (Attempt 2) ← アプローチ2
    └─ False → Merge Video URL
    ↓
Merge Video URL (アプローチ1またはアプローチ2の結果を統合)
    ↓
Download Video
```

---

## 📊 動作ロジック

1. **アプローチ1を試行**: `Fetch Status`のレスポンスから直接動画URLを抽出
2. **動画URLが見つかった場合**: `Merge Video URL`ノードに直接進む
3. **動画URLが見つからない場合**: `Needs Get Request?`ノードで`true`分岐
4. **アプローチ2を実行**: `response_url`にGETリクエストを送信して動画URLを取得
5. **結果を統合**: `Merge Video URL`ノードでアプローチ1またはアプローチ2の結果を使用

---

## 🧪 テスト実行

### Step 1: テスト実行

1. n8n UIでワークフロー `chPw11OY5sex6d9I` を開く
2. 右上の **"Test workflow"** ボタンをクリック
3. 実行結果を確認

### Step 2: 各ノードの確認

1. **Extract Video URL (Attempt 1)**: 
   - 実行ログで`Fetch Status response keys`を確認
   - `video_url`が抽出されているか確認
   - `needs_get_request`フラグの値を確認

2. **Needs Get Request?**: 
   - `true`分岐が実行されたか（アプローチ2が必要か）
   - `false`分岐が実行されたか（アプローチ1で成功したか）

3. **Get Result (Approach 2)** (アプローチ2が実行された場合):
   - エラーが発生していないか確認
   - レスポンス構造を確認

4. **Extract Video URL (Attempt 2)** (アプローチ2が実行された場合):
   - 実行ログで`Get Result response keys`を確認
   - `video_url`が抽出されているか確認

5. **Merge Video URL**: 
   - `approach`フィールドで使用されたアプローチを確認（`status_response_direct`または`response_url_get`）
   - `video_url`が正しく設定されているか確認

6. **Download Video**: 
   - 動画がダウンロードできているか確認

---

## ⚠️ 注意事項

### デバッグ方法

1. **実行ログを確認**: 各ノードの実行ログで`response keys`と`response preview`を確認
2. **`raw_status_response`フィールド**: `Extract Video URL (Attempt 1)`の出力に`Fetch Status`の完全なレスポンスが含まれています
3. **`raw_response`フィールド**: `Extract Video URL (Attempt 2)`の出力に`Get Result`の完全なレスポンスが含まれています
4. **`approach`フィールド**: `Merge Video URL`の出力で使用されたアプローチが記録されています

### エラーハンドリング

- アプローチ1で動画URLが見つからない場合、自動的にアプローチ2を試行
- アプローチ2でも動画URLが見つからない場合、詳細なエラーメッセージを出力
- どちらのアプローチも失敗した場合、`Merge Video URL`ノードでエラーをスロー

---

## 📝 次のステップ

1. ⏳ テスト実行して動作確認
2. ⏳ どちらのアプローチが動作するか確認
3. ⏳ 動作したアプローチを優先的に使用するように最適化（オプション）
4. ⏳ エラーが発生した場合は、実行ログを確認してレスポンス構造を分析

---

## 🔗 関連ドキュメント

- [WF7-Phase4c-実行1032-改善手順.md](WF7-Phase4c-実行1032-改善手順.md)
- [WF7-Phase4c-MCP修正手順.md](WF7-Phase4c-MCP修正手順.md)

---

---

## 📝 実行1036の修正（2025-11-09 13:07）

### 発見された問題

1. **`needs_get_request`が文字列になっている**
   - `Extract Video URL (Attempt 1)`ノードで、`needs_get_request`が`response_url`の文字列になっていた
   - 原因: `const needsGetRequest = !videoUrl && statusData.response_url;` が文字列を返していた

2. **`response_url`にGETリクエストで422エラー**
   - `Get Result (Approach 2)`ノードで、`response_url`にGETリクエストを送信した際に422エラーが発生
   - FAL APIがPOSTリクエストとして解釈して、元のペイロードを再送信しようとしている

### 実施した修正

1. ✅ **`Extract Video URL (Attempt 1)`ノードを修正**
   - `needs_get_request`をboolean型に変換: `const needsGetRequest = Boolean(!videoUrl && statusData.response_url);`
   - `video_url`が`null`の場合も明示的に`null`を設定

2. ✅ **`Get Result (Approach 2)`ノードを修正**
   - `neverError: true`を追加して、422エラーでも処理を続行できるようにした

3. ✅ **`Extract Video URL (Attempt 2)`ノードを修正**
   - エラーハンドリングを追加: 422エラーの場合、`video_url: null`と`error`フィールドを返す
   - エラーメッセージをログに出力

4. ✅ **`Merge Video URL`ノードを修正**
   - エラーハンドリングを改善: どちらのアプローチも失敗した場合、詳細なエラーメッセージを返す

### 次のステップ

1. ⏳ テスト実行して動作確認
2. ⏳ `needs_get_request`が正しくboolean型になっているか確認
3. ⏳ 422エラーが発生した場合でも、エラーメッセージが正しく表示されるか確認

---

**作成者**: Claude Code (Composer)  
**更新日**: 2025-11-09 13:07

