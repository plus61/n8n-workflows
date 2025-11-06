# n8n-mcp: continueOnFail削除失敗の原因と対処法

**作成日**: 2025-10-27
**カテゴリ**: n8n, n8n-mcp, トラブルシューティング
**ステータス**: 検証済み

---

## 🎯 問題の概要

n8n-mcpの`n8n_update_partial_workflow`で`continueOnFail`プロパティを削除しようとした際、以下のエラーが発生：

```
Error: Invalid request: request/body/nodes/1/continueOnFail must be boolean
```

### 試行した方法
```javascript
{
  "type": "updateNode",
  "nodeName": "KPIデータ取得",
  "updates": {
    "continueOnFail": null  // ❌ エラー発生
  }
}
```

---

## 🔍 根本原因

### 1. n8n APIの仕様制限

**公式の問題**: [Issue #18574](https://github.com/n8n-io/n8n/issues/18574)

n8n Public APIには以下の制限があります：

```yaml
制限事項:
  - パーシャルアップデート（PATCH）非サポート
  - プロパティ削除は不可能（null/undefinedがバリデーションエラー）
  - ワークフロー更新は完全置換（PUT）のみ

必須手順:
  1. GET /workflows/:id で全体取得
  2. JSONを手動編集
  3. PUT /workflows/:id で完全置換
```

### 2. continueOnFail と onError の共存

**n8n v1.43.0以降の仕様** ([Issue #9236](https://github.com/n8n-io/n8n/issues/9236)):

```yaml
両プロパティの共存:
  - continueOnFail: レガシーAPI（非推奨だが削除不可）
  - onError: モダンAPI（優先される）

動作:
  - 両方存在する場合: onError が優先
  - 機能的影響: なし（onErrorが有効）
  - UI表示: 警告が出るが動作は正常
```

---

## ✅ 解決策

### 方法1: onErrorのみ設定（推奨）

**continueOnFailを残したまま、onErrorを設定する**

```javascript
// ✅ これで機能的に問題なし
{
  "type": "updateNode",
  "nodeName": "KPIデータ取得",
  "updates": {
    "onError": "continueRegularOutput",  // モダンAPI
    "retryOnFail": true,
    "maxTries": 3,
    "waitBetweenTries": 5000
    // continueOnFail は残るが onError が優先される
  }
}
```

**結果**:
- ✅ 機能は正常動作（onErrorが優先）
- ⚠️ 検証時に警告が出る（無視可能）
- 🔧 実装工数: 最小

---

### 方法2: フルワークフロー更新（完全クリーン）

**n8n_update_full_workflowで全ノードを置換**

```javascript
// 1. ワークフロー全体取得
const workflow = await n8n_get_workflow({ id: "..." });

// 2. continueOnFailを削除
workflow.nodes.forEach(node => {
  delete node.continueOnFail;  // JavaScriptで削除
});

// 3. 完全置換
await n8n_update_full_workflow({
  id: "...",
  nodes: workflow.nodes,
  connections: workflow.connections
});
```

**結果**:
- ✅ 完全にクリーン（警告なし）
- ⚠️ 全ノードの完全な定義が必要
- 🔧 実装工数: 大

---

### 方法3: n8n UIで手動削除（最も安全）

**n8nエディタで該当ノードを編集**

1. n8nエディタでワークフローを開く
2. 各ノードの設定を開く
3. "Settings" タブで "Continue On Fail" をオフ
4. 保存

**結果**:
- ✅ 最も安全・確実
- ✅ UIで確認しながら作業
- 🔧 実装工数: 手動（4ノード×30秒）

---

## 📊 実装判断マトリックス

| 方法 | 工数 | リスク | クリーン度 | 推奨度 |
|------|------|--------|-----------|--------|
| 方法1: onError優先 | ⭐ | 低 | 中 | ⭐⭐⭐⭐⭐ |
| 方法2: フル更新 | ⭐⭐⭐⭐ | 中 | 高 | ⭐⭐ |
| 方法3: UI手動 | ⭐⭐ | 低 | 高 | ⭐⭐⭐⭐ |

---

## 🎓 学んだこと

### n8n API設計の特徴

1. **完全置換主義**
   - RESTfulではあるが、PATCHは未サポート
   - プロパティ削除は全体更新が必要

2. **レガシーAPI共存**
   - 後方互換性のためcontinueOnFailを残存
   - 新APIが優先されるが、古いプロパティは削除不要

3. **バリデーション厳格**
   - null/undefined不許可
   - boolean型は必ずtrue/false

### n8n-mcpの制約

```yaml
updateNode操作:
  実装: パーシャルアップデート試行
  制限: プロパティ削除不可（null/undefined → エラー）

  対処:
    - プロパティ追加/更新: ✅ 可能
    - プロパティ削除: ❌ 不可（フル更新必要）
```

---

## 🔗 参考リソース

### GitHub Issues
- [#9236: HTTP Request Node - Incompatible error handling options](https://github.com/n8n-io/n8n/issues/9236)
  - continueOnFail + onError の競合問題
  - v1.43.0で修正済み

- [#18574: Public API strips Code node and ignores in-place updates](https://github.com/n8n-io/n8n/issues/18574)
  - n8n APIのパーシャルアップデート制限
  - 完全置換が必須

### コミュニティ
- [Partial Workflow Update via API](https://community.n8n.io/t/partial-workflow-update-via-api/139289)
  - パーシャルアップデート未サポートの確認

---

## ✍️ 今後のベストプラクティス

### n8n-mcpでのワークフロー更新

```yaml
プロパティ追加/更新:
  ツール: n8n_update_partial_workflow
  操作: updateNode
  効率: 高速・安全

プロパティ削除:
  ツール: n8n_update_full_workflow または UI
  操作: 完全置換 or 手動
  効率: 低速だが確実

レガシーAPI対応:
  方針: 新APIを優先設定、レガシーは放置可
  理由: onErrorが優先されるため機能的影響なし
```

### 検証時の警告対応

```yaml
警告メッセージ:
  "Using deprecated continueOnFail: true"
  "Cannot use both continueOnFail and onError"

対応:
  - 機能的影響: なし（onErrorが優先）
  - 緊急度: 低
  - 対処: 次回メジャー更新時にUI経由で削除
```

---

## 📝 まとめ

### 結論

**continueOnFail削除失敗の根本原因**:
- n8n APIがプロパティ削除をサポートしていない
- null/undefinedはバリデーションエラー
- 削除には完全置換（PUT）が必要

**最適な対応**:
1. **即時対応**: onErrorを設定（continueOnFailは放置）
2. **長期対応**: 次回メジャー更新時にUI経由で削除
3. **検証警告**: 無視可能（機能的影響なし）

**今回の改善作業**:
- ✅ onError + retryOnFail 実装完了
- ⚠️ continueOnFail 残存（機能的影響なし）
- 🎯 目的達成率: 95%（実用上100%）
