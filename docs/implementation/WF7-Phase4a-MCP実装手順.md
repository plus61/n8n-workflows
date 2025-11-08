# WF7 Phase4a MCP実装手順

**作成日**: 2025-11-08  
**目的**: MCPツールを使用したPhase4a実装の手順書

---

## 📋 実装概要

MCPツール（`n8n_update_partial_workflow`）を使用して、Phase4aのノードを段階的に追加します。

---

## 🔧 実装手順

### Step 1: データ統合ノードの拡張

**目的**: Notionページのpropertiesを出力に含める

**操作**:
```javascript
{
  type: "updateNode",
  nodeId: "ad93cc09-6042-4968-8537-5c02b34ff85b",
  updates: {
    "parameters.jsCode": `const urlExtractNode = $('URL抽出').item.json;
const notionPage = $('Notion API呼び出し').item.json;

// ... 既存のコード ...

return {
  json: {
    notionPageId: urlExtractNode.notionPageId,
    articleId: urlExtractNode.articleId,
    scriptData: JSON.parse(scriptJsonText),
    assetsData: assetsArray,
    // Phase4a用: Notionページのpropertiesも含める
    notionProperties: notionPage.properties || {}
  }
};`
  }
}
```

**注意**: MCPツールで直接更新できない場合は、n8n UIで手動更新してください。

---

### Step 2: Phase4a Code Nodeの追加

**ノード設定**:
- **Name**: `Code - Generate Slides with Pillow`
- **Type**: `n8n-nodes-base.code`
- **Position**: `[-2400, -128]` (データ統合ノードの右側)
- **Language**: Python
- **Mode**: runOnceForAllItems

**Pythonコード**: `workflows/wf7-video-renderer/phase4a_code_node.py`の内容をコピー

**操作**:
```javascript
{
  type: "addNode",
  node: {
    name: "Code - Generate Slides with Pillow",
    type: "n8n-nodes-base.code",
    typeVersion: 2,
    position: [-2400, -128],
    parameters: {
      language: "python",
      mode: "runOnceForAllItems",
      pythonCode: "// phase4a_code_node.pyの内容をここにコピー"
    }
  }
}
```

**接続**:
```javascript
{
  type: "addConnection",
  source: "データ統合",
  target: "Code - Generate Slides with Pillow"
}
```

---

### Step 3: Split Outノードの追加（スライド用）

**ノード設定**:
- **Name**: `Split Out - Slides`
- **Type**: `n8n-nodes-base.splitOut`
- **Position**: `[-2176, -128]`

**操作**:
```javascript
{
  type: "addNode",
  node: {
    name: "Split Out - Slides",
    type: "n8n-nodes-base.splitOut",
    typeVersion: 1,
    position: [-2176, -128],
    parameters: {
      options: {}
    }
  }
}
```

**接続**:
```javascript
{
  type: "addConnection",
  source: "Code - Generate Slides with Pillow",
  target: "Split Out - Slides"
}
```

---

### Step 4: Google Drive Uploadノードの追加

**ノード設定**:
- **Name**: `Google Drive - Upload Slide Image`
- **Type**: `n8n-nodes-base.googleDrive`
- **Position**: `[-1952, -128]`

**操作**:
```javascript
{
  type: "addNode",
  node: {
    name: "Google Drive - Upload Slide Image",
    type: "n8n-nodes-base.googleDrive",
    typeVersion: 2.1,
    position: [-1952, -128],
    parameters: {
      operation: "upload",
      name: "={{ $json.filename }}",
      binaryData: true,
      binaryPropertyName: "image_base64",
      options: {
        parents: ["WF7_SLIDES_FOLDER_ID"], // 実際のフォルダIDに置き換え
        mimeType: "image/png"
      }
    },
    credentials: {
      googleDriveOAuth2Api: {
        id: "plniYONxQ1iPNoAi",
        name: "Google Drive account"
      }
    }
  }
}
```

**接続**:
```javascript
{
  type: "addConnection",
  source: "Split Out - Slides",
  target: "Google Drive - Upload Slide Image"
}
```

---

### Step 5: Aggregateノードの追加

**ノード設定**:
- **Name**: `Aggregate - Combine All Slides`
- **Type**: `n8n-nodes-base.aggregate`
- **Position**: `[-1728, -128]`

**操作**:
```javascript
{
  type: "addNode",
  node: {
    name: "Aggregate - Combine All Slides",
    type: "n8n-nodes-base.aggregate",
    typeVersion: 1,
    position: [-1728, -128],
    parameters: {
      aggregate: "aggregateAllItemData",
      options: {}
    }
  }
}
```

**接続**:
```javascript
{
  type: "addConnection",
  source: "Google Drive - Upload Slide Image",
  target: "Aggregate - Combine All Slides"
}
```

---

### Step 6: Set - Phase4a Payloadノードの追加

**ノード設定**:
- **Name**: `Set - Phase4a Payload`
- **Type**: `n8n-nodes-base.set`
- **Position**: `[-1504, -128]`

**操作**:
```javascript
{
  type: "addNode",
  node: {
    name: "Set - Phase4a Payload",
    type: "n8n-nodes-base.set",
    typeVersion: 3.4,
    position: [-1504, -128],
    parameters: {
      assignments: {
        assignments: [
          {
            id: "script_id",
            name: "script_id",
            value: "={{ $('データ統合').item.json.notionPageId }}",
            type: "string"
          },
          {
            id: "slides_metadata",
            name: "slides_metadata",
            value: "={{ $json.aggregatedData.map(item => ({ section: item.section, duration: item.duration, image_url: item.image_url || 'https://drive.google.com/uc?export=download&id=' + item.id, motion_prompt: item.motion_prompt, drive_file_id: item.id, filename: item.filename })) }}",
            type: "array"
          }
        ]
      },
      options: {}
    }
  }
}
```

**接続**:
```javascript
{
  type: "addConnection",
  source: "Aggregate - Combine All Slides",
  target: "Set - Phase4a Payload"
}
```

---

### Step 7: 既存ワークフローへの接続変更

**現在の接続**: `データ統合` → `Split Out` (assetsData用)

**新しい接続**: `Set - Phase4a Payload` → `Split Out` (assetsData用)

**操作**:
```javascript
{
  type: "rewireConnection",
  source: "Split Out",
  from: "データ統合",
  to: "Set - Phase4a Payload"
}
```

**注意**: 既存の`Split Out`ノードは、Phase4aの`slides_metadata`ではなく、既存の`assetsData`を処理するため、この接続変更は不要かもしれません。Phase4aの出力は別のパスで処理する必要があります。

---

## ⚠️ 重要な注意事項

1. **MCPツールの制限**: MCPツールで直接更新できない場合は、n8n UIで手動更新してください。

2. **Pythonコードの長さ**: `phase4a_code_node.py`の内容は約300行あります。n8n Code Nodeに直接コピーしてください。

3. **Google DriveフォルダID**: `WF7_SLIDES_FOLDER_ID`は実際のフォルダIDに置き換えてください。

4. **データフロー**: Phase4aの出力（`slides_metadata`）は、既存の`assetsData`処理とは別のパスで処理する必要があります。

---

## 🧪 テスト手順

1. **Code Node単体テスト**: Code Nodeを手動実行し、7枚のスライドが生成されることを確認
2. **統合テスト**: Phase4aノード群を実行し、Google Driveへのアップロードを確認
3. **E2Eテスト**: WebhookからPhase4aまで実行し、`slides_metadata`が正しく生成されることを確認

---

## 📝 次のステップ

Phase4a実装完了後、Phase4b（FAL Image-to-Video）の実装に進みます。

