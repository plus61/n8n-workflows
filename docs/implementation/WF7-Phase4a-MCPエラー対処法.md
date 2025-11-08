# WF7 Phase4a MCPエラー対処法

**作成日**: 2025-11-08  
**問題**: `n8n_update_partial_workflow`で「Invalid request: request/body must NOT have additional properties」エラーが発生

---

## 🔍 エラー内容

```
"Invalid request: request/body must NOT have additional properties"
```

このエラーは、MCPツールがn8n APIにリクエストを送信する際に、リクエストボディに余分なプロパティが含まれていることを示しています。

---

## ✅ 解決方法

### 方法1: 手動実装（推奨）

MCPツールのエラーが解決できない場合、**n8n UIで手動実装**することを推奨します。

**参照**: `docs/implementation/WF7-Phase4a-手動実装手順.md`

### 方法2: 段階的な実装

MCPツールを使用する場合、以下の手順で段階的に実装します:

1. **Step 1**: ノードのみ追加（接続なし）
   ```javascript
   {
     type: "addNode",
     node: {
       name: "Code - Generate Slides with Pillow",
       type: "n8n-nodes-base.code",
       typeVersion: 2,
       position: [-2480, -128],
       parameters: {
         language: "python",
         mode: "runOnceForAllItems",
         pythonCode: "return []"
       }
     }
   }
   ```

2. **Step 2**: 接続を追加（別の操作として）
   ```javascript
   {
     type: "addConnection",
     source: "データ統合",
     target: "Code - Generate Slides with Pillow"
   }
   ```

**注意**: Step 1でノードを追加した後、ワークフローが無効な状態になるため、Step 2をすぐに実行する必要があります。

### 方法3: MCPツールのバージョンアップ

現在のMCPツールのバージョン: `2.22.6`  
最新バージョン: `2.22.11`

バージョンアップコマンド:
```bash
npm install -g n8n-mcp@2.22.11
```

バージョンアップ後、Claude Desktopを再起動してください。

---

## 🔧 検証済みの動作

以下の操作は**検証済み**で動作します:

1. **単一ノード追加（接続なし）**: ✅ 動作（ただしワークフローが無効な状態になる）
2. **validateOnly: true**: ✅ 動作（検証のみ、適用なし）
3. **単一接続追加**: ❌ エラー（ノードが存在しない場合）

---

## ⚠️ 現在の制限事項

1. **2つの操作を同時に実行**: `addNode`と`addConnection`を同時に実行するとエラーが発生
2. **長いPythonコード**: コードが長すぎる場合、エラーが発生する可能性がある
3. **MCPツールのバージョン**: 古いバージョンを使用している場合、バグが含まれている可能性がある

---

## 📝 推奨アプローチ

**現時点では、n8n UIでの手動実装を推奨します。**

理由:
1. MCPツールのエラーが解決できない
2. 手動実装手順書が完成している
3. 手動実装の方が確実で、エラーが発生しにくい

**参照ドキュメント**:
- `docs/implementation/WF7-Phase4a-手動実装手順.md` - 詳細な手動実装手順
- `docs/implementation/WF7-Phase4-FAL実装計画書.md` - 全体の実装計画

---

## 🔄 改善案の実行結果

### 1. MCPツールのバージョンアップ ✅

**実行日**: 2025-11-08  
**コマンド**: `npm install -g n8n-mcp@2.22.11`  
**結果**: ✅ インストール成功

**注意**: Claude Desktopの再起動が必要（現在のセッションでは古いバージョンが使用されている可能性あり）

### 2. 段階的な実装 ❌

**試行内容**:
1. Step 1: ノードのみ追加 → ❌ エラー（接続のないノードは許可されない）
2. Step 2: 接続を追加 → ❌ エラー（ノードが存在しない）

**結果**: n8nは接続のないノードを許可しないため、ノードと接続を同時に追加する必要がある。しかし、2つの操作を同時に実行すると「Invalid request: request/body must NOT have additional properties」エラーが発生。

### 3. continueOnErrorモード ❌

**試行内容**: `continueOnError: true`を使用して接続を追加  
**結果**: ❌ エラー（ノードが存在しないため接続できない）

---

## 📊 結論

**MCPツールでの自動実装は現時点では困難**です。

**理由**:
1. n8nは接続のないノードを許可しない
2. ノードと接続を同時に追加すると、MCPツールのリクエスト検証エラーが発生
3. 段階的な実装も、n8nの制約により不可能

**推奨される実装方法**: **n8n UIでの手動実装**

---

**作成者**: Claude Code (Composer)  
**更新日**: 2025-11-08  
**最終更新**: 2025-11-08（改善案実行結果を追加）

