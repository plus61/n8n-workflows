# Notionページへの手動データ設定ガイド

## 📋 手順1: Notionページを開く

### 既存のテストページを使用する場合
1. ブラウザで以下のURLを開く：
   ```
   https://www.notion.so/2a068d5c298681a3ab0cff0bc1e4ebb9
   ```
   または
   ```
   https://www.notion.so/ページタイトル-2a068d5c298681a3ab0cff0bc1e4ebb9
   ```

### 新しいページを作成する場合
1. Notionで新しいページを作成
2. ページのURLからページIDを取得（URLの最後の部分）

---

## 📝 手順2: プロパティを追加/編集

### プロパティが存在しない場合

1. **ページの上部にある「Add a property」をクリック**
   - または、ページの右上の「...」メニューから「Properties」を選択

2. **以下の3つのプロパティを追加**：

   #### プロパティ1: Script JSON
   - **名前**: `Script JSON`
   - **タイプ**: `Text` または `Rich text` を選択
   - **追加**をクリック

   #### プロパティ2: Assets JSON
   - **名前**: `Assets JSON`
   - **タイプ**: `Text` または `Rich text` を選択
   - **追加**をクリック

   #### プロパティ3: Article ID
   - **名前**: `Article ID`
   - **タイプ**: `Text` または `Rich text` を選択
   - **追加**をクリック

---

## ✏️ 手順3: データを入力

### Script JSON プロパティに以下をコピー＆ペースト：

```json
{
  "segments": [
    {"duration": 5, "telop": "テスト動画1"},
    {"duration": 5, "telop": "テスト動画2"},
    {"duration": 5, "telop": "テスト動画3"}
  ]
}
```

**重要**: JSON全体を1行で入力するか、またはそのままコピー＆ペーストしてください。

---

### Assets JSON プロパティに以下をコピー＆ペースト：

```json
{
  "assets": [
    {"driveFileId": "1t3BFRFgHMLYhmfp9BobiNhdK3DlUhUaC", "assetTag": "test_asset_1"},
    {"driveFileId": "1qyNTS3pX21H_EM6myRt9cvMBM5G1RDf7", "assetTag": "test_asset_2"},
    {"driveFileId": "1d4PlR2_JcXvLXVB38jyU5zdzbAE-KgQd", "assetTag": "test_asset_3"}
  ]
}
```

**重要**: JSON全体を1行で入力するか、またはそのままコピー＆ペーストしてください。

---

### Article ID プロパティに以下を入力：

```
test-phase4-001
```

---

## ✅ 手順4: 設定の確認

設定後、ページのプロパティセクションで以下が表示されていることを確認：

- ✅ **Script JSON**: JSONデータが表示されている
- ✅ **Assets JSON**: JSONデータが表示されている
- ✅ **Article ID**: `test-phase4-001` が表示されている

---

## 🚀 手順5: テスト実行

データ設定が完了したら、以下のコマンドでテストを実行：

```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-video-script \
  -H "Content-Type: application/json" \
  -d '{"notionPageId": "2a068d5c-2986-81a3-ab0c-ff0bc1e4ebb9"}'
```

**新しいページを作成した場合**は、上記の`notionPageId`を実際のページIDに置き換えてください。

---

## 📸 スクリーンショット参考

### プロパティの追加方法
1. ページ上部の「Add a property」ボタンをクリック
2. プロパティ名を入力
3. プロパティタイプを選択（Text または Rich text）
4. 「Add」をクリック

### データ入力方法
1. プロパティのフィールドをクリック
2. JSONデータをコピー＆ペースト
3. Enterキーを押すか、フィールド外をクリックして保存

---

## ⚠️ よくある問題

### 問題1: プロパティが見つからない
**解決策**: ページの右上の「...」メニュー → 「Properties」からプロパティを追加

### 問題2: JSONが正しく保存されない
**解決策**: 
- JSON全体を1行で入力する
- または、コードブロック（```）を使わずに直接入力

### 問題3: プロパティタイプが違う
**解決策**: 
- `Text` または `Rich text` タイプを使用
- `URL` タイプは使用しない（ワークフローはRich textからも読み取れます）

---

## 📞 次のステップ

データ設定が完了したら、テストを実行して結果を確認してください。






