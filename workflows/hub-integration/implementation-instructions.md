# MEO Operations Hub 実装手順書

**作成日**: 2025-11-05
**目的**: n8nワークフローとMEO Operations Hubの統合実装ガイド

---

## 🎯 実装の目標

散在しているNotionページとn8nワークフローを1つの統合ハブから管理・監視できるようにする。

## ✅ 実装完了項目

### 1. Hub Database作成 (完了)
- **Database ID**: `2a268d5c-2986-813c-a8e5-eba390fb71fd`
- **Database URL**: [MEO Operations Hub](https://www.notion.so/2a268d5c2986813ca8e5eba390fb71fd)
- 全必要プロパティを設定済み

### 2. 既存DB更新 (完了)
- **動画管理DB**: Hub Entryリレーション追加済み
- **note記事管理DB**: Hub Entryリレーション追加済み
- Lifecycle Stage, Last Sync Atプロパティ追加済み

### 3. 統合テンプレート作成 (完了)
- `fetch-hub-context-node.js`: Hub Context取得用
- `update-hub-status-node.js`: Hub Status更新用
- `wf7-phase1-hub-integrated.json`: Phase1統合版ワークフロー

---

## 📝 実装手順

### Step 1: n8n UIでワークフローインポート

1. n8nダッシュボードにアクセス
   ```
   https://n8n-python-production-344b.up.railway.app
   ```

2. 新規ワークフロー作成または既存ワークフロー編集

3. 設定アイコン → "Import from File"

4. 以下のファイルをインポート:
   ```
   workflows/hub-integration/wf7-phase1-hub-integrated.json
   ```

### Step 2: 既存Phase1ワークフローの更新

#### 方法A: 手動でノード追加（推奨）

1. **Fetch Hub Context ノード追加**
   - 位置: "入力データ整形"の直後
   - タイプ: Code Node
   - コード: `fetch-hub-context-node.js`の内容をコピー

2. **既存Notionノードを更新**
   - "Notionペイロード作成" → "Update Hub Status"に変更
   - コード: `update-hub-status-node.js`のPhase1部分を使用

3. **Notion API呼び出しを更新**
   - HTTPメソッド: POST → PATCH
   - URL: `https://api.notion.com/v1/pages/{{ $json.hubPageId }}`

#### 方法B: 完全置換

1. 既存ワークフローをバックアップ（Export）
2. Hub統合版をインポート
3. Webhook URLを確認・更新

### Step 3: Phase2-5の統合

各Phaseに対して以下を実施：

#### Phase2 (素材取得)
```javascript
// Update Hub Statusノードに追加
const phaseName = 'Phase2';
updatePayload.properties['Assets JSON'] = {
  url: `https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase2-assets-google?articleId=${articleId}`
};
updatePayload.properties['Workflow Status'] = {
  select: { name: 'AssetsReady' }
};
```

#### Phase3 (音声・字幕)
```javascript
const phaseName = 'Phase3';
updatePayload.properties['Voice URL'] = {
  url: voiceUrl
};
updatePayload.properties['Subtitle URL'] = {
  url: subtitleUrl
};
updatePayload.properties['Workflow Status'] = {
  select: { name: 'NarrationReady' }
};
```

#### Phase4 (レンダリング)
```javascript
const phaseName = 'Phase4';
updatePayload.properties['Render URL'] = {
  url: videoUrl
};
updatePayload.properties['Thumbnail URL'] = {
  url: thumbnailUrl
};
updatePayload.properties['Workflow Status'] = {
  select: { name: 'Rendered' }
};
```

#### Phase5 (配信)
```javascript
const phaseName = 'Phase5';
updatePayload.properties['Channel'] = {
  multi_select: channels.map(ch => ({ name: ch }))
};
updatePayload.properties['Workflow Status'] = {
  select: { name: 'Distributed' }
};
```

---

## 🔍 検証方法

### 1. 単体テスト

各Phaseワークフローで以下を確認：

```bash
# Webhook呼び出しテスト
curl -X POST https://n8n-python-production-344b.up.railway.app/webhook/wf7-phase1-video-script \
  -H "Content-Type: application/json" \
  -d '{
    "articleId": "test-001",
    "title": "テスト記事",
    "keyPoints": ["ポイント1", "ポイント2"]
  }'
```

期待される結果：
- Hub DBに新規エントリ作成
- ステータスが適切に更新
- エラーログが記録されない

### 2. 統合テスト

1. **新規記事処理フロー**
   - Article IDを新規発行
   - Phase1-5を順番に実行
   - Hub DBでステータス遷移を確認

2. **エラーリカバリテスト**
   - Phase3でエラーを発生させる
   - Hub DBのError Logを確認
   - 修正後の再実行を検証

### 3. Hub DBビューでの確認

Notionで以下のビューを確認：

- **Kanbanビュー**: ステータス別に記事が表示
- **Tableビュー**: 全プロパティが正しく更新
- **Error Inboxビュー**: Failed状態のエントリのみ表示

---

## ⚠️ 注意事項

### API制限
- Notion API: 3リクエスト/秒
- 大量処理時は適切な遅延を設定

### エラーハンドリング
- 各Phaseでtry-catchを実装
- エラー時はHub DBのError Logに記録
- ステータスを"Failed"に更新

### Webhook設定
- 必ず新しいインスタンスURLを使用
- 古いURL: ~~primary-production-cb87.up.railway.app~~
- 新URL: **n8n-python-production-344b.up.railway.app**

---

## 🚀 次のアクション

1. [ ] Phase2-5の統合実装
2. [ ] LINE配信フローとの連携
3. [ ] 自動化トリガーの設定
4. [ ] ダッシュボード作成
5. [ ] 本番環境でのテスト

---

## 📚 参考資料

- [MEO Operations Hub 再設計計画書](../meo-operations-hub-redesign-plan.md)
- [n8n-Notion統合ガイド](../n8n-notion-hub-integration.md)
- [Hub統合テンプレート](./README.md)

---

**最終更新**: 2025-11-05