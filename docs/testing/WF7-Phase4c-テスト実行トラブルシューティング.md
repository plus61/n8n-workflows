# WF7 Phase4c テスト実行トラブルシューティング

**作成日**: 2025-11-08  
**問題**: Pin Dataを設定して`Code - Phase4c FFmpeg Concat`を実行したが、次のノードで反応がない

---

## 🐛 問題の原因

`Code - Phase4c FFmpeg Concat`ノードは`mode: "runOnceForAllItems"`に設定されています。このモードでは、**すべてのアイテムを一度に処理**する必要があります。

Pin Dataで単一のアイテムを設定して実行した場合、次のノードにデータが正しく渡されない可能性があります。

---

## ✅ 解決方法

### 方法1: Pin Dataの形式を確認する

Pin Dataは**配列形式**である必要があります。以下の形式を確認してください：

```json
[
  {
    "json": {
      "script_id": "test-script-phase4c-001",
      "articleId": "test-article-001",
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

**重要**: 
- 外側は**配列** `[]` で囲む必要があります
- 各アイテムは `{"json": {...}}` の形式である必要があります

### 方法2: 前のノードからPin Dataを設定する

`Code - Phase4c FFmpeg Concat`ノードに直接Pin Dataを設定するのではなく、**前のノード**（`IF - Phase4b Success Check`または`Set - Phase4b Payload`）にPin Dataを設定して、ワークフロー全体を実行する方法を試してください。

#### Step 1: Set - Phase4b Payloadノードを開く

1. ワークフローエディタで **"Set - Phase4b Payload"** ノードを探す
2. ノードをクリックして選択
3. 右側の設定パネルが表示されることを確認

#### Step 2: Pin Dataを設定

1. 設定パネルで **"Pin Data"** タブを選択
2. 以下の形式でPin Dataを設定:

```json
[
  {
    "json": {
      "script_id": "test-script-phase4c-001",
      "articleId": "test-article-001",
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

3. **"Save"** をクリックしてPin Dataを保存

#### Step 3: ワークフロー全体を実行

1. 右上の **"Execute Workflow"** ボタンをクリック
2. または、`Set - Phase4b Payload`ノードから **"Execute Node"** をクリックして、後続のノードも実行されるようにする

### 方法3: ノードの実行結果を確認する

`Code - Phase4c FFmpeg Concat`ノードを実行した後、以下の点を確認してください：

1. **実行結果が表示されているか**
   - ノードの出力パネルで実行結果が表示されているか確認
   - `success: true` が返されているか確認

2. **エラーメッセージがないか**
   - ノードに赤いエラー表示がないか確認
   - エラーメッセージの内容を確認

3. **次のノードへの接続が正しいか**
   - `Code - Phase4c FFmpeg Concat`から`Code - Read Video Binary`への接続が正しく設定されているか確認
   - ノード間の接続線が表示されているか確認

---

## 🔍 デバッグ手順

### Step 1: ノードの実行結果を確認

1. `Code - Phase4c FFmpeg Concat`ノードをクリック
2. 出力パネルで実行結果を確認
3. 以下のフィールドが存在するか確認:
   - `success: true`
   - `output_video_path`
   - `output_video_size`
   - `total_duration`

### Step 2: 次のノードを手動で実行

1. `Code - Read Video Binary`ノードをクリック
2. **"Execute Node"** ボタンをクリック
3. エラーが発生するか確認

### Step 3: Pin Dataの形式を再確認

1. `Code - Phase4c FFmpeg Concat`ノードのPin Dataを確認
2. 配列形式 `[]` で囲まれているか確認
3. 各アイテムが `{"json": {...}}` の形式か確認

---

## ⚠️ よくあるエラー

### エラー1: "動画数が不正です"

**原因**: `videos_metadata`の配列の長さが7ではない

**解決方法**:
- `videos_metadata`配列に7本の動画が含まれているか確認
- 各動画に`section`, `duration`, `video_url`が設定されているか確認

### エラー2: "動画URL未設定"

**原因**: `video_url`が設定されていない

**解決方法**:
- 各動画の`video_url`が正しく設定されているか確認
- URLが有効か確認（ブラウザで直接アクセスできるか）

### エラー3: "動画ダウンロード失敗"

**原因**: 動画URLが無効、またはネットワークエラー

**解決方法**:
- 動画URLが有効か確認
- 動画URLに直接アクセスできるか確認
- ネットワーク接続を確認

### エラー4: "FFmpeg結合失敗"

**原因**: FFmpegがインストールされていない、または動画ファイルの形式が異なる

**解決方法**:
- n8nサーバーでFFmpegがインストールされているか確認
- 動画ファイルの形式を確認（MP4形式であることを確認）

---

## 📝 チェックリスト

- [ ] Pin Dataが配列形式 `[]` で囲まれている
- [ ] 各アイテムが `{"json": {...}}` の形式である
- [ ] `videos_metadata`配列に7本の動画が含まれている
- [ ] 各動画に`section`, `duration`, `video_url`が設定されている
- [ ] 動画URLが有効である（ブラウザで直接アクセスできる）
- [ ] `Code - Phase4c FFmpeg Concat`ノードの実行結果が表示されている
- [ ] エラーメッセージがない
- [ ] 次のノードへの接続が正しく設定されている

---

## 🔗 関連ドキュメント

- `docs/testing/WF7-Phase4c-テスト実行ガイド.md`: テスト実行ガイド
- `docs/testing/WF7-Phase4c-テスト実行手順.md`: 詳細なテスト実行手順
- `test-phase4c-pindata.json`: Pin Data用のテストデータ

---

**作成者**: Claude Code (Composer)  
**更新日**: 2025-11-08




