# Claude Code実装指示: S1 - Phase4a統合

## 📋 タスク概要

WF7phase4_v3ワークフロー (`qSN7EHj5yl0nPXij`) にPhase4aサブワークフロー統合を実装してください。

## 📖 参照ドキュメント

詳細な実装手順は以下を参照:
- `/docs/implementation/WF7-Phase4a-integration-instructions.md`

## 🎯 実装内容

### 1. ワークフロー取得
```javascript
const workflow = await mcp_n8n_get_workflow({ id: "qSN7EHj5yl0nPXij" });
```

### 2. 追加するノード（3つ）

#### ノード1: HTTP Request - Call Phase4a
- **タイプ**: `n8n-nodes-base.httpRequest`
- **位置**: 「データ統合」ノードの後（X: -2256, Y: -128）
- **設定**: 
  - URL: `https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4a-slide-generator`
  - Method: POST
  - Body: `{ script_id: $('データ統合').item.json.notionPageId }`
  - Timeout: 300000

#### ノード2: Set - Phase4a Payload
- **タイプ**: `n8n-nodes-base.set`
- **位置**: Phase4a呼び出しノードの後（X: -2032, Y: -128）
- **設定**: `slides_metadata`, `slides_count`, `phase4a_success`を設定

#### ノード3: IF - Phase4a Success Check
- **タイプ**: `n8n-nodes-base.if`
- **位置**: Setノードの後（X: -1808, Y: -128）
- **条件**: `phase4a_success === true && slides_count === 7`

### 3. 既存ノードの修正

#### Split Outノード
- **変更**: `fieldToSplitOut: "assetsData"` → `"slides_metadata"`
- **名前変更**: `Split Out - Phase4a Slides`

#### メタデータ整形ノード
- **変更**: Phase4aの出力形式（`slides_metadata`）に合わせて設定を更新
- **名前変更**: `Set - Slide Metadata`

### 4. 接続の変更

**削除**:
- 「データ統合」→「Split Out」の接続

**追加**:
- 「データ統合」→「HTTP Request - Call Phase4a」
- 「HTTP Request - Call Phase4a」→「Set - Phase4a Payload」
- 「Set - Phase4a Payload」→「IF - Phase4a Success Check」
- 「IF - Phase4a Success Check」[True]→「Split Out - Phase4a Slides」
- 「IF - Phase4a Success Check」[False]→「Notion - Update Status Error」（新規追加）

### 5. エラー処理ノード追加（2つ）

- `Notion - Update Status Error`: Phase4a失敗時にNotionステータスを`Failed`に更新
- `Respond to Webhook - Error`: エラーレスポンスを返す

## 🔧 実装方法

`n8n_update_partial_workflow`を使用して段階的に実装:

1. ノード追加（`addNode`操作）
2. 接続追加/削除（`addConnection`/`removeConnection`操作）
3. 既存ノード更新（`updateNode`操作）

## ✅ 完了条件

- [ ] 3つの新規ノードが追加されている
- [ ] 接続が正しく設定されている
- [ ] 既存ノードが正しく更新されている
- [ ] エラー処理ノードが追加されている
- [ ] ワークフロー検証が成功する（`validate_workflow`）

## 🧪 テスト準備

実装完了後、以下でテスト実行:
- Webhook URL: `https://n8n-python-production-344b.up.railway.app/webhook/wf7-video-script`
- テストデータ: `{ "notionPageId": "既存のNotionページID" }`

---

**重要**: 詳細な設定値は `/docs/implementation/WF7-Phase4a-integration-instructions.md` を参照してください。

