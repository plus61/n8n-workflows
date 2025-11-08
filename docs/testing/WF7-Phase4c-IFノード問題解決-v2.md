# WF7 Phase4c IFノード問題解決（詳細版）

**作成日**: 2025-11-08  
**問題**: `IF - Phase4b Success Check`ノードが動かない（修正後も動かない）

---

## 🔍 詳細な問題分析

### 問題1: Set - Phase4b PayloadノードのarticleId参照

`Set - Phase4b Payload`ノードの設定を確認すると：

```json
{
  "name": "articleId",
  "value": "={{ $('Set - Phase4a Payload New').item.json.articleId }}",
  "type": "string"
}
```

Pin Dataを`Set - Phase4b Payload`ノードに設定した場合、前のノード（`Set - Phase4a Payload New`）は実行されていないため、この参照が失敗する可能性があります。

### 問題2: IFノードの条件評価

`IF - Phase4b Success Check`ノードの条件：
- `phase4b_success` が `true` であること
- `videos_count` が `7` であること

両方の条件が満たされていても、`Set - Phase4b Payload`ノードがエラーで停止している可能性があります。

---

## ✅ 解決方法

### 方法1: Set - Phase4b PayloadノードのarticleId設定を修正

`Set - Phase4b Payload`ノードの`articleId`設定を、Pin Dataから直接取得するように変更：

**修正前**:
```json
{
  "name": "articleId",
  "value": "={{ $('Set - Phase4a Payload New').item.json.articleId }}",
  "type": "string"
}
```

**修正後**:
```json
{
  "name": "articleId",
  "value": "={{ $json.articleId }}",
  "type": "string"
}
```

### 方法2: Set - Phase4a Payload NewノードにもPin Dataを設定

`Set - Phase4a Payload New`ノードにもPin Dataを設定して、`articleId`を参照できるようにする。

---

## 🚀 推奨される解決方法

**方法1を推奨**：`Set - Phase4b Payload`ノードの`articleId`設定を修正する方が簡単です。

### 修正手順

1. n8n UIで `Set - Phase4b Payload` ノードを開く
2. **"Assignments"** セクションで `articleId` フィールドを探す
3. 値を `={{ $('Set - Phase4a Payload New').item.json.articleId }}` から `={{ $json.articleId }}` に変更
4. **"Save"** をクリック

### 修正後のPin Data（変更なし）

```json
[
  {
    "json": {
      "script_id": "test-script-phase4c-001",
      "articleId": "test-article-001",
      "success": true,
      "phase4b_success": true,
      "videos_count": 7,
      "total_duration": 80,
      "videos_metadata": [
        {
          "section": "hook",
          "duration": 3,
          "video_url": "https://v3b.fal.media/files/b/penguin/X6YpaYnUTrgdaoUwG1RpN_output.mp4"
        },
        {
          "section": "intro",
          "duration": 10,
          "video_url": "https://v3b.fal.media/files/b/rabbit/W0yXmayD3qLoY9pCzcZGr_output.mp4"
        },
        {
          "section": "point1",
          "duration": 13,
          "video_url": "https://v3b.fal.media/files/b/penguin/X6YpaYnUTrgdaoUwG1RpN_output.mp4"
        },
        {
          "section": "point2",
          "duration": 13,
          "video_url": "https://v3b.fal.media/files/b/rabbit/W0yXmayD3qLoY9pCzcZGr_output.mp4"
        },
        {
          "section": "point3",
          "duration": 14,
          "video_url": "https://v3b.fal.media/files/b/penguin/X6YpaYnUTrgdaoUwG1RpN_output.mp4"
        },
        {
          "section": "summary",
          "duration": 20,
          "video_url": "https://v3b.fal.media/files/b/rabbit/W0yXmayD3qLoY9pCzcZGr_output.mp4"
        },
        {
          "section": "cta",
          "duration": 7,
          "video_url": "https://v3b.fal.media/files/b/penguin/X6YpaYnUTrgdaoUwG1RpN_output.mp4"
        }
      ]
    }
  }
]
```

---

## 🔍 デバッグ手順

### Step 1: Set - Phase4b Payloadノードの実行結果を確認

1. `Set - Phase4b Payload`ノードをクリック
2. 出力パネルで実行結果を確認
3. 以下のフィールドが正しく設定されているか確認：
   - ✅ `script_id`: "test-script-phase4c-001"
   - ✅ `articleId`: "test-article-001"（エラーが出ていないか確認）
   - ✅ `phase4b_success`: true
   - ✅ `videos_count`: 7
   - ✅ `videos_metadata`: 配列が正しく設定されている

### Step 2: IF - Phase4b Success Checkノードの実行結果を確認

1. `IF - Phase4b Success Check`ノードをクリック
2. 出力パネルで実行結果を確認
3. True分岐（上側）にデータが流れているか確認
4. False分岐（下側）にデータが流れていないか確認

### Step 3: エラーメッセージを確認

1. 各ノードに赤いエラー表示がないか確認
2. エラーメッセージの内容を確認
3. 特に`Set - Phase4b Payload`ノードのエラーを確認

---

## 📝 チェックリスト

- [ ] `Set - Phase4b Payload`ノードの`articleId`設定が `={{ $json.articleId }}` になっている
- [ ] Pin Dataに `success: true` が含まれている
- [ ] Pin Dataに `videos_count: 7` が含まれている
- [ ] Pin Dataに `articleId` が含まれている
- [ ] `Set - Phase4b Payload`ノードの実行結果でエラーが出ていない
- [ ] `Set - Phase4b Payload`ノードの出力で `phase4b_success: true` が設定されている
- [ ] `IF - Phase4b Success Check`ノードがTrue分岐に進んでいる

---

## 🔗 関連ファイル

- `test-phase4b-pindata-for-phase4c.json`: Pin Dataファイル
- `docs/testing/WF7-Phase4c-IFノード問題解決.md`: 初版の問題解決ドキュメント
- `workflows/wf7_phase4b_fixed_r9Sp5n0mkUCcH8cw.json`: ワークフローJSON

---

**作成者**: Claude Code (Composer)  
**更新日**: 2025-11-08

