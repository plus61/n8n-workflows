# WF7 Phase4c デバッグ手順

**作成日**: 2025-11-08  
**問題**: `IF - Phase4b Success Check`ノードが動かない

---

## 🔍 問題の原因を特定する手順

### Step 1: Set - Phase4b Payloadノードの実行結果を確認

1. n8n UIで `Set - Phase4b Payload` ノードをクリック
2. **"Output"** パネル（または実行結果パネル）を開く
3. 以下の情報を確認：

**確認項目**:
- ✅ ノードが正常に実行されているか（エラーがないか）
- ✅ 出力データに以下のフィールドが含まれているか：
  - `script_id`
  - `articleId`
  - `phase4b_success`
  - `videos_count`
  - `videos_metadata`

**エラーが出ている場合**:
- エラーメッセージの内容を確認
- 特に `articleId` の参照エラーがないか確認
  - `Set - Phase4a Payload New` を参照しようとしてエラーになっている可能性があります

### Step 2: IF - Phase4b Success Checkノードの実行結果を確認

1. `IF - Phase4b Success Check` ノードをクリック
2. **"Output"** パネルを開く
3. 以下の情報を確認：

**確認項目**:
- ✅ True分岐（上側の出力）にデータが流れているか
- ✅ False分岐（下側の出力）にデータが流れているか
- ✅ 条件が正しく評価されているか

**True分岐にデータが流れていない場合**:
- `Set - Phase4b Payload` ノードの出力を確認
- `phase4b_success` の値が `true` であることを確認
- `videos_count` の値が `7` であることを確認

### Step 3: データ型の確認

n8nでは、データ型が重要です。以下の点を確認してください：

1. **boolean型**: `phase4b_success` が `true`（boolean）であること
   - `"true"`（文字列）ではなく `true`（boolean）である必要があります

2. **number型**: `videos_count` が `7`（number）であること
   - `"7"`（文字列）ではなく `7`（number）である必要があります

### Step 4: Pin Dataの形式を再確認

Pin Dataが正しい形式であることを確認：

```json
[
  {
    "json": {
      "script_id": "test-script-phase4c-001",
      "articleId": "test-article-001",
      "success": true,           // ← boolean型（文字列ではない）
      "phase4b_success": true,   // ← boolean型（文字列ではない）
      "videos_count": 7,         // ← number型（文字列ではない）
      "total_duration": 80,       // ← number型（文字列ではない）
      "videos_metadata": [...]
    }
  }
]
```

**重要なポイント**:
- 外側は配列 `[]` で囲む
- 各アイテムは `{"json": {...}}` の形式
- boolean値は `true`/`false`（引用符なし）
- number値は `7`/`80`（引用符なし）

---

## 🛠️ よくある問題と解決方法

### 問題1: articleIdの参照エラー

**症状**: `Set - Phase4b Payload`ノードでエラーが発生

**原因**: `articleId`が`Set - Phase4a Payload New`を参照しようとしているが、Pin Dataを設定した場合、前のノードは実行されていない

**解決方法**: 
1. `Set - Phase4b Payload`ノードの`articleId`設定を `={{ $json.articleId }}` に変更
2. または、`Set - Phase4a Payload New`ノードにもPin Dataを設定

### 問題2: データ型の不一致

**症状**: `IF - Phase4b Success Check`ノードの条件が正しく評価されない

**原因**: boolean値やnumber値が文字列として扱われている

**解決方法**: 
- Pin Dataでboolean値は `true`（引用符なし）
- number値は `7`（引用符なし）

### 問題3: Pin Dataの形式が間違っている

**症状**: ノードが実行されない、またはデータが正しく渡されない

**原因**: Pin Dataの形式が正しくない

**解決方法**: 
- 外側を配列 `[]` で囲む
- 各アイテムを `{"json": {...}}` の形式にする

---

## 📝 デバッグチェックリスト

- [ ] `Set - Phase4b Payload`ノードが正常に実行されている
- [ ] `Set - Phase4b Payload`ノードの出力にエラーがない
- [ ] `Set - Phase4b Payload`ノードの出力で `phase4b_success: true` が設定されている
- [ ] `Set - Phase4b Payload`ノードの出力で `videos_count: 7` が設定されている
- [ ] `IF - Phase4b Success Check`ノードがTrue分岐に進んでいる
- [ ] Pin Dataの形式が正しい（配列形式、boolean/number型が正しい）

---

## 🔗 関連ファイル

- `test-phase4b-pindata-for-phase4c.json`: Pin Dataファイル
- `docs/testing/WF7-Phase4c-IFノード問題解決.md`: 初版の問題解決ドキュメント
- `docs/testing/WF7-Phase4c-IFノード問題解決-v2.md`: 詳細版の問題解決ドキュメント

---

**作成者**: Claude Code (Composer)  
**更新日**: 2025-11-08




