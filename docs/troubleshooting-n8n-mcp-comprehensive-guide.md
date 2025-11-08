# n8n MCP トラブルシューティング完全ガイド

**作成日**: 2025-11-08  
**最終更新**: 2025-11-08  
**カテゴリ**: n8n, n8n-mcp, Claude Code, Cursor, トラブルシューティング  
**ステータス**: 網羅的調査完了

---

## 📋 目次

1. [問題の概要](#問題の概要)
2. [よくある問題と解決策](#よくある問題と解決策)
3. [設定ファイルの確認と修正](#設定ファイルの確認と修正)
4. [診断手順](#診断手順)
5. [ベストプラクティス](#ベストプラクティス)
6. [事例集](#事例集)

---

## 🎯 問題の概要

n8n MCPを使用する際に発生する主な問題を以下に分類：

### 問題カテゴリ

1. **接続問題**
   - MCPサーバーが起動しない
   - API接続エラー
   - URL設定の不整合

2. **バリデーションエラー**
   - `Invalid request: request/body must NOT have additional properties`
   - `continueOnFail must be boolean`
   - プロパティ削除エラー

3. **バージョン問題**
   - 古いバージョンが使用される
   - バージョン混在
   - キャッシュ問題

4. **設定問題**
   - 設定ファイルの不整合
   - 環境変数の未設定
   - 複数設定ファイルの競合

---

## 🔧 よくある問題と解決策

### 問題1: MCPサーバーが起動しない

#### 症状
- `mcp__n8n-mcp__n8n_diagnostic`が実行できない
- MCPツールが利用できない
- エラーメッセージ: "MCP server not found"

#### 原因
- 設定ファイルが存在しない
- 設定ファイルのJSON形式が不正
- Node.js/npxが正しくインストールされていない

#### 解決策

**Step 1: 設定ファイルの確認**

```bash
# Cursor用設定ファイル
cat .cursor/mcp.json

# Claude Desktop用設定ファイル
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Step 2: 設定ファイルの作成/修正**

`.cursor/mcp.json`を作成/更新：

```json
{
  "mcpServers": {
    "n8n-mcp": {
      "command": "/Users/yuichiroooosuger/.nvm/versions/node/v22.20.0/bin/npx",
      "args": ["-y", "n8n-mcp@2.22.11"],
      "env": {
        "N8N_API_URL": "${N8N_API_URL:-https://n8n-python-production-344b.up.railway.app}",
        "N8N_API_KEY": "${N8N_API_KEY}",
        "MCP_MODE": "stdio",
        "LOG_LEVEL": "error",
        "DISABLE_CONSOLE_OUTPUT": "true"
      }
    }
  }
}
```

**Step 3: Cursor/Claude Desktopの再起動**

設定変更後、必ず再起動してください。

---

### 問題2: バリデーションエラー「additional properties」

#### 症状

```json
{
  "success": false,
  "error": "Invalid request: request/body must NOT have additional properties",
  "code": "VALIDATION_ERROR"
}
```

#### 原因
- n8n Public APIがパーシャルアップデートをサポートしていない
- MCPツールが古いバージョンでリクエスト形式が不一致
- ノードと接続を同時に追加しようとしている

#### 解決策

**方法1: 完全更新を使用（推奨）**

```javascript
// ✅ 推奨パターン
// 1. 現在のワークフロー取得
const workflow = await mcp__n8n-mcp__n8n_get_workflow({ 
  id: "workflow-id" 
});

// 2. 必要な修正を適用
workflow.nodes.forEach(node => {
  if (node.name === "Target Node") {
    node.onError = "continueRegularOutput";
  }
});

// 3. 全体を更新
await mcp__n8n-mcp__n8n_update_full_workflow({
  id: "workflow-id",
  name: workflow.name,
  nodes: workflow.nodes,
  connections: workflow.connections
});
```

**方法2: MCPツールを最新バージョンに更新**

```bash
# グローバルインストールを更新
npm install -g n8n-mcp@2.22.11

# npxキャッシュをクリア
rm -rf ~/.npm/_npx

# 設定ファイルでバージョン指定
# .cursor/mcp.json の args を ["-y", "n8n-mcp@2.22.11"] に変更
```

**方法3: 段階的な実装**

```javascript
// Step 1: ノードのみ追加
await mcp__n8n-mcp__n8n_update_partial_workflow({
  id: "workflow-id",
  operations: [{
    type: "addNode",
    node: { /* ノード定義 */ }
  }]
});

// Step 2: 接続を追加（別の操作として）
await mcp__n8n-mcp__n8n_update_partial_workflow({
  id: "workflow-id",
  operations: [{
    type: "addConnection",
    source: "Source Node",
    target: "Target Node"
  }]
});
```

---

### 問題3: continueOnFail削除エラー

#### 症状

```
Error: Invalid request: request/body/nodes/1/continueOnFail must be boolean
```

#### 原因
- n8n APIがプロパティ削除をサポートしていない
- `null`や`undefined`はバリデーションエラーになる

#### 解決策

**方法1: onErrorを設定（推奨）**

```javascript
// ✅ continueOnFailを残したまま、onErrorを設定
await mcp__n8n-mcp__n8n_update_partial_workflow({
  id: "workflow-id",
  operations: [{
    type: "updateNode",
    nodeName: "Target Node",
    updates: {
      onError: "continueRegularOutput",  // モダンAPI
      retryOnFail: true,
      maxTries: 3
      // continueOnFail は残るが onError が優先される
    }
  }]
});
```

**方法2: 完全更新で削除**

```javascript
// 1. ワークフロー全体取得
const workflow = await mcp__n8n-mcp__n8n_get_workflow({ id: "workflow-id" });

// 2. continueOnFailを削除
workflow.nodes.forEach(node => {
  delete node.continueOnFail;
});

// 3. 完全置換
await mcp__n8n-mcp__n8n_update_full_workflow({
  id: "workflow-id",
  name: workflow.name,
  nodes: workflow.nodes,
  connections: workflow.connections
});
```

**方法3: n8n UIで手動削除**

最も安全な方法。n8nエディタで該当ノードの設定を開き、「Continue On Fail」をオフにします。

---

### 問題4: バージョンが古い

#### 症状
- 診断結果で `upToDate: false` が表示される
- 最新機能が使用できない
- 既知のバグが修正されていない

#### 原因
- 設定ファイルでバージョン指定がない
- npxキャッシュに古いバージョンが残っている
- グローバルインストールが古い

#### 解決策

**Step 1: 現在のバージョンを確認**

```javascript
mcp__n8n-mcp__n8n_diagnostic({verbose: true})
```

**Step 2: 設定ファイルでバージョン指定**

`.cursor/mcp.json`を更新：

```json
{
  "mcpServers": {
    "n8n-mcp": {
      "args": ["-y", "n8n-mcp@2.22.11"]  // ← バージョン固定
    }
  }
}
```

**Step 3: キャッシュクリア**

```bash
# npxキャッシュをクリア
rm -rf ~/.npm/_npx

# グローバルインストールを更新（オプション）
npm install -g n8n-mcp@2.22.11
```

**Step 4: 再起動**

Cursor/Claude Desktopを再起動して設定を反映させます。

---

### 問題5: URL接続エラー

#### 症状
- API接続が失敗する
- 異なるURLに接続している
- プロセスキャッシュが残っている

#### 原因
- 設定ファイルのURLが間違っている
- URL末尾のスラッシュ問題
- 古いプロセスが実行中

#### 解決策

**Step 1: 実行中のプロセスを停止**

```bash
# すべてのn8n-mcpプロセスを停止
pkill -f "n8n-mcp"

# 確認
ps aux | grep n8n-mcp
```

**Step 2: 設定ファイルのURLを確認**

```bash
# 設定ファイルを確認
cat .cursor/mcp.json | grep N8N_API_URL

# URL末尾のスラッシュを削除（重要）
# ❌ "https://...app/"
# ✅ "https://...app"
```

**Step 3: 環境変数の確認**

```bash
# 環境変数を確認
echo $N8N_API_URL
echo $N8N_API_KEY

# 設定されていない場合は設定ファイルで直接指定
```

**Step 4: 接続確認**

```javascript
// ヘルスチェック
mcp__n8n-mcp__n8n_health_check()

// 期待される結果
{
  "status": "ok",
  "apiUrl": "https://n8n-python-production-344b.up.railway.app",
  "mcpVersion": "2.22.11"
}
```

---

## ⚙️ 設定ファイルの確認と修正

### 設定ファイルの場所

| 環境 | 設定ファイルパス |
|------|----------------|
| Cursor | `.cursor/mcp.json` |
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| プロジェクト共通 | `.mcp/config.json` |
| プロジェクトルート | `.mcp.json` |

### 推奨設定テンプレート

**`.cursor/mcp.json`（Cursor用）**

```json
{
  "mcpServers": {
    "n8n-mcp": {
      "command": "/Users/yuichiroooosuger/.nvm/versions/node/v22.20.0/bin/npx",
      "args": ["-y", "n8n-mcp@2.22.11"],
      "env": {
        "N8N_API_URL": "${N8N_API_URL:-https://n8n-python-production-344b.up.railway.app}",
        "N8N_API_KEY": "${N8N_API_KEY}",
        "MCP_MODE": "stdio",
        "LOG_LEVEL": "error",
        "DISABLE_CONSOLE_OUTPUT": "true"
      }
    }
  }
}
```

**重要ポイント**:
- ✅ バージョンを明示的に指定（`n8n-mcp@2.22.11`）
- ✅ URL末尾にスラッシュを付けない
- ✅ 環境変数は`${VAR:-default}`形式でフォールバック設定
- ✅ `LOG_LEVEL`を`error`に設定してログを抑制

---

## 🔍 診断手順

### 基本診断

```javascript
// 1. ヘルスチェック
mcp__n8n-mcp__n8n_health_check()

// 2. 詳細診断
mcp__n8n-mcp__n8n_diagnostic({verbose: true})
```

### 確認項目チェックリスト

- [ ] **API接続**: `status: "ok"`
- [ ] **バージョン**: `current: "2.22.11"`（最新）
- [ ] **URL**: 正しいn8nインスタンスURL
- [ ] **ツール数**: `totalAvailable: 38`（ドキュメント22 + 管理16）
- [ ] **設定ファイル**: バージョン指定がある
- [ ] **環境変数**: `N8N_API_URL`と`N8N_API_KEY`が設定されている

### トラブルシューティングフロー

```
1. 診断実行
   ↓
2. エラー内容を確認
   ↓
3. 該当する問題カテゴリを特定
   ↓
4. 解決策を適用
   ↓
5. 再診断で確認
   ↓
6. 問題が解決しない場合、次の解決策を試す
```

---

## 📝 ベストプラクティス

### 1. ワークフロー更新パターン

**推奨: 完全更新を使用**

```javascript
async function updateWorkflow(workflowId, updates) {
  // 1. 現在のワークフロー取得
  const workflow = await mcp__n8n-mcp__n8n_get_workflow({ id: workflowId });
  
  // 2. 修正を適用
  updates.forEach(update => {
    const node = workflow.nodes.find(n => n.id === update.nodeId);
    if (node) {
      Object.assign(node, update.changes);
    }
  });
  
  // 3. 完全更新
  return await mcp__n8n-mcp__n8n_update_full_workflow({
    id: workflowId,
    name: workflow.name,
    nodes: workflow.nodes,
    connections: workflow.connections
  });
}
```

### 2. エラーハンドリング

```javascript
try {
  await mcp__n8n-mcp__n8n_update_partial_workflow({...});
} catch (error) {
  if (error.code === "VALIDATION_ERROR") {
    // バリデーションエラーの場合、完全更新にフォールバック
    console.log("部分更新失敗、完全更新に切り替え");
    await updateWorkflowWithFullUpdate(...);
  } else {
    throw error;
  }
}
```

### 3. 設定ファイル管理

- ✅ バージョンを明示的に指定
- ✅ 環境変数はフォールバック値を設定
- ✅ 設定ファイルをGitで管理（APIキーは除外）
- ✅ 複数の設定ファイルの整合性を保つ

### 4. プロセス管理

```bash
# 定期的に古いプロセスをクリーンアップ
pkill -f "n8n-mcp"

# プロセス数を確認
ps aux | grep n8n-mcp | wc -l
```

---

## 📚 事例集

### 事例1: バリデーションエラー「additional properties」

**発生日**: 2025-11-07  
**問題**: `n8n_update_partial_workflow`でエラー発生  
**原因**: n8n APIがパーシャルアップデートをサポートしていない  
**解決策**: `n8n_update_full_workflow`を使用  
**参照**: `docs/troubleshooting-n8n-mcp-validation-error.md`

### 事例2: continueOnFail削除失敗

**発生日**: 2025-10-27  
**問題**: `continueOnFail: null`でエラー発生  
**原因**: n8n APIがプロパティ削除をサポートしていない  
**解決策**: `onError`を設定（`continueOnFail`は残す）  
**参照**: `docs/mcp/troubleshooting-continueonerror.md`

### 事例3: URL接続問題

**発生日**: 2025-11-03  
**問題**: 古いURLに接続している  
**原因**: プロセスキャッシュとURL末尾のスラッシュ  
**解決策**: プロセス停止、URL修正、キャッシュクリア  
**参照**: `n8n-mcp-url-issue-20251103_153138.md`

### 事例4: バージョン混在

**発生日**: 2025-11-08  
**問題**: 診断結果で`v2.22.6`、最新は`v2.22.11`  
**原因**: 設定ファイルでバージョン指定がない  
**解決策**: 設定ファイルで`n8n-mcp@2.22.11`を指定  
**参照**: 本ガイド

---

## 🚨 既知の制限事項

### n8n APIの制限

1. **パーシャルアップデート非サポート**
   - PATCHメソッドは使用できない
   - 完全置換（PUT）のみ

2. **プロパティ削除不可**
   - `null`や`undefined`はバリデーションエラー
   - 削除には完全更新が必要

3. **ワークフローアクティブ化**
   - MCP経由ではアクティブ化できない
   - n8n UIまたはAPIで手動アクティブ化が必要

### MCPツールの制限

1. **バージョン依存**
   - 古いバージョンでリクエスト形式が不一致
   - バージョン2.22.11以降で改善

2. **ノードと接続の同時追加**
   - 同時追加でバリデーションエラーが発生
   - 段階的な実装が必要

### Cursor/Claude Desktopの制限

1. **設定変更後の再起動**
   - MCP設定変更後、再起動が必要
   - `npx -y`がキャッシュを使用する可能性

2. **プロセス管理**
   - 複数のプロセスが実行中になる可能性
   - 定期的なクリーンアップが必要

---

## ✅ チェックリスト

### 初回セットアップ

- [ ] `.cursor/mcp.json`を作成
- [ ] バージョンを`n8n-mcp@2.22.11`に指定
- [ ] `N8N_API_URL`と`N8N_API_KEY`を設定
- [ ] URL末尾にスラッシュがないことを確認
- [ ] Cursor/Claude Desktopを再起動
- [ ] `n8n_diagnostic`で接続確認

### 問題発生時

- [ ] `n8n_diagnostic`で現在の状態を確認
- [ ] エラーメッセージの詳細を確認
- [ ] 該当する問題カテゴリを特定
- [ ] 解決策を順番に試す
- [ ] 再診断で問題が解決したか確認

### 定期メンテナンス

- [ ] バージョンが最新か確認
- [ ] 実行中のプロセスをクリーンアップ
- [ ] 設定ファイルの整合性を確認
- [ ] キャッシュをクリア

---

## 📚 関連ドキュメント

- [n8n MCP統合ガイド](./mcp-integration-guide.md)
- [n8n MCP APIバリデーションエラー対処法](./troubleshooting-n8n-mcp-validation-error.md)
- [continueOnFail削除失敗の原因と対処法](../n8n-mcp_continueOnFail削除失敗の原因と対処法.md)
- [WF7 Phase4 トラブルシューティングガイド](./knowledge/wf7-phase4-troubleshooting-guide.md)
- [MCP使用ガイド集](./mcp/README.md)

---

## 🔄 更新履歴

- **2025-11-08**: 網羅的トラブルシューティングガイド作成
  - よくある問題5つを整理
  - 設定ファイルの確認と修正手順を追加
  - 診断手順とベストプラクティスを追加
  - 事例集を追加

---

**最終更新**: 2025-11-08  
**次回確認**: 新しい問題が発生した場合、本ガイドに追記

