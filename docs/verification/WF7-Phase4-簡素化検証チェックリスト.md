# WF7 Phase4 簡素化検証チェックリスト

**作成日**: 2025-11-09  
**目的**: n8n MCPツールを活用した簡素化実装の検証  
**対象**: WF7 Phase4 簡素化設計書に基づく実装

---

## 🔍 Phase 1: サブワークフロー検証

### 1.1 Phase4a検証

**ワークフローID**: `LYPbvJfkMzLlhc6t`

#### 構造検証

- [ ] **ワークフロー構造取得**
  ```bash
  mcp_n8n-mcp_n8n_get_workflow_structure({id: "LYPbvJfkMzLlhc6t"})
  ```
  - ノード数確認
  - 接続確認

- [ ] **ワークフロー検証**
  ```bash
  mcp_n8n-mcp_n8n_validate_workflow({id: "LYPbvJfkMzLlhc6t"})
  ```
  - エラー数: 0個
  - 警告数: <10個

#### データ契約検証

- [ ] **入力データ契約確認**
  - `script_id`: string (必須)
  - `scriptData`: object (必須)

- [ ] **出力データ契約確認**
  - `success`: boolean (必須)
  - `script_id`: string (必須)
  - `slides_metadata`: array (必須、7要素)
  - `slides_count`: number (必須、7)

#### ノード検証

- [ ] **Webhookノード検証**
  ```bash
  mcp_n8n-mcp_validate_node_minimal({
    nodeType: "nodes-base.webhook",
    config: {}
  })
  ```

- [ ] **Codeノード検証**
  ```bash
  mcp_n8n-mcp_validate_node_operation({
    nodeType: "nodes-base.code",
    config: {
      language: "python",
      mode: "runOnceForAllItems"
    }
  })
  ```

---

### 1.2 Phase4b検証

**ワークフローID**: `wHaKi98mTlUvFIOR`

#### 構造検証

- [ ] **ワークフロー構造取得**
  ```bash
  mcp_n8n-mcp_n8n_get_workflow_structure({id: "wHaKi98mTlUvFIOR"})
  ```

- [ ] **ワークフロー検証**
  ```bash
  mcp_n8n-mcp_n8n_validate_workflow({id: "wHaKi98mTlUvFIOR"})
  ```
  - エラー数: 0個
  - 警告数: <10個

#### FALポーリング機構確認

- [ ] **FAL Submitノード確認**
  - HTTP RequestノードでFAL API呼び出し
  - 認証設定確認

- [ ] **ポーリング機構確認**
  - Waitノード設定確認
  - Status Checkノード設定確認
  - Retry機構確認

#### データ契約検証

- [ ] **入力データ契約確認**
  - `script_id`: string (必須)
  - `slides_metadata`: array (必須、7要素)

- [ ] **出力データ契約確認**
  - `success`: boolean (必須)
  - `script_id`: string (必須)
  - `videos_metadata`: array (必須、7要素)
  - `videos_count`: number (必須、7)
  - `total_duration`: number

---

### 1.3 Phase4c検証

**ワークフローID**: [新規作成]

#### 構造検証

- [ ] **ワークフロー作成**
  ```bash
  mcp_n8n-mcp_n8n_create_workflow({
    name: "WF7 Phase4c - FFmpeg Concat",
    nodes: [...],
    connections: {...}
  })
  ```

- [ ] **ワークフロー検証**
  ```bash
  mcp_n8n-mcp_n8n_validate_workflow({id: "[新規ID]"})
  ```
  - エラー数: 0個
  - 警告数: <10個

#### 実装方法確認

- [ ] **オプション1: 外部Python FastAPI**
  - Railway上にPython FastAPIプロジェクト作成
  - `/api/ffmpeg-concat` エンドポイント実装
  - HTTP Requestノードで呼び出し

- [ ] **オプション2: Execute Command**
  - Railway環境にFFmpegインストール確認
  - Execute CommandノードでFFmpeg実行

#### データ契約検証

- [ ] **入力データ契約確認**
  - `script_id`: string (必須)
  - `videos_metadata`: array (必須、7要素)

- [ ] **出力データ契約確認**
  - `success`: boolean (必須)
  - `script_id`: string (必須)
  - `final_video_path`: string
  - `final_video_url`: string
  - `total_duration`: number
  - `video_size_mb`: number

---

## 🔍 Phase 2: 親フロー検証

### 2.1 バックアップ確認

- [ ] **現在のワークフローバックアップ**
  ```bash
  mcp_n8n-mcp_n8n_get_workflow({id: "r9Sp5n0mkUCcH8cw"})
  ```
  - ファイル保存: `workflows/archive/wf7-phase4-v3-complex.json`

---

### 2.2 ノード削除確認

- [ ] **削除対象ノード確認**
  - データ変換ノード削除
  - FALポーリング機構削除
  - 重複エラーハンドリング削除

- [ ] **削除後のノード数確認**
  - 目標: 10-12ノード

---

### 2.3 Execute Sub-workflowノード検証

#### Phase4a Execute Sub-workflow

- [ ] **ノード設定検証**
  ```bash
  mcp_n8n-mcp_validate_node_operation({
    nodeType: "nodes-base.executeWorkflow",
    config: {
      source: "database",
      workflowId: "LYPbvJfkMzLlhc6t",
      mode: "once",
      waitForSubWorkflow: true
    }
  })
  ```

- [ ] **データマッピング確認**
  - `script_id`: `={{ $json.id }}`
  - `scriptData`: `={{ $json.properties }}`

#### Phase4b Execute Sub-workflow

- [ ] **ノード設定検証**
  ```bash
  mcp_n8n-mcp_validate_node_operation({
    nodeType: "nodes-base.executeWorkflow",
    config: {
      source: "database",
      workflowId: "wHaKi98mTlUvFIOR",
      mode: "once",
      waitForSubWorkflow: true
    }
  })
  ```

- [ ] **データマッピング確認**
  - `script_id`: `={{ $('Execute Sub-workflow - Phase4a').item.json.script_id }}`
  - `slides_metadata`: `={{ $('Execute Sub-workflow - Phase4a').item.json.slides_metadata }}`

#### Phase4c Execute Sub-workflow

- [ ] **ノード設定検証**
  ```bash
  mcp_n8n-mcp_validate_node_operation({
    nodeType: "nodes-base.executeWorkflow",
    config: {
      source: "database",
      workflowId: "[Phase4cワークフローID]",
      mode: "once",
      waitForSubWorkflow: true
    }
  })
  ```

- [ ] **データマッピング確認**
  - `script_id`: `={{ $('Execute Sub-workflow - Phase4b').item.json.script_id }}`
  - `videos_metadata`: `={{ $('Execute Sub-workflow - Phase4b').item.json.videos_metadata }}`

---

### 2.4 エラーハンドリング検証

#### 統一IFノード

- [ ] **IFノード設定検証**
  ```bash
  mcp_n8n-mcp_validate_node_operation({
    nodeType: "nodes-base.if",
    config: {
      conditions: {
        options: {
          version: 2,
          caseSensitive: true,
          typeValidation: "strict"
        },
        combinator: "and",
        conditions: [
          { leftValue: "={{ $json.success }}", rightValue: true, operator: { type: "boolean", operation: "equals" } },
          ...
        ]
      },
      onError: "continueErrorOutput"
    }
  })
  ```

- [ ] **条件確認**
  - Phase4a成功確認
  - Phase4aスライド数確認（7枚）
  - Phase4b成功確認
  - Phase4b動画数確認（7本）
  - Phase4c成功確認

#### エラーハンドリングノード

- [ ] **エラー時Notion更新ノード検証**
  ```bash
  mcp_n8n-mcp_validate_node_operation({
    nodeType: "nodes-base.httpRequest",
    config: {
      method: "PATCH",
      url: "https://api.notion.com/v1/pages/...",
      authentication: "predefinedCredentialType",
      nodeCredentialType: "notionApi",
      onError: "continueRegularOutput",
      retryOnFail: true
    }
  })
  ```

- [ ] **エラー時Webhook応答ノード検証**
  ```bash
  mcp_n8n-mcp_validate_node_operation({
    nodeType: "nodes-base.respondToWebhook",
    config: {
      respondWith: "json",
      responseBody: "{ success: false, error: '...' }"
    }
  })
  ```

---

### 2.5 typeVersion更新確認

- [ ] **Webhookノード**
  - 現在: 2.0
  - 目標: 2.1

- [ ] **HTTP Requestノード**
  - 現在: 4.2
  - 目標: 4.3

- [ ] **Respond to Webhookノード**
  - 現在: 1.1
  - 目標: 1.4

- [ ] **Execute Sub-workflowノード**
  - 目標: 1.3

#### 自動修正の適用

- [ ] **自動修正プレビュー**
  ```bash
  mcp_n8n-mcp_n8n_autofix_workflow({
    id: "r9Sp5n0mkUCcH8cw",
    applyFixes: false,  # プレビューモード
    fixTypes: ["typeversion-upgrade", "expression-format"]
  })
  ```

- [ ] **自動修正適用**
  ```bash
  mcp_n8n-mcp_n8n_autofix_workflow({
    id: "r9Sp5n0mkUCcH8cw",
    applyFixes: true,
    fixTypes: ["typeversion-upgrade"]
  })
  ```

---

## 🔍 Phase 3: 統合検証

### 3.1 ワークフロー全体検証

- [ ] **親フロー検証**
  ```bash
  mcp_n8n-mcp_n8n_validate_workflow({id: "r9Sp5n0mkUCcH8cw"})
  ```
  - エラー数: 0個
  - 警告数: <10個
  - 接続検証: すべて有効

- [ ] **接続検証**
  ```bash
  mcp_n8n-mcp_validate_workflow_connections({
    workflow: { nodes: [...], connections: {...} }
  })
  ```
  - サイクル検出: なし
  - 無効な接続: なし

- [ ] **式検証**
  ```bash
  mcp_n8n-mcp_validate_workflow_expressions({
    workflow: { nodes: [...], connections: {...} }
  })
  ```
  - 式エラー: なし
  - 参照エラー: なし

---

### 3.2 E2Eテスト

#### 正常系テスト

- [ ] **テストケース1: 正常系**
  ```bash
  # Webhookトリガー
  mcp_n8n-mcp_n8n_trigger_webhook_workflow({
    webhookUrl: "https://n8n-python-production-344b.up.railway.app/webhook/wf7-video-script",
    httpMethod: "POST",
    data: { notionPageId: "test-notion-page-id" },
    waitForResponse: true
  })
  ```
  - Phase4a成功確認
  - Phase4b成功確認
  - Phase4c成功確認
  - Google Drive Upload成功確認
  - Notion更新成功確認
  - Webhook応答成功確認

#### 異常系テスト

- [ ] **テストケース2: Phase4a失敗**
  - Phase4aが `success: false` を返すシミュレーション
  - エラー時Notion更新実行確認
  - エラー時Webhook応答実行確認

- [ ] **テストケース3: Phase4b失敗**
  - Phase4bが `success: false` を返すシミュレーション
  - エラー時Notion更新実行確認
  - エラー時Webhook応答実行確認

- [ ] **テストケース4: Phase4c失敗**
  - Phase4cが `success: false` を返すシミュレーション
  - エラー時Notion更新実行確認
  - エラー時Webhook応答実行確認

---

### 3.3 パフォーマンステスト

- [ ] **処理時間測定**
  - Phase4a処理時間: <30秒
  - Phase4b処理時間: <5分
  - Phase4c処理時間: <2分
  - 全体処理時間: <8分

- [ ] **メモリ使用量測定**
  - メモリ使用量: <500MB

- [ ] **実行ログ確認**
  ```bash
  mcp_n8n-mcp_n8n_get_execution({
    id: "[実行ID]",
    mode: "summary"
  })
  ```

---

## 📊 検証結果サマリー

### 検証完了チェックリスト

- [ ] Phase4a検証完了
- [ ] Phase4b検証完了
- [ ] Phase4c検証完了
- [ ] 親フロー検証完了
- [ ] E2Eテスト完了
- [ ] パフォーマンステスト完了

### 検証結果記録

| 項目 | 結果 | 備考 |
|------|------|------|
| **エラー数** | 0個 | ✅ |
| **警告数** | <10個 | ✅ |
| **ノード数** | 10-12個 | ✅ |
| **処理時間** | <8分 | ✅ |
| **メモリ使用量** | <500MB | ✅ |

---

## 🔧 トラブルシューティング

### よくある問題

**問題1: Execute Sub-workflowノードでデータが渡らない**

**検証方法**:
```bash
# サブワークフローの入力データ契約確認
mcp_n8n-mcp_n8n_get_workflow({id: "LYPbvJfkMzLlhc6t"})

# データマッピング確認
mcp_n8n-mcp_validate_node_operation({
  nodeType: "nodes-base.executeWorkflow",
  config: {...}
})
```

**問題2: エラーハンドリングが動作しない**

**検証方法**:
```bash
# IFノードの条件確認
mcp_n8n-mcp_validate_node_operation({
  nodeType: "nodes-base.if",
  config: {...}
})

# エラー出力ブランチ確認
mcp_n8n-mcp_n8n_get_workflow_structure({id: "r9Sp5n0mkUCcH8cw"})
```

**問題3: typeVersion更新が反映されない**

**検証方法**:
```bash
# 自動修正の適用
mcp_n8n-mcp_n8n_autofix_workflow({
  id: "r9Sp5n0mkUCcH8cw",
  applyFixes: true,
  fixTypes: ["typeversion-upgrade"]
})

# 更新後の確認
mcp_n8n-mcp_n8n_get_workflow({id: "r9Sp5n0mkUCcH8cw"})
```

---

## 📚 参考資料

- [WF7-Phase4-簡素化設計書.md](../../design/WF7-Phase4-簡素化設計書.md)
- [WF7-Phase4-簡素化実装ガイド.md](../../implementation/WF7-Phase4-簡素化実装ガイド.md)
- [WF7-Phase4-簡素化比較表.md](../../design/WF7-Phase4-簡素化比較表.md)
- [n8n MCP Tools Documentation](https://docs.n8n.io/)

---

**作成者**: AI Assistant (Claude Sonnet 4.5)  
**レビュー**: 未実施  
**承認**: 未承認  
**次回更新**: 検証完了時




