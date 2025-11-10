# WF7 Phase4 統合トラブルシューティング・ナレッジベース

**作成日**: 2025-11-10
**対象**: Phase4a (Slide Generator) + Phase4b (Video Orchestrator) 統合
**出典**: 実際の統合作業とトラブルシューティングから得られた知見

## 目次

1. [問題の概要](#問題の概要)
2. [根本原因分析](#根本原因分析)
3. [解決アプローチ](#解決アプローチ)
4. [n8nワークフロー統合の重要概念](#n8nワークフロー統合の重要概念)
5. [トラブルシューティング手順](#トラブルシューティング手順)
6. [ベストプラクティス](#ベストプラクティス)
7. [チェックリスト](#チェックリスト)

---

## 問題の概要

### 初期状態
- **Phase4a**: 7枚のスライド画像生成完了後、`Respond to Webhook - Success`で終了
- **Phase4b**: 独立したワークフローとして7本の動画を並列生成（~51秒）
- **問題**: Phase4aがPhase4bを呼び出していないため、エンドツーエンドフローが不完全

### 統合要件
1. Phase4aが7枚のスライドメタデータを生成
2. Phase4aがPhase4bを呼び出して7本の動画生成を実行
3. Phase4bの完了を待ってから動画URL付きレスポンスを返却
4. タイムアウト: 120秒以内で完了（Phase4b ~50秒 + Phase4a ~5秒）

---

## 根本原因分析

### 🔴 Critical Issue 1: 並列実行による即座のレスポンス返却

**症状**:
```json
// 初回テスト結果（10.33秒で完了）
{
  "script_id": "2a068d5c-2986-81a3-ab0c-ff0bc1e4ebb9",
  "slides_metadata": [...7 slides with image_url only...],
  "slides_count": 7
}
// 動画URL (video_url) が含まれていない
```

**根本原因**:
```
ワークフロー構造の問題: 並列実行パス

Set - Phase 4b Input Data
  ├─ → HTTP Request - Call Phase4b Orchestrator → Respond to Webhook ❌
  └─ → Respond to Webhook (直接接続) ← これが先に実行される
```

**なぜこれが問題か**:
- n8nは同じノードから複数の接続が出ている場合、**並列実行**する
- 直接接続パス（Set → Respond）が先に完了（数ミリ秒）
- HTTP Request → Respond パスはPhase4b完了まで待機（~50秒）
- **結果**: Phase4b完了前にレスポンスが返される

**実行時間の証拠**:
- 初回テスト: 10.33秒（Phase4b待機なし）
- 修正後: 54.51秒（Phase4b完了待機）

### 🟡 Issue 2: n8n_update_partial_workflow API理解不足

**症状**:
```javascript
// 初回試行: 接続削除エラー
Error: "Source node not found: undefined"
```

**根本原因**:
- `removeConnection`操作でobject形式 `{nodeId: "...", outputIndex: 0}` を使用
- 正しい形式は**ノード名（string）**

**修正**:
```javascript
// ❌ 誤り
{
  type: "removeConnection",
  source: {nodeId: "856249e1-...", outputIndex: 0},
  target: {nodeId: "81be1ecb-...", inputIndex: 0}
}

// ✅ 正解
{
  type: "removeConnection",
  source: "Set - Phase 4b Input Data",  // ノード名
  target: "Respond to Webhook - Success",  // ノード名
  ignoreErrors: true  // 接続が存在しない場合でも続行
}
```

---

## 解決アプローチ

### Step 1: ワークフロー構造の分析

**実施した調査**:
```javascript
// Phase4aの構造を取得
mcp__n8n-mcp__n8n_get_workflow_structure({id: "LYPbvJfkMzLlhc6t"})
```

**発見**:
- Phase4a は `Respond to Webhook - Success` で終了
- Phase4b への接続が存在しない
- 最終ノード `Set - Phase 4b Input Data` から直接Respondへ接続

### Step 2: HTTP Request ノード追加

**設計判断**:
- ✅ **選択**: HTTP Request node経由でPhase4bを呼び出し
- ❌ **不採用**: Execute Workflow node（同期問題とタイムアウト制御の複雑さ）

**実装**:
```javascript
{
  type: "addNode",
  node: {
    id: "http-request-call-phase4b",
    name: "HTTP Request - Call Phase4b Orchestrator",
    type: "n8n-nodes-base.httpRequest",
    typeVersion: 4.2,
    position: [1200, 500],
    parameters: {
      method: "POST",
      url: "https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4b-orchestrator",
      sendBody: true,
      specifyBody: "json",
      jsonBody: "={{ { script_id: $json.script_id, slides_metadata: $json.slides_metadata } }}",
      options: {
        timeout: 120000,  // 120秒
        response: {
          response: {
            responseFormat: "json"
          }
        }
      }
    }
  }
}
```

**重要な設計選択**:
1. **タイムアウト 120秒**: Phase4b実行時間（~50秒）+ バッファ
2. **specifyBody: "json"**: n8n式 `={{ }}` を正しく評価
3. **responseFormat: "json"**: Phase4bのJSON responseを自動パース

### Step 3: 接続の再構成（並列実行 → 順次実行）

**問題のある構造**:
```
Set - Phase 4b Input Data
  ├─ → HTTP Request - Call Phase4b  [~50秒]
  └─ → Respond to Webhook             [即座]  ← 並列実行
```

**修正後の構造**:
```
Set - Phase 4b Input Data
  → HTTP Request - Call Phase4b  [~50秒]
    → Respond to Webhook - Phase4b Result  [Phase4b完了後]
```

**実装**:
```javascript
[
  // 1. 並列実行の原因となる直接接続を削除
  {
    type: "removeConnection",
    source: "Set - Phase 4b Input Data",
    target: "Respond to Webhook - Phase4b Result",
    ignoreErrors: true
  },

  // 2. 順次実行チェーンを構築
  {
    type: "addConnection",
    source: "Set - Phase 4b Input Data",
    target: "HTTP Request - Call Phase4b Orchestrator"
  },
  {
    type: "addConnection",
    source: "HTTP Request - Call Phase4b Orchestrator",
    target: "Respond to Webhook - Phase4b Result"
  }
]
```

### Step 4: テストと検証

**初回テスト（並列実行バグあり）**:
```bash
curl -X POST "https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase4a-slide-generator" \
  -H "Content-Type: application/json" \
  -d '{"script_id": "2a068d5c-2986-81a3-ab0c-ff0bc1e4ebb9"}' \
  --max-time 180

# 結果: 10.33秒, video_url なし
```

**修正後テスト（順次実行）**:
```bash
# 同じコマンド
# 結果: 54.51秒, 7本すべての video_url 含む ✅
```

**検証項目**:
- ✅ `success: true`
- ✅ `videos_count: 7`
- ✅ `total_duration: 80`
- ✅ 全7本の動画に `video_url` フィールド存在
- ✅ 実行時間が~55秒（Phase4b完了待機）

---

## n8nワークフロー統合の重要概念

### 1. 並列実行 vs 順次実行

#### 並列実行（Parallel Execution）
```
Node A
  ├─ → Node B  [実行時間: 50秒]
  └─ → Node C  [実行時間: 1秒]

結果: Node CとNode Bが同時に実行開始
     → Node Cが先に完了（1秒後）
     → Node Bは独立して継続実行（50秒後完了）
```

**使用ケース**:
- ✅ 独立した複数の処理を同時実行（例: 複数APIへの並列リクエスト）
- ✅ 処理時間の短縮が必要

**注意点**:
- ❌ 後続ノードが複数の入力を期待する場合は不適切
- ❌ 実行順序の制御が必要な場合は不適切

#### 順次実行（Sequential Execution）
```
Node A → Node B [50秒] → Node C

結果: Node A完了 → Node B実行（50秒） → Node B完了 → Node C実行
     合計時間: 50秒 + α
```

**使用ケース**:
- ✅ 後続処理が前の処理結果に依存
- ✅ 実行順序の制御が必須
- ✅ 最終結果を待ってからレスポンス返却

### 2. n8n_update_partial_workflow API使用パターン

#### パターン1: ノード追加と接続
```javascript
[
  // Step 1: 新しいノードを追加
  {
    type: "addNode",
    node: {
      id: "new-node-id",
      name: "New Node Name",
      type: "n8n-nodes-base.httpRequest",
      typeVersion: 4.2,
      position: [x, y],
      parameters: { /* node config */ }
    }
  },

  // Step 2: 既存ノードから新ノードへ接続
  {
    type: "addConnection",
    source: "Existing Node Name",  // ノード名（string）
    target: "New Node Name"
  },

  // Step 3: 新ノードから別の既存ノードへ接続
  {
    type: "addConnection",
    source: "New Node Name",
    target: "Final Node Name"
  }
]
```

#### パターン2: 接続の再構成（並列→順次）
```javascript
[
  // Step 1: 問題のある直接接続を削除
  {
    type: "removeConnection",
    source: "Node A",
    target: "Node C",
    ignoreErrors: true  // 接続が既に削除されていてもエラーにしない
  },

  // Step 2: 中間ノード経由の接続を確立
  // （Node A → Node B は既存）
  {
    type: "addConnection",
    source: "Node B",
    target: "Node C"
  }
]
```

#### パターン3: ノード名変更と位置調整
```javascript
[
  {
    type: "updateNode",
    nodeId: "81be1ecb-bd09-490f-9d80-c8b0d93b3df9",
    updates: {
      name: "New Node Name",  // 名前変更
      position: [1400, 500]   // UI上の位置調整
    }
  }
]
```

### 3. HTTP Request Node タイムアウト設計

#### タイムアウト計算式
```
Required Timeout = (Target Workflow Execution Time * 1.5) + Network Buffer

例: Phase4b実行時間 = 50秒
   Required Timeout = (50 * 1.5) + 10 = 85秒
   安全マージン考慮 → 120秒設定
```

#### タイムアウト設定の重要性
```javascript
{
  parameters: {
    options: {
      timeout: 120000  // ミリ秒単位（120秒）
    }
  }
}
```

**設定が不足している場合**:
- デフォルトタイムアウト（通常30秒）で切断
- Phase4b処理中断
- 不完全なレスポンス返却

### 4. Webhook Response モード

#### responseNode モード（今回使用）
```javascript
{
  name: "Respond to Webhook",
  type: "n8n-nodes-base.respondToWebhook",
  parameters: {
    respondWith: "json",
    responseBody: "={{ $json }}"  // Phase4bの結果をそのまま返却
  }
}
```

**動作**:
- ワークフローの任意の位置でレスポンス返却可能
- 前のノードの `$json` データを使用

**メリット**:
- 複数の条件分岐後に異なるレスポンスを返却可能
- データ変換後のレスポンス返却が容易

---

## トラブルシューティング手順

### 問題: ワークフロー統合後、即座にレスポンスが返るが期待したデータが含まれない

#### 診断フロー

**Step 1: 実行時間を確認**
```bash
curl -X POST "url" -w "\nTotal Time: %{time_total}s\n"
```

**判定基準**:
- 予想実行時間より大幅に短い（例: 50秒予想なのに10秒で完了）
  → **並列実行バグの可能性高**
- 予想実行時間と同等（例: 50秒予想で55秒完了）
  → **正常、データ構造の問題を調査**

**Step 2: レスポンスデータを確認**
```bash
curl -X POST "url" -o /tmp/response.json
cat /tmp/response.json | jq .
```

**確認項目**:
- 必要なフィールドが存在するか？
- データ型は正しいか？
- 配列の要素数は期待通りか？

**Step 3: ワークフロー構造を取得**
```javascript
mcp__n8n-mcp__n8n_get_workflow_structure({id: "workflow-id"})
```

**確認項目**:
```javascript
// connections オブジェクトをチェック
{
  "connections": {
    "Set - Phase 4b Input Data": {
      "main": [
        [
          {"node": "HTTP Request - Call Phase4b", "type": "main", "index": 0},
          {"node": "Respond to Webhook", "type": "main", "index": 0}  // ← 並列実行の原因
        ]
      ]
    }
  }
}
```

**並列実行の特定方法**:
- 同じ `main` 配列内に複数のノード接続が存在
- 例: `[{node: "A"}, {node: "B"}]` → AとBが並列実行

**Step 4: 接続を再構成**
```javascript
// 並列実行の原因となる直接接続を削除
{
  type: "removeConnection",
  source: "Set - Phase 4b Input Data",
  target: "Respond to Webhook",
  ignoreErrors: true
}
```

**Step 5: 再テストと検証**
```bash
curl -X POST "url" -w "\nTotal Time: %{time_total}s\n" -o /tmp/response_fixed.json

# 実行時間が予想と一致することを確認
# レスポンスデータに期待したフィールドが含まれることを確認
```

### 問題: removeConnection で "Source node not found" エラー

#### 診断フロー

**Step 1: エラーメッセージを確認**
```
Error: Source node not found: "undefined"
Available nodes: "Webhook - Phase 4a Start" (id: 96667f56...), ...
```

**根本原因**:
- ノード名の参照ミス
- ノード名を変更した後に古い名前で参照
- object形式で指定（正しくはstring）

**Step 2: 正しいノード名を確認**
```javascript
// ワークフロー構造取得
mcp__n8n-mcp__n8n_get_workflow_structure({id: "workflow-id"})

// nodes配列から正しい名前を確認
{
  "nodes": [
    {
      "id": "81be1ecb-...",
      "name": "Respond to Webhook - Phase4b Result"  // ← これを使用
    }
  ]
}
```

**Step 3: 正しい形式で接続操作**
```javascript
// ✅ 正解
{
  type: "removeConnection",
  source: "Set - Phase 4b Input Data",  // ノード名（string）
  target: "Respond to Webhook - Phase4b Result",  // ノード名（string）
  ignoreErrors: true
}

// ❌ 誤り
{
  type: "removeConnection",
  source: {nodeId: "856249e1-...", outputIndex: 0},  // object形式は不可
  target: {nodeId: "81be1ecb-...", inputIndex: 0}
}
```

### 問題: タイムアウトエラー（504 Gateway Timeout）

#### 診断フロー

**Step 1: エラー発生タイミングを確認**
```bash
curl -X POST "url" -w "\nTotal Time: %{time_total}s\n"
# Total Time: 30.000000s ← デフォルトタイムアウト
```

**根本原因**:
- HTTP Request nodeのタイムアウト設定不足
- デフォルトタイムアウト（30秒）より長い処理

**Step 2: 必要なタイムアウトを計算**
```
実際の処理時間: 50秒
安全マージン: 50秒 * 1.5 = 75秒
ネットワークバッファ: +10秒
推奨タイムアウト: 85秒 → 安全のため120秒設定
```

**Step 3: タイムアウト設定を更新**
```javascript
{
  type: "updateNode",
  nodeId: "http-request-node-id",
  updates: {
    parameters: {
      options: {
        timeout: 120000  // 120秒（ミリ秒単位）
      }
    }
  }
}
```

---

## ベストプラクティス

### 1. ワークフロー統合設計

#### ✅ DO: 順次実行チェーンを明確に設計
```
Parent Workflow
  → Data Preparation Node
    → HTTP Request (Call Child Workflow) [timeout: 120s]
      → Process Response Node
        → Final Response Node
```

**メリット**:
- 実行順序が明確
- デバッグが容易
- タイムアウト制御が簡単

#### ❌ DON'T: 並列実行と順次実行を混在させる
```
Parent Workflow
  → Data Preparation
    ├─ → HTTP Request (Child)  [遅い]
    └─ → Final Response        [速い] ← 問題の原因
```

**問題**:
- 実行順序が不明確
- レースコンディション発生
- デバッグが困難

### 2. HTTP Request Node設計

#### ✅ DO: 適切なタイムアウトとリトライ戦略
```javascript
{
  parameters: {
    method: "POST",
    url: "child-workflow-webhook-url",
    sendBody: true,
    specifyBody: "json",
    jsonBody: "={{ $json }}",
    options: {
      timeout: 120000,  // 十分なマージン
      redirect: {
        redirect: {
          maxRedirects: 3
        }
      },
      response: {
        response: {
          responseFormat: "json"
        }
      }
    }
  }
}
```

#### ❌ DON'T: デフォルト設定に依存
```javascript
{
  parameters: {
    method: "POST",
    url: "url",
    sendBody: true,
    body: "some body"  // specifyBody未指定、timeoutデフォルト
  }
}
```

**問題**:
- タイムアウト不足（30秒デフォルト）
- レスポンス形式が不明確
- エラーハンドリング不足

### 3. n8n_update_partial_workflow 使用パターン

#### ✅ DO: 操作をアトミックに実行
```javascript
[
  // まず削除（ignoreErrorsで既存接続なしでもOK）
  {type: "removeConnection", source: "A", target: "C", ignoreErrors: true},

  // 次に追加（順次実行チェーン構築）
  {type: "addConnection", source: "A", target: "B"},
  {type: "addConnection", source: "B", target: "C"}
]
```

**メリット**:
- 操作の意図が明確
- エラー時のロールバックが容易
- 段階的なテストが可能

#### ❌ DON'T: 複雑な操作を1回で実行
```javascript
[
  {type: "addNode", ...},
  {type: "updateNode", nodeId: "old-id", ...},  // old-idが存在しない可能性
  {type: "removeConnection", source: "old-name", ...},  // 名前変更後なので失敗
  {type: "addConnection", ...}
]
```

**問題**:
- 操作の依存関係が不明確
- 途中でエラー発生時の対処が困難
- デバッグが複雑

### 4. テストと検証

#### ✅ DO: 段階的なテストと検証
```bash
# Step 1: Phase4a単体テスト（Phase4b接続前）
curl -X POST "phase4a-url" -o /tmp/phase4a_only.json

# Step 2: Phase4b単体テスト
curl -X POST "phase4b-url" -d @/tmp/phase4a_only.json -o /tmp/phase4b_only.json

# Step 3: 統合テスト（Phase4a → Phase4b）
curl -X POST "phase4a-url" -o /tmp/integration_test.json

# Step 4: レスポンス検証
cat /tmp/integration_test.json | jq '.videos_metadata | length'  # 7を期待
cat /tmp/integration_test.json | jq '.videos_metadata[0].video_url'  # URLを期待
```

**メリット**:
- 問題の切り分けが容易
- 各段階の正常性を確認
- エラー発生時の原因特定が迅速

#### ❌ DON'T: いきなりエンドツーエンドテスト
```bash
# 問題があった場合、どこで失敗したか不明
curl -X POST "phase4a-url"
# エラー発生... Phase4a? Phase4b? 接続?
```

### 5. エラーハンドリング

#### ✅ DO: ignoreErrors フラグの適切な使用
```javascript
{
  type: "removeConnection",
  source: "A",
  target: "B",
  ignoreErrors: true  // 接続が既に削除されている場合でも続行
}
```

**使用ケース**:
- 接続が存在するか不明な場合
- 冪等性が必要な操作
- ロールバック処理

#### ❌ DON'T: すべての操作でignoreErrorsを使用
```javascript
{
  type: "addNode",
  node: {...},
  ignoreErrors: true  // ノード追加失敗を無視すると後続操作が失敗
}
```

**問題**:
- エラーの見逃し
- 不完全な状態での続行
- デバッグが困難

---

## チェックリスト

### ワークフロー統合前

- [ ] 子ワークフローの平均実行時間を測定
- [ ] 必要なタイムアウトを計算（実行時間 * 1.5 + バッファ）
- [ ] 親ワークフローの最終ノードを特定
- [ ] データフロー設計（どのデータを渡すか）を明確化
- [ ] エラーハンドリング戦略を決定

### HTTP Request Node追加時

- [ ] `method: "POST"` を設定
- [ ] `url` に子ワークフローのWebhook URLを設定
- [ ] `sendBody: true` を設定
- [ ] `specifyBody: "json"` + `jsonBody` を使用（n8n式 `={{ }}` の場合）
- [ ] `timeout` を適切に設定（ミリ秒単位）
- [ ] `responseFormat: "json"` を設定

### 接続再構成時

- [ ] 現在の接続構造を`n8n_get_workflow_structure`で確認
- [ ] 並列実行パスが存在しないか確認
- [ ] 削除する接続を`removeConnection`で指定（`ignoreErrors: true`）
- [ ] 新しい接続を`addConnection`で追加
- [ ] ノード名（string）を使用（object形式は不可）

### テストと検証

- [ ] 子ワークフロー単体テスト実行
- [ ] 統合テスト実行（`--max-time`でタイムアウト設定）
- [ ] 実行時間が予想と一致することを確認
- [ ] レスポンスに期待したフィールドが含まれることを確認
- [ ] エラーケースのテスト（タイムアウト、不正なデータ等）

### デプロイ前

- [ ] ワークフローが`active: true`に設定されているか確認
- [ ] Webhook URLが正しいか確認（本番環境のURL）
- [ ] タイムアウト設定が本番環境に適しているか確認
- [ ] エラー通知設定を確認
- [ ] ロールバック手順を準備

---

## まとめ

### 重要な学び

1. **並列実行 vs 順次実行**: n8nは同じノードから複数の接続が出ている場合、デフォルトで並列実行する。順次実行が必要な場合は接続を1本のチェーンにする。

2. **タイムアウト設計**: HTTP Request nodeのタイムアウトは必ず明示的に設定する。計算式: `(実行時間 * 1.5) + バッファ`

3. **n8n式の評価**: `specifyBody: "json"` + `jsonBody` を使用しないと `={{ }}` 式が評価されない。

4. **接続操作**: `removeConnection` と `addConnection` でノード名（string）を使用。object形式は不可。

5. **段階的テスト**: 単体テスト → 統合テスト → エンドツーエンドテストの順で検証。

### 適用範囲

このナレッジは以下のケースで適用可能:
- ワークフロー間のHTTP Request経由統合
- 長時間実行ワークフローの呼び出し
- 並列実行と順次実行の制御
- n8n_update_partial_workflow APIを使用した接続再構成

### 参考ドキュメント

- [n8n HTTP Request Node Documentation](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.httprequest/)
- [n8n Workflow Execution](https://docs.n8n.io/workflows/executions/)
- `docs/knowledge/n8n-workflow-construction-knowledge.md` - HTTP Request v4設定ルール
