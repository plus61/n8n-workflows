# WF7 Phase4 簡素化実装ガイド

**作成日**: 2025-11-09  
**対象**: WF7 Phase4 簡素化設計書に基づく実装  
**前提**: n8n MCPツールによる分析結果 + ベストプラクティス

---

## 🎯 実装概要

現在の48ノードのワークフローを10-12ノードに簡素化し、Phase4a/b/cを独立したサブワークフローとして実装します。

---

## 📋 Phase 1: サブワークフロー準備

### 1.1 Phase4a確認・改修

**既存ワークフローID**: `LYPbvJfkMzLlhc6t`

**確認項目**:
- [ ] 入力データ契約が標準化されているか
- [ ] 出力データ契約が標準化されているか
- [ ] エラーハンドリングが実装されているか

**改修が必要な場合**:

```yaml
# 入力データ契約の標準化
入力: {
  script_id: string (必須),
  scriptData: object (必須)
}

# 出力データ契約の標準化
出力: {
  success: boolean (必須),
  script_id: string (必須),
  slides_metadata: array (必須、7要素),
  slides_count: number (必須、7)
}

# エラーハンドリング追加
エラー時: {
  success: false,
  error: string,
  script_id: string
}
```

**n8n MCPツールでの検証**:
```bash
# ワークフロー構造確認
mcp_n8n-mcp_n8n_get_workflow_structure({id: "LYPbvJfkMzLlhc6t"})

# ワークフロー検証
mcp_n8n-mcp_n8n_validate_workflow({id: "LYPbvJfkMzLlhc6t"})
```

---

### 1.2 Phase4b改修

**既存ワークフローID**: `wHaKi98mTlUvFIOR`

**改修内容**:
1. FALポーリング・リトライロジックをサブワークフロー内に完結
2. 入力/出力データ契約の標準化
3. エラーハンドリングの統一

**改修後の構造**:
```
Webhook (入力)
  ↓
Split Out (slides_metadata)
  ↓
HTTP Request - FAL Submit (各スライド)
  ↓
Wait for Processing (10秒)
  ↓
HTTP Request - Check Status (ポーリング)
  ↓
IF - Render Completed?
  ├─ [true] → Get Video URL
  └─ [false] → Retry Counter → Check Retry Limit → Wait Before Retry → Check Status
  ↓
Aggregate Videos
  ↓
Respond to Webhook (出力)
```

**n8n MCPツールでの検証**:
```bash
# ノード設定の検証
mcp_n8n-mcp_validate_node_operation({
  nodeType: "nodes-base.httpRequest",
  config: {
    method: "POST",
    url: "https://queue.fal.run/fal-ai/...",
    authentication: "genericCredentialType",
    genericAuthType: "httpHeaderAuth"
  }
})
```

---

### 1.3 Phase4c作成

**新規ワークフロー作成**

**実装方法の選択**:

#### オプション1: 外部Python FastAPIエンドポイント

**メリット**:
- ファイルシステムアクセス可能
- FFmpeg実行環境を完全制御
- エラーハンドリングが容易

**実装手順**:
1. Railway上にPython FastAPIプロジェクト作成
2. `/api/ffmpeg-concat` エンドポイント実装
3. n8nからHTTP Requestで呼び出し

**Pythonコード例**:
```python
from fastapi import FastAPI, HTTPException
import subprocess
import tempfile
import os

app = FastAPI()

@app.post("/api/ffmpeg-concat")
async def concat_videos(request: dict):
    videos_metadata = request.get("videos_metadata", [])
    script_id = request.get("script_id", "")
    
    # 動画ダウンロード
    temp_dir = tempfile.mkdtemp()
    video_paths = []
    
    for video_meta in videos_metadata:
        video_url = video_meta.get("video_url")
        # ダウンロード処理
        video_path = os.path.join(temp_dir, f"{video_meta['section']}.mp4")
        # curl or requestsでダウンロード
        video_paths.append(video_path)
    
    # FFmpeg結合
    concat_file = os.path.join(temp_dir, "concat.txt")
    with open(concat_file, "w") as f:
        for video_path in video_paths:
            f.write(f"file '{video_path}'\n")
    
    output_path = os.path.join(temp_dir, f"final_{script_id}.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-safe", "0", "-f", "concat",
        "-i", concat_file, "-c", "copy", output_path
    ])
    
    # Google Drive Upload
    # ...
    
    return {
        "success": True,
        "final_video_url": "...",
        "total_duration": sum(v["duration"] for v in videos_metadata)
    }
```

#### オプション2: Execute Commandノード

**メリット**:
- n8n内で完結
- 外部API不要

**デメリット**:
- Railway環境にFFmpegが必要
- ファイルシステムアクセス制限あり

**実装手順**:
1. Railway環境にFFmpegインストール確認
2. Execute CommandノードでFFmpeg実行

**n8nノード設定例**:
```yaml
Node: Execute Command
Command: ffmpeg
Arguments:
  - "-y"
  - "-safe"
  - "0"
  - "-f"
  - "concat"
  - "-i"
  - "{{ $json.concat_file_path }}"
  - "-c"
  - "copy"
  - "{{ $json.output_path }}"
```

**推奨**: オプション1（外部Python FastAPI）を推奨

---

## 📋 Phase 2: 親フロー簡素化

### 2.1 バックアップ

**現在のワークフローID**: `r9Sp5n0mkUCcH8cw`

**バックアップ手順**:
```bash
# n8n MCPツールでワークフロー取得
mcp_n8n-mcp_n8n_get_workflow({id: "r9Sp5n0mkUCcH8cw"})

# ファイルとして保存
workflows/archive/wf7-phase4-v3-complex.json
```

---

### 2.2 ノード削除

**削除対象ノード**:

1. **データ変換ノード**:
   - `レスポンスデータ準備`
   - `レスポンスデータ復元`
   - 複数の`Set`ノード（データ統合で完結）

2. **FALポーリング機構** (Phase4bに移行):
   - `Submit to FAL`
   - `Fetch Status`
   - `Wait for Processing`
   - `Check Render Status`
   - `Render Completed?`
   - `Retry Counter`
   - `Check Retry Limit`
   - `Wait Before Retry`
   - `Get Image Result URL`
   - `Download Image`
   - `DriveへUL`

3. **重複エラーハンドリング**:
   - `エラー時Notion更新(Phase4b)`
   - `エラー時Webhook応答(Phase4b)`

**削除後のノード数**: 48 → 約20ノード

---

### 2.3 Execute Sub-workflowノード追加

**Phase4a Execute Sub-workflowノード設定**:

```yaml
Node: Execute Sub-workflow - Phase4a
Type: n8n-nodes-base.executeWorkflow
Version: 1.3
Settings:
  source: database
  workflowId: LYPbvJfkMzLlhc6t
  mode: once
  waitForSubWorkflow: true
  workflowInputs:
    mapping:
      - script_id: "={{ $json.id }}"
      - scriptData: "={{ $json.properties }}"
```

**Phase4b Execute Sub-workflowノード設定**:

```yaml
Node: Execute Sub-workflow - Phase4b
Type: n8n-nodes-base.executeWorkflow
Version: 1.3
Settings:
  source: database
  workflowId: wHaKi98mTlUvFIOR
  mode: once
  waitForSubWorkflow: true
  workflowInputs:
    mapping:
      - script_id: "={{ $('Execute Sub-workflow - Phase4a').item.json.script_id }}"
      - slides_metadata: "={{ $('Execute Sub-workflow - Phase4a').item.json.slides_metadata }}"
```

**Phase4c Execute Sub-workflowノード設定**:

```yaml
Node: Execute Sub-workflow - Phase4c
Type: n8n-nodes-base.executeWorkflow
Version: 1.3
Settings:
  source: database
  workflowId: [新規作成したPhase4cワークフローID]
  mode: once
  waitForSubWorkflow: true
  workflowInputs:
    mapping:
      - script_id: "={{ $('Execute Sub-workflow - Phase4b').item.json.script_id }}"
      - videos_metadata: "={{ $('Execute Sub-workflow - Phase4b').item.json.videos_metadata }}"
```

**n8n MCPツールでの検証**:
```bash
# Execute Sub-workflowノードの検証
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

---

### 2.4 エラーハンドリング統合

**統一IFノード設定**:

```yaml
Node: IF - All Phases Success Check
Type: n8n-nodes-base.if
Version: 2.2
Settings:
  conditions:
    options:
      version: 2
      caseSensitive: true
      typeValidation: strict
    combinator: and
    conditions:
      - id: phase4a-success
        leftValue: "={{ $('Execute Sub-workflow - Phase4a').item.json.success }}"
        rightValue: true
        operator:
          type: boolean
          operation: equals
      - id: phase4a-slides-count
        leftValue: "={{ $('Execute Sub-workflow - Phase4a').item.json.slides_count }}"
        rightValue: 7
        operator:
          type: number
          operation: equals
      - id: phase4b-success
        leftValue: "={{ $('Execute Sub-workflow - Phase4b').item.json.success }}"
        rightValue: true
        operator:
          type: boolean
          operation: equals
      - id: phase4b-videos-count
        leftValue: "={{ $('Execute Sub-workflow - Phase4b').item.json.videos_count }}"
        rightValue: 7
        operator:
          type: number
          operation: equals
      - id: phase4c-success
        leftValue: "={{ $('Execute Sub-workflow - Phase4c').item.json.success }}"
        rightValue: true
        operator:
          type: boolean
          operation: equals
  onError: continueErrorOutput
```

**エラーハンドリングノード設定**:

```yaml
Node: エラー時Notion更新
Type: n8n-nodes-base.httpRequest
Version: 4.3
Settings:
  method: PATCH
  url: "={{ 'https://api.notion.com/v1/pages/' + $('Notion API呼び出し').item.json.id }}"
  authentication: predefinedCredentialType
  nodeCredentialType: notionApi
  sendHeaders: true
  headerParameters:
    - name: Notion-Version
      value: 2022-06-28
  sendBody: true
  specifyBody: json
  jsonBody: "={{
    properties: {
      status: { status: { name: 'Error' } },
      errorMessage: {
        rich_text: [{
          text: {
            content: 'Phase4処理に失敗しました: ' + ($json.error || 'Unknown error')
          }
        }]
      }
    }
  }}"
  onError: continueRegularOutput
  retryOnFail: true
```

**エラー時Webhook応答ノード設定**:

```yaml
Node: エラー時Webhook応答
Type: n8n-nodes-base.respondToWebhook
Version: 1.4
Settings:
  respondWith: json
  responseBody: "={{
    success: false,
    error: $json.error || 'Unknown error',
    phase: $json.phase || 'unknown',
    script_id: $('Notion API呼び出し').item.json.id
  }}"
```

---

### 2.5 データマッピング設定

**各ノード間のデータマッピング**:

```yaml
# Notion API呼び出し → Execute Phase4a
script_id: "={{ $json.id }}"
scriptData: "={{ $json.properties }}"

# Execute Phase4a → Execute Phase4b
script_id: "={{ $('Execute Sub-workflow - Phase4a').item.json.script_id }}"
slides_metadata: "={{ $('Execute Sub-workflow - Phase4a').item.json.slides_metadata }}"

# Execute Phase4b → Execute Phase4c
script_id: "={{ $('Execute Sub-workflow - Phase4b').item.json.script_id }}"
videos_metadata: "={{ $('Execute Sub-workflow - Phase4b').item.json.videos_metadata }}"

# Execute Phase4c → Google Drive Upload
binary_data: "={{ $('Execute Sub-workflow - Phase4c').item.json.final_video_path }}"

# Google Drive Upload → Notion更新
notionPageId: "={{ $('Notion API呼び出し').item.json.id }}"
videoUrl: "={{ $json.webViewLink }}"
```

---

### 2.6 typeVersion更新

**更新が必要なノード**:

| ノードタイプ | 現在のVersion | 最新Version | 更新方法 |
|-------------|--------------|------------|---------|
| Webhook | 2 | 2.1 | ノード削除→再追加 |
| HTTP Request | 4.2 | 4.3 | ノード削除→再追加 |
| Respond to Webhook | 1.1 | 1.4 | ノード削除→再追加 |
| Execute Sub-workflow | - | 1.3 | 新規追加 |

**n8n MCPツールでの検証**:
```bash
# ワークフロー全体の検証
mcp_n8n-mcp_n8n_validate_workflow({id: "r9Sp5n0mkUCcH8cw"})

# 自動修正の提案
mcp_n8n-mcp_n8n_autofix_workflow({
  id: "r9Sp5n0mkUCcH8cw",
  applyFixes: false,  # プレビューモード
  fixTypes: ["typeversion-upgrade", "expression-format"]
})
```

---

## 📋 Phase 3: テスト・検証

### 3.1 単体テスト

**Phase4a単体テスト**:

```yaml
テストケース1: 正常系
  入力: {
    script_id: "test-001",
    scriptData: { ... }
  }
  期待出力: {
    success: true,
    slides_metadata: [7要素],
    slides_count: 7
  }

テストケース2: 異常系（Script Data不足）
  入力: {
    script_id: "test-002",
    scriptData: {}
  }
  期待出力: {
    success: false,
    error: "Script data is missing"
  }
```

**Phase4b単体テスト**:

```yaml
テストケース1: 正常系
  入力: {
    script_id: "test-001",
    slides_metadata: [7要素]
  }
  期待出力: {
    success: true,
    videos_metadata: [7要素],
    videos_count: 7
  }

テストケース2: 異常系（FAL API失敗）
  入力: {
    script_id: "test-002",
    slides_metadata: [無効なURL]
  }
  期待出力: {
    success: false,
    error: "FAL API failed"
  }
```

**Phase4c単体テスト**:

```yaml
テストケース1: 正常系
  入力: {
    script_id: "test-001",
    videos_metadata: [7要素]
  }
  期待出力: {
    success: true,
    final_video_url: "https://drive.google.com/...",
    total_duration: 73
  }

テストケース2: 異常系（動画ダウンロード失敗）
  入力: {
    script_id: "test-002",
    videos_metadata: [無効なURL]
  }
  期待出力: {
    success: false,
    error: "Video download failed"
  }
```

---

### 3.2 統合テスト

**E2Eテストフロー**:

```yaml
1. Webhook受信
   POST /wf7-video-script
   body: { notionPageId: "test-notion-page-id" }

2. Notion API呼び出し
   期待: 台本データ取得成功

3. Execute Phase4a
   期待: スライド生成成功（7枚）

4. Execute Phase4b
   期待: 動画生成成功（7本）

5. Execute Phase4c
   期待: 動画結合成功

6. Google Drive Upload
   期待: アップロード成功

7. Notion更新
   期待: ステータス更新成功

8. Respond to Webhook
   期待: 成功応答
```

**エラーハンドリングテスト**:

```yaml
テストケース1: Phase4a失敗
  シミュレーション: Phase4aが success: false を返す
  期待動作:
    - IFノードでエラー検知
    - エラー時Notion更新実行
    - エラー時Webhook応答実行

テストケース2: Phase4b失敗
  シミュレーション: Phase4bが success: false を返す
  期待動作:
    - IFノードでエラー検知
    - エラー時Notion更新実行
    - エラー時Webhook応答実行

テストケース3: Phase4c失敗
  シミュレーション: Phase4cが success: false を返す
  期待動作:
    - IFノードでエラー検知
    - エラー時Notion更新実行
    - エラー時Webhook応答実行
```

---

### 3.3 パフォーマンステスト

**測定項目**:

| 項目 | 目標値 | 測定方法 |
|------|--------|---------|
| **Phase4a処理時間** | <30秒 | n8n実行ログ |
| **Phase4b処理時間** | <5分 | n8n実行ログ |
| **Phase4c処理時間** | <2分 | n8n実行ログ |
| **全体処理時間** | <8分 | Webhook受信から応答まで |
| **メモリ使用量** | <500MB | Railwayメトリクス |

---

## 🔧 トラブルシューティング

### よくある問題と解決方法

**問題1: Execute Sub-workflowノードでデータが渡らない**

**原因**: データマッピング設定が間違っている

**解決方法**:
- `workflowInputs.mapping` の設定を確認
- サブワークフローの入力データ契約を確認
- n8n MCPツールで検証: `validate_node_operation`

**問題2: Phase4cでファイルシステムアクセスエラー**

**原因**: Codeノードではファイルシステムアクセス不可

**解決方法**:
- 外部Python FastAPIエンドポイントを使用
- またはExecute CommandノードでFFmpeg実行

**問題3: エラーハンドリングが動作しない**

**原因**: IFノードの条件設定が間違っている

**解決方法**:
- IFノードの条件を確認
- `onError: continueErrorOutput` を設定
- エラー出力ブランチを確認

---

## 📚 参考資料

- [WF7-Phase4-簡素化設計書.md](../design/WF7-Phase4-簡素化設計書.md)
- [n8n Execute Sub-workflow Documentation](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.executeworkflow/)
- [n8n Error Handling Best Practices](https://docs.n8n.io/flow-logic/error-handling/)
- Phase4-FAL移行-要件定義.md

---

**作成者**: AI Assistant (Claude Sonnet 4.5)  
**レビュー**: 未実施  
**承認**: 未承認  
**次回更新**: Phase 1完了時

