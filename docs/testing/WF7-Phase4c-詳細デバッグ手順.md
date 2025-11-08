# WF7 Phase4c 詳細デバッグ手順

**作成日**: 2025-11-08  
**問題**: Pin Dataを設定して実行したが、`IF - Phase4b Success Check`ノードが反応しない

---

## 🔍 Step-by-Step デバッグ手順

### Step 1: Set - Phase4b Payloadノードの実行結果を確認

1. n8n UIで `Set - Phase4b Payload` ノードをクリック
2. **"Output"** パネル（または実行結果パネル）を開く
3. 以下の情報を確認してください：

**確認項目**:
- ✅ ノードが正常に実行されているか（エラーがないか）
- ✅ 出力データに以下のフィールドが含まれているか：
  - `script_id`: "test-script-phase4c-001"
  - `articleId`: "test-article-001"
  - `phase4b_success`: **true**（boolean型、文字列ではない）
  - `videos_count`: **7**（number型、文字列ではない）
  - `videos_metadata`: 配列が正しく設定されている

**エラーが出ている場合**:
- エラーメッセージの内容を教えてください
- 特に `articleId` の参照エラーがないか確認

**出力データの確認方法**:
- 出力パネルでJSONデータを確認
- `phase4b_success` の値が `true`（boolean）であることを確認
- `videos_count` の値が `7`（number）であることを確認

---

### Step 2: IF - Phase4b Success Checkノードの実行結果を確認

1. `IF - Phase4b Success Check` ノードをクリック
2. **"Output"** パネルを開く
3. 以下の情報を確認してください：

**確認項目**:
- ✅ True分岐（上側の出力）にデータが流れているか
- ✅ False分岐（下側の出力）にデータが流れているか
- ✅ どちらの分岐にもデータが流れていないか

**True分岐にデータが流れていない場合**:
- `Set - Phase4b Payload` ノードの出力を再確認
- `phase4b_success` の値が `true`（boolean）であることを確認
- `videos_count` の値が `7`（number）であることを確認

---

### Step 3: データ型の確認（重要）

n8nでは、データ型が非常に重要です。以下の点を確認してください：

#### boolean型の確認

`phase4b_success` が `true`（boolean型）である必要があります：
- ✅ 正しい: `true`（引用符なし）
- ❌ 間違い: `"true"`（文字列）

#### number型の確認

`videos_count` が `7`（number型）である必要があります：
- ✅ 正しい: `7`（引用符なし）
- ❌ 間違い: `"7"`（文字列）

#### 確認方法

`Set - Phase4b Payload` ノードの出力パネルで、データの型を確認：
- 値の表示が `true` か `"true"` か
- 値の表示が `7` か `"7"` か

---

### Step 4: Pin Dataの形式を再確認

Pin Dataが正しい形式であることを確認：

```json
[
  {
    "json": {
      "script_id": "test-script-phase4c-001",
      "articleId": "test-article-001",
      "success": true,           // ← boolean型（引用符なし）
      "phase4b_success": true,   // ← boolean型（引用符なし）
      "videos_count": 7,         // ← number型（引用符なし）
      "total_duration": 80,      // ← number型（引用符なし）
      "videos_metadata": [
        {
          "section": "hook",
          "duration": 3,
          "video_url": "https://v3b.fal.media/files/b/penguin/X6YpaYnUTrgdaoUwG1RpN_output.mp4"
        },
        // ... 残りの6本の動画
      ]
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

### Step 5: ノードの接続を確認

1. `Set - Phase4b Payload` ノードから `IF - Phase4b Success Check` ノードへの接続線が表示されているか確認
2. 接続線が正しく設定されているか確認

---

## 🛠️ よくある問題と解決方法

### 問題1: データ型の不一致

**症状**: `IF - Phase4b Success Check`ノードの条件が正しく評価されない

**原因**: boolean値やnumber値が文字列として扱われている

**解決方法**: 
- Pin Dataでboolean値は `true`（引用符なし）
- number値は `7`（引用符なし）
- `Set - Phase4b Payload`ノードの出力でデータ型を確認

### 問題2: Set - Phase4b Payloadノードが実行されていない

**症状**: `IF - Phase4b Success Check`ノードにデータが流れない

**原因**: `Set - Phase4b Payload`ノードがエラーで停止している

**解決方法**: 
- `Set - Phase4b Payload`ノードのエラーメッセージを確認
- 特に `articleId` の参照エラーがないか確認

### 問題3: Pin Dataの形式が間違っている

**症状**: ノードが実行されない、またはデータが正しく渡されない

**原因**: Pin Dataの形式が正しくない

**解決方法**: 
- 外側を配列 `[]` で囲む
- 各アイテムを `{"json": {...}}` の形式にする

---

## 📝 確認チェックリスト

以下の項目を順番に確認してください：

- [ ] `Set - Phase4b Payload`ノードが正常に実行されている
- [ ] `Set - Phase4b Payload`ノードの出力にエラーがない
- [ ] `Set - Phase4b Payload`ノードの出力で `phase4b_success: true`（boolean型）が設定されている
- [ ] `Set - Phase4b Payload`ノードの出力で `videos_count: 7`（number型）が設定されている
- [ ] `IF - Phase4b Success Check`ノードがTrue分岐に進んでいる
- [ ] Pin Dataの形式が正しい（配列形式、boolean/number型が正しい）
- [ ] ノード間の接続が正しく設定されている

---

## 💡 次のステップ

上記の確認を行った後、以下の情報を教えてください：

1. **`Set - Phase4b Payload`ノードの出力データ**:
   - `phase4b_success` の値と型
   - `videos_count` の値と型
   - エラーメッセージがあれば内容

2. **`IF - Phase4b Success Check`ノードの出力**:
   - True分岐にデータが流れているか
   - False分岐にデータが流れているか
   - どちらの分岐にもデータが流れていないか

3. **エラーメッセージ**:
   - どのノードでエラーが発生しているか
   - エラーメッセージの内容

この情報があれば、より具体的な解決方法を提案できます。

---

**作成者**: Claude Code (Composer)  
**更新日**: 2025-11-08

