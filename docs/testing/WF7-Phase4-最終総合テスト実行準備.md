# WF7 Phase4 最終総合テスト実行準備

**作成日**: 2025-11-09  
**目的**: Phase4b修正後の統合テストを実行するための準備手順

---

## 📋 現在の状況

### ✅ 完了済み
- Phase4bワークフロー（`wHaKi98mTlUvFIOR`）の単体テスト成功
- 修正済みワークフローファイル（`wf7_phase4b_fixed_r9Sp5n0mkUCcH8cw.json`）の作成完了
- `Execute Sub-workflow - Phase4b`ノードの設定確認完了

### ⏸️ 実施待ち
- 修正済みワークフローのn8nへのアップロード
- Phase4a → Phase4b → Phase4cの統合テスト実行

---

## 🔧 ステップ1: 修正済みワークフローのアップロード

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

4. **確認項目**
   - ✅ `Execute Sub-workflow - Phase4b` ノードが存在する
   - ✅ ワークフローID: `wHaKi98mTlUvFIOR` が設定されている
   - ✅ データマッピング設定:
     - `script_id`: `={{ $('Set - Phase4a Payload New').item.json.script_id }}`
     - `slides_metadata`: `={{ $('Set - Phase4a Payload New').item.json.slides_metadata }}`
   - ✅ `HTTP Request - Call Phase4b` ノードが削除されている

5. **ワークフローを保存**
   - 「Save」をクリック
   - ワークフロー名が「WF7 Phase4 - V3 with Execute Sub-workflow Phase4b」に更新されていることを確認

6. **ワークフローをアクティブ化**
   - 右上のトグルスイッチをONにしてアクティブ化

---

## 🧪 ステップ2: 統合テストの実行

### 前提条件チェック

- [ ] n8n UIにアクセス可能
- [ ] 親ワークフローID `r9Sp5n0mkUCcH8cw` が存在し、アクティブ
- [ ] Phase4bワークフローID `wHaKi98mTlUvFIOR` が存在し、アクティブ
- [ ] FAL API認証情報が設定済み
- [ ] Google Drive OAuth2認証が設定済み
- [ ] Notion API認証が設定済み

### テスト実行

**方法1: スクリプトを使用（推奨）**
```bash
cd /Users/yuichiroooosuger/Desktop/n8n-workflows
./test-phase4b-fixed-e2e.sh
```

**方法2: curlコマンドを直接実行**
```bash
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-video-script \
  -H "Content-Type: application/json" \
  -d '{
    "notionPageId": "2a068d5c-2986-81a3-ab0c-ff0bc1e4ebb9"
  }'
```

---

## ✅ 確認項目

### Phase4a実行確認
- ✅ Phase4aが正常に実行され、7枚のスライドが生成される
- ✅ `slides_metadata`に7要素が含まれている
- ✅ `slides_count: 7`が正しく設定された
- ✅ `phase4a_success: true`が設定された

### Phase4b実行確認
- ✅ Phase4bがExecute Sub-workflowで正常に呼び出される
- ✅ Phase4bが正常に実行され、7本の動画が生成される
- ✅ `videos_metadata`に7要素が含まれている
- ✅ `videos_count: 7`が正しく設定された
- ✅ `phase4b_success: true`が設定された

### Phase4c実行確認
- ✅ Phase4cが正常に実行され、1本の完成動画が生成される
- ✅ Google Driveに最終動画がアップロードされる
- ✅ Notion DBが正しく更新される（Status: `Rendered`, Video URL設定）

### 最終確認
- ✅ Webhook応答が成功を返す
- ✅ 実行ログにエラーがない
- ✅ 全フェーズが正常に完了している

---

## 📊 テスト結果の記録

テスト実行後、以下の情報を記録してください：

1. **実行ID**: n8n実行ログから取得
2. **実行時間**: 各フェーズの処理時間
3. **エラー**: 発生したエラーがあれば記録
4. **Google Drive**: 最終動画のURL
5. **Notion**: 更新後のステータスとVideo URL

---

## 🔗 関連ドキュメント

- `/docs/testing/WF7-Phase4-最終総合テスト計画書.md`: 詳細なテスト計画
- `/docs/testing/WF7-Phase4b-修正後アップロード手順.md`: アップロード手順
- `/test-phase4b-fixed-e2e.sh`: テスト実行スクリプト

---

**作成者**: Claude Code (Composer)  
**更新日**: 2025-11-09  
**次のステップ**: ワークフローをアップロード後、統合テストを実行

