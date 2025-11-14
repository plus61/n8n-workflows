# WF7 Phase4c MCPツールを使用した修正手順

**作成日**: 2025-11-09  
**対象ワークフロー**: `chPw11OY5sex6d9I` (WF7 Phase4c - Perfect Implementation)  
**実行ID**: 1032  
**問題**: `Get Result`ノードのレスポンスに動画URLが含まれていない

---

## 🔍 問題の詳細

### 実行結果の分析

実行1032の結果を確認したところ：

1. **`Get Result`ノード**: `response_url`に対してGETリクエストを送信
2. **レスポンス構造**: `status`, `request_id`, `response_url`, `status_url`, `cancel_url`, `logs`, `metrics`が含まれているが、**動画URLが含まれていない**
3. **`Extract Video URL`ノード**: `response_url`を`video_url`として抽出（❌ 誤り）
4. **`Download Video`ノード**: `response_url`に対してGETリクエストを送信 → 422エラー

### 問題の根本原因

`Get Result`ノードが`response_url`に対してGETリクエストを送信していますが、そのレスポンスには動画URLが含まれていません。`response_url`はリクエスト情報を返すエンドポイントであり、実際の動画URLは別の場所にある可能性があります。

---

## 🔧 MCPツールを使用した修正手順

### Step 1: ワークフローの現在の状態を確認

```javascript
// MCPツールを使用してワークフローを取得
mcp_n8n-mcp_n8n_get_workflow({id: "chPw11OY5sex6d9I"})
```

### Step 2: `Get Result`ノードのレスポンス構造を確認

実行1032の結果から、`Get Result`ノードのレスポンスには以下のフィールドが含まれています：
- `status`: "COMPLETED"
- `request_id`: "b73641b3-705b-41d1-838f-7d97fe2b0893"
- `response_url`: "https://queue.fal.run/fal-ai/ffmpeg-api/requests/..."
- `status_url`: "https://queue.fal.run/fal-ai/ffmpeg-api/requests/.../status"
- `cancel_url`: "https://queue.fal.run/fal-ai/ffmpeg-api/requests/.../cancel"
- `logs`: null
- `metrics`: { "inference_time": 0.030183076858520508 }

**動画URLが含まれていない**ため、別の方法で取得する必要があります。

### Step 3: FAL APIのドキュメントを確認

FAL APIの`/compose`エンドポイントの場合、完了後の動画URLは以下のいずれかの方法で取得できる可能性があります：

1. **`response_url`にGETリクエストを送信**（現在の方法、動画URLが含まれていない）
2. **`status_url`にGETリクエストを送信**（ステータス情報のみ）
3. **別のエンドポイントを使用**（例: `/requests/{request_id}/result`）

### Step 4: `Extract Video URL`ノードを修正

`Get Result`ノードのレスポンスに動画URLが含まれていない場合、以下のいずれかの方法を試します：

#### 方法1: `response_url`に再度GETリクエストを送信（推奨）

`Get Result`ノードのレスポンスが`Fetch Status`ノードのレスポンスと同じである可能性があるため、`response_url`に対して再度GETリクエストを送信し、実際の動画URLを取得します。

#### 方法2: `status_url`から動画URLを取得

`status_url`にGETリクエストを送信し、レスポンスに動画URLが含まれているか確認します。

#### 方法3: エラーメッセージから動画URLを抽出

422エラーメッセージに動画URLが含まれている可能性があります。

---

## 📝 次のステップ

1. ⏳ FAL APIのドキュメントを確認して、動画URLの取得方法を特定
2. ⏳ `Get Result`ノードのレスポンス構造を詳細に分析
3. ⏳ `Extract Video URL`ノードを修正して、正しい動画URLを抽出
4. ⏳ テスト実行して動作確認

---

**作成者**: Claude Code (Composer)  
**更新日**: 2025-11-09




