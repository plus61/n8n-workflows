# WF7 Phase4b修正後ワークフローアップロード手順

**作成日**: 2025-11-09  
**対象ワークフロー**: `r9Sp5n0mkUCcH8cw`  
**ワークフローファイル**: `workflows/wf7_phase4b_fixed_r9Sp5n0mkUCcH8cw.json`

---

## 📋 アップロード手順

### 方法1: n8n UIでインポート（推奨）

1. **n8n UIにアクセス**
   - URL: `https://n8n-python-production-344b.up.railway.app/`
   - ログイン

2. **既存ワークフローを開く**
   - ワークフロー一覧から `WF7 Phase4 - V3 Fixed_final` (ID: `r9Sp5n0mkUCcH8cw`) を開く

3. **ワークフローをインポート**
   - 右上の「⋮」メニューから「Import from File」を選択
   - `workflows/wf7_phase4b_fixed_r9Sp5n0mkUCcH8cw.json` を選択
   - 「Import」をクリック

4. **ワークフローを保存**
   - 「Save」をクリック
   - ワークフロー名が「WF7 Phase4 - V3 with Execute Sub-workflow Phase4b」に更新されていることを確認

5. **ワークフローをアクティブ化**
   - 右上のトグルスイッチをONにしてアクティブ化

### 方法2: 手動で更新

1. **Execute Sub-workflowノードの確認**
   - `Execute Sub-workflow - Phase4b` ノードが存在することを確認
   - ワークフローIDが `wHaKi98mTlUvFIOR` に設定されていることを確認

2. **データマッピングの確認**
   - `script_id`: `={{ $('Set - Phase4a Payload New').item.json.script_id }}`
   - `slides_metadata`: `={{ $('Set - Phase4a Payload New').item.json.slides_metadata }}`

3. **HTTP Requestノードの削除**
   - `HTTP Request - Call Phase4b` ノードが存在する場合は削除

4. **接続の確認**
   - `IF - Phase4a Success Check` → `Execute Sub-workflow - Phase4b` に接続されていることを確認
   - `Execute Sub-workflow - Phase4b` → `Set - Phase4b Payload` に接続されていることを確認

---

## ✅ 確認項目

### 修正内容の確認

- ✅ `Execute Sub-workflow - Phase4b` ノードが存在する
- ✅ ワークフローID: `wHaKi98mTlUvFIOR` が設定されている
- ✅ データマッピングが正しく設定されている
- ✅ `HTTP Request - Call Phase4b` ノードが削除されている（存在しない）
- ✅ 接続が正しく設定されている

### ワークフローの状態確認

- ✅ ワークフローがアクティブになっている
- ✅ エラーがない
- ✅ すべてのノードが正しく接続されている

---

## 🧪 テスト実行

アップロード後、以下のコマンドでテストを実行します：

```bash
./test-phase4b-fixed-e2e.sh
```

または、curlコマンドで直接実行：

```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-video-script \
  -H "Content-Type: application/json" \
  -d '{
    "notionPageId": "2a068d5c-2986-81a3-ab0c-ff0bc1e4ebb9"
  }'
```

---

## 📊 テスト結果の確認

1. **n8n UIで実行ログを確認**
   - ワークフロー実行履歴を確認
   - 各ノードの実行状況を確認

2. **確認ポイント**
   - Phase4aが正常に実行され、7枚のスライドが生成される
   - Phase4bがExecute Sub-workflowで正常に呼び出される
   - Phase4bが正常に実行され、7本の動画が生成される
   - Phase4cが正常に実行され、1本の完成動画が生成される
   - Google Driveに最終動画がアップロードされる
   - Notion DBが正しく更新される

---

**作成者**: AI Assistant (Claude Sonnet 4.5)  
**最終更新**: 2025-11-09




