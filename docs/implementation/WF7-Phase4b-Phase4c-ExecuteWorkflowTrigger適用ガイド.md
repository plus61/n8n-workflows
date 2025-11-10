# Phase4b/Phase4c Execute Workflow Trigger適用ガイド

Phase4aで実施した改善をPhase4bとPhase4cにも適用するための手順書です。

## 📋 改善内容の概要

Phase4aで実施した改善により、親ワークフロー（Orchestrator）からExecute Workflow経由で呼び出された際に、正しくデータを受け取れるようになりました。

### 実施した改善

1. **Execute Workflow Triggerノードの追加**
   - Webhookノードの下に配置
   - `inputSource: "passthrough"` で設定（すべてのデータをそのまま渡す）

2. **接続の変更**
   - 変更前: `Webhook → Notion`
   - 変更後: `Webhook → Execute Workflow Trigger → Notion`

3. **NotionノードのPage IDフィールドの修正**
   - 変更前: `={{ $json.body.script_id }}`
   - 変更後: `={{ $json.notionPageId || $json.script_id }}`
   - Execute Workflow Triggerから渡される`notionPageId`と、直接呼び出し時の`script_id`の両方に対応

---

## 🎯 Phase4bワークフローへの適用

### ワークフロー情報

- **ワークフローID**: `wHaKi98mTlUvFIOR`
- **ワークフロー名**: WF7 Phase4b - Video Generator
- **URL**: https://n8n-python-production-344b.up.railway.app/workflow/wHaKi98mTlUvFIOR

### 修正手順

#### ステップ1: ワークフローを開く

1. n8n管理画面にアクセス
2. ワークフローID `wHaKi98mTlUvFIOR` を開く
3. または直接URLにアクセス: https://n8n-python-production-344b.up.railway.app/workflow/wHaKi98mTlUvFIOR

#### ステップ2: Execute Workflow Triggerノードを追加

1. 左側のノードパネルから「Execute Workflow Trigger」を検索
2. ワークフローに追加
3. **配置位置**: Webhookノードの下（WebhookノードとNotionノードの間）
4. **設定**:
   - **Input data mode**: `Accept all data` (passthrough)
   - または `inputSource: "passthrough"` を設定

#### ステップ3: 接続を変更

1. **既存の接続を削除**:
   - WebhookノードからNotionノードへの接続を削除

2. **新しい接続を追加**:
   - Webhookノード → Execute Workflow Triggerノード
   - Execute Workflow Triggerノード → Notionノード

#### ステップ4: NotionノードのPage IDフィールドを修正

1. 「Notion - Get Script Data」（または類似のNotionノード）を開く
2. 「Page ID」フィールドを以下の式に変更:
   ```
   ={{ $json.notionPageId || $json.script_id }}
   ```
3. これにより、Execute Workflow Triggerから渡される`notionPageId`と、直接呼び出し時の`script_id`の両方に対応できます

#### ステップ5: ワークフローを保存

1. 右上の「Save」ボタンをクリック
2. 変更内容を確認

### Phase4bの確認事項

Phase4bでは、親ワークフローから以下のデータが渡されます：
- `script_id`: NotionページID
- `slides_metadata`: スライドメタデータの配列

Execute Workflow Triggerの設定で、これらのデータが正しく受け取れることを確認してください。

---

## 🎯 Phase4cワークフローへの適用

### ワークフロー情報

- **ワークフローID**: `chPw11OY5sex6d9I`
- **ワークフロー名**: WF7 Phase4c - Video Concatenator
- **URL**: https://n8n-python-production-344b.up.railway.app/workflow/chPw11OY5sex6d9I

### 修正手順

Phase4bと同様の手順で修正します。

#### ステップ1: ワークフローを開く

1. n8n管理画面にアクセス
2. ワークフローID `chPw11OY5sex6d9I` を開く
3. または直接URLにアクセス: https://n8n-python-production-344b.up.railway.app/workflow/chPw11OY5sex6d9I

#### ステップ2: Execute Workflow Triggerノードを追加

1. 左側のノードパネルから「Execute Workflow Trigger」を検索
2. ワークフローに追加
3. **配置位置**: Webhookノードの下（Webhookノードと最初の処理ノードの間）
4. **設定**:
   - **Input data mode**: `Accept all data` (passthrough)

#### ステップ3: 接続を変更

1. **既存の接続を削除**:
   - Webhookノードから最初の処理ノードへの接続を削除

2. **新しい接続を追加**:
   - Webhookノード → Execute Workflow Triggerノード
   - Execute Workflow Triggerノード → 最初の処理ノード

#### ステップ4: データ受け取りノードの修正

Phase4cでは、Notionノードがない可能性があります。その場合、最初の処理ノード（CodeノードやSetノードなど）で、以下のようにデータを受け取るように修正してください：

```javascript
// 例: Codeノードでのデータ受け取り
const scriptId = $json.notionPageId || $json.script_id;
const videosMetadata = $json.videos_metadata || $json.videos_metadata;
```

または、Setノードを使用している場合：
- `script_id`: `={{ $json.notionPageId || $json.script_id }}`
- `videos_metadata`: `={{ $json.videos_metadata }}`

#### ステップ5: ワークフローを保存

1. 右上の「Save」ボタンをクリック
2. 変更内容を確認

### Phase4cの確認事項

Phase4cでは、親ワークフローから以下のデータが渡されます：
- `script_id`: NotionページID
- `videos_metadata`: 動画メタデータの配列

Execute Workflow Triggerの設定で、これらのデータが正しく受け取れることを確認してください。

---

## ✅ 検証手順

### 1. 単体テスト

各ワークフローを単体でテストします：

#### Phase4bのテスト

1. Phase4bワークフローを開く
2. 「Execute Workflow」ボタンをクリック
3. テストデータを入力:
   ```json
   {
     "notionPageId": "テスト用のNotionページID",
     "script_id": "テスト用のNotionページID",
     "slides_metadata": [
       {
         "section": "hook",
         "duration": 3,
         "image_url": "https://example.com/slide1.png"
       }
     ]
   }
   ```
4. 実行して、エラーなく処理が完了することを確認

#### Phase4cのテスト

1. Phase4cワークフローを開く
2. 「Execute Workflow」ボタンをクリック
3. テストデータを入力:
   ```json
   {
     "notionPageId": "テスト用のNotionページID",
     "script_id": "テスト用のNotionページID",
     "videos_metadata": [
       {
         "section": "hook",
         "duration": 3,
         "video_url": "https://example.com/video1.mp4"
       }
     ]
   }
   ```
4. 実行して、エラーなく処理が完了することを確認

### 2. 統合テスト

親ワークフロー（Orchestrator）から実行して、全フェーズが正常に動作することを確認：

1. 親ワークフローを開く
2. Webhookをトリガー
3. Phase4a → Phase4b → Phase4c の順で実行されることを確認
4. 各フェーズでエラーが発生しないことを確認
5. 最終的な動画が生成されることを確認

---

## 🔍 トラブルシューティング

### 問題1: Execute Workflow Triggerからデータが渡されない

**症状**: NotionノードでPage IDが取得できない

**解決方法**:
1. Execute Workflow Triggerノードの設定を確認
   - `inputSource: "passthrough"` が設定されているか確認
2. 親ワークフローからのデータマッピングを確認
   - `notionPageId` または `script_id` が正しく渡されているか確認
3. NotionノードのPage IDフィールドの式を確認
   - `={{ $json.notionPageId || $json.script_id }}` になっているか確認

### 問題2: 接続エラーが発生する

**症状**: ノード間の接続が正しく機能しない

**解決方法**:
1. 接続の順序を確認
   - `Webhook → Execute Workflow Trigger → Notion` の順になっているか確認
2. 古い接続が残っていないか確認
   - WebhookからNotionへの直接接続が残っていないか確認

### 問題3: データ形式が異なる

**症状**: 期待するデータ形式と異なる

**解決方法**:
1. 親ワークフローからのデータマッピングを確認
2. Execute Workflow Triggerの出力データを確認
   - デバッグモードでデータを確認
3. データ受け取りノードの式を修正

---

## 📝 チェックリスト

### Phase4b適用チェックリスト

- [x] Execute Workflow Triggerノードを追加 ✅
- [x] Webhook → Execute Workflow Trigger → Code - Validate Input の接続に変更 ✅
- [x] Code - Validate Inputノードで `notionPageId || script_id` に対応 ✅
- [x] ワークフローを保存 ✅
- [ ] 単体テストを実施
- [ ] 統合テストを実施

**適用状況**: Phase4bワークフロー（`wf7_phase4b.json`）にExecute Workflow Triggerが既に適用済みです。
- Execute Workflow Triggerノードが追加され、`inputSource: "passthrough"`で設定されています
- 接続: `Webhook → Execute Workflow Trigger → Code - Validate Input`
- Code - Validate Inputノードで`notionPageId || script_id`の両方に対応しています

### Phase4c適用チェックリスト

- [x] Execute Workflow Triggerノードを追加 ✅
- [x] Webhook → Execute Workflow Trigger → Aggregate Videos の接続に変更 ✅
- [x] データ受け取りノード（ペイロード構築、Update Notion DB）で `notionPageId || script_id` に対応 ✅
- [x] ワークフローを保存 ✅
- [ ] 単体テストを実施
- [ ] 統合テストを実施

**適用状況**: Phase4cワークフロー（`wf7_phase4c_with_execute_trigger.json`）にExecute Workflow Triggerが既に適用済みです。
- Execute Workflow Triggerノードが追加され、`inputSource: "passthrough"`で設定されています
- 接続: `Webhook → Execute Workflow Trigger → Aggregate Videos`
- ペイロード構築ノードとUpdate Notion DBノードで`notionPageId || script_id`の両方に対応しています

---

## 🔗 関連ドキュメント

- [Phase4a改善実装記録](./WF7-Phase4a-ExecuteWorkflowTrigger適用記録.md)（作成予定）
- [Phase4-FAL移行-要件定義](../Phase4-FAL移行-要件定義.md)
- [WF7-Phase4-最終総合テスト計画書](../testing/WF7-Phase4-最終総合テスト計画書.md)

---

## 📅 更新履歴

- **2025-11-09**: 初版作成（Phase4aの改善をPhase4b/Phase4cに適用するための手順書）
- **2025-11-09**: 適用状況確認完了 - Phase4bとPhase4cの両方でExecute Workflow Triggerが既に適用済みであることを確認

---

## 💡 補足情報

### Execute Workflow Triggerの動作

Execute Workflow Triggerノードは、親ワークフローからExecute Workflowノード経由で呼び出された際に、渡されたデータをそのまま出力します。

- **親ワークフローからの呼び出し**: Execute Workflow Triggerがデータを受け取り、そのまま次のノードに渡す
- **直接Webhook呼び出し**: WebhookノードからExecute Workflow Triggerを経由してデータが渡される

このため、両方の呼び出し方法に対応できるようになります。

### データフロー

```
親ワークフロー（Orchestrator）
  ↓ Execute Workflow
Phase4b/Phase4c
  ↓ Webhook → Execute Workflow Trigger → 処理ノード
```

この構成により、親ワークフローからの呼び出しと、直接Webhook呼び出しの両方に対応できます。

